"""
Enhanced rate limiting using SurrealDB for distributed rate limiting.
Supports both global and per-endpoint rate limits with sliding window algorithm.
"""
import time
import logfire
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.database.connection import get_database
from app.config.settings import get_settings

settings = get_settings()


class RateLimiter:
    """
    Distributed rate limiter using SurrealDB.
    Implements sliding window algorithm for accurate rate limiting.
    """
    
    def __init__(
        self,
        requests: int = 100,
        window: int = 60,
        identifier: Optional[str] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests: Number of allowed requests
            window: Time window in seconds
            identifier: Optional identifier for per-endpoint limits
        """
        self.requests = requests
        self.window = window
        self.identifier = identifier or "global"
    
    async def check_rate_limit(
        self,
        key: str,
        requests: Optional[int] = None,
        window: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit.
        
        Returns:
            Tuple of (is_allowed, metadata)
        """
        requests = requests or self.requests
        window = window or self.window
        
        try:
            db = await get_database()
            now = time.time()
            window_start = now - window
            
            # Create rate limit bucket key
            bucket_key = f"rate_limit:{self.identifier}:{key}"
            
            # Clean old entries and count recent requests
            result = await db.execute("""
                BEGIN TRANSACTION;
                
                -- Delete old entries
                DELETE rate_limit_entry WHERE 
                    bucket = $bucket AND 
                    timestamp < $window_start;
                
                -- Count recent requests
                LET $count = (
                    SELECT count() as total
                    FROM rate_limit_entry
                    WHERE bucket = $bucket
                    AND timestamp >= $window_start
                    GROUP ALL
                );
                
                -- Check if under limit
                LET $allowed = IF $count[0].total < $requests THEN true ELSE false END;
                
                -- If allowed, add new entry
                IF $allowed THEN
                    CREATE rate_limit_entry SET
                        bucket = $bucket,
                        timestamp = $now,
                        created_at = time::now()
                END;
                
                -- Return result
                RETURN {
                    allowed: $allowed,
                    current: IF $count[0].total THEN $count[0].total ELSE 0 END,
                    limit: $requests,
                    window: $window,
                    reset: $window_start + $window
                };
                
                COMMIT TRANSACTION;
            """, {
                "bucket": bucket_key,
                "window_start": window_start,
                "now": now,
                "requests": requests,
                "window": window
            })
            
            if result and len(result) > 0:
                rate_limit_info = result[-1]['result']
                if isinstance(rate_limit_info, list) and len(rate_limit_info) > 0:
                    rate_limit_info = rate_limit_info[0]
                
                metadata = {
                    "X-RateLimit-Limit": str(rate_limit_info.get('limit', requests)),
                    "X-RateLimit-Remaining": str(max(0, rate_limit_info.get('limit', requests) - rate_limit_info.get('current', 0))),
                    "X-RateLimit-Reset": str(int(rate_limit_info.get('reset', now + window))),
                    "X-RateLimit-Window": str(rate_limit_info.get('window', window))
                }
                
                return rate_limit_info.get('allowed', True), metadata
            
            # Default to allowing if query fails
            return True, {
                "X-RateLimit-Limit": str(requests),
                "X-RateLimit-Remaining": str(requests),
                "X-RateLimit-Reset": str(int(now + window)),
                "X-RateLimit-Window": str(window)
            }
            
        except Exception as e:
            logfire.error("Rate limit check failed", error=str(e))
            # Fail open - allow request if rate limiting fails
            return True, {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Enhanced rate limiting middleware with distributed storage.
    """
    
    def __init__(
        self,
        app,
        global_limits: Dict[str, Dict[str, int]] = None,
        endpoint_limits: Dict[str, Dict[str, int]] = None
    ):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI app
            global_limits: Global rate limits by method
            endpoint_limits: Per-endpoint rate limits
        """
        super().__init__(app)
        self.global_limits = global_limits or {
            "GET": {"requests": 100, "window": 60},
            "POST": {"requests": 50, "window": 60},
            "PUT": {"requests": 50, "window": 60},
            "DELETE": {"requests": 20, "window": 60}
        }
        self.endpoint_limits = endpoint_limits or {}
        self._init_endpoint_limits()
    
    def _init_endpoint_limits(self):
        """Initialize default endpoint-specific limits for auth endpoints."""
        auth_endpoints = {
            "/api/v1/auth/login": {"requests": 5, "window": 300},  # 5 per 5 minutes
            "/api/v1/auth/register": {"requests": 3, "window": 3600},  # 3 per hour
            "/api/v1/auth/forgot-password": {"requests": 3, "window": 3600},  # 3 per hour
            "/api/v1/auth/reset-password": {"requests": 3, "window": 3600},  # 3 per hour
            "/api/v1/auth/change-password": {"requests": 5, "window": 3600},  # 5 per hour
            "/api/v1/auth/refresh": {"requests": 10, "window": 300},  # 10 per 5 minutes
        }
        
        # Merge with any provided endpoint limits
        for endpoint, limits in auth_endpoints.items():
            if endpoint not in self.endpoint_limits:
                self.endpoint_limits[endpoint] = limits
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            response = await call_next(request)
            return response
        
        # Skip if rate limiting is disabled
        if not settings.RATE_LIMIT_ENABLED:
            response = await call_next(request)
            return response
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check endpoint-specific limits first
        endpoint_limit = self.endpoint_limits.get(request.url.path)
        if endpoint_limit:
            limiter = RateLimiter(
                requests=endpoint_limit["requests"],
                window=endpoint_limit["window"],
                identifier=f"endpoint:{request.url.path}"
            )
            allowed, metadata = await limiter.check_rate_limit(client_id)
            
            if not allowed:
                logfire.warning(
                    "Endpoint rate limit exceeded",
                    client_id=client_id,
                    endpoint=request.url.path,
                    limit=endpoint_limit
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded for this endpoint",
                    headers=metadata
                )
        
        # Check global method-based limits
        method_limit = self.global_limits.get(request.method, self.global_limits.get("GET"))
        limiter = RateLimiter(
            requests=method_limit["requests"],
            window=method_limit["window"],
            identifier=f"global:{request.method}"
        )
        allowed, metadata = await limiter.check_rate_limit(client_id)
        
        if not allowed:
            logfire.warning(
                "Global rate limit exceeded",
                client_id=client_id,
                method=request.method,
                limit=method_limit
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers=metadata
            )
        
        # Process request and add rate limit headers to response
        response = await call_next(request)
        
        # Add rate limit headers
        for header, value in metadata.items():
            response.headers[header] = value
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        Uses IP address, but could be extended to use API keys or user IDs.
        """
        # Try to get real IP from proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Could also incorporate user ID if authenticated
        # if hasattr(request.state, "user"):
        #     return f"user:{request.state.user.id}"
        
        return f"ip:{client_ip}"


def create_rate_limit_table_sql() -> str:
    """SQL to create rate limit table in SurrealDB."""
    return """
    -- Define rate limit entry table
    DEFINE TABLE rate_limit_entry SCHEMALESS;
    
    -- Define indexes for efficient queries
    DEFINE INDEX rate_limit_bucket_idx ON TABLE rate_limit_entry COLUMNS bucket;
    DEFINE INDEX rate_limit_timestamp_idx ON TABLE rate_limit_entry COLUMNS timestamp;
    DEFINE INDEX rate_limit_composite_idx ON TABLE rate_limit_entry COLUMNS bucket, timestamp;
    
    -- Add cleanup event to remove old entries (runs every hour)
    -- Note: This is a conceptual example, actual implementation depends on SurrealDB version
    """