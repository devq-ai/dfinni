"""Minimal test to verify basic functionality"""
import pytest
from app.services.auth_service import AuthService
from app.models.user import UserResponse

def test_auth_service_exists():
    """Test that AuthService can be instantiated."""
    service = AuthService()
    assert service is not None
    assert hasattr(service, 'create_access_token')

def test_create_token():
    """Test token creation."""
    service = AuthService()
    user = UserResponse(
        id="user:test123",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        role="PROVIDER",
        is_active=True,
        password_reset_required=False,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
    
    token = service.create_access_token(user)
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0