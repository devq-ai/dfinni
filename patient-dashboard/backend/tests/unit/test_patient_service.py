"""
Unit tests for PatientService
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from app.services.patient_service import PatientService
from app.models.patient import PatientCreate, PatientUpdate, PatientResponse, PatientStatus


@pytest.mark.unit
@pytest.mark.db
class TestPatientService:
    """Test cases for PatientService."""
    
    @pytest.mark.asyncio
    async def test_create_patient_success(self, patient_service, patient_data, mock_db):
        """Test successful patient creation."""
        # Mock database response
        mock_db.create.return_value = [{
            "id": "patient:123",
            **patient_data,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_by": "user:456"
        }]
        
        patient_create = PatientCreate(**patient_data)
        result = await patient_service.create_patient(patient_create, "user:456")
        
        assert result.id == "patient:123"
        assert result.first_name == patient_data["first_name"]
        assert result.last_name == patient_data["last_name"]
        assert result.medical_record_number == patient_data["medical_record_number"]
        
        # Verify database call
        mock_db.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_patient_duplicate_mrn(self, patient_service, patient_data, mock_db):
        """Test patient creation with duplicate MRN."""
        # Mock database to raise exception for duplicate
        mock_db.create.side_effect = Exception("Duplicate medical_record_number")
        
        patient_create = PatientCreate(**patient_data)
        
        with pytest.raises(Exception, match="Duplicate medical_record_number"):
            await patient_service.create_patient(patient_create, "user:456")
    
    @pytest.mark.asyncio
    async def test_get_patient_by_id_found(self, patient_service, patient_data, mock_db):
        """Test getting patient by ID when found."""
        # Mock database response
        mock_db.select.return_value = [{
            "id": "patient:123",
            **patient_data,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_by": "user:456"
        }]
        
        result = await patient_service.get_patient("patient:123")
        
        assert result is not None
        assert result.id == "patient:123"
        assert result.first_name == patient_data["first_name"]
        
        # Verify database call
        mock_db.select.assert_called_once_with("patient:123")
    
    @pytest.mark.asyncio
    async def test_get_patient_by_id_not_found(self, patient_service, mock_db):
        """Test getting patient by ID when not found."""
        # Mock database to return empty list
        mock_db.select.return_value = []
        
        result = await patient_service.get_patient("patient:999")
        
        assert result is None
        mock_db.select.assert_called_once_with("patient:999")
    
    @pytest.mark.asyncio
    async def test_get_patients_with_filters(self, patient_service, mock_db):
        """Test getting patients with filters."""
        # Mock database response
        mock_db.query.return_value = [
            {
                "id": "patient:1",
                "first_name": "John",
                "last_name": "Doe",
                "status": "active"
            },
            {
                "id": "patient:2",
                "first_name": "Jane",
                "last_name": "Smith",
                "status": "active"
            }
        ]
        
        result = await patient_service.get_patients(
            skip=0,
            limit=10,
            status=PatientStatus.ACTIVE,
            search="John"
        )
        
        assert len(result) == 2
        assert result[0].id == "patient:1"
        
        # Verify query was called with proper filters
        mock_db.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_patient_success(self, patient_service, patient_data, mock_db):
        """Test successful patient update."""
        # Mock database responses
        mock_db.select.return_value = [{
            "id": "patient:123",
            **patient_data,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_by": "user:456"
        }]
        
        updated_data = patient_data.copy()
        updated_data["phone"] = "555-9999"
        
        mock_db.update.return_value = [{
            "id": "patient:123",
            **updated_data,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z",
            "created_by": "user:456"
        }]
        
        update = PatientUpdate(phone="555-9999")
        result = await patient_service.update_patient("patient:123", update)
        
        assert result is not None
        assert result.phone == "555-9999"
        
        # Verify both select and update were called
        mock_db.select.assert_called_once_with("patient:123")
        mock_db.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_patient_not_found(self, patient_service, mock_db):
        """Test updating non-existent patient."""
        # Mock database to return empty list
        mock_db.select.return_value = []
        
        update = PatientUpdate(phone="555-9999")
        result = await patient_service.update_patient("patient:999", update)
        
        assert result is None
        mock_db.select.assert_called_once_with("patient:999")
        mock_db.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_patient_success(self, patient_service, mock_db):
        """Test successful patient deletion."""
        # Mock database response
        mock_db.select.return_value = [{"id": "patient:123"}]
        mock_db.delete.return_value = True
        
        result = await patient_service.delete_patient("patient:123")
        
        assert result is True
        mock_db.select.assert_called_once_with("patient:123")
        mock_db.delete.assert_called_once_with("patient:123")
    
    @pytest.mark.asyncio
    async def test_delete_patient_not_found(self, patient_service, mock_db):
        """Test deleting non-existent patient."""
        # Mock database to return empty list
        mock_db.select.return_value = []
        
        result = await patient_service.delete_patient("patient:999")
        
        assert result is False
        mock_db.select.assert_called_once_with("patient:999")
        mock_db.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_patient_status(self, patient_service, patient_data, mock_db):
        """Test updating patient status."""
        # Mock database responses
        mock_db.select.return_value = [{
            "id": "patient:123",
            **patient_data,
            "status": "active"
        }]
        
        mock_db.update.return_value = [{
            "id": "patient:123",
            **patient_data,
            "status": "inactive"
        }]
        
        result = await patient_service.update_patient_status(
            "patient:123",
            PatientStatus.INACTIVE,
            "user:456",
            "Patient moved out of state"
        )
        
        assert result is not None
        assert result.status == PatientStatus.INACTIVE
        
        # Verify audit logging was called
        with patch('app.services.patient_service.audit_logger') as mock_audit:
            await patient_service.update_patient_status(
                "patient:123",
                PatientStatus.INACTIVE,
                "user:456",
                "Patient moved out of state"
            )
            mock_audit.log_status_change.assert_called()
    
    @pytest.mark.asyncio
    async def test_search_patients(self, patient_service, mock_db):
        """Test patient search functionality."""
        # Mock database response
        mock_db.query.return_value = [
            {
                "id": "patient:1",
                "first_name": "John",
                "last_name": "Doe",
                "medical_record_number": "MRN123"
            }
        ]
        
        result = await patient_service.search_patients("john")
        
        assert len(result) == 1
        assert result[0].first_name == "John"
        
        # Verify query includes search terms
        mock_db.query.assert_called_once()
        query_call = mock_db.query.call_args[0][0]
        assert "john" in query_call.lower()
    
    @pytest.mark.asyncio
    async def test_get_patient_statistics(self, patient_service, mock_db):
        """Test getting patient statistics."""
        # Mock database response for statistics
        mock_db.query.return_value = [{
            "total": 100,
            "active": 80,
            "inactive": 15,
            "inquiry": 5
        }]
        
        result = await patient_service.get_patient_statistics()
        
        assert result["total"] == 100
        assert result["active"] == 80
        assert result["inactive"] == 15
        assert result["inquiry"] == 5
        
        mock_db.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_bulk_update_patients(self, patient_service, mock_db):
        """Test bulk patient update."""
        patient_ids = ["patient:1", "patient:2", "patient:3"]
        update_data = {"status": "inactive"}
        
        # Mock successful updates
        mock_db.query.return_value = [
            {"id": pid, "updated": True} for pid in patient_ids
        ]
        
        result = await patient_service.bulk_update_patients(patient_ids, update_data)
        
        assert result["updated_count"] == 3
        assert all(r["updated"] for r in result["results"])
        
        mock_db.query.assert_called_once()