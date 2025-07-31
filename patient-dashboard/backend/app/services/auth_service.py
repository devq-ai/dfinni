"""
Authentication service for handling JWT tokens and authentication logic.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import secrets

from app.models.user import UserResponse, UserInDB
from app.services.user_service import UserService
from app.config.settings import get_settings
from app.config.logging import audit_logger
from app.core.exceptions import AuthenticationException, ValidationException
from app.database.connection import get_database

settings = get_settings()


class AuthService:
    """Service for authentication and token management."""
    
    def __init__(self):
        self.user_service = UserService()
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        self._reset_tokens = {}  # In-memory storage for reset tokens (use Redis in production)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password."""
        # TEMPORARY: Hardcoded demo users for testing
        demo_users = {
            "dion@devq.ai": {
                "password": "Admin123!",
                "user": UserInDB(
                    id="demo_admin_1",
                    email="dion@devq.ai",
                    password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGNfrHeNWCu",  # Admin123!
                    first_name="Dion",
                    last_name="Edge",
                    role="ADMIN",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            },
            "pfinni@devq.ai": {
                "password": "Admin123!",
                "user": UserInDB(
                    id="demo_provider_1",
                    email="pfinni@devq.ai",
                    password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiGNfrHeNWCu",  # Admin123!
                    first_name="Provider",
                    last_name="Finni",
                    role="PROVIDER",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            }
        }
        
        # Check demo users first
        if email in demo_users and password == demo_users[email]["password"]:
            return demo_users[email]["user"]
        
        try:
            # Get user with password hash
            user = await self.user_service.get_user_with_password(email)
            
            if not user:
                return None
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationException("User account is disabled")
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return None
            
            return user
            
        except AuthenticationException:
            raise
        except Exception as e:
            raise AuthenticationException(f"Authentication failed: {str(e)}")
    
    def create_access_token(self, user: UserInDB) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: UserInDB) -> str:
        """Create JWT refresh token."""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "access":
                raise AuthenticationException("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationException(f"Invalid token: {str(e)}")
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT refresh token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "refresh":
                raise AuthenticationException("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationException(f"Invalid refresh token: {str(e)}")
    
    async def verify_password(self, password: str, user_id: str) -> bool:
        """Verify password for a user."""
        try:
            # Get user with password
            user = await self.user_service.get_user_by_id(user_id)
            if not user:
                return False
            
            # Get password hash from database
            db = await self.user_service._get_db()
            result = await db.execute(
                "SELECT password_hash FROM user WHERE id = $id",
                {"id": user_id}
            )
            
            if not result or not result[0].get('result'):
                return False
            
            password_hash = result[0]['result'][0]['password_hash']
            
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            
        except Exception:
            return False
    
    async def create_password_reset_token(self, user_id: str) -> str:
        """Create a password reset token."""
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        
        # Store token with expiration (15 minutes)
        self._reset_tokens[token] = {
            "user_id": user_id,
            "expires": datetime.utcnow() + timedelta(minutes=15)
        }
        
        return token
    
    async def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return user ID."""
        token_data = self._reset_tokens.get(token)
        
        if not token_data:
            return None
        
        # Check expiration
        if datetime.utcnow() > token_data["expires"]:
            # Remove expired token
            del self._reset_tokens[token]
            return None
        
        # Remove token after use
        user_id = token_data["user_id"]
        del self._reset_tokens[token]
        
        return user_id
    
    async def log_authentication(
        self,
        email: str,
        action: str,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log authentication event."""
        try:
            db = await get_database()
            
            await db.execute("""
                CREATE audit_log SET
                    action = $action,
                    resource_type = 'USER',
                    user_email = $email,
                    user_role = 'UNKNOWN',
                    ip_address = $ip_address,
                    user_agent = $user_agent,
                    success = $success,
                    error_message = $error_message,
                    created_at = time::now()
            """, {
                "action": action,
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": success,
                "error_message": error_message
            })
            
        except Exception as e:
            # Don't fail authentication if logging fails
            print(f"Failed to log authentication: {str(e)}")