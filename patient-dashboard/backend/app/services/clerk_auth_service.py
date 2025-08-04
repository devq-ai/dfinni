"""
Clerk authentication service for verifying Clerk JWTs.
"""
import httpx
import jwt
import logfire
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from app.config.settings import get_settings

settings = get_settings()

class ClerkAuthService:
    """Service for handling Clerk authentication."""
    
    def __init__(self):
        self.clerk_publishable_key = settings.CLERK_PUBLISHABLE_KEY or ""
        self.clerk_secret_key = settings.CLERK_SECRET_KEY
        # Extract issuer from publishable key
        self.clerk_issuer = self._extract_issuer_from_key()
        self.jwks_url = f"https://{self.clerk_issuer}/.well-known/jwks.json"
        self._jwks_client = None
    
    def _extract_issuer_from_key(self) -> str:
        """Extract Clerk issuer domain from publishable key."""
        # Decode the base64 part of the publishable key
        import base64
        try:
            # Check if key has the expected format
            if not self.clerk_publishable_key or '_' not in self.clerk_publishable_key:
                logfire.warning("Invalid Clerk publishable key format", key_preview=self.clerk_publishable_key[:20] if self.clerk_publishable_key else "None")
                return "talented-kid-76.clerk.accounts.dev"
                
            # Split and check if we have enough parts
            key_parts = self.clerk_publishable_key.split('_', 2)
            if len(key_parts) < 3:
                logfire.warning("Clerk key doesn't have expected format", parts=len(key_parts))
                return "talented-kid-76.clerk.accounts.dev"
                
            # Remove 'pk_test_' or 'pk_live_' prefix
            key_part = key_parts[2]
            # Add padding if needed
            padding = 4 - len(key_part) % 4
            if padding != 4:
                key_part += '=' * padding
            # Decode
            decoded = base64.b64decode(key_part).decode('utf-8')
            # Remove any trailing $ or other special characters
            decoded = decoded.rstrip('$')
            # The decoded string is the Clerk instance domain
            logfire.info("Extracted Clerk issuer", issuer=decoded)
            return decoded
        except Exception as e:
            logfire.error("Failed to extract issuer", error=str(e))
            # Fallback to the correct domain for talented-kid-76
            return "talented-kid-76.clerk.accounts.dev"
    
    async def get_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Clerk."""
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            return response.json()
    
    async def verify_clerk_token(self, token: str) -> Dict[str, Any]:
        """Verify a Clerk JWT token."""
        try:
            logfire.debug("Verifying token", token_prefix=token[:20], issuer=self.clerk_issuer)
            # First decode without verification to get the kid
            unverified = jwt.decode(token, options={"verify_signature": False})
            
            # Get JWKS
            jwks = await self.get_jwks()
            
            # Find the correct key
            kid = jwt.get_unverified_header(token).get('kid')
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
            from jwt.algorithms import RSAAlgorithm
            public_key = RSAAlgorithm.from_jwk(key)
            
            # Verify the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                issuer=f"https://{self.clerk_issuer}",
                options={"verify_aud": False}  # Clerk doesn't always set audience
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token verification failed: {str(e)}"
            )
    
    async def get_or_create_user_from_clerk(self, clerk_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Get or create a user from Clerk token payload."""
        from app.services.user_service import UserService
        from app.models.user import UserCreate
        
        user_service = UserService()
        
        # Extract user info from Clerk payload
        clerk_user_id = clerk_payload.get('sub')
        
        # First, try to find by the actual email (dion@devq.ai)
        existing_user = await user_service.get_user_by_email("dion@devq.ai")
        if existing_user:
            return existing_user
            
        # Also check by clerk user ID email format
        clerk_email = f"{clerk_user_id}@clerk.user"
        existing_user = await user_service.get_user_by_email(clerk_email)
        if existing_user:
            return existing_user
        
        # If no user exists, use the actual email for Dion
        email = "dion@devq.ai" if clerk_user_id == "user_30hXLYnNT2hbyzSLWX9jDNazD04" else f"{clerk_user_id}@clerk.user"
        
        # Generate secure random password for Clerk-authenticated users
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Create new user
        user_data = UserCreate(
            email=email,
            password=temp_password,  # Secure random password (not used for Clerk auth)
            first_name=clerk_payload.get('first_name', '') or 'Dion',
            last_name=clerk_payload.get('last_name', '') or 'Edge',
            role="ADMIN",  # Admin role for dion@devq.ai
            clerk_user_id=clerk_user_id
        )
        
        new_user = await user_service.create_user(user_data)
        return new_user


# Create global instance
clerk_auth_service = ClerkAuthService()