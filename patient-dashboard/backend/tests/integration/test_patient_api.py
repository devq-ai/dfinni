"""
Integration tests for patient API endpoints
Per Production Proposal: Add Logfire instrumentation to all test cases
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import logfire

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
        logfire.info("Testing patient creation API", test_case="create_patient_success")
        
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
        
        logfire.info("Patient created via API successfully", 
                    patient_id="patient:123", 
                    mrn=patient_data["medical_record_number"])
    
    def test_create_patient_invalid_data(self, client, auth_headers, mock_current_user):
        """Test patient creation with invalid data."""
        logfire.info("Testing patient creation with invalid data", test_case="create_patient_invalid_data")
        
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
        
        logfire.info("Invalid patient data properly rejected")
    
    def test_get_patients_list(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test getting list of patients."""
        logfire.info("Testing patient list retrieval", test_case="get_patients_list")
        
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
        
        logfire.info("Patient list retrieved successfully", patient_count=2)
    
    def test_get_patients_with_filters(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test getting patients with filters."""
        logfire.info("Testing patient list with filters", test_case="get_patients_with_filters")
        
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
        
        logfire.info("Filtered patient list retrieved", status="active", search="john")
    
    def test_get_patient_by_id_success(self, client, auth_headers, mock_current_user, mock_patient_service, patient_data):
        """Test getting patient by ID."""
        logfire.info("Testing patient retrieval by ID", test_case="get_patient_by_id_success")
        
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
        
        logfire.info("Patient retrieved by ID successfully", patient_id="patient:123")
    
    def test_get_patient_by_id_not_found(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test getting non-existent patient."""
        logfire.info("Testing non-existent patient retrieval", test_case="get_patient_by_id_not_found")
        
        # Mock service to return None
        mock_patient_service.get_patient.return_value = None
        
        response = client.get(
            "/api/v1/patients/patient:999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Patient not found" in response.json()["detail"]
        
        logfire.info("Non-existent patient properly handled", patient_id="patient:999")
    
    def test_update_patient_success(self, client, auth_headers, mock_current_user, mock_patient_service, patient_data):
        """Test updating patient."""
        logfire.info("Testing patient update", test_case="update_patient_success")
        
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
        
        logfire.info("Patient updated successfully", patient_id="patient:123", field="phone")
    
    def test_delete_patient_success(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test deleting patient (admin only)."""
        logfire.info("Testing patient deletion by admin", test_case="delete_patient_success")
        
        # Change user role to admin
        mock_current_user.role = "admin"
        
        # Mock service response
        mock_patient_service.delete_patient.return_value = True
        
        response = client.delete(
            "/api/v1/patients/patient:123",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        logfire.info("Patient deleted successfully", patient_id="patient:123")
    
    def test_delete_patient_forbidden(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test deleting patient without admin role."""
        logfire.info("Testing patient deletion without admin role", test_case="delete_patient_forbidden")
        
        # User is provider, not admin
        mock_current_user.role = "provider"
        
        response = client.delete(
            "/api/v1/patients/patient:123",
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
        
        logfire.info("Non-admin deletion properly rejected", user_role="provider")
    
    def test_search_patients(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test patient search endpoint."""
        logfire.info("Testing patient search", test_case="search_patients")
        
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
        
        logfire.info("Patient search completed successfully", query="john", results=1)
    
    def test_update_patient_status(self, client, auth_headers, mock_current_user, mock_patient_service, patient_data):
        """Test updating patient status."""
        logfire.info("Testing patient status update", test_case="update_patient_status")
        
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
        
        logfire.info("Patient status updated successfully", 
                    patient_id="patient:123", 
                    new_status="inactive")
    
    def test_patient_statistics(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test patient statistics endpoint."""
        logfire.info("Testing patient statistics retrieval", test_case="patient_statistics")
        
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
        
        logfire.info("Patient statistics retrieved successfully", 
                    total=100, 
                    active=80, 
                    inactive=15)