# Updated: 2025-07-27T12:58:15-05:00
"""
Healthcare Provider Patient Management Dashboard
FastAPI Backend Application Entry Point
"""

# Configure logging FIRST before any other imports
from app.config.logging import configure_logging, get_logger
configure_logging()

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config.settings import get_settings
from app.core.middleware import (
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestValidationMiddleware,
)
from app.core.exceptions import (
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ExternalServiceException,
    DatabaseException,
)
from app.database.connection import init_database, close_database
from app.cache.surreal_cache_manager import initialize_cache, close_cache
from app.api.v1 import (
    auth,
    patients,
    users,
    dashboard,
    alerts,
    analytics,
    insurance,
    reports,
    webhooks,
    chat,
)

# Get configuration
settings = get_settings()

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Patient Dashboard API...")

    # Initialize database connection
    await init_database()
    logger.info("Database connection initialized")

    # Initialize SurrealDB cache
    try:
        await initialize_cache()
        logger.info("SurrealDB cache initialized")
    except Exception as e:
        logger.warning(f"Cache initialization skipped: {e}")
        # Continue without cache for development

    # Initialize monitoring
    if settings.ENABLE_METRICS:
        logger.info("Metrics collection enabled")

    logger.info("Patient Dashboard API started successfully")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down Patient Dashboard API...")

    # Close database connection
    await close_database()
    logger.info("Database connection closed")

    # Close SurrealDB cache
    await close_cache()
    logger.info("SurrealDB cache closed")

    logger.info("Patient Dashboard API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Patient Management Dashboard API",
    description="Healthcare Provider Patient Management System with HIPAA compliance",
    version="1.0.0",
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

# Security middleware
# Temporarily disabled TrustedHostMiddleware for development
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=settings.ALLOWED_HOSTS,
# )

app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Cache-Control",
        "X-File-Name",
    ],
    expose_headers=["X-Total-Count", "X-Page-Count"],
)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestValidationMiddleware)

if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.RATE_LIMIT_REQUESTS
    )


# Exception handlers
@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions."""
    logger.warning(f"Validation error: {exc.detail}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "detail": exc.detail,
            "timestamp": time.time(),
        },
    )


@app.exception_handler(AuthenticationException)
async def authentication_exception_handler(request: Request, exc: AuthenticationException):
    """Handle authentication exceptions."""
    logger.warning(f"Authentication error: {exc.detail}")
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication Required",
            "detail": exc.detail,
            "timestamp": time.time(),
        },
    )


@app.exception_handler(AuthorizationException)
async def authorization_exception_handler(request: Request, exc: AuthorizationException):
    """Handle authorization exceptions."""
    logger.warning(f"Authorization error: {exc.detail}")
    return JSONResponse(
        status_code=403,
        content={
            "error": "Access Forbidden",
            "detail": exc.detail,
            "timestamp": time.time(),
        },
    )


@app.exception_handler(BusinessLogicException)
async def business_logic_exception_handler(request: Request, exc: BusinessLogicException):
    """Handle business logic exceptions."""
    logger.error(f"Business logic error: {exc.detail}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Business Logic Error",
            "detail": exc.detail,
            "timestamp": time.time(),
        },
    )


@app.exception_handler(ExternalServiceException)
async def external_service_exception_handler(request: Request, exc: ExternalServiceException):
    """Handle external service exceptions."""
    logger.error(f"External service error: {exc.detail}")
    return JSONResponse(
        status_code=503,
        content={
            "error": "External Service Unavailable",
            "detail": "A required external service is currently unavailable. Please try again later.",
            "timestamp": time.time(),
        },
    )


@app.exception_handler(DatabaseException)
async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle database exceptions."""
    logger.error(f"Database error: {exc.detail}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "detail": "A database error occurred. Please try again later.",
            "timestamp": time.time(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": time.time(),
        },
    )


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with service status."""
    from app.integrations.monitoring.health_checker import HealthChecker

    health_checker = HealthChecker()
    health_status = await health_checker.check_all_services()

    return {
        "status": "healthy" if health_status["overall_healthy"] else "unhealthy",
        "timestamp": time.time(),
        "services": health_status["services"],
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


# API version info
@app.get("/version", tags=["Info"])
async def get_version():
    """Get API version information."""
    return {
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "build_time": "2025-07-25T10:00:00Z",
        "python_version": "3.11+",
        "features": {
            "patient_management": True,
            "insurance_integration": True,
            "real_time_alerts": True,
            "hipaa_compliance": True,
            "audit_logging": True,
        },
    }


# Include API routers
API_V1_PREFIX = "/api/v1"

app.include_router(
    auth,
    prefix=f"{API_V1_PREFIX}/auth",
    tags=["Authentication"],
)

app.include_router(
    patients,
    prefix=f"{API_V1_PREFIX}/patients",
    tags=["Patients"],
)

app.include_router(
    users,
    prefix=f"{API_V1_PREFIX}/users",
    tags=["Users"],
)

app.include_router(
    dashboard,
    prefix=f"{API_V1_PREFIX}/dashboard",
    tags=["Dashboard"],
)

app.include_router(
    alerts,
    prefix=f"{API_V1_PREFIX}/alerts",
    tags=["Alerts"],
)

app.include_router(
    analytics,
    prefix=f"{API_V1_PREFIX}/analytics",
    tags=["Analytics"],
)

app.include_router(
    insurance,
    prefix=f"{API_V1_PREFIX}/insurance",
    tags=["Insurance"],
)

app.include_router(
    reports,
    prefix=f"{API_V1_PREFIX}/reports",
    tags=["Reports"],
)

app.include_router(
    webhooks,
    prefix=f"{API_V1_PREFIX}/webhooks",
    tags=["Webhooks"],
)

app.include_router(
    chat,
    prefix=f"{API_V1_PREFIX}/chat",
    tags=["AI Chat"],
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint with basic information."""
    return {
        "message": "Healthcare Provider Patient Management Dashboard API",
        "version": "1.0.0",
        "documentation": "/docs" if settings.ENVIRONMENT != "production" else None,
        "health": "/health",
        "status": "operational",
    }


# Add request ID to all responses
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to all responses."""
    import uuid

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


# Metrics endpoint (if enabled)
if settings.ENABLE_METRICS:
    @app.get("/metrics", tags=["Monitoring"])
    async def get_metrics():
        """Prometheus-compatible metrics endpoint."""
        from app.integrations.monitoring.metrics_collector import MetricsCollector

        metrics_collector = MetricsCollector()
        metrics = await metrics_collector.get_prometheus_metrics()

        return Response(
            content=metrics,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_config=None,  # Use our custom logging configuration
    )
