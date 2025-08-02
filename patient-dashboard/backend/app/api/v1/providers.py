"""
Providers API endpoints.
Handles CRUD operations for healthcare providers management.
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.models.provider import (
    ProviderCreate, ProviderUpdate, ProviderResponse, 
    ProviderListResponse, ProviderSearchFilters
)
from app.models.user import UserResponse
from app.api.v1.auth import get_current_user
from app.services.provider_service import ProviderService
from app.core.exceptions import ValidationException, ResourceNotFoundException
from app.config.settings import get_settings

settings = get_settings()
router = APIRouter()

# Initialize provider service
provider_service = ProviderService()


@router.post("/", response_model=ProviderResponse)
async def create_provider(
    provider_data: ProviderCreate,
    # current_user: UserResponse = Depends(get_current_user)  # Temporarily disabled for development
):
    """Create a new provider record."""
    try:
        # Check permissions - only admins can create providers
        # if current_user.role != "ADMIN":
        #     raise HTTPException(
        #         status_code=403,
        #         detail="Only administrators can create provider records"
        #     )
        
        # Create provider
        provider = await provider_service.create_provider(provider_data, "admin-user-id")
        return provider
        
    except ValidationException as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create provider: {str(e)}"
        )


@router.get("/", response_model=ProviderListResponse)
async def list_providers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    # current_user: UserResponse = Depends(get_current_user)  # Temporarily disabled for development
):
    """List providers with pagination and filtering."""
    try:
        # Create filters
        filters = ProviderSearchFilters(
            search=search,
            role=role,
            department=department,
            status=status
        )
        
        # Get providers
        result = await provider_service.list_providers(
            filters=filters,
            page=page,
            limit=limit
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list providers: {str(e)}"
        )


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get provider by ID."""
    try:
        provider = await provider_service.get_provider_by_id(provider_id)
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail="Provider not found"
            )
        
        return provider
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get provider: {str(e)}"
        )


@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: str,
    provider_data: ProviderUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update provider information."""
    try:
        # Check permissions - only admins can update providers
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Only administrators can update provider records"
            )
        
        # Update provider
        provider = await provider_service.update_provider(
            provider_id, 
            provider_data, 
            current_user.id
        )
        
        if not provider:
            raise HTTPException(
                status_code=404,
                detail="Provider not found"
            )
        
        return provider
        
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update provider: {str(e)}"
        )


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a provider record (soft delete)."""
    try:
        # Check permissions - only admins can delete
        if current_user.role != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Only administrators can delete provider records"
            )
        
        # Delete provider
        success = await provider_service.delete_provider(provider_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Provider not found"
            )
        
        return {"message": "Provider deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete provider: {str(e)}"
        )


@router.post("/{provider_id}/assign-patient/{patient_id}")
async def assign_patient_to_provider(
    provider_id: str,
    patient_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Assign a patient to a provider."""
    try:
        # Check permissions
        if current_user.role not in ["ADMIN", "DOCTOR"]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to assign patients"
            )
        
        # Assign patient
        result = await provider_service.assign_patient_to_provider(
            provider_id=provider_id,
            patient_id=patient_id,
            user_id=current_user.id
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Provider or patient not found"
            )
        
        return {"message": "Patient assigned successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign patient: {str(e)}"
        )


@router.delete("/{provider_id}/unassign-patient/{patient_id}")
async def unassign_patient_from_provider(
    provider_id: str,
    patient_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Unassign a patient from a provider."""
    try:
        # Check permissions
        if current_user.role not in ["ADMIN", "DOCTOR"]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to unassign patients"
            )
        
        # Unassign patient
        result = await provider_service.unassign_patient_from_provider(
            provider_id=provider_id,
            patient_id=patient_id,
            user_id=current_user.id
        )
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Provider or patient not found"
            )
        
        return {"message": "Patient unassigned successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to unassign patient: {str(e)}"
        )


@router.get("/{provider_id}/patients")
async def get_provider_patients(
    provider_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all patients assigned to a provider."""
    try:
        patients = await provider_service.get_provider_patients(provider_id)
        
        if patients is None:
            raise HTTPException(
                status_code=404,
                detail="Provider not found"
            )
        
        return {"patients": patients, "total": len(patients)}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get provider patients: {str(e)}"
        )