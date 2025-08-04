"""
Global pytest configuration and fixtures for PFINNI Patient Dashboard tests.
Per Production Proposal: Enable Logfire logging in all tests for observability
"""
import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
import os
import sys
import logfire

# Add the app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure Logfire for testing per Production Proposal
logfire.configure(
    service_name="pfinni-backend-tests",
    environment="testing",
    send_to_logfire=os.getenv("PFINNI_LOGFIRE_TOKEN") is not None  # Only send if token exists
)

from app.database.connection import DatabaseConnection
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.patient_service import PatientService
from app.models.user import UserCreate, UserResponse


# Configure event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_db() -> AsyncGenerator[AsyncMock, None]:
    """Mock database connection."""
    mock = AsyncMock(spec=DatabaseConnection)
    mock.query = AsyncMock()
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    mock.select = AsyncMock()
    yield mock


@pytest.fixture
def auth_service() -> AuthService:
    """Create auth service instance."""
    return AuthService()


@pytest.fixture
def user_service(mock_db) -> UserService:
    """Create user service instance with mocked database."""
    service = UserService()
    service.db = mock_db
    return service


@pytest.fixture
def patient_service(mock_db) -> PatientService:
    """Create patient service instance with mocked database."""
    service = PatientService()
    service.db = mock_db
    return service


@pytest.fixture
def sample_user_create() -> UserCreate:
    """Sample user creation data."""
    return UserCreate(
        email="test@example.com",
        password="Test123!@#",
        first_name="Test",
        last_name="User",
        role="PROVIDER"
    )


@pytest.fixture
def sample_user_response() -> UserResponse:
    """Sample user response data."""
    return UserResponse(
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


@pytest.fixture
def auth_headers() -> dict:
    """Sample auth headers with JWT token."""
    return {
        "Authorization": "Bearer test-jwt-token"
    }


@pytest_asyncio.fixture
async def test_client():
    """Create test client for API testing."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    # Override database connection for tests
    async def override_get_db():
        return AsyncMock(spec=DatabaseConnection)
    
    from app.database.connection import get_database
    app.dependency_overrides[get_database] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


# Test data fixtures
@pytest.fixture
def patient_data():
    """Sample patient data."""
    return {
        "medical_record_number": "MRN123456",
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1980-01-01",
        "gender": "male",
        "phone": "555-1234",
        "email": "john.doe@example.com",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        },
        "emergency_contact": {
            "name": "Jane Doe",
            "relationship": "spouse",
            "phone": "555-5678"
        },
        "status": "active",
        "insurance": {
            "provider": "Blue Cross",
            "policy_number": "BC123456",
            "group_number": "GRP789"
        }
    }


@pytest.fixture
def alert_data():
    """Sample alert data."""
    return {
        "patient_id": "patient:123",
        "type": "medication",
        "severity": "high",
        "title": "Medication Non-Adherence",
        "description": "Patient missed 3 doses of prescribed medication",
        "triggered_by": "system",
        "requires_action": True
    }


# Logfire fixture for test logging
@pytest.fixture(autouse=True)
def log_test_info(request):
    """Automatically log test information to Logfire."""
    test_name = request.node.name
    test_file = request.node.parent.name
    test_markers = [marker.name for marker in request.node.iter_markers()]
    
    logfire.info(
        "Test started",
        test_name=test_name,
        test_file=test_file,
        markers=test_markers
    )
    
    yield
    
    # Log test result
    if hasattr(request.node, 'rep_call'):
        outcome = request.node.rep_call.outcome
        duration = request.node.rep_call.duration
        
        if outcome == 'passed':
            logfire.info(
                "Test passed",
                test_name=test_name,
                duration_seconds=duration
            )
        elif outcome == 'failed':
            logfire.error(
                "Test failed",
                test_name=test_name,
                duration_seconds=duration,
                error=str(request.node.rep_call.longrepr)
            )
        elif outcome == 'skipped':
            logfire.info(
                "Test skipped",
                test_name=test_name,
                reason=str(request.node.rep_call.longrepr)
            )


# Hook to capture test results
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test results for Logfire logging."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# Marker configurations
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "db: mark test as database related"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API endpoint related"
    )