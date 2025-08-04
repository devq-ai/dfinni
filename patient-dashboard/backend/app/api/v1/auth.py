"""
Authentication API endpoints.
Handles login, logout, token refresh, and user session management.
"""
import logfire
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.models.user import (
    UserCreate, UserResponse,
    UserPasswordChange, UserPasswordReset, UserPasswordResetConfirm
)
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.clerk_auth_service import clerk_auth_service
from app.core.exceptions import AuthenticationException, ValidationException
from app.config.settings import get_settings
from app.database.connection import get_database

settings = get_settings()
router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# Initialize services
user_service = UserService()
auth_service = AuthService()


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> UserResponse:
    """Get current authenticated user from JWT token (Clerk or internal)."""
    # Check for Bearer token in Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    # Debug logging
    logfire.info(
        "Authentication attempt",
        has_auth_header=bool(auth_header),
        has_token=bool(token),
        token_prefix=token[:20] + "..." if token else None
    )
    
    if not token:
        logfire.warning("No authentication token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Try Clerk verification first
    try:
        # Use consolidated Clerk auth service
        clerk_claims = await clerk_auth_service.verify_clerk_token(token)
        # Get or create user from validated claims
        user = await clerk_auth_service.get_or_create_user_from_clerk(clerk_claims)
        
        # Store session info in request state for audit
        if hasattr(request, 'state'):
            request.state.session_id = clerk_claims.sid
            request.state.org_id = clerk_claims.org_id
        
        logfire.info(
            "User authenticated via Clerk",
            user_id=user.id,
            clerk_user_id=clerk_claims.sub,
            session_id=clerk_claims.sid
        )
        
        return user
    except HTTPException:
        # If Clerk verification fails, try internal JWT
        pass
    
    # Fall back to internal JWT verification
    try:
        payload = auth_service.verify_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationException("Invalid token")
        
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[UserResponse]:
    """Get current authenticated user if available, return None if not authenticated."""
    try:
        return await get_current_user(request, token)
    except HTTPException:
        return None


@router.post("/register")
async def register(
    user_create: UserCreate,
    request: Request = None
):
    """Legacy registration endpoint - returns error directing to Clerk."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="User registration is now handled through Clerk. Please use the signup flow on the frontend."
    )


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    """Legacy login endpoint - returns error directing to Clerk."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password-based authentication is no longer supported. Please use Clerk authentication on the frontend."
    )


@router.post("/logout")
async def logout(
    current_user: UserResponse = Depends(get_current_user),
    request: Request = None
):
    """Logout user (client should discard tokens)."""
    # Log logout event
    if request:
        await auth_service.log_authentication(
            email=current_user.email,
            action="LOGOUT",
            success=True,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
    
    return {"message": "Successfully logged out"}


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """Legacy refresh token endpoint - Clerk handles token refresh automatically."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Token refresh is handled automatically by Clerk. The frontend SDK will refresh tokens as needed."
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user information."""
    return current_user


@router.post("/change-password")
async def change_password(
    password_change: UserPasswordChange,
    current_user: UserResponse = Depends(get_current_user)
):
    """Legacy password change endpoint - directs to Clerk."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password management is now handled through Clerk. Please use the account settings in the frontend."
    )


@router.post("/forgot-password")
async def forgot_password(
    password_reset: UserPasswordReset
):
    """Legacy password reset endpoint - directs to Clerk."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password reset is now handled through Clerk. Please use the forgot password option on the login page."
    )


@router.post("/reset-password")
async def reset_password(
    password_reset_confirm: UserPasswordResetConfirm
):
    """Legacy password reset confirmation endpoint - directs to Clerk."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password reset is now handled through Clerk. Please use the password reset flow on the frontend."
    )