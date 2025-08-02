"""
User model with role-based access control.
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

class UserRole(str, Enum):
    """User roles for access control."""
    PROVIDER = "PROVIDER"
    ADMIN = "ADMIN"
    AUDIT = "AUDIT"
    USER = "USER"  # Default role for Clerk users
    DOCTOR = "DOCTOR"
    NURSE = "NURSE"

class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole
    is_active: bool = True
    clerk_user_id: Optional[str] = None

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    def validate_password_strength(cls, v):
        """Ensure password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserUpdate(BaseModel):
    """Model for updating user information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """User model as stored in database."""
    id: str
    password_hash: str
    password_reset_required: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    """User model for API responses (excludes password)."""
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    password_reset_required: bool = False
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserListResponse(BaseModel):
    """Response model for user list endpoint."""
    users: list[UserResponse]
    total: int
    page: int
    per_page: int
    pages: int

class UserLogin(BaseModel):
    """Model for user login."""
    email: EmailStr
    password: str

class UserPasswordChange(BaseModel):
    """Model for password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    _validate_password = field_validator('new_password')(UserCreate.validate_password_strength)

class UserPasswordReset(BaseModel):
    """Model for password reset request."""
    email: EmailStr

class UserPasswordResetConfirm(BaseModel):
    """Model for confirming password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    _validate_password = field_validator('new_password')(UserCreate.validate_password_strength)

class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    password_reset_required: bool = False

class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: str
    role: UserRole
    exp: datetime