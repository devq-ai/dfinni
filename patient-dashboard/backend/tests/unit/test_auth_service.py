"""
Unit tests for AuthService
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import jwt

from app.services.auth_service import AuthService
from app.models.user import UserResponse
from app.core.exceptions import AuthenticationException, AuthorizationException


@pytest.mark.unit
@pytest.mark.auth
class TestAuthService:
    """Test cases for AuthService."""
    
    def test_create_access_token(self, auth_service, sample_user_response):
        """Test access token creation."""
        token = auth_service.create_access_token(sample_user_response)
        
        # Verify token is a string
        assert isinstance(token, str)
        
        # Decode and verify token contents
        decoded = jwt.decode(
            token, 
            auth_service.secret_key, 
            algorithms=[auth_service.algorithm]
        )
        
        assert decoded["user_id"] == sample_user_response.id
        assert decoded["email"] == sample_user_response.email
        assert decoded["role"] == sample_user_response.role
        assert "exp" in decoded
        assert "iat" in decoded
    
    def test_create_refresh_token(self, auth_service, sample_user_response):
        """Test refresh token creation."""
        token = auth_service.create_refresh_token(sample_user_response)
        
        # Verify token is a string
        assert isinstance(token, str)
        
        # Decode and verify token contents
        decoded = jwt.decode(
            token, 
            auth_service.secret_key, 
            algorithms=[auth_service.algorithm]
        )
        
        assert decoded["user_id"] == sample_user_response.id
        assert decoded["type"] == "refresh"
        assert "exp" in decoded
    
    def test_verify_token_valid(self, auth_service, sample_user_response):
        """Test token verification with valid token."""
        token = auth_service.create_access_token(sample_user_response)
        payload = auth_service.verify_token(token)
        
        assert payload["user_id"] == sample_user_response.id
        assert payload["email"] == sample_user_response.email
        assert payload["role"] == sample_user_response.role
    
    def test_verify_token_expired(self, auth_service):
        """Test token verification with expired token."""
        # Create an expired token
        payload = {
            "user_id": "user:123",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            payload, 
            auth_service.secret_key, 
            algorithm=auth_service.algorithm
        )
        
        with pytest.raises(AuthenticationException, match="Token has expired"):
            auth_service.verify_token(expired_token)
    
    def test_verify_token_invalid(self, auth_service):
        """Test token verification with invalid token."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(AuthenticationException, match="Invalid token"):
            auth_service.verify_token(invalid_token)
    
    def test_verify_password_correct(self, auth_service):
        """Test password verification with correct password."""
        plain_password = "Test123!@#"
        hashed_password = auth_service.hash_password(plain_password)
        
        assert auth_service.verify_password(plain_password, hashed_password) is True
    
    def test_verify_password_incorrect(self, auth_service):
        """Test password verification with incorrect password."""
        plain_password = "Test123!@#"
        wrong_password = "Wrong123!@#"
        hashed_password = auth_service.hash_password(plain_password)
        
        assert auth_service.verify_password(wrong_password, hashed_password) is False
    
    def test_hash_password(self, auth_service):
        """Test password hashing."""
        plain_password = "Test123!@#"
        hashed = auth_service.hash_password(plain_password)
        
        # Verify hash is different from plain password
        assert hashed != plain_password
        
        # Verify hash is consistent (can be verified)
        assert auth_service.verify_password(plain_password, hashed) is True
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, sample_user_response):
        """Test user authentication with valid credentials."""
        email = "test@example.com"
        password = "Test123!@#"
        hashed_password = auth_service.hash_password(password)
        
        # Mock user service
        with patch.object(auth_service, 'user_service') as mock_user_service:
            mock_user_service.get_user_by_email.return_value = sample_user_response
            # Simulate the user having the correct password hash
            sample_user_response.password_hash = hashed_password
            
            result = await auth_service.authenticate_user(email, password)
            
            assert result == sample_user_response
            mock_user_service.get_user_by_email.assert_called_once_with(email)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, auth_service):
        """Test user authentication with non-existent user."""
        email = "nonexistent@example.com"
        password = "Test123!@#"
        
        # Mock user service to return None
        with patch.object(auth_service, 'user_service') as mock_user_service:
            mock_user_service.get_user_by_email.return_value = None
            
            result = await auth_service.authenticate_user(email, password)
            
            assert result is None
            mock_user_service.get_user_by_email.assert_called_once_with(email)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service, sample_user_response):
        """Test user authentication with wrong password."""
        email = "test@example.com"
        password = "Test123!@#"
        wrong_password = "Wrong123!@#"
        hashed_password = auth_service.hash_password(password)
        
        # Mock user service
        with patch.object(auth_service, 'user_service') as mock_user_service:
            sample_user_response.password_hash = hashed_password
            mock_user_service.get_user_by_email.return_value = sample_user_response
            
            result = await auth_service.authenticate_user(email, wrong_password)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, auth_service, sample_user_response):
        """Test user authentication with inactive user."""
        email = "test@example.com"
        password = "Test123!@#"
        hashed_password = auth_service.hash_password(password)
        
        # Mock user service with inactive user
        with patch.object(auth_service, 'user_service') as mock_user_service:
            sample_user_response.is_active = False
            sample_user_response.password_hash = hashed_password
            mock_user_service.get_user_by_email.return_value = sample_user_response
            
            result = await auth_service.authenticate_user(email, password)
            
            assert result is None
    
    def test_check_permissions_admin(self, auth_service):
        """Test permission check for admin user."""
        user_role = "admin"
        required_roles = ["admin", "provider"]
        
        # Should not raise exception
        auth_service.check_permissions(user_role, required_roles)
    
    def test_check_permissions_authorized(self, auth_service):
        """Test permission check for authorized user."""
        user_role = "provider"
        required_roles = ["admin", "provider"]
        
        # Should not raise exception
        auth_service.check_permissions(user_role, required_roles)
    
    def test_check_permissions_unauthorized(self, auth_service):
        """Test permission check for unauthorized user."""
        user_role = "patient"
        required_roles = ["admin", "provider"]
        
        with pytest.raises(AuthorizationException, match="Insufficient permissions"):
            auth_service.check_permissions(user_role, required_roles)
    
    @pytest.mark.asyncio
    async def test_log_authentication(self, auth_service):
        """Test authentication logging."""
        # Mock the audit logger
        with patch.object(auth_service, 'audit_logger') as mock_logger:
            await auth_service.log_authentication(
                email="test@example.com",
                action="LOGIN",
                success=True,
                ip_address="127.0.0.1",
                user_agent="Test Browser"
            )
            
            mock_logger.log_authentication.assert_called_once_with(
                email="test@example.com",
                action="LOGIN",
                success=True,
                ip_address="127.0.0.1",
                user_agent="Test Browser",
                error_message=None
            )