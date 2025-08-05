"""
Health check endpoint for monitoring and load balancer health checks.
"""
from fastapi import APIRouter, Response, status
from typing import Dict, Any
import asyncio
import logfire
from datetime import datetime
from app.database.connection import get_database
from app.config.settings import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/health")
@logfire.instrument("health_check")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.
    Returns system health status and database connectivity.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "services": {
            "api": "healthy",
            "database": "unknown"
        }
    }
    
    # Check database connection
    try:
        db = await get_database()
        # Simple query with timeout
        result = await asyncio.wait_for(
            db.execute("SELECT 1"),
            timeout=5.0
        )
        health_status["services"]["database"] = "healthy"
        logfire.info("Health check passed", services=health_status["services"])
    except asyncio.TimeoutError:
        health_status["status"] = "degraded"
        health_status["services"]["database"] = "timeout"
        logfire.warning("Database health check timeout")
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = "error"
        health_status["error"] = str(e)
        logfire.error("Database health check failed", error=str(e))
    
    # Return appropriate status code
    if health_status["status"] == "unhealthy":
        return Response(
            content=health_status,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json"
        )
    
    return health_status

@router.get("/health/detailed")
@logfire.instrument("detailed_health_check")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with additional system information.
    Should be protected in production.
    """
    basic_health = await health_check()
    
    detailed_status = {
        **basic_health,
        "version": "1.0.0",
        "uptime": "N/A",  # Would need to track application start time
        "configuration": {
            "debug": settings.DEBUG,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "cache_enabled": settings.CACHE_ENABLED,
            "features": {
                "insurance_integration": settings.ENABLE_INSURANCE_INTEGRATION,
                "real_time_alerts": settings.ENABLE_REAL_TIME_ALERTS,
                "birthday_alerts": settings.ENABLE_BIRTHDAY_ALERTS,
            }
        }
    }
    
    # Database detailed check
    if basic_health["services"]["database"] == "healthy":
        try:
            db = await get_database()
            db_info = await db.execute("INFO FOR DB")
            detailed_status["database_info"] = {
                "connected": True,
                "namespace": settings.DATABASE_NAMESPACE,
                "database": settings.DATABASE_NAME
            }
        except Exception as e:
            detailed_status["database_info"] = {
                "connected": False,
                "error": str(e)
            }
    
    return detailed_status