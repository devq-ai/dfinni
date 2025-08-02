"""Debug endpoints for testing authentication."""
from fastapi import APIRouter, Request, Depends
from app.api.v1.auth import get_current_user
from app.models.user import UserResponse

router = APIRouter()

@router.get("/auth-test")
async def test_auth(request: Request):
    """Test endpoint to check auth headers."""
    auth_header = request.headers.get("Authorization", "No auth header")
    return {
        "auth_header": auth_header,
        "all_headers": dict(request.headers)
    }

@router.get("/auth-user")
async def test_auth_user(current_user: UserResponse = Depends(get_current_user)):
    """Test endpoint to check authenticated user."""
    return {
        "user": current_user.dict(),
        "message": "Authentication successful"
    }