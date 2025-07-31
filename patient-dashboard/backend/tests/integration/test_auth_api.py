"""
Integration tests for authentication API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import jwt

from app.main import app
from app.models.user import UserResponse
from app.services.auth_service import AuthService


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.auth
class TestAuthAPI:
    """Test authentication API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock auth service."""
        with patch('app.api.v1.auth.auth_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_user_service(self):
        """Mock user service."""
        with patch('app.api.v1.auth.user_service') as mock:
            yield mock
    
    def test_register_success(self, client, mock_user_service):
        """Test successful user registration."""
        # Mock user service response
        mock_user_service.create_user.return_value = UserResponse(
            id="user:123",
            email="newuser@example.com",
            first_name="New",
            last_name="User",
            role="provider",
            is_active=True,
            password_reset_required=False,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "Test123!@#",
                "first_name": "New",
                "last_name": "User",
                "role": "provider"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["id"] == "user:123"
        assert "password" not in data
    
    def test_register_duplicate_email(self, client, mock_user_service):
        """Test registration with duplicate email."""
        # Mock user service to raise exception
        mock_user_service.create_user.side_effect = Exception("User already exists")
        
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@example.com",
                "password": "Test123!@#",
                "first_name": "Existing",
                "last_name": "User",
                "role": "provider"
            }
        )
        
        assert response.status_code == 400
        assert "Registration failed" in response.json()["detail"]
    
    def test_login_success(self, client, mock_auth_service, sample_user_response):
        """Test successful login."""
        # Mock authentication
        mock_auth_service.authenticate_user.return_value = sample_user_response
        mock_auth_service.create_access_token.return_value = "access_token_123"
        mock_auth_service.create_refresh_token.return_value = "refresh_token_123"
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",  # OAuth2 uses username field
                "password": "Test123!@#"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "access_token_123"
        assert data["refresh_token"] == "refresh_token_123"
        assert data["token_type"] == "Bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self, client, mock_auth_service):
        """Test login with invalid credentials."""
        # Mock failed authentication
        mock_auth_service.authenticate_user.return_value = None
        
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "WrongPassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        with patch('app.api.v1.auth.get_current_user') as mock_get_user:
            mock_get_user.return_value = UserResponse(
                id="user:123",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                role="provider",
                is_active=True,
                password_reset_required=False,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
            
            response = client.post(
                "/api/v1/auth/logout",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["message"] == "Logged out successfully"
    
    def test_refresh_token_success(self, client, mock_auth_service, sample_user_response):
        """Test token refresh."""
        # Mock token verification and user retrieval
        mock_auth_service.verify_token.return_value = {
            "user_id": "user:123",
            "type": "refresh"
        }
        
        with patch('app.api.v1.auth.user_service') as mock_user_service:
            mock_user_service.get_user_by_id.return_value = sample_user_response
            mock_auth_service.create_access_token.return_value = "new_access_token"
            mock_auth_service.create_refresh_token.return_value = "new_refresh_token"
            
            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "valid_refresh_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "new_access_token"
            assert data["refresh_token"] == "new_refresh_token"
    
    def test_change_password_success(self, client, auth_headers, mock_user_service):
        """Test password change."""
        with patch('app.api.v1.auth.get_current_user') as mock_get_user:
            current_user = UserResponse(
                id="user:123",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                role="provider",
                is_active=True,
                password_reset_required=False,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
            mock_get_user.return_value = current_user
            
            mock_user_service.change_password.return_value = True
            
            response = client.post(
                "/api/v1/auth/change-password",
                headers=auth_headers,
                json={
                    "current_password": "OldPassword123!",
                    "new_password": "NewPassword123!"
                }
            )
            
            assert response.status_code == 200
            assert response.json()["message"] == "Password changed successfully"
    
    def test_reset_password_request(self, client, mock_user_service):
        """Test password reset request."""
        mock_user_service.get_user_by_email.return_value = UserResponse(
            id="user:123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            role="provider",
            is_active=True,
            password_reset_required=False,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200
        assert "Password reset email sent" in response.json()["message"]
    
    def test_me_endpoint(self, client, auth_headers):
        """Test current user endpoint."""
        with patch('app.api.v1.auth.get_current_user') as mock_get_user:
            mock_get_user.return_value = UserResponse(
                id="user:123",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                role="provider",
                is_active=True,
                password_reset_required=False,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
            
            response = client.get(
                "/api/v1/auth/me",
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["id"] == "user:123"