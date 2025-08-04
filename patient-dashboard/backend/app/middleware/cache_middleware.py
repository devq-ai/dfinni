"""
Response caching middleware for API performance optimization.
Per Production Proposal Phase 2: Implement response caching
"""
import hashlib
import json
import time
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logfire

from app.cache.surreal_cache_manager import surreal_cache_manager
from app.config.settings import get_settings

settings = get_settings()


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for caching API responses."""
    
    # Cache configuration by endpoint pattern
    CACHE_CONFIG = {
        # Dashboard endpoints - cache for 1 minute
        "/api/v1/dashboard/metrics": {"ttl": 60, "vary_by": ["user_id"]},
        "/api/v1/dashboard/patients/overview": {"ttl": 60, "vary_by": ["user_id"]},
        "/api/v1/dashboard/alerts/overview": {"ttl": 30, "vary_by": ["user_id"]},
        "/api/v1/dashboard/analytics/time-series": {"ttl": 300, "vary_by": ["user_id", "metric", "start_date", "end_date"]},
        "/api/v1/dashboard/provider/stats": {"ttl": 120, "vary_by": ["user_id"]},
        "/api/v1/dashboard/activities/recent": {"ttl": 30, "vary_by": ["user_id", "limit"]},
        
        # Patient list endpoints - cache for 30 seconds
        "/api/v1/patients": {"ttl": 30, "vary_by": ["user_id", "skip", "limit", "status", "search"]},
        "/api/v1/patients/statistics": {"ttl": 120, "vary_by": []},
        
        # Alert endpoints - cache for 30 seconds
        "/api/v1/alerts": {"ttl": 30, "vary_by": ["user_id", "patient_id", "severity", "status"]},
        
        # Analytics endpoints - cache for 5 minutes
        "/api/v1/analytics/patient-trends": {"ttl": 300, "vary_by": ["period"]},
        "/api/v1/analytics/adherence-metrics": {"ttl": 300, "vary_by": ["patient_id", "start_date", "end_date"]},
        "/api/v1/analytics/provider-performance": {"ttl": 300, "vary_by": ["provider_id", "period"]},
        
        # Reports - cache for 10 minutes
        "/api/v1/reports": {"ttl": 600, "vary_by": ["user_id", "type", "period"]},
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.cache_client = None
        self.cache_enabled = settings.CACHE_ENABLED
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with caching logic."""
        # Skip caching if disabled or not a GET request
        if not self.cache_enabled or request.method != "GET":
            return await call_next(request)
        
        # Skip caching for non-cacheable endpoints
        cache_config = self._get_cache_config(request.url.path)
        if not cache_config:
            return await call_next(request)
        
        # Initialize SurrealDB cache client if needed
        if not self.cache_client:
            try:
                self.cache_client = surreal_cache_manager.get_client()
                if not self.cache_client:
                    raise RuntimeError("SurrealDB cache not initialized")
            except Exception as e:
                logfire.warning("SurrealDB cache not available, caching disabled", error=str(e))
                self.cache_enabled = False
                return await call_next(request)
        
        # Generate cache key
        cache_key = await self._generate_cache_key(request, cache_config)
        
        # Try to get from cache
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            logfire.info(
                "Cache hit",
                path=request.url.path,
                cache_key=cache_key
            )
            return self._build_cached_response(cached_response)
        
        # Process request and cache response
        response = await call_next(request)
        
        # Only cache successful responses
        if 200 <= response.status_code < 300:
            await self._cache_response(
                cache_key,
                response,
                cache_config["ttl"]
            )
            logfire.info(
                "Response cached",
                path=request.url.path,
                cache_key=cache_key,
                ttl=cache_config["ttl"]
            )
        
        return response
    
    def _get_cache_config(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cache configuration for a given path."""
        # Direct match
        if path in self.CACHE_CONFIG:
            return self.CACHE_CONFIG[path]
        
        # Pattern matching for parameterized paths
        for pattern, config in self.CACHE_CONFIG.items():
            if self._path_matches_pattern(path, pattern):
                return config
        
        return None
    
    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a pattern (simple implementation)."""
        # Remove query parameters
        path = path.split("?")[0]
        
        # Simple pattern matching for now
        if "{" in pattern:
            # For patterns with parameters, just check the base
            pattern_base = pattern.split("{")[0]
            return path.startswith(pattern_base)
        
        return path == pattern
    
    async def _generate_cache_key(self, request: Request, cache_config: Dict[str, Any]) -> str:
        """Generate a cache key based on request and configuration."""
        # Base key components
        key_parts = [
            "cache",
            request.method,
            request.url.path
        ]
        
        # Add vary-by parameters
        vary_by = cache_config.get("vary_by", [])
        
        # Add user_id if specified
        if "user_id" in vary_by:
            user = getattr(request.state, "user", None)
            if user:
                key_parts.append(f"user:{user.id}")
        
        # Add query parameters if specified
        for param in vary_by:
            if param not in ["user_id"]:  # Skip already handled
                value = request.query_params.get(param)
                if value:
                    key_parts.append(f"{param}:{value}")
        
        # Generate hash of key parts
        key_string = ":".join(key_parts)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:16]
        
        return f"response_cache:{key_hash}"
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response from SurrealDB."""
        try:
            # Query SurrealDB for cached response
            result = await self.cache_client.query(
                "SELECT * FROM cache WHERE id = $id AND expires_at > time::now()",
                {"id": cache_key}
            )
            
            if result and len(result) > 0 and result[0].get('result'):
                cached_record = result[0]['result'][0]
                return cached_record.get('data')
            return None
        except Exception as e:
            logfire.error("Failed to get cached response", error=str(e), cache_key=cache_key)
            return None
    
    async def _cache_response(self, cache_key: str, response: Response, ttl: int):
        """Cache response in SurrealDB."""
        try:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Cache the response data
            cache_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body.decode("utf-8"),
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": ttl
            }
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            
            # Store in SurrealDB with TTL
            await self.cache_client.query(
                """
                CREATE cache:⟨$id⟩ SET
                    data = $data,
                    expires_at = $expires_at,
                    created_at = time::now()
                """,
                {
                    "id": cache_key,
                    "data": cache_data,
                    "expires_at": expires_at.isoformat()
                }
            )
            
            # Recreate response body iterator
            async def body_iterator():
                yield body
            
            response.body_iterator = body_iterator()
            
        except Exception as e:
            logfire.error("Failed to cache response", error=str(e), cache_key=cache_key)
    
    def _build_cached_response(self, cached_data: Dict[str, Any]) -> Response:
        """Build response from cached data."""
        response = Response(
            content=cached_data["body"],
            status_code=cached_data["status_code"],
            headers=cached_data["headers"]
        )
        
        # Add cache headers
        cached_at = datetime.fromisoformat(cached_data["cached_at"])
        age = int((datetime.utcnow() - cached_at).total_seconds())
        
        response.headers["X-Cache"] = "HIT"
        response.headers["X-Cache-Age"] = str(age)
        response.headers["X-Cache-TTL"] = str(cached_data["ttl"])
        
        return response


class CacheControl:
    """Decorator for fine-grained cache control on endpoints."""
    
    @staticmethod
    def cache(ttl: int = 60, vary_by: Optional[list] = None, private: bool = False):
        """
        Decorator to add cache control headers to responses.
        
        Args:
            ttl: Time to live in seconds
            vary_by: List of parameters to vary cache by
            private: Whether cache is private (user-specific)
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                response = await func(*args, **kwargs)
                
                if isinstance(response, Response):
                    # Add cache control headers
                    cache_control = []
                    
                    if private:
                        cache_control.append("private")
                    else:
                        cache_control.append("public")
                    
                    cache_control.append(f"max-age={ttl}")
                    
                    if ttl == 0:
                        cache_control.append("no-cache")
                        cache_control.append("must-revalidate")
                    
                    response.headers["Cache-Control"] = ", ".join(cache_control)
                    
                    # Add vary header
                    if vary_by:
                        vary_values = []
                        if "user_id" in vary_by:
                            vary_values.append("Authorization")
                        if any(p in vary_by for p in ["skip", "limit", "search"]):
                            vary_values.append("Accept")
                        
                        if vary_values:
                            response.headers["Vary"] = ", ".join(vary_values)
                    
                    # Add ETag for conditional requests
                    if hasattr(response, "body"):
                        etag = hashlib.md5(response.body).hexdigest()
                        response.headers["ETag"] = f'"{etag}"'
                
                return response
            
            return wrapper
        return decorator
    
    @staticmethod
    def no_cache():
        """Decorator to prevent caching of responses."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                response = await func(*args, **kwargs)
                
                if isinstance(response, Response):
                    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                    response.headers["Pragma"] = "no-cache"
                    response.headers["Expires"] = "0"
                
                return response
            
            return wrapper
        return decorator