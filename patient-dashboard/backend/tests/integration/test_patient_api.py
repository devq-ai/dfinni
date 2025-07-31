"""
Integration tests for patient API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.models.patient import PatientResponse, PatientStatus
from app.models.user import UserResponse


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.db
class TestPatientAPI:
    """Test patient API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user dependency."""
        user = UserResponse(
            id="user:123",
            email="provider@example.com",
            first_name="Test",
            last_name="Provider",
            role="provider",
            is_active=True,
            password_reset_required=False,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        with patch('app.api.v1.patients.get_current_user') as mock:
            mock.return_value = user
            yield user
    
    @pytest.fixture
    def mock_patient_service(self):
        """Mock patient service."""
        with patch('app.api.v1.patients.patient_service') as mock:
            yield mock
    
    def test_create_patient_success(self, client, auth_headers, mock_current_user, mock_patient_service, patient_data):
        """Test successful patient creation."""
        # Mock service response
        mock_patient_service.create_patient.return_value = PatientResponse(
            id="patient:123",
            **patient_data,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            created_by="user:123"
        )
        
        response = client.post(
            "/api/v1/patients/",
            headers=auth_headers,
            json=patient_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "patient:123"
        assert data["medical_record_number"] == patient_data["medical_record_number"]
        assert data["created_by"] == "user:123"
    
    def test_create_patient_invalid_data(self, client, auth_headers, mock_current_user):
        """Test patient creation with invalid data."""
        # Missing required fields
        response = client.post(
            "/api/v1/patients/",
            headers=auth_headers,
            json={
                "first_name": "John"
                # Missing other required fields
            }
        )
        
        assert response.status_code == 422
    
    def test_get_patients_list(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test getting list of patients."""
        # Mock service response
        mock_patient_service.get_patients.return_value = [
            PatientResponse(
                id="patient:1",
                medical_record_number="MRN001",
                first_name="John",
                last_name="Doe",
                date_of_birth="1980-01-01",
                gender="male",
                status=PatientStatus.ACTIVE,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                created_by="user:123"
            ),
            PatientResponse(
                id="patient:2",
                medical_record_number="MRN002",
                first_name="Jane",
                last_name="Smith",
                date_of_birth="1985-05-15",
                gender="female",
                status=PatientStatus.ACTIVE,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                created_by="user:123"
            )
        ]
        
        response = client.get(
            "/api/v1/patients/",
            headers=auth_headers,
            params={"skip": 0, "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "patient:1"
        assert data[1]["id"] == "patient:2"
    
    def test_get_patients_with_filters(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test getting patients with filters."""
        mock_patient_service.get_patients.return_value = []
        
        response = client.get(
            "/api/v1/patients/",
            headers=auth_headers,
            params={
                "skip": 0,
                "limit": 10,
                "status": "active",
                "search": "john"
            }
        )
        
        assert response.status_code == 200
        # Verify service was called with correct parameters
        mock_patient_service.get_patients.assert_called_once_with(
            skip=0,
            limit=10,
            status=PatientStatus.ACTIVE,
            search="john"
        )
    
    def test_get_patient_by_id_success(self, client, auth_headers, mock_current_user, mock_patient_service, patient_data):
        """Test getting patient by ID."""
        # Mock service response
        mock_patient_service.get_patient.return_value = PatientResponse(
            id="patient:123",
            **patient_data,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            created_by="user:123"
        )
        
        response = client.get(
            "/api/v1/patients/patient:123",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "patient:123"
        assert data["medical_record_number"] == patient_data["medical_record_number"]
    
    def test_get_patient_by_id_not_found(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test getting non-existent patient."""
        # Mock service to return None
        mock_patient_service.get_patient.return_value = None
        
        response = client.get(
            "/api/v1/patients/patient:999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Patient not found" in response.json()["detail"]
    
    def test_update_patient_success(self, client, auth_headers, mock_current_user, mock_patient_service, patient_data):
        """Test updating patient."""
        # Mock service response
        updated_data = patient_data.copy()
        updated_data["phone"] = "555-9999"
        
        mock_patient_service.update_patient.return_value = PatientResponse(
            id="patient:123",
            **updated_data,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
            created_by="user:123"
        )
        
        response = client.put(
            "/api/v1/patients/patient:123",
            headers=auth_headers,
            json={"phone": "555-9999"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "555-9999"
    
    def test_delete_patient_success(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test deleting patient (admin only)."""
        # Change user role to admin
        mock_current_user.role = "admin"
        
        # Mock service response
        mock_patient_service.delete_patient.return_value = True
        
        response = client.delete(
            "/api/v1/patients/patient:123",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    def test_delete_patient_forbidden(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test deleting patient without admin role."""
        # User is provider, not admin
        mock_current_user.role = "provider"
        
        response = client.delete(
            "/api/v1/patients/patient:123",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
    
    def test_search_patients(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test patient search endpoint."""
        # Mock service response
        mock_patient_service.search_patients.return_value = [
            PatientResponse(
                id="patient:1",
                medical_record_number="MRN001",
                first_name="John",
                last_name="Doe",
                date_of_birth="1980-01-01",
                gender="male",
                status=PatientStatus.ACTIVE,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                created_by="user:123"
            )
        ]
        
        response = client.get(
            "/api/v1/patients/search",
            headers=auth_headers,
            params={"q": "john"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["first_name"] == "John"
    
    def test_update_patient_status(self, client, auth_headers, mock_current_user, mock_patient_service, patient_data):
        """Test updating patient status."""
        # Mock service response
        updated_data = patient_data.copy()
        updated_data["status"] = "inactive"
        
        mock_patient_service.update_patient_status.return_value = PatientResponse(
            id="patient:123",
            **updated_data,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T12:00:00Z",
            created_by="user:123"
        )
        
        response = client.patch(
            "/api/v1/patients/patient:123/status",
            headers=auth_headers,
            json={
                "status": "inactive",
                "reason": "Patient moved out of state"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"
    
    def test_patient_statistics(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test patient statistics endpoint."""
        # Mock service response
        mock_patient_service.get_patient_statistics.return_value = {
            "total": 100,
            "active": 80,
            "inactive": 15,
            "inquiry": 5,
            "by_status": {
                "active": 80,
                "inactive": 15,
                "inquiry": 5
            }
        }
        
        response = client.get(
            "/api/v1/patients/statistics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 100
        assert data["active"] == 80