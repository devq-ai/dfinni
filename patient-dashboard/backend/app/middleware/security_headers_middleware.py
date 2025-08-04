"""
Security headers middleware for HIPAA compliance and general security best practices.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logfire


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy - strict by default
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
        
        # Strict Transport Security - enforce HTTPS
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
        
        # Log security headers applied
        with logfire.span("security_headers_applied"):
            logfire.info(
                "Security headers added",
                path=request.url.path,
                method=request.method,
                has_csp=True,
                has_hsts=True,
                has_frame_options=True
            )
        
        return response