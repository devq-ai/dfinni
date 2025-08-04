"""
Audit logging service for tracking all data access and modifications.
Per Production Proposal: Implement audit logging for all data access
"""
import json
import logfire
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

from app.database.connection import DatabaseConnection
from app.models.user import UserRole


class AuditAction(str, Enum):
    """Types of audit actions."""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # Data access
    VIEW = "view"
    LIST = "list"
    SEARCH = "search"
    EXPORT = "export"
    
    # Data modification
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    
    # Security
    ACCESS_DENIED = "access_denied"
    PERMISSION_CHANGE = "permission_change"
    IMPERSONATION = "impersonation"


class AuditResource(str, Enum):
    """Types of resources being audited."""
    PATIENT = "patient"
    USER = "user"
    APPOINTMENT = "appointment"
    MEDICATION = "medication"
    ALERT = "alert"
    DOCUMENT = "document"
    REPORT = "report"
    DASHBOARD = "dashboard"
    SYSTEM = "system"


class AuditEntry(BaseModel):
    """Model for audit log entries."""
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    user_email: str
    user_role: UserRole
    action: AuditAction
    resource: AuditResource
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    organization_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    
    # HIPAA compliance fields
    patient_id: Optional[str] = None  # If action involves patient data
    phi_accessed: bool = False  # Whether PHI was accessed
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AuditService:
    """Service for audit logging and compliance tracking."""
    
    def __init__(self):
        self.db: Optional[DatabaseConnection] = None
        self.audit_table = "audit_logs"
        
    async def initialize(self):
        """Initialize the audit service and create table if needed."""
        if not self.db:
            self.db = DatabaseConnection()
            await self.db.connect()
            
        # Create audit table if it doesn't exist
        await self._create_audit_table()
    
    async def _create_audit_table(self):
        """Create the audit logs table in SurrealDB."""
        query = f"""
        DEFINE TABLE {self.audit_table} SCHEMAFULL;
        DEFINE FIELD timestamp ON {self.audit_table} TYPE datetime;
        DEFINE FIELD user_id ON {self.audit_table} TYPE string;
        DEFINE FIELD user_email ON {self.audit_table} TYPE string;
        DEFINE FIELD user_role ON {self.audit_table} TYPE string;
        DEFINE FIELD action ON {self.audit_table} TYPE string;
        DEFINE FIELD resource ON {self.audit_table} TYPE string;
        DEFINE FIELD resource_id ON {self.audit_table} TYPE string;
        DEFINE FIELD details ON {self.audit_table} TYPE object;
        DEFINE FIELD ip_address ON {self.audit_table} TYPE string;
        DEFINE FIELD user_agent ON {self.audit_table} TYPE string;
        DEFINE FIELD session_id ON {self.audit_table} TYPE string;
        DEFINE FIELD organization_id ON {self.audit_table} TYPE string;
        DEFINE FIELD success ON {self.audit_table} TYPE bool;
        DEFINE FIELD error_message ON {self.audit_table} TYPE string;
        DEFINE FIELD patient_id ON {self.audit_table} TYPE string;
        DEFINE FIELD phi_accessed ON {self.audit_table} TYPE bool;
        
        DEFINE INDEX user_idx ON {self.audit_table} COLUMNS user_id;
        DEFINE INDEX timestamp_idx ON {self.audit_table} COLUMNS timestamp;
        DEFINE INDEX resource_idx ON {self.audit_table} COLUMNS resource, resource_id;
        DEFINE INDEX patient_idx ON {self.audit_table} COLUMNS patient_id;
        """
        
        try:
            await self.db.query(query)
            logfire.info("Audit table created successfully")
        except Exception as e:
            logfire.error("Failed to create audit table", error=str(e))
    
    async def log(
        self,
        user_id: str,
        user_email: str,
        user_role: UserRole,
        action: AuditAction,
        resource: AuditResource,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        patient_id: Optional[str] = None,
        phi_accessed: bool = False
    ) -> AuditEntry:
        """
        Log an audit entry.
        
        Args:
            user_id: ID of the user performing the action
            user_email: Email of the user
            user_role: Role of the user
            action: Type of action performed
            resource: Type of resource accessed
            resource_id: ID of the specific resource
            details: Additional details about the action
            ip_address: IP address of the request
            user_agent: User agent string
            session_id: Session ID if available
            organization_id: Organization ID if applicable
            success: Whether the action was successful
            error_message: Error message if action failed
            patient_id: Patient ID if action involves patient data
            phi_accessed: Whether PHI was accessed
            
        Returns:
            Created audit entry
        """
        entry = AuditEntry(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            organization_id=organization_id,
            success=success,
            error_message=error_message,
            patient_id=patient_id,
            phi_accessed=phi_accessed
        )
        
        # Log to Logfire immediately
        with logfire.span(
            "audit_log",
            user_id=user_id,
            action=action.value,
            resource=resource.value,
            resource_id=resource_id,
            success=success
        ):
            logfire.info(
                f"Audit: {action.value} on {resource.value}",
                **entry.dict(exclude_none=True)
            )
        
        # Store in database
        try:
            if not self.db:
                await self.initialize()
            
            result = await self.db.create(
                self.audit_table,
                entry.dict(exclude_none=True)
            )
            
            if result and len(result) > 0:
                entry.id = result[0].get('id')
            
        except Exception as e:
            logfire.error("Failed to store audit log", error=str(e), entry=entry.dict())
            # Don't fail the operation if audit logging fails
        
        return entry
    
    async def log_patient_access(
        self,
        user_id: str,
        user_email: str,
        user_role: UserRole,
        patient_id: str,
        action: AuditAction,
        fields_accessed: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Log patient data access with PHI tracking.
        
        Args:
            user_id: ID of the user accessing data
            user_email: Email of the user
            user_role: Role of the user
            patient_id: ID of the patient whose data is accessed
            action: Type of action performed
            fields_accessed: List of fields accessed (for PHI tracking)
            **kwargs: Additional audit parameters
        """
        # Determine if PHI was accessed
        phi_fields = {
            'ssn', 'date_of_birth', 'medical_record_number',
            'address', 'phone', 'email', 'insurance',
            'emergency_contact', 'health_information'
        }
        
        phi_accessed = False
        if fields_accessed:
            phi_accessed = any(field in phi_fields for field in fields_accessed)
        
        details = kwargs.get('details', {})
        details['fields_accessed'] = fields_accessed
        
        await self.log(
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            action=action,
            resource=AuditResource.PATIENT,
            resource_id=patient_id,
            patient_id=patient_id,
            phi_accessed=phi_accessed,
            details=details,
            **{k: v for k, v in kwargs.items() if k != 'details'}
        )
    
    async def log_authentication(
        self,
        user_id: str,
        user_email: str,
        action: AuditAction,
        success: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error_message: Optional[str] = None,
        **kwargs
    ):
        """
        Log authentication-related actions.
        
        Args:
            user_id: ID of the user (or attempted user)
            user_email: Email of the user
            action: Authentication action (login, logout, etc.)
            success: Whether the action was successful
            ip_address: IP address of the request
            user_agent: User agent string
            error_message: Error message if failed
            **kwargs: Additional parameters
        """
        await self.log(
            user_id=user_id,
            user_email=user_email,
            user_role=kwargs.get('user_role', UserRole.PATIENT),
            action=action,
            resource=AuditResource.SYSTEM,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
            **{k: v for k, v in kwargs.items() if k not in ['user_role']}
        )
    
    async def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        resource: Optional[AuditResource] = None,
        resource_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEntry]:
        """
        Query audit logs with filters.
        
        Args:
            user_id: Filter by user ID
            resource: Filter by resource type
            resource_id: Filter by specific resource ID
            action: Filter by action type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of audit entries
        """
        if not self.db:
            await self.initialize()
        
        # Build query conditions
        conditions = []
        if user_id:
            conditions.append(f"user_id = '{user_id}'")
        if resource:
            conditions.append(f"resource = '{resource.value}'")
        if resource_id:
            conditions.append(f"resource_id = '{resource_id}'")
        if action:
            conditions.append(f"action = '{action.value}'")
        if start_date:
            conditions.append(f"timestamp >= '{start_date.isoformat()}'")
        if end_date:
            conditions.append(f"timestamp <= '{end_date.isoformat()}'")
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        query = f"""
        SELECT * FROM {self.audit_table}
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT {limit} START {offset}
        """
        
        try:
            results = await self.db.query(query)
            return [AuditEntry(**log) for log in results]
        except Exception as e:
            logfire.error("Failed to query audit logs", error=str(e))
            return []
    
    async def get_user_activity_summary(
        self,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get a summary of user activity for compliance reporting.
        
        Args:
            user_id: User ID to get summary for
            days: Number of days to look back
            
        Returns:
            Summary of user activity
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        logs = await self.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            limit=1000
        )
        
        summary = {
            "user_id": user_id,
            "period_days": days,
            "total_actions": len(logs),
            "actions_by_type": {},
            "resources_accessed": {},
            "phi_access_count": 0,
            "failed_actions": 0,
            "unique_patients_accessed": set()
        }
        
        for log in logs:
            # Count by action type
            action_type = log.action.value
            summary["actions_by_type"][action_type] = summary["actions_by_type"].get(action_type, 0) + 1
            
            # Count by resource type
            resource_type = log.resource.value
            summary["resources_accessed"][resource_type] = summary["resources_accessed"].get(resource_type, 0) + 1
            
            # Track PHI access
            if log.phi_accessed:
                summary["phi_access_count"] += 1
            
            # Track failed actions
            if not log.success:
                summary["failed_actions"] += 1
            
            # Track unique patients
            if log.patient_id:
                summary["unique_patients_accessed"].add(log.patient_id)
        
        summary["unique_patients_accessed"] = len(summary["unique_patients_accessed"])
        
        return summary


# Singleton instance
audit_service = AuditService()