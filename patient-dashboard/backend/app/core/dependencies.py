"""
Core dependencies for FastAPI endpoints.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import User, UserRole
from app.services.clerk_auth_service import clerk_auth_service
import logfire

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get the current authenticated user from the JWT token.
    """
    try:
        # Extract token
        token = credentials.credentials
        
        # Verify with Clerk
        claims = await clerk_auth_service.verify_clerk_token(token)
        
        if not claims:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Extract user information from claims
        user = User(
            id=claims.get("sub", ""),
            email=claims.get("email", ""),
            first_name=claims.get("first_name", ""),
            last_name=claims.get("last_name", ""),
            role=UserRole(claims.get("role", "VIEWER")),
            is_active=True
        )
        
        logfire.info(
            "User authenticated",
            user_id=user.id,
            user_email=user.email,
            role=user.role
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logfire.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def require_role(user: User, allowed_roles: list[UserRole]) -> None:
    """
    Check if the user has one of the required roles.
    
    Args:
        user: The authenticated user
        allowed_roles: List of allowed roles
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    if user.role not in allowed_roles:
        logfire.warning(
            "Access denied - insufficient role",
            user_id=user.id,
            user_role=user.role,
            required_roles=[r.value for r in allowed_roles]
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {', '.join(r.value for r in allowed_roles)}"
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    """
    if not credentials:
        return None
        
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None