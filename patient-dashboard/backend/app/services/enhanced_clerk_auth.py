"""
Enhanced Clerk authentication service with improved JWT validation.
Per Production Proposal: Enhanced security and validation
"""
import httpx
import jwt
import logfire
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from functools import lru_cache
from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.models.user import UserRole

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


class EnhancedClerkAuthService:
    """Enhanced service for Clerk authentication with improved security."""
    
    def __init__(self):
        self.clerk_publishable_key = settings.CLERK_PUBLISHABLE_KEY
        self.clerk_secret_key = settings.CLERK_SECRET_KEY
        self.clerk_issuer = self._extract_issuer_from_key()
        self.jwks_url = f"https://{self.clerk_issuer}/.well-known/jwks.json"
        self._jwks_cache = None
        self._jwks_cache_time = None
        self._cache_duration = 3600  # 1 hour cache for JWKS
        
    def _extract_issuer_from_key(self) -> str:
        """Extract Clerk issuer domain from publishable key."""
        import base64
        try:
            # Remove 'pk_test_' or 'pk_live_' prefix
            key_part = self.clerk_publishable_key.split('_', 2)[2]
            # Add padding if needed
            padding = 4 - len(key_part) % 4
            if padding != 4:
                key_part += '=' * padding
            # Decode
            decoded = base64.b64decode(key_part).decode('utf-8')
            # Remove any trailing $ or other special characters
            decoded = decoded.rstrip('$')
            
            logfire.info("Clerk issuer extracted", issuer=decoded)
            return decoded
        except Exception as e:
            logfire.error("Failed to extract Clerk issuer", error=str(e))
            # Fallback to known domain
            return "talented-kid-76.clerk.accounts.dev"
    
    async def get_jwks(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch JWKS from Clerk with caching."""
        now = datetime.now(timezone.utc).timestamp()
        
        # Check cache
        if not force_refresh and self._jwks_cache and self._jwks_cache_time:
            if now - self._jwks_cache_time < self._cache_duration:
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
                
                logfire.info("JWKS fetched successfully", keys_count=len(jwks.get('keys', [])))
                return jwks
        except Exception as e:
            logfire.error("Failed to fetch JWKS", error=str(e), url=self.jwks_url)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch authentication keys"
            )
    
    async def verify_clerk_token(self, token: str) -> ClerkTokenClaims:
        """
        Verify a Clerk JWT token with enhanced validation.
        
        Args:
            token: The JWT token to verify
            
        Returns:
            ClerkTokenClaims: Validated token claims
            
        Raises:
            HTTPException: If token validation fails
        """
        with logfire.span("verify_clerk_token"):
            try:
                # Get unverified header to find the key ID
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
                    # Try refreshing JWKS once
                    logfire.info("Key not found in cache, refreshing JWKS", kid=kid)
                    jwks = await self.get_jwks(force_refresh=True)
                    for k in jwks.get('keys', []):
                        if k.get('kid') == kid:
                            key = k
                            break
                    
                    if not key:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token key not found"
                        )
                
                # Convert JWK to PEM
                from jwt.algorithms import RSAAlgorithm
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
                        "verify_nbf": True,
                        "verify_iat": True,
                        "verify_iss": True,
                        "require_exp": True,
                        "require_iat": True,
                        "require_sub": True
                    }
                )
                
                # Validate and parse claims
                claims = ClerkTokenClaims(**payload)
                
                # Additional validation
                if not claims.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token is not yet active or has expired"
                    )
                
                # Check for impersonation
                if claims.act:
                    logfire.info(
                        "Impersonation detected",
                        actor=claims.act.get('sub'),
                        target=claims.sub
                    )
                
                logfire.info(
                    "Token verified successfully",
                    user_id=claims.sub,
                    session_id=claims.sid,
                    org_id=claims.org_id
                )
                
                return claims
                
            except jwt.ExpiredSignatureError:
                logfire.warning("Token expired", user_id=jwt.decode(token, options={"verify_signature": False}).get('sub'))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            except jwt.InvalidTokenError as e:
                logfire.warning("Invalid token", error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token: {str(e)}"
                )
            except HTTPException:
                raise
            except Exception as e:
                logfire.error("Token verification failed", error=str(e))
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token verification failed"
                )
    
    async def get_or_create_user_from_clerk(self, claims: ClerkTokenClaims) -> Dict[str, Any]:
        """
        Get or create a user from validated Clerk token claims.
        
        Args:
            claims: Validated Clerk token claims
            
        Returns:
            User dictionary
        """
        from app.services.user_service import UserService
        from app.models.user import UserCreate
        
        with logfire.span("get_or_create_user_from_clerk", user_id=claims.sub):
            user_service = UserService()
            
            # Try to find existing user by Clerk ID
            existing_user = await user_service.get_user_by_clerk_id(claims.sub)
            if existing_user:
                logfire.info("Existing user found", user_id=existing_user.id)
                return existing_user
            
            # Check if this is a known user (e.g., dion@devq.ai)
            email = self._get_email_for_clerk_user(claims.sub)
            existing_user = await user_service.get_user_by_email(email)
            if existing_user:
                # Update with Clerk ID if not set
                if not existing_user.clerk_user_id:
                    await user_service.update_clerk_id(existing_user.id, claims.sub)
                return existing_user
            
            # Determine role based on organization or other claims
            role = self._determine_user_role(claims)
            
            # Generate secure random password for Clerk-authenticated users
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            temp_password = ''.join(secrets.choice(alphabet) for _ in range(32))
            
            # Create new user
            user_data = UserCreate(
                email=email,
                password=temp_password,  # Secure random password (not used for Clerk auth)
                first_name="Clerk",
                last_name="User",
                role=role,
                clerk_user_id=claims.sub
            )
            
            new_user = await user_service.create_user(user_data)
            logfire.info("New user created from Clerk", user_id=new_user.id, email=email)
            
            return new_user
    
    def _get_email_for_clerk_user(self, clerk_user_id: str) -> str:
        """Get email address for a Clerk user ID."""
        # Map known Clerk IDs to actual emails
        known_mappings = {
            "user_30hXLYnNT2hbyzSLWX9jDNazD04": "dion@devq.ai"
        }
        
        return known_mappings.get(clerk_user_id, f"{clerk_user_id}@clerk.user")
    
    def _determine_user_role(self, claims: ClerkTokenClaims) -> UserRole:
        """Determine user role from Clerk claims."""
        # Check organization role
        if claims.org_role == "admin":
            return UserRole.ADMIN
        
        # Check specific permissions
        if claims.org_permissions and "admin" in claims.org_permissions:
            return UserRole.ADMIN
        
        # Check known admin users
        admin_users = ["user_30hXLYnNT2hbyzSLWX9jDNazD04"]
        if claims.sub in admin_users:
            return UserRole.ADMIN
        
        # Default to provider role
        return UserRole.PROVIDER
    
    async def validate_session(self, session_id: str) -> bool:
        """
        Validate that a session is still active with Clerk.
        
        Args:
            session_id: The session ID to validate
            
        Returns:
            bool: True if session is valid
        """
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
                    return session_data.get('status') == 'active'
                
                return False
        except Exception as e:
            logfire.error("Failed to validate session", error=str(e), session_id=session_id)
            return False


# Singleton instance
enhanced_clerk_auth_service = EnhancedClerkAuthService()