"""
Audit middleware for automatically logging all API requests.
Per Production Proposal: Implement audit logging for all data access
"""
import time
import json
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.services.audit_service import audit_service, AuditAction, AuditResource
from app.api.v1.auth import get_current_user_optional


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to audit all API requests."""
    
    # Map HTTP methods and paths to audit actions and resources
    AUDIT_MAPPING = {
        # Patient endpoints
        ("GET", "/api/v1/patients"): (AuditAction.LIST, AuditResource.PATIENT),
        ("GET", "/api/v1/patients/{id}"): (AuditAction.VIEW, AuditResource.PATIENT),
        ("POST", "/api/v1/patients"): (AuditAction.CREATE, AuditResource.PATIENT),
        ("PUT", "/api/v1/patients/{id}"): (AuditAction.UPDATE, AuditResource.PATIENT),
        ("PATCH", "/api/v1/patients/{id}"): (AuditAction.UPDATE, AuditResource.PATIENT),
        ("DELETE", "/api/v1/patients/{id}"): (AuditAction.DELETE, AuditResource.PATIENT),
        ("GET", "/api/v1/patients/search"): (AuditAction.SEARCH, AuditResource.PATIENT),
        
        # User endpoints
        ("GET", "/api/v1/users"): (AuditAction.LIST, AuditResource.USER),
        ("GET", "/api/v1/users/{id}"): (AuditAction.VIEW, AuditResource.USER),
        ("POST", "/api/v1/users"): (AuditAction.CREATE, AuditResource.USER),
        ("PUT", "/api/v1/users/{id}"): (AuditAction.UPDATE, AuditResource.USER),
        ("DELETE", "/api/v1/users/{id}"): (AuditAction.DELETE, AuditResource.USER),
        
        # Authentication endpoints
        ("POST", "/api/v1/auth/login"): (AuditAction.LOGIN, AuditResource.SYSTEM),
        ("POST", "/api/v1/auth/logout"): (AuditAction.LOGOUT, AuditResource.SYSTEM),
        ("POST", "/api/v1/auth/refresh"): (AuditAction.TOKEN_REFRESH, AuditResource.SYSTEM),
        ("POST", "/api/v1/auth/change-password"): (AuditAction.PASSWORD_CHANGE, AuditResource.SYSTEM),
        ("POST", "/api/v1/auth/reset-password"): (AuditAction.PASSWORD_RESET, AuditResource.SYSTEM),
        
        # Dashboard endpoints
        ("GET", "/api/v1/dashboard"): (AuditAction.VIEW, AuditResource.DASHBOARD),
        ("GET", "/api/v1/dashboard/metrics"): (AuditAction.VIEW, AuditResource.DASHBOARD),
        ("POST", "/api/v1/dashboard/export"): (AuditAction.EXPORT, AuditResource.DASHBOARD),
        
        # Alert endpoints
        ("GET", "/api/v1/alerts"): (AuditAction.LIST, AuditResource.ALERT),
        ("GET", "/api/v1/alerts/{id}"): (AuditAction.VIEW, AuditResource.ALERT),
        ("POST", "/api/v1/alerts"): (AuditAction.CREATE, AuditResource.ALERT),
        ("PUT", "/api/v1/alerts/{id}"): (AuditAction.UPDATE, AuditResource.ALERT),
        
        # Report endpoints
        ("GET", "/api/v1/reports"): (AuditAction.LIST, AuditResource.REPORT),
        ("POST", "/api/v1/reports/generate"): (AuditAction.CREATE, AuditResource.REPORT),
        ("GET", "/api/v1/reports/export"): (AuditAction.EXPORT, AuditResource.REPORT),
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and audit it."""
        # Skip audit for health checks and docs
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")
        
        # Initialize audit details
        user_id = "anonymous"
        user_email = "anonymous"
        user_role = "guest"
        session_id = None
        resource_id = None
        patient_id = None
        error_message = None
        success = True
        
        try:
            # Try to get current user from request state
            if hasattr(request.state, "user") and request.state.user:
                user = request.state.user
                user_id = user.id
                user_email = user.email
                user_role = user.role
            
            # Get session ID from headers or cookies
            session_id = request.headers.get("x-session-id") or request.cookies.get("session_id")
            
            # Extract resource ID from path if present
            path_parts = path.split("/")
            if "{id}" in str(request.url) or (len(path_parts) > 4 and path_parts[-1]):
                # Try to extract ID from path
                potential_id = path_parts[-1]
                if potential_id and not potential_id.startswith("?"):
                    resource_id = potential_id
            
            # Process the request
            response = await call_next(request)
            
            # Check response status
            success = 200 <= response.status_code < 400
            if not success:
                error_message = f"HTTP {response.status_code}"
            
        except Exception as e:
            # Log the error and return 500
            error_message = str(e)
            success = False
            response = Response(
                content=json.dumps({"detail": "Internal server error"}),
                status_code=500,
                media_type="application/json"
            )
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Determine audit action and resource
        audit_info = self._get_audit_info(method, path)
        if audit_info:
            action, resource = audit_info
            
            # Special handling for patient-related endpoints
            if resource == AuditResource.PATIENT and resource_id:
                patient_id = resource_id
            
            # Check if request body contains patient_id
            if method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        data = json.loads(body)
                        if "patient_id" in data:
                            patient_id = data["patient_id"]
                except:
                    pass
            
            # Log the audit entry
            details = {
                "method": method,
                "path": path,
                "duration_ms": round(duration * 1000, 2),
                "status_code": response.status_code
            }
            
            await audit_service.log(
                user_id=user_id,
                user_email=user_email,
                user_role=user_role,
                action=action,
                resource=resource,
                resource_id=resource_id,
                details=details,
                ip_address=client_ip,
                user_agent=user_agent,
                session_id=session_id,
                success=success,
                error_message=error_message,
                patient_id=patient_id,
                phi_accessed=(resource == AuditResource.PATIENT and success)
            )
        
        return response
    
    def _get_audit_info(self, method: str, path: str) -> Optional[tuple[AuditAction, AuditResource]]:
        """Get audit action and resource for a given method and path."""
        # Direct match
        key = (method, path)
        if key in self.AUDIT_MAPPING:
            return self.AUDIT_MAPPING[key]
        
        # Pattern matching for parameterized paths
        for pattern_key, audit_info in self.AUDIT_MAPPING.items():
            pattern_method, pattern_path = pattern_key
            if method == pattern_method:
                # Simple pattern matching for {id} parameters
                if "{id}" in pattern_path:
                    pattern_base = pattern_path.replace("{id}", "")
                    if path.startswith(pattern_base) and path.count("/") == pattern_path.count("/"):
                        return audit_info
        
        return None


class AuditedRoute(APIRoute):
    """Custom route class that adds user info to request state for audit middleware."""
    
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            # Try to get current user and add to request state
            try:
                user = await get_current_user_optional(request)
                if user:
                    request.state.user = user
            except:
                pass
            
            return await original_route_handler(request)
        
        return custom_route_handler