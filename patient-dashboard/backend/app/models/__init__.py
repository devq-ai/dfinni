"""
Pydantic models for the patient dashboard.
"""
from .patient import (
    PatientStatus,
    RiskLevel,
    Gender,
    Address,
    Insurance,
    PatientBase,
    PatientCreate,
    PatientUpdate,
    PatientInDB,
    PatientResponse,
    PatientListResponse,
    PatientSearchFilters,
    PatientStatusChange
)

from .user import (
    UserRole,
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    UserResponse,
    UserListResponse,
    UserLogin,
    UserPasswordChange,
    UserPasswordReset,
    UserPasswordResetConfirm,
    TokenResponse,
    TokenData
)

from .audit import (
    AuditAction,
    ResourceType,
    AuditLogBase,
    AuditLogCreate,
    AuditLogInDB,
    AuditLogResponse,
    AuditLogListResponse,
    AuditLogSearchParams
)

from .alert import (
    AlertType,
    AlertSeverity,
    AlertStatus,
    AlertPriority,
    AlertBase,
    AlertCreate,
    AlertUpdate,
    AlertInDB,
    AlertResponse,
    AlertListResponse,
    AlertSearchParams,
    AlertBulkAcknowledge
)

from .analytics import (
    MetricType,
    DashboardMetrics,
    TimeSeriesData,
    PatientMetrics,
    MetricTrend,
    AnalyticsReport,
    ProviderMetrics,
    SystemHealthMetrics
)

from .chat import (
    ChatRole,
    MessageType,
    ChatContext,
    ChatMessage,
    ChatSession,
    ChatRequest,
    ChatResponse,
    ChatSummary,
    ChatAnalytics
)

__all__ = [
    # Patient models
    "PatientStatus",
    "RiskLevel",
    "Gender",
    "Address",
    "Insurance",
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientInDB",
    "PatientResponse",
    "PatientListResponse",
    "PatientSearchFilters",
    "PatientStatusChange",
    
    # User models
    "UserRole",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserListResponse",
    "UserLogin",
    "UserPasswordChange",
    "UserPasswordReset",
    "UserPasswordResetConfirm",
    "TokenResponse",
    "TokenData",
    
    # Audit models
    "AuditAction",
    "ResourceType",
    "AuditLogBase",
    "AuditLogCreate",
    "AuditLogInDB",
    "AuditLogResponse",
    "AuditLogListResponse",
    "AuditLogSearchParams",
    
    # Alert models
    "AlertType",
    "AlertSeverity",
    "AlertStatus",
    "AlertPriority",
    "AlertBase",
    "AlertCreate",
    "AlertUpdate",
    "AlertInDB",
    "AlertResponse",
    "AlertListResponse",
    "AlertSearchParams",
    "AlertBulkAcknowledge",
    
    # Analytics models
    "MetricType",
    "DashboardMetrics",
    "TimeSeriesData",
    "PatientMetrics",
    "MetricTrend",
    "AnalyticsReport",
    "ProviderMetrics",
    "SystemHealthMetrics",
    
    # Chat models
    "ChatRole",
    "MessageType",
    "ChatContext",
    "ChatMessage",
    "ChatSession",
    "ChatRequest",
    "ChatResponse",
    "ChatSummary",
    "ChatAnalytics"
]
