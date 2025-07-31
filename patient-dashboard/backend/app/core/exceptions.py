"""
Custom exception classes for the patient dashboard.
All exceptions ensure HIPAA compliance by not exposing sensitive data.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    """Base exception class for API errors."""
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "details": self.details
            }
        )

class ValidationException(BaseAPIException):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )

class AuthenticationException(BaseAPIException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            message=message
        )

class AuthorizationException(BaseAPIException):
    """Raised when user lacks required permissions."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            message=message
        )

class BusinessLogicException(BaseAPIException):
    """Raised when business rules are violated."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BUSINESS_LOGIC_ERROR",
            message=message,
            details=details
        )

class ResourceNotFoundException(BaseAPIException):
    """Raised when a requested resource is not found."""
    def __init__(self, resource_type: str, resource_id: Optional[str] = None):
        message = f"{resource_type} not found"
        details = {"resource_type": resource_type}
        if resource_id:
            details["resource_id"] = resource_id
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            message=message,
            details=details
        )

class DatabaseException(BaseAPIException):
    """Raised when database operations fail."""
    def __init__(self, message: str = "Database operation failed"):
        # Never expose internal database errors to clients
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message="An error occurred while processing your request"
        )

class ExternalServiceException(BaseAPIException):
    """Raised when external service calls fail."""
    def __init__(self, service_name: str, message: str = "External service error"):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            message=message,
            details={"service": service_name}
        )

class RateLimitException(BaseAPIException):
    """Raised when rate limits are exceeded."""
    def __init__(self, retry_after: Optional[int] = None):
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please try again later.",
            details=details
        )

class ConflictException(BaseAPIException):
    """Raised when there's a conflict with existing data."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT_ERROR",
            message=message,
            details=details
        )