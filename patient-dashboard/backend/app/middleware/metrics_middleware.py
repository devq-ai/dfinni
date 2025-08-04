"""
Metrics middleware for automatic API performance tracking.
Per Production Proposal Phase 2: Add comprehensive Logfire metrics
"""
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.metrics_service import metrics_service


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically track API metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.exclude_paths = {
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track metrics."""
        # Skip metrics for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Extract request metadata
        method = request.method
        path = request.url.path
        user_id = None
        user_role = None
        
        # Try to get user info from request state
        if hasattr(request.state, "user") and request.state.user:
            user = request.state.user
            user_id = user.id
            user_role = user.role
        
        # Track request start
        request_id = f"{method}:{path}:{start_time}"
        
        # Process request
        response = None
        error = None
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            error = e
            # Track error
            metrics_service.track_error(
                error_type=type(e).__name__,
                error_message=str(e),
                user_id=user_id,
                method=method,
                path=path
            )
            raise
            
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Determine status code
            status_code = response.status_code if response else 500
            
            # Track API request
            metrics_service.track_api_request(
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                user_id=user_id,
                user_role=user_role,
                error=str(error) if error else None
            )
            
            # Track slow requests
            if duration_ms > 1000:  # Requests taking more than 1 second
                metrics_service.track_custom_metric(
                    "slow_request",
                    value=duration_ms,
                    unit="milliseconds",
                    method=method,
                    path=path,
                    user_id=user_id
                )
            
            # Track specific endpoint metrics
            self._track_endpoint_specific_metrics(
                method, path, status_code, duration_ms, request, response
            )
    
    def _track_endpoint_specific_metrics(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        request: Request,
        response: Response
    ):
        """Track metrics specific to certain endpoints."""
        # Dashboard metrics
        if path == "/api/v1/dashboard/metrics" and status_code == 200:
            metrics_service.track_dashboard_load(
                user_id=getattr(request.state, "user", {}).get("id", "unknown"),
                load_time_ms=duration_ms,
                widget_count=8  # Default widget count
            )
        
        # Patient operations
        elif path.startswith("/api/v1/patients"):
            if method == "POST" and status_code == 201:
                # New patient created
                try:
                    # Try to get patient ID from response
                    if hasattr(response, "body"):
                        body = json.loads(response.body)
                        metrics_service.track_patient_created(
                            patient_id=body.get("id"),
                            created_by=getattr(request.state, "user", {}).get("id", "unknown")
                        )
                except:
                    pass
            
            elif method == "GET" and "/search" in path:
                # Patient search
                metrics_service.track_custom_metric(
                    "patient_search",
                    value=1,
                    duration_ms=duration_ms,
                    query=request.query_params.get("q", "")
                )
        
        # Alert operations
        elif path.startswith("/api/v1/alerts"):
            if method == "POST" and status_code == 201:
                # New alert created
                metrics_service.track_custom_metric(
                    "alert_created",
                    value=1
                )
            elif method == "PATCH" and "resolve" in path:
                # Alert resolved
                metrics_service.track_custom_metric(
                    "alert_resolved",
                    value=1
                )
        
        # Authentication
        elif path == "/api/v1/auth/login":
            if status_code == 200:
                # Successful login
                metrics_service.track_user_login(
                    user_id="pending",  # Will be in response
                    user_role="pending",
                    auth_method="internal"
                )
            else:
                # Failed login
                metrics_service.track_auth_failure(
                    reason="invalid_credentials",
                    ip_address=request.client.host if request.client else None
                )
        
        # Data exports
        elif "export" in path and status_code == 200:
            metrics_service.track_data_export(
                user_id=getattr(request.state, "user", {}).get("id", "unknown"),
                export_type=path.split("/")[-1],
                record_count=0  # Would need to parse response
            )