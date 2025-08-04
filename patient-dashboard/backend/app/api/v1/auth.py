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
    UserCreate, UserLogin, UserResponse, TokenResponse, 
    UserPasswordChange, UserPasswordReset, UserPasswordResetConfirm
)
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.clerk_auth_service import ClerkAuthService
from app.services.enhanced_clerk_auth import enhanced_clerk_auth_service
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
clerk_auth_service = ClerkAuthService()


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> UserResponse:
    """Get current authenticated user from JWT token (Clerk or internal)."""
    # Check for Bearer token in Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Try enhanced Clerk verification first
    try:
        # Use enhanced Clerk auth service for better security
        clerk_claims = await enhanced_clerk_auth_service.verify_clerk_token(token)
        # Get or create user from validated claims
        user = await enhanced_clerk_auth_service.get_or_create_user_from_clerk(clerk_claims)
        
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


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    request: Request = None
):
    """Register a new user."""
    try:
        # Create user
        user = await user_service.create_user(user_create)
        
        # Log registration event
        if request:
            await auth_service.log_authentication(
                email=user.email,
                action="REGISTER",
                success=True,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
):
    """Authenticate user and return JWT tokens."""
    with logfire.span("user_login", email=form_data.username):
        try:
            logfire.info("User login attempt", email=form_data.username)
            
            # Authenticate user
            with logfire.span("authenticate_user"):
                user = await auth_service.authenticate_user(
                    email=form_data.username,  # OAuth2 uses 'username' field
                    password=form_data.password
                )
            
            if not user:
                logfire.warning("Login failed - invalid credentials", email=form_data.username)
                raise AuthenticationException("Invalid email or password")
            
            # Generate tokens
            with logfire.span("generate_tokens"):
                access_token = auth_service.create_access_token(user)
                refresh_token = auth_service.create_refresh_token(user)
            
            # Update last login
            with logfire.span("update_last_login"):
                await user_service.update_last_login(user.id)
            
            # Log authentication event
            if request:
                await auth_service.log_authentication(
                    email=user.email,
                    action="LOGIN",
                    success=True,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent")
                )
            
            logfire.info("User login successful", 
                        email=user.email, 
                        user_id=user.id, 
                        role=user.role)
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                password_reset_required=user.password_reset_required
            )
            
        except AuthenticationException:
            raise
        except Exception as e:
            raise AuthenticationException(f"Login failed: {str(e)}")


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


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    try:
        # Verify refresh token
        payload = auth_service.verify_refresh_token(refresh_token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise AuthenticationException("Invalid refresh token")
        
        # Get user
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")
        
        # Generate new access token
        access_token = auth_service.create_access_token(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Return same refresh token
            token_type="Bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except Exception as e:
        raise AuthenticationException(f"Token refresh failed: {str(e)}")


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
    """Change user password."""
    try:
        # Verify current password
        is_valid = await auth_service.verify_password(
            password_change.current_password,
            current_user.id
        )
        
        if not is_valid:
            raise ValidationException("Current password is incorrect")
        
        # Update password
        await user_service.update_password(
            user_id=current_user.id,
            new_password=password_change.new_password
        )
        
        return {"message": "Password changed successfully"}
        
    except ValidationException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password change failed: {str(e)}"
        )


@router.post("/forgot-password")
async def forgot_password(
    password_reset: UserPasswordReset
):
    """Initiate password reset process."""
    try:
        # Check if user exists
        user = await user_service.get_user_by_email(password_reset.email)
        
        if user:
            # Generate reset token and send email
            reset_token = await auth_service.create_password_reset_token(user.id)
            # TODO: Send reset email via Resend
            # For now, just return success
        
        # Always return success to prevent email enumeration
        return {
            "message": "If the email exists, a password reset link has been sent"
        }
        
    except Exception as e:
        # Log error but don't expose it
        print(f"Password reset error: {str(e)}")
        return {
            "message": "If the email exists, a password reset link has been sent"
        }


@router.post("/reset-password")
async def reset_password(
    password_reset_confirm: UserPasswordResetConfirm
):
    """Reset password using reset token."""
    try:
        # Verify reset token
        user_id = await auth_service.verify_password_reset_token(
            password_reset_confirm.token
        )
        
        if not user_id:
            raise ValidationException("Invalid or expired reset token")
        
        # Update password
        await user_service.update_password(
            user_id=user_id,
            new_password=password_reset_confirm.new_password
        )
        
        return {"message": "Password reset successfully"}
        
    except ValidationException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )