"""
Audit log model for HIPAA compliance.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class AuditAction(str, Enum):
    """Types of auditable actions."""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    STATUS_CHANGE = "STATUS_CHANGE"

class ResourceType(str, Enum):
    """Types of resources that can be audited."""
    PATIENT = "PATIENT"
    USER = "USER"
    ALERT = "ALERT"
    REPORT = "REPORT"
    SYSTEM = "SYSTEM"

class AuditLogBase(BaseModel):
    """Base audit log model."""
    action: AuditAction
    resource_type: ResourceType
    resource_id: Optional[str] = None
    user_id: str
    user_email: str
    user_role: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    changes: Optional[Dict[str, Any]] = Field(None, description="JSON object of changes made")
    success: bool = True
    error_message: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    """Model for creating audit log entries."""
    pass

class AuditLogInDB(AuditLogBase):
    """Audit log model as stored in database."""
    id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AuditLogResponse(AuditLogInDB):
    """Audit log model for API responses."""
    pass

class AuditLogListResponse(BaseModel):
    """Response model for audit log list endpoint."""
    logs: list[AuditLogResponse]
    total: int
    page: int
    per_page: int
    pages: int

class AuditLogSearchParams(BaseModel):
    """Parameters for audit log search."""
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[str] = None
    success: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=200)
    sort_order: str = Field("desc", pattern="^(asc|desc)$")