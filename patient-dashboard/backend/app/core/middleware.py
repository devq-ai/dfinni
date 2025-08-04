"""
Core middleware for security, logging, and request handling.
"""
import time
import uuid
import json
from typing import Callable, Dict, Any
from datetime import datetime

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.core.exceptions import RateLimitException
from app.core.rate_limiter import RateLimitMiddleware as EnhancedRateLimitMiddleware

logger = structlog.get_logger()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add enhanced security headers for HIPAA compliance."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Content Security Policy - strict with Clerk support
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://clerk.*.lcl.dev https://*.clerk.accounts.dev; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://clerk.*.lcl.dev https://*.clerk.accounts.dev ws://localhost:* wss://localhost:* http://localhost:8001 https://api.pfinni.com; "
            "frame-src 'self' https://clerk.*.lcl.dev https://*.clerk.accounts.dev; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests;"
        )
        
        # Strict Transport Security - enforce HTTPS with preload
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer policy for privacy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy - disable unnecessary features
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "camera=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        
        # HIPAA-specific headers
        response.headers["X-HIPAA-Compliance"] = "enabled"
        response.headers["X-Data-Classification"] = "PHI"
        
        # Remove server header for security
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Log security headers applied (with request_id if available)
        request_id = getattr(request.state, 'request_id', 'unknown')
        logger.info(
            "security_headers_applied",
            request_id=request_id,
            path=request.url.path,
            method=request.method
        )
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses with request ID tracking."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "request_completed",
                request_id=request_id,
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2)
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                request_id=request_id,
                error=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client identifier (IP address)
        client_id = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        # Current timestamp
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old requests
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove requests older than 1 minute
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            logger.warning(
                "rate_limit_exceeded",
                client_id=client_id,
                requests_count=len(self.requests[client_id])
            )
            raise RateLimitException(retry_after=60)
        
        # Record this request
        self.requests[client_id].append(now)
        
        # Process request
        return await call_next(request)

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize incoming requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip validation for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
            
        # Check content type for POST/PUT requests (skip OAuth2 form login)
        if request.method in ["POST", "PUT", "PATCH"] and request.url.path != "/api/v1/auth/login":
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json") and not content_type.startswith("multipart/form-data") and not content_type.startswith("application/x-www-form-urlencoded"):
                return JSONResponse(
                    status_code=415,
                    content={
                        "error_code": "UNSUPPORTED_MEDIA_TYPE",
                        "message": "Content-Type must be application/json or multipart/form-data"
                    }
                )
        
        # Check for suspiciously large requests
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                # 10MB limit
                if length > 10 * 1024 * 1024:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error_code": "PAYLOAD_TOO_LARGE",
                            "message": "Request body too large"
                        }
                    )
            except ValueError:
                pass
        
        return await call_next(request)

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log all data access for HIPAA compliance."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for health checks and static assets
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Capture request details
        request_data = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store for potential audit logging
        request.state.audit_data = request_data
        
        # Process request
        response = await call_next(request)
        
        # Log if this was a data access request
        if response.status_code < 400 and any(
            resource in request.url.path 
            for resource in ["/patients", "/users", "/alerts"]
        ):
            # This would be logged to audit_log table
            # Implementation depends on having user context
            pass
        
        return response