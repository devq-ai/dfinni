# Updated: 2025-07-27T12:58:15-05:00
"""
BetterAuth Configuration and Integration
Handles authentication, authorization, and session management
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets

from app.config.settings import get_settings

# Get settings instance
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
JWT_REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


class UserRole:
    """User role constants"""
    PROVIDER = "provider"
    ADMIN = "admin"
    AUDIT = "audit"

    @classmethod
    def all_roles(cls) -> List[str]:
        return [cls.PROVIDER, cls.ADMIN, cls.AUDIT]


class TokenData(BaseModel):
    """Token payload data structure"""
    user_id: str
    email: str
    role: str
    token_type: str  # "access" or "refresh"
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for token revocation


class AuthUser(BaseModel):
    """User data structure for authentication"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class BetterAuth:
    """BetterAuth implementation for patient management system"""

    def __init__(self):
        self.config = settings.better_auth_config
        self.secret_key = settings.BETTER_AUTH_SECRET
        self.jwt_secret = settings.JWT_SECRET_KEY

    def hash_password(self, password: str) -> str:
        """Hash a password for storage"""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user: AuthUser) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "token_type": "access",
            "exp": expire,
            "iat": now,
            "jti": secrets.token_urlsafe(32),
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=JWT_ALGORITHM)

    def create_refresh_token(self, user: AuthUser) -> str:
        """Create JWT refresh token"""
        now = datetime.utcnow()
        expire = now + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

        payload = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "token_type": "refresh",
            "exp": expire,
            "iat": now,
            "jti": secrets.token_urlsafe(32),
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[JWT_ALGORITHM])

            return TokenData(
                user_id=payload["user_id"],
                email=payload["email"],
                role=payload["role"],
                token_type=payload["token_type"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                jti=payload["jti"],
            )
        except jwt.PyJWTError:
            return None

    def validate_access_token(self, token: str) -> Optional[TokenData]:
        """Validate access token and return token data"""
        token_data = self.decode_token(token)

        if not token_data:
            return None

        if token_data.token_type != "access":
            return None

        if token_data.exp < datetime.utcnow():
            return None

        return token_data

    def validate_refresh_token(self, token: str) -> Optional[TokenData]:
        """Validate refresh token and return token data"""
        token_data = self.decode_token(token)

        if not token_data:
            return None

        if token_data.token_type != "refresh":
            return None

        if token_data.exp < datetime.utcnow():
            return None

        return token_data

    def generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)

    def create_password_reset_token(self, user_id: str, email: str) -> str:
        """Create password reset token"""
        now = datetime.utcnow()
        expire = now + timedelta(hours=1)  # Reset tokens expire in 1 hour

        payload = {
            "user_id": user_id,
            "email": email,
            "token_type": "password_reset",
            "exp": expire,
            "iat": now,
            "jti": secrets.token_urlsafe(16),
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=JWT_ALGORITHM)

    def validate_password_reset_token(self, token: str) -> Optional[Dict[str, str]]:
        """Validate password reset token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[JWT_ALGORITHM])

            if payload.get("token_type") != "password_reset":
                return None

            if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
                return None

            return {
                "user_id": payload["user_id"],
                "email": payload["email"],
            }
        except jwt.PyJWTError:
            return None

    def has_permission(self, user_role: str, required_role: str) -> bool:
        """Check if user has required permission level"""
        role_hierarchy = {
            UserRole.AUDIT: 1,
            UserRole.PROVIDER: 2,
            UserRole.ADMIN: 3,
        }

        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level

    def has_any_role(self, user_role: str, allowed_roles: List[str]) -> bool:
        """Check if user has any of the allowed roles"""
        return user_role in allowed_roles

    def is_valid_role(self, role: str) -> bool:
        """Check if role is valid"""
        return role in UserRole.all_roles()

    def get_user_permissions(self, role: str) -> List[str]:
        """Get list of permissions for a role"""
        permissions = {
            UserRole.AUDIT: [
                "read_patients",
                "read_audit_logs",
                "read_reports",
            ],
            UserRole.PROVIDER: [
                "read_patients",
                "create_patients",
                "update_patients",
                "read_insurance",
                "read_alerts",
                "read_reports",
            ],
            UserRole.ADMIN: [
                "read_patients",
                "create_patients",
                "update_patients",
                "delete_patients",
                "read_users",
                "create_users",
                "update_users",
                "delete_users",
                "read_insurance",
                "update_insurance",
                "read_alerts",
                "create_alerts",
                "update_alerts",
                "delete_alerts",
                "read_reports",
                "create_reports",
                "read_audit_logs",
                "manage_system",
            ],
        }

        return permissions.get(role, [])

    def check_permission(self, user_role: str, permission: str) -> bool:
        """Check if user role has specific permission"""
        user_permissions = self.get_user_permissions(user_role)
        return permission in user_permissions


# Global BetterAuth instance
better_auth = BetterAuth()


# Utility functions for common auth operations
def hash_password(password: str) -> str:
    """Hash password utility function"""
    return better_auth.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password utility function"""
    return better_auth.verify_password(plain_password, hashed_password)


def create_tokens(user: AuthUser) -> Dict[str, str]:
    """Create access and refresh tokens for user"""
    return {
        "access_token": better_auth.create_access_token(user),
        "refresh_token": better_auth.create_refresh_token(user),
        "token_type": "bearer",
        "expires_in": JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
    }


def validate_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """Validate token utility function"""
    if token_type == "access":
        return better_auth.validate_access_token(token)
    elif token_type == "refresh":
        return better_auth.validate_refresh_token(token)
    else:
        return None


def has_permission(user_role: str, required_permission: str) -> bool:
    """Check user permission utility function"""
    return better_auth.check_permission(user_role, required_permission)


def requires_role(allowed_roles: List[str]):
    """Decorator to check user roles"""
    def decorator(func):
        func._required_roles = allowed_roles
        return func
    return decorator


def requires_permission(permission: str):
    """Decorator to check user permissions"""
    def decorator(func):
        func._required_permission = permission
        return func
    return decorator
