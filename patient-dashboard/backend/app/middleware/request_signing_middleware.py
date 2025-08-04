"""
Request signing middleware for sensitive operations.
"""
import hmac
import hashlib
import time
import json
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import logfire
import os


class RequestSigningMiddleware(BaseHTTPMiddleware):
    """Validate request signatures for sensitive operations."""
    
    # Define sensitive endpoints that require signing
    PROTECTED_ENDPOINTS = {
        "/api/patients",  # Patient data operations
        "/api/auth/login",  # Authentication
        "/api/auth/register",  # Registration
        "/api/dashboard/alerts",  # Alert management
        "/api/audit",  # Audit logs
    }
    
    # Sensitive HTTP methods
    PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
    
    def __init__(self, app):
        super().__init__(app)
        self.signing_key = os.getenv('PFINNI_REQUEST_SIGNING_KEY')
        if not self.signing_key:
            logfire.warning("No PFINNI_REQUEST_SIGNING_KEY found")
            self.signing_key = "development-signing-key"  # Development only
            
    async def dispatch(self, request: Request, call_next):
        # Check if this endpoint requires signing
        if self._requires_signing(request):
            # Validate the signature
            is_valid = await self._validate_signature(request)
            
            if not is_valid:
                with logfire.span("request_signature_invalid"):
                    logfire.error(
                        "Invalid request signature",
                        path=request.url.path,
                        method=request.method
                    )
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid request signature"}
                )
        
        response = await call_next(request)
        return response
    
    def _requires_signing(self, request: Request) -> bool:
        """Check if the request requires signature validation."""
        # Check if it's a protected endpoint
        path = request.url.path
        method = request.method
        
        # Check exact matches first
        if path in self.PROTECTED_ENDPOINTS and method in self.PROTECTED_METHODS:
            return True
            
        # Check prefix matches for nested endpoints
        for endpoint in self.PROTECTED_ENDPOINTS:
            if path.startswith(endpoint + "/") and method in self.PROTECTED_METHODS:
                return True
                
        return False
    
    async def _validate_signature(self, request: Request) -> bool:
        """Validate the request signature."""
        try:
            # Get signature headers
            signature = request.headers.get("X-Request-Signature")
            timestamp = request.headers.get("X-Request-Timestamp")
            nonce = request.headers.get("X-Request-Nonce")
            
            if not all([signature, timestamp, nonce]):
                logfire.warning("Missing signature headers")
                return False
            
            # Check timestamp (prevent replay attacks)
            current_time = int(time.time())
            request_time = int(timestamp)
            if abs(current_time - request_time) > 300:  # 5 minute window
                logfire.warning("Request timestamp too old")
                return False
            
            # Get request body
            body = await request.body()
            
            # Create the message to sign
            message_parts = [
                request.method,
                request.url.path,
                timestamp,
                nonce,
                body.decode() if body else ""
            ]
            message = "|".join(message_parts)
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.signing_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if is_valid:
                with logfire.span("request_signature_valid"):
                    logfire.info(
                        "Valid request signature",
                        path=request.url.path,
                        method=request.method
                    )
            
            return is_valid
            
        except Exception as e:
            logfire.error("Signature validation error", error=str(e))
            return False


def generate_request_signature(
    method: str,
    path: str,
    body: Optional[dict] = None,
    signing_key: Optional[str] = None
) -> dict:
    """Generate signature headers for a request."""
    if not signing_key:
        signing_key = os.getenv('PFINNI_REQUEST_SIGNING_KEY', 'development-signing-key')
        
    timestamp = str(int(time.time()))
    nonce = os.urandom(16).hex()
    
    # Create the message to sign
    message_parts = [
        method,
        path,
        timestamp,
        nonce,
        json.dumps(body) if body else ""
    ]
    message = "|".join(message_parts)
    
    # Calculate signature
    signature = hmac.new(
        signing_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        "X-Request-Signature": signature,
        "X-Request-Timestamp": timestamp,
        "X-Request-Nonce": nonce
    }