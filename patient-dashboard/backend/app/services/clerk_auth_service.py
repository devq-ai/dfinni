"""
Consolidated Clerk authentication service with enhanced JWT validation.
Combines functionality from clerk_auth_service.py and enhanced_clerk_auth.py
"""
import httpx
import jwt
import logfire
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from functools import lru_cache
from fastapi import HTTPException, status
from pydantic import BaseModel, Field
from jwt.algorithms import RSAAlgorithm

from app.config.settings import get_settings
from app.models.user import UserRole, UserResponse, UserInDB
from app.services.user_service import UserService
from app.database.connection import get_database

settings = get_settings()


class ClerkTokenClaims(BaseModel):
    """Validated Clerk JWT token claims."""
    sub: str = Field(..., description="Subject (user ID)")
    iss: str = Field(..., description="Issuer")
    iat: int = Field(..., description="Issued at timestamp")
    exp: int = Field(..., description="Expiration timestamp")
    nbf: Optional[int] = Field(None, description="Not before timestamp")
    azp: Optional[str] = Field(None, description="Authorized party")
    sid: Optional[str] = Field(None, description="Session ID")
    org_id: Optional[str] = Field(None, description="Organization ID")
    org_role: Optional[str] = Field(None, description="Organization role")
    org_slug: Optional[str] = Field(None, description="Organization slug")
    org_permissions: Optional[List[str]] = Field(default_factory=list, description="Organization permissions")
    act: Optional[Dict[str, Any]] = Field(None, description="Actor claim for impersonation")
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc).timestamp() > self.exp
    
    @property
    def is_active(self) -> bool:
        """Check if token is currently active."""
        now = datetime.now(timezone.utc).timestamp()
        if self.nbf and now < self.nbf:
            return False
        return not self.is_expired


class ClerkAuthService:
    """Consolidated service for Clerk authentication with enhanced security."""
    
    def __init__(self):
        self.clerk_publishable_key = settings.CLERK_PUBLISHABLE_KEY or ""
        self.clerk_secret_key = settings.CLERK_SECRET_KEY
        self.clerk_issuer = self._extract_issuer_from_key()
        self.jwks_url = f"https://{self.clerk_issuer}/.well-known/jwks.json"
        self._jwks_cache = None
        self._jwks_cache_time = None
        self._cache_duration = 300  # 5 minutes
        self.user_service = UserService()
    
    def _extract_issuer_from_key(self) -> str:
        """Extract Clerk issuer domain from publishable key."""
        import base64
        try:
            if not self.clerk_publishable_key or '_' not in self.clerk_publishable_key:
                logfire.warning("Invalid Clerk publishable key format")
                return "talented-kid-76.clerk.accounts.dev"
                
            key_parts = self.clerk_publishable_key.split('_', 2)
            if len(key_parts) < 3:
                logfire.warning("Clerk key doesn't have expected format")
                return "talented-kid-76.clerk.accounts.dev"
                
            key_part = key_parts[2]
            padding = 4 - len(key_part) % 4
            if padding != 4:
                key_part += '=' * padding
            decoded = base64.b64decode(key_part).decode('utf-8')
            decoded = decoded.rstrip('$')
            logfire.info("Extracted Clerk issuer", issuer=decoded)
            return decoded
        except Exception as e:
            logfire.error("Failed to extract issuer", error=str(e))
            return "talented-kid-76.clerk.accounts.dev"
    
    @lru_cache(maxsize=128)
    async def get_jwks(self) -> Dict[str, Any]:
        """Fetch and cache JWKS from Clerk."""
        now = datetime.now(timezone.utc)
        
        # Check cache
        if self._jwks_cache and self._jwks_cache_time:
            cache_age = (now - self._jwks_cache_time).total_seconds()
            if cache_age < self._cache_duration:
                return self._jwks_cache
        
        # Fetch new JWKS
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()
                jwks = response.json()
                
                # Update cache
                self._jwks_cache = jwks
                self._jwks_cache_time = now
                
                return jwks
        except Exception as e:
            logfire.error("Failed to fetch JWKS", error=str(e))
            if self._jwks_cache:
                logfire.warning("Using stale JWKS cache")
                return self._jwks_cache
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch JWKS"
            )
    
    async def verify_clerk_token(self, token: str) -> ClerkTokenClaims:
        """Verify a Clerk JWT token and return validated claims."""
        try:
            with logfire.span("verify_clerk_token"):
                # Decode without verification to get header
                unverified_header = jwt.get_unverified_header(token)
                kid = unverified_header.get('kid')
                
                if not kid:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token missing key ID"
                    )
                
                # Get JWKS
                jwks = await self.get_jwks()
                
                # Find the correct key
                key = None
                for k in jwks.get('keys', []):
                    if k.get('kid') == kid:
                        key = k
                        break
                
                if not key:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token key"
                    )
                
                # Convert JWK to PEM
                public_key = RSAAlgorithm.from_jwk(key)
                
                # Verify the token
                payload = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    issuer=f"https://{self.clerk_issuer}",
                    options={
                        "verify_aud": False,  # Clerk doesn't always set audience
                        "verify_exp": True,
                        "verify_iat": True
                    }
                )
                
                # Convert to validated claims model
                claims = ClerkTokenClaims(**payload)
                
                # Additional validation
                if not claims.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token is not active"
                    )
                
                logfire.info(
                    "Token verified successfully",
                    user_id=claims.sub,
                    session_id=claims.sid,
                    org_id=claims.org_id
                )
                
                return claims
                
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            logfire.error("Invalid token", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except HTTPException:
            raise
        except Exception as e:
            logfire.error("Token verification failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    
    async def get_or_create_user_from_clerk(self, claims: ClerkTokenClaims) -> UserResponse:
        """Get or create user from Clerk token claims."""
        try:
            with logfire.span("get_or_create_user_from_clerk", clerk_user_id=claims.sub):
                # First try to get user by clerk_user_id
                db = await get_database()
                result = await db.execute(
                    "SELECT * FROM user WHERE clerk_user_id = $clerk_user_id",
                    {"clerk_user_id": claims.sub}
                )
                
                if result and len(result) > 0 and result[0].get('result'):
                    user_data = result[0]['result'][0] if isinstance(result[0]['result'], list) else result[0]['result']
                    return UserResponse(**user_data)
                
                # If not found, fetch from Clerk API
                user_info = await self.fetch_clerk_user_info(claims.sub)
                
                # Determine role from org_role or default
                role = self._map_clerk_role_to_app_role(claims.org_role)
                
                # Create user in database
                user_data = {
                    "clerk_user_id": claims.sub,
                    "email": user_info.get("email_addresses", [{}])[0].get("email_address", ""),
                    "first_name": user_info.get("first_name", ""),
                    "last_name": user_info.get("last_name", ""),
                    "role": role,
                    "is_active": True,
                    "organization_id": claims.org_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                created = await db.create("user", user_data)
                
                if created and len(created) > 0:
                    return UserResponse(**created[0])
                
                raise Exception("Failed to create user")
                
        except HTTPException:
            raise
        except Exception as e:
            logfire.error("Failed to get/create user", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process user"
            )
    
    async def fetch_clerk_user_info(self, user_id: str) -> Dict[str, Any]:
        """Fetch user information from Clerk API."""
        if not self.clerk_secret_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Clerk secret key not configured"
            )
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {self.clerk_secret_key}",
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logfire.error("Failed to fetch user from Clerk", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch user information"
            )
    
    def _map_clerk_role_to_app_role(self, org_role: Optional[str]) -> str:
        """Map Clerk organization role to application role."""
        if not org_role:
            return UserRole.PATIENT
        
        role_mapping = {
            "admin": UserRole.ADMIN,
            "provider": UserRole.PROVIDER,
            "staff": UserRole.STAFF,
            "patient": UserRole.PATIENT
        }
        
        return role_mapping.get(org_role.lower(), UserRole.PATIENT)
    
    async def validate_session(self, session_id: str) -> bool:
        """Validate a Clerk session ID."""
        if not self.clerk_secret_key or not session_id:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://api.clerk.com/v1/sessions/{session_id}",
                    headers={
                        "Authorization": f"Bearer {self.clerk_secret_key}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    session_data = response.json()
                    # Check if session is active
                    return session_data.get("status") == "active"
                    
                return False
                
        except Exception as e:
            logfire.error("Failed to validate session", error=str(e))
            return False


# Create singleton instance
clerk_auth_service = ClerkAuthService()