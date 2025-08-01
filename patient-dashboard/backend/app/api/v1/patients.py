"""
Patients API endpoints.
Handles CRUD operations for patient management.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.models.patient import (
    PatientCreate, PatientUpdate, PatientResponse, 
    PatientListResponse, PatientSearchFilters
)
from app.models.user import UserResponse
from app.api.v1.auth import get_current_user
from app.services.patient_service import PatientService
from app.core.exceptions import ValidationException, ResourceNotFoundException
from app.config.settings import get_settings

settings = get_settings()
router = APIRouter()

# Initialize patient service
patient_service = PatientService()




@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a new patient record."""
    try:
        # Check permissions
        if current_user.role not in ["ADMIN", "DOCTOR", "NURSE"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to create patients"
            )
        
        # Create patient
        patient = await patient_service.create_patient(patient_data, current_user.id)
        return patient
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}"
        )


@router.get("/", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    filter_by_status: Optional[str] = None,
    risk_level: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """List patients with pagination and filtering."""
    try:
        # Create filters
        filters = PatientSearchFilters(
            search=search,
            status=filter_by_status,
            risk_level=risk_level
        )
        
        # Get patients
        result = await patient_service.list_patients(
            filters=filters,
            page=page,
            limit=limit
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list patients: {str(e)}"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get patient by ID."""
    try:
        patient = await patient_service.get_patient_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get patient: {str(e)}"
        )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update patient information."""
    try:
        # Check permissions
        if current_user.role not in ["ADMIN", "DOCTOR", "NURSE"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update patients"
            )
        
        # Update patient
        patient = await patient_service.update_patient(
            patient_id, 
            patient_data, 
            current_user.id
        )
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return patient
        
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update patient: {str(e)}"
        )


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a patient record (soft delete)."""
    try:
        # Check permissions - only ADMIN can delete
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can delete patient records"
            )
        
        # Delete patient
        success = await patient_service.delete_patient(patient_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return {"message": "Patient deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete patient: {str(e)}"
        )


@router.get("/{patient_id}/insurance")
async def get_patient_insurance(
    patient_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get patient insurance information."""
    try:
        patient = await patient_service.get_patient_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return patient.insurance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insurance information: {str(e)}"
        )


class PatientNoteRequest(BaseModel):
    note: str = Field(..., description="Note content")

@router.post("/{patient_id}/notes")
async def add_patient_note(
    patient_id: str,
    note_data: PatientNoteRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Add a note to patient record."""
    try:
        # Check permissions
        if current_user.role not in ["ADMIN", "DOCTOR", "NURSE"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add notes"
            )
        
        # Add note
        result = await patient_service.add_patient_note(
            patient_id=patient_id,
            note=note_data.note,
            user_id=current_user.id
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        return {"message": "Note added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add note: {str(e)}"
        )


@router.get("/search/advanced")
async def advanced_search(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    member_id: Optional[str] = None,
    ssn_last_four: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """Advanced patient search with multiple criteria."""
    try:
        # Build search criteria
        criteria = {}
        if first_name:
            criteria["first_name"] = first_name
        if last_name:
            criteria["last_name"] = last_name
        if member_id:
            criteria["member_id"] = member_id
        if ssn_last_four:
            criteria["ssn_last_four"] = ssn_last_four
        if date_of_birth:
            criteria["date_of_birth"] = date_of_birth
        
        # Search patients
        patients = await patient_service.advanced_search(criteria)
        
        return {"patients": patients, "total": len(patients)}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )