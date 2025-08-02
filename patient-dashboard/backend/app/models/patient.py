"""
Patient model with HIPAA-compliant field handling and validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
import re

class PatientStatus(str, Enum):
    """Patient status workflow states."""
    INQUIRY = "inquiry"
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    CHURNED = "churned"
    URGENT = "urgent"

class RiskLevel(str, Enum):
    """Patient risk levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Gender(str, Enum):
    """Gender options."""
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"

class Address(BaseModel):
    """Address model."""
    street: str = Field(..., max_length=200)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=2)
    zip: str = Field(..., max_length=10)
    
    @field_validator('state')
    def validate_state(cls, v):
        if not v.isupper() or len(v) != 2:
            raise ValueError('State must be 2 uppercase letters')
        return v
    
    @field_validator('zip')
    def validate_zip_code(cls, v):
        # Validate US postal code (5 digits or 5+4 format)
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid postal code format')
        return v

class Insurance(BaseModel):
    """Insurance information model."""
    member_id: str = Field(..., max_length=50)
    company: str = Field(..., max_length=100)
    plan_type: str = Field(..., max_length=100)
    group_number: str = Field(..., max_length=50)
    effective_date: str
    termination_date: Optional[str] = None

class PatientBase(BaseModel):
    """Base patient model with common fields."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: str
    email: EmailStr
    phone: str = Field(..., max_length=20)
    ssn: str = Field(..., max_length=11, description="Social Security Number")
    address: Address
    insurance: Insurance
    status: PatientStatus = Field(default=PatientStatus.INQUIRY)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    
    @field_validator('phone')
    def validate_phone(cls, v):
        # Remove all non-numeric characters
        phone_digits = re.sub(r'\D', '', v)
        # Validate US phone number (10 digits)
        if len(phone_digits) != 10:
            raise ValueError('Phone number must be 10 digits')
        return v
    
    @field_validator('ssn')
    def validate_ssn(cls, v):
        # Remove any hyphens
        ssn_digits = re.sub(r'\D', '', v)
        if len(ssn_digits) != 9:
            raise ValueError('SSN must be 9 digits')
        return v
    
    @field_validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        try:
            dob = datetime.strptime(v, "%Y-%m-%d")
            if dob > datetime.now():
                raise ValueError('Date of birth cannot be in the future')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Date of birth must be in YYYY-MM-DD format')
            raise

class PatientCreate(PatientBase):
    """Model for creating a new patient."""
    pass

class PatientUpdate(BaseModel):
    """Model for updating patient information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    middle_name: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Address] = None
    insurance: Optional[Insurance] = None
    status: Optional[PatientStatus] = None
    risk_level: Optional[RiskLevel] = None
    
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
    
    @field_validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v is None:
            return v
        try:
            dob = datetime.strptime(v, "%Y-%m-%d")
            if dob > datetime.now():
                raise ValueError('Date of birth cannot be in the future')
            return v
        except ValueError as e:
            if "time data" in str(e):
                raise ValueError('Date of birth must be in YYYY-MM-DD format')
            raise

class PatientInDB(PatientBase):
    """Patient model as stored in database."""
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PatientResponse(BaseModel):
    """Patient model for API responses (may exclude sensitive fields)."""
    id: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    date_of_birth: str
    email: str
    phone: str
    address: Address
    insurance: Insurance
    status: PatientStatus
    risk_level: RiskLevel
    created_at: datetime
    updated_at: datetime
    
    # Mask SSN for security
    ssn_last_four: Optional[str] = Field(None, description="Last 4 digits of SSN")
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_db(cls, patient: Dict[str, Any]) -> "PatientResponse":
        """Create response from database patient data."""
        # Extract last 4 digits of SSN
        ssn = patient.get("ssn", "")
        ssn_last_four = ssn[-4:] if ssn and len(ssn) >= 4 else None
        
        return cls(
            id=patient["id"],
            first_name=patient["first_name"],
            last_name=patient["last_name"],
            middle_name=patient.get("middle_name"),
            date_of_birth=patient["date_of_birth"],
            email=patient["email"],
            phone=patient["phone"],
            address=patient["address"],
            insurance=patient["insurance"],
            status=patient["status"],
            risk_level=patient["risk_level"],
            created_at=patient["created_at"],
            updated_at=patient["updated_at"],
            ssn_last_four=ssn_last_four
        )

class PatientListResponse(BaseModel):
    """Response model for patient list endpoint."""
    patients: List[PatientResponse]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PatientSearchFilters(BaseModel):
    """Parameters for patient search."""
    search: Optional[str] = Field(None, description="Search in name, email, member ID")
    status: Optional[PatientStatus] = None
    risk_level: Optional[RiskLevel] = None

class PatientStatusChange(BaseModel):
    """Model for patient status change requests."""
    status: PatientStatus
    reason: Optional[str] = Field(None, max_length=500, description="Reason for status change")