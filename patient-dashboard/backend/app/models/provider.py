"""
Provider model for healthcare providers management.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
import re

class ProviderRole(str, Enum):
    """Provider role types."""
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"
    RECEPTIONIST = "receptionist"
    SPECIALIST = "specialist"

class ProviderStatus(str, Enum):
    """Provider status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"

class ProviderBase(BaseModel):
    """Base provider model with common fields."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    role: ProviderRole
    specialization: Optional[str] = Field(None, max_length=100)
    license_number: str = Field(..., max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    status: ProviderStatus = Field(default=ProviderStatus.ACTIVE)
    hire_date: str
    
    @field_validator('phone')
    def validate_phone(cls, v):
        # Remove all non-numeric characters
        phone_digits = re.sub(r'\D', '', v)
        # Validate US phone number (10 digits)
        if len(phone_digits) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v
    
    @field_validator('hire_date')
    def validate_hire_date(cls, v):
        try:
            hire_date = datetime.strptime(v, "%Y-%m-%d")
            if hire_date > datetime.now():
                raise ValueError('Hire date cannot be in the future')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Hire date must be in YYYY-MM-DD format')
            raise

class ProviderCreate(ProviderBase):
    """Model for creating a new provider."""
    pass

class ProviderUpdate(BaseModel):
    """Model for updating provider information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[ProviderRole] = None
    specialization: Optional[str] = Field(None, max_length=100)
    license_number: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    status: Optional[ProviderStatus] = None
    hire_date: Optional[str] = None
    assigned_patients: Optional[List[str]] = None
    
    @field_validator('phone')
    def validate_phone(cls, v):
        if v is None:
            return v
        # Remove all non-numeric characters
        phone_digits = re.sub(r'\D', '', v)
        # Validate US phone number (10 digits)
        if len(phone_digits) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v
    
    @field_validator('hire_date')
    def validate_hire_date(cls, v):
        if v is None:
            return v
        try:
            hire_date = datetime.strptime(v, "%Y-%m-%d")
            if hire_date > datetime.now():
                raise ValueError('Hire date cannot be in the future')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Hire date must be in YYYY-MM-DD format')
            raise

class ProviderInDB(ProviderBase):
    """Provider model as stored in database."""
    id: str
    assigned_patients: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProviderResponse(BaseModel):
    """Provider model for API responses."""
    id: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: str
    phone: str
    role: ProviderRole
    specialization: Optional[str] = None
    license_number: str
    department: Optional[str] = None
    status: ProviderStatus
    hire_date: str
    assigned_patients: List[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_db(cls, provider: Dict[str, Any]) -> "ProviderResponse":
        """Create response from database provider data."""
        # Handle RecordID type from SurrealDB
        provider_id = provider["id"]
        if hasattr(provider_id, 'record_id'):
            provider_id = str(provider_id.record_id)
        else:
            provider_id = str(provider_id)
            
        # Handle datetime strings
        created_at = provider["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        
        updated_at = provider["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            
        return cls(
            id=provider_id,
            first_name=provider["first_name"],
            last_name=provider["last_name"],
            middle_name=provider.get("middle_name"),
            email=provider["email"],
            phone=provider["phone"],
            role=provider["role"],
            specialization=provider.get("specialization"),
            license_number=provider["license_number"],
            department=provider.get("department"),
            status=provider["status"],
            hire_date=provider["hire_date"],
            assigned_patients=provider.get("assigned_patients", []),
            created_at=created_at,
            updated_at=updated_at
        )

class ProviderListResponse(BaseModel):
    """Response model for provider list endpoint."""
    providers: List[ProviderResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

class ProviderSearchFilters(BaseModel):
    """Parameters for provider search."""
    search: Optional[str] = Field(None, description="Search in name, email, license number")
    role: Optional[ProviderRole] = None
    department: Optional[str] = None
    status: Optional[ProviderStatus] = None

class ProviderPatientAssignment(BaseModel):
    """Model for provider-patient assignment."""
    provider_id: str
    patient_id: str
    assigned_by: str
    assigned_at: datetime