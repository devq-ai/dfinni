"""Test endpoint for Clerk authentication debugging"""
from fastapi import APIRouter, Request, HTTPException
from app.services.clerk_auth_service import ClerkAuthService

router = APIRouter()
clerk_service = ClerkAuthService()

@router.get("/test-clerk")
async def test_clerk_auth(request: Request):
    """Test Clerk authentication"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return {"error": "No Authorization header"}
    
    if not auth_header.startswith("Bearer "):
        return {"error": "Invalid Authorization header format"}
    
    token = auth_header.split(" ")[1]
    
    # Get issuer info
    issuer_info = {
        "expected_issuer": clerk_service.clerk_issuer,
        "jwks_url": clerk_service.jwks_url,
        "token_preview": token[:20] + "..." if len(token) > 20 else token
    }
    
    # Try to decode without verification first
    try:
        import jwt
        unverified = jwt.decode(token, options={"verify_signature": False})
        issuer_info["token_issuer"] = unverified.get("iss")
        issuer_info["token_sub"] = unverified.get("sub")
        issuer_info["token_aud"] = unverified.get("aud")
    except Exception as e:
        issuer_info["decode_error"] = str(e)
    
    # Try to verify
    try:
        result = await clerk_service.verify_clerk_token(token)
        return {
            "success": True,
            "user_id": result.get("sub"),
            "email": result.get("email"),
            "issuer_info": issuer_info
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "issuer_info": issuer_info
        }