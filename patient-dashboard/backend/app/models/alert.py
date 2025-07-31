"""
Alert model for notifications and real-time updates.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class AlertType(str, Enum):
    """Types of alerts."""
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    VITALS = "vitals"
    LAB_RESULT = "lab_result"
    PATIENT_MESSAGE = "patient_message"
    BIRTHDAY = "birthday"
    STATUS_CHANGE = "status_change"
    INSURANCE_EXPIRY = "insurance_expiry"
    SYSTEM = "system"
    URGENT = "urgent"

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertPriority(str, Enum):
    """Alert priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class AlertStatus(str, Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    SNOOZED = "snoozed"
    RESOLVED = "resolved"
    EXPIRED = "expired"

class AlertBase(BaseModel):
    """Base alert model."""
    type: AlertType
    severity: AlertSeverity = AlertSeverity.MEDIUM
    priority: AlertPriority = AlertPriority.MEDIUM
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    patient_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    requires_action: bool = False
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AlertCreate(AlertBase):
    """Model for creating a new alert."""
    triggered_by: str  # user_id or 'system'

class AlertUpdate(BaseModel):
    """Model for updating alert status."""
    status: Optional[AlertStatus] = None
    is_read: Optional[bool] = None
    is_acknowledged: Optional[bool] = None
    resolution_notes: Optional[str] = None
    snoozed_until: Optional[datetime] = None

class AlertInDB(AlertBase):
    """Alert model as stored in database."""
    id: str
    triggered_by: str
    status: AlertStatus = AlertStatus.ACTIVE
    is_read: bool = False
    read_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    snoozed_until: Optional[datetime] = None
    snoozed_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AlertResponse(AlertInDB):
    """Alert model for API responses."""
    pass

class AlertListResponse(BaseModel):
    """Response model for alert list endpoint."""
    alerts: list[AlertResponse]
    total: int
    unread_count: int
    page: int
    per_page: int
    pages: int

class AlertSearchParams(BaseModel):
    """Parameters for alert search."""
    type: Optional[AlertType] = None
    severity: Optional[AlertSeverity] = None
    priority: Optional[AlertPriority] = None
    status: Optional[AlertStatus] = None
    is_read: Optional[bool] = None
    is_acknowledged: Optional[bool] = None
    patient_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)

class AlertBulkAcknowledge(BaseModel):
    """Model for bulk alert acknowledgment."""
    alert_ids: list[str] = Field(..., min_items=1, max_items=100)