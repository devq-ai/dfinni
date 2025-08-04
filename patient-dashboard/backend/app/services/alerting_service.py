"""
Alerting service for monitoring critical events and conditions.
Per Production Proposal Phase 2: Set up alerting rules
"""
import asyncio
import logfire
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta, timezone
from enum import Enum
from pydantic import BaseModel, Field
from collections import defaultdict

from app.config.settings import get_settings
from app.services.metrics_service import metrics_service
from app.database.connection import DatabaseConnection

settings = get_settings()


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(str, Enum):
    """Types of system alerts."""
    # Performance
    SLOW_API = "slow_api"
    HIGH_ERROR_RATE = "high_error_rate"
    DATABASE_SLOW = "database_slow"
    CACHE_FAILURE = "cache_failure"
    
    # Security
    AUTH_FAILURE_SPIKE = "auth_failure_spike"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # Business
    PATIENT_DATA_ISSUE = "patient_data_issue"
    ALERT_OVERDUE = "alert_overdue"
    HIGH_RISK_PATIENT = "high_risk_patient"
    
    # System
    SERVICE_DOWN = "service_down"
    DISK_SPACE_LOW = "disk_space_low"
    MEMORY_HIGH = "memory_high"
    
    # Compliance
    PHI_ACCESS_VIOLATION = "phi_access_violation"
    AUDIT_LOG_FAILURE = "audit_log_failure"
    BACKUP_FAILURE = "backup_failure"


class AlertRule(BaseModel):
    """Definition of an alert rule."""
    name: str
    type: AlertType
    severity: AlertSeverity
    condition: Dict[str, Any]
    threshold: float
    time_window_minutes: int = 5
    description: str
    action: str = "notify"
    enabled: bool = True


class Alert(BaseModel):
    """Alert instance."""
    id: Optional[str] = None
    rule_name: str
    type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    details: Dict[str, Any]
    triggered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    status: str = "active"


class AlertingService:
    """Service for managing system alerts and notifications."""
    
    def __init__(self):
        self.db: Optional[DatabaseConnection] = None
        self.alert_rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self._metrics_cache: Dict[str, List[float]] = defaultdict(list)
        self._last_check: Dict[str, datetime] = {}
        self._initialize_rules()
    
    async def initialize(self):
        """Initialize the alerting service."""
        if not self.db:
            self.db = DatabaseConnection()
            await self.db.connect()
        
        # Create alerts table if needed
        await self._create_alerts_table()
        
        # Start monitoring
        asyncio.create_task(self._monitor_loop())
        
        logfire.info("Alerting service initialized", rules_count=len(self.alert_rules))
    
    def _initialize_rules(self):
        """Initialize default alert rules."""
        self.alert_rules = [
            # Performance alerts
            AlertRule(
                name="slow_api_response",
                type=AlertType.SLOW_API,
                severity=AlertSeverity.HIGH,
                condition={"metric": "api.request.duration_ms", "operator": "gt"},
                threshold=5000,  # 5 seconds
                time_window_minutes=5,
                description="API response time exceeds 5 seconds"
            ),
            AlertRule(
                name="high_error_rate",
                type=AlertType.HIGH_ERROR_RATE,
                severity=AlertSeverity.CRITICAL,
                condition={"metric": "api.request.error_rate", "operator": "gt"},
                threshold=0.05,  # 5% error rate
                time_window_minutes=10,
                description="API error rate exceeds 5%"
            ),
            AlertRule(
                name="database_slow_query",
                type=AlertType.DATABASE_SLOW,
                severity=AlertSeverity.MEDIUM,
                condition={"metric": "database.query.duration_ms", "operator": "gt"},
                threshold=1000,  # 1 second
                time_window_minutes=5,
                description="Database queries taking over 1 second"
            ),
            
            # Security alerts
            AlertRule(
                name="auth_failure_spike",
                type=AlertType.AUTH_FAILURE_SPIKE,
                severity=AlertSeverity.HIGH,
                condition={"metric": "auth.failure.count", "operator": "gt"},
                threshold=10,  # 10 failures
                time_window_minutes=5,
                description="Multiple authentication failures detected"
            ),
            AlertRule(
                name="unauthorized_access_attempt",
                type=AlertType.UNAUTHORIZED_ACCESS,
                severity=AlertSeverity.CRITICAL,
                condition={"metric": "auth.unauthorized", "operator": "gt"},
                threshold=5,
                time_window_minutes=1,
                description="Multiple unauthorized access attempts"
            ),
            
            # Business alerts
            AlertRule(
                name="patient_alert_overdue",
                type=AlertType.ALERT_OVERDUE,
                severity=AlertSeverity.HIGH,
                condition={"metric": "alert.overdue.count", "operator": "gt"},
                threshold=5,
                time_window_minutes=60,
                description="Patient alerts not resolved within SLA"
            ),
            AlertRule(
                name="high_risk_patient_added",
                type=AlertType.HIGH_RISK_PATIENT,
                severity=AlertSeverity.MEDIUM,
                condition={"metric": "patient.high_risk.created", "operator": "gt"},
                threshold=1,
                time_window_minutes=1,
                description="High risk patient added to system"
            ),
            
            # Compliance alerts
            AlertRule(
                name="phi_access_violation",
                type=AlertType.PHI_ACCESS_VIOLATION,
                severity=AlertSeverity.CRITICAL,
                condition={"metric": "phi.unauthorized_access", "operator": "gt"},
                threshold=1,
                time_window_minutes=1,
                description="Unauthorized PHI access detected"
            ),
            AlertRule(
                name="audit_log_failure",
                type=AlertType.AUDIT_LOG_FAILURE,
                severity=AlertSeverity.HIGH,
                condition={"metric": "audit.log.failure", "operator": "gt"},
                threshold=5,
                time_window_minutes=5,
                description="Audit logging failures detected"
            )
        ]
    
    async def _create_alerts_table(self):
        """Create alerts and metrics tables in database."""
        # Create alerts table
        alerts_query = """
        DEFINE TABLE system_alerts SCHEMAFULL;
        DEFINE FIELD rule_name ON system_alerts TYPE string;
        DEFINE FIELD type ON system_alerts TYPE string;
        DEFINE FIELD severity ON system_alerts TYPE string;
        DEFINE FIELD title ON system_alerts TYPE string;
        DEFINE FIELD description ON system_alerts TYPE string;
        DEFINE FIELD details ON system_alerts TYPE object;
        DEFINE FIELD triggered_at ON system_alerts TYPE datetime;
        DEFINE FIELD resolved_at ON system_alerts TYPE datetime;
        DEFINE FIELD acknowledged_at ON system_alerts TYPE datetime;
        DEFINE FIELD acknowledged_by ON system_alerts TYPE string;
        DEFINE FIELD status ON system_alerts TYPE string;
        
        DEFINE INDEX alert_status_idx ON system_alerts COLUMNS status;
        DEFINE INDEX alert_severity_idx ON system_alerts COLUMNS severity;
        DEFINE INDEX alert_triggered_idx ON system_alerts COLUMNS triggered_at;
        """
        
        # Create metrics table for alert checking
        metrics_query = """
        DEFINE TABLE metrics SCHEMAFULL;
        DEFINE FIELD type ON metrics TYPE string;
        DEFINE FIELD value ON metrics TYPE number;
        DEFINE FIELD metadata ON metrics TYPE object;
        DEFINE FIELD created_at ON metrics TYPE datetime;
        
        DEFINE INDEX metrics_type_idx ON metrics COLUMNS type;
        DEFINE INDEX metrics_created_idx ON metrics COLUMNS created_at;
        """
        
        try:
            await self.db.query(alerts_query)
            await self.db.query(metrics_query)
        except Exception as e:
            logfire.error("Failed to create alerts/metrics tables", error=str(e))
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while True:
            try:
                await self._check_all_rules()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logfire.error("Alert monitoring error", error=str(e))
                await asyncio.sleep(60)
    
    async def _check_all_rules(self):
        """Check all alert rules."""
        for rule in self.alert_rules:
            if rule.enabled:
                try:
                    await self._check_rule(rule)
                except Exception as e:
                    logfire.error(
                        "Failed to check alert rule",
                        rule=rule.name,
                        error=str(e)
                    )
    
    async def _check_rule(self, rule: AlertRule):
        """Check a single alert rule."""
        # Check if rule is already triggered
        if rule.name in self.active_alerts:
            return
        
        # Get metric value based on rule type
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=rule.time_window_minutes)
        
        triggered = False
        value = 0
        details = {"threshold": rule.threshold, "time_window": rule.time_window_minutes}
        
        try:
            if rule.type == AlertType.SLOW_API:
                # Query recent API response times
                metrics = await self._get_recent_metrics("api_request_duration", window_start)
                if metrics:
                    # Calculate 95th percentile
                    sorted_metrics = sorted(metrics)
                    p95_index = int(len(sorted_metrics) * 0.95)
                    value = sorted_metrics[p95_index] if p95_index < len(sorted_metrics) else sorted_metrics[-1]
                    triggered = value > rule.threshold
                    details["p95_duration_ms"] = value
                    details["sample_count"] = len(metrics)
            
            elif rule.type == AlertType.HIGH_ERROR_RATE:
                # Calculate error rate
                total_requests = await self._count_metrics("api_request", window_start)
                error_requests = await self._count_metrics("api_request_error", window_start)
                
                if total_requests > 0:
                    value = (error_requests / total_requests) * 100
                    triggered = value > (rule.threshold * 100)  # Convert to percentage
                    details["error_rate_percent"] = value
                    details["total_requests"] = total_requests
                    details["error_count"] = error_requests
            
            elif rule.type == AlertType.DATABASE_SLOW:
                # Check database query times
                metrics = await self._get_recent_metrics("database_query_duration", window_start)
                if metrics:
                    # Calculate average
                    value = sum(metrics) / len(metrics)
                    triggered = value > rule.threshold
                    details["avg_duration_ms"] = value
                    details["slow_query_count"] = sum(1 for m in metrics if m > rule.threshold)
            
            elif rule.type == AlertType.CACHE_FAILURE:
                # Check cache failures
                failures = await self._count_metrics("cache_failure", window_start)
                value = failures
                triggered = value > rule.threshold
                details["failure_count"] = value
            
            elif rule.type == AlertType.AUTH_FAILURE_SPIKE:
                # Count authentication failures
                failures = await self._count_metrics("auth_failure", window_start)
                value = failures
                triggered = value > rule.threshold
                details["auth_failure_count"] = value
                details["window_minutes"] = rule.time_window_minutes
            
            elif rule.type == AlertType.UNAUTHORIZED_ACCESS:
                # Count unauthorized access attempts
                attempts = await self._count_metrics("auth_unauthorized", window_start)
                value = attempts
                triggered = value > rule.threshold
                details["unauthorized_attempts"] = value
            
            elif rule.type == AlertType.ALERT_OVERDUE:
                # Check overdue patient alerts
                overdue_count = await self._count_overdue_alerts()
                value = overdue_count
                triggered = value > rule.threshold
                details["overdue_alert_count"] = value
            
            elif rule.type == AlertType.HIGH_RISK_PATIENT:
                # Check recently added high risk patients
                high_risk_count = await self._count_high_risk_patients(window_start)
                value = high_risk_count
                triggered = value >= rule.threshold
                details["high_risk_patients_added"] = value
            
            elif rule.type == AlertType.PHI_ACCESS_VIOLATION:
                # Check for unauthorized PHI access
                violations = await self._count_phi_violations(window_start)
                value = violations
                triggered = value >= rule.threshold
                details["phi_violations"] = value
            
            elif rule.type == AlertType.AUDIT_LOG_FAILURE:
                # Check audit log failures
                failures = await self._count_metrics("audit_log_failure", window_start)
                value = failures
                triggered = value > rule.threshold
                details["audit_failures"] = value
            
            # Log metric check
            logfire.debug(
                "Alert rule checked",
                rule=rule.name,
                value=value,
                threshold=rule.threshold,
                triggered=triggered
            )
            
            if triggered:
                await self.trigger_alert(rule, details)
                
        except Exception as e:
            logfire.error(
                "Error checking alert rule",
                rule=rule.name,
                error=str(e)
            )
    
    async def trigger_alert(self, rule: AlertRule, details: Dict[str, Any]):
        """Trigger an alert."""
        alert = Alert(
            rule_name=rule.name,
            type=rule.type,
            severity=rule.severity,
            title=f"{rule.name}: {rule.description}",
            description=rule.description,
            details=details
        )
        
        # Store in active alerts
        self.active_alerts[rule.name] = alert
        
        # Log to Logfire with high priority
        logfire.error(
            f"ALERT: {alert.title}",
            alert_type=alert.type.value,
            severity=alert.severity.value,
            details=alert.details,
            alert_id=alert.id
        )
        
        # Store in database
        try:
            result = await self.db.create(
                "system_alerts",
                alert.dict(exclude_none=True)
            )
            if result and len(result) > 0:
                alert.id = result[0].get('id')
        except Exception as e:
            logfire.error("Failed to store alert", error=str(e))
        
        # Send notifications
        await self._send_notifications(alert)
        
        # Track metric
        metrics_service.track_custom_metric(
            "alert_triggered",
            value=1,
            alert_type=alert.type.value,
            severity=alert.severity.value
        )
    
    async def _send_notifications(self, alert: Alert):
        """Send alert notifications via Logfire."""
        # Log critical alerts with high priority
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            logfire.error(
                "CRITICAL ALERT - Immediate action required",
                alert_type=alert.type.value,
                severity=alert.severity.value,
                title=alert.title,
                description=alert.description,
                details=alert.details,
                alert_id=alert.id
            )
        else:
            logfire.warning(
                "Alert triggered",
                alert_type=alert.type.value,
                severity=alert.severity.value,
                title=alert.title,
                description=alert.description,
                details=alert.details,
                alert_id=alert.id
            )
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Acknowledge an alert."""
        try:
            # Update in database
            await self.db.query(
                f"UPDATE {alert_id} SET acknowledged_at = time::now(), acknowledged_by = $acknowledged_by",
                {"acknowledged_by": acknowledged_by}
            )
            
            # Update in memory
            for rule_name, alert in self.active_alerts.items():
                if alert.id == alert_id:
                    alert.acknowledged_at = datetime.now(timezone.utc)
                    alert.acknowledged_by = acknowledged_by
                    break
            
            logfire.info(
                "Alert acknowledged",
                alert_id=alert_id,
                acknowledged_by=acknowledged_by
            )
            
        except Exception as e:
            logfire.error("Failed to acknowledge alert", error=str(e))
    
    async def resolve_alert(self, alert_id: str, resolved_by: str):
        """Resolve an alert."""
        try:
            # Update in database
            await self.db.query(
                f"UPDATE {alert_id} SET resolved_at = time::now(), status = 'resolved'",
                {}
            )
            
            # Remove from active alerts
            resolved_alert = None
            for rule_name, alert in list(self.active_alerts.items()):
                if alert.id == alert_id:
                    resolved_alert = alert
                    del self.active_alerts[rule_name]
                    break
            
            if resolved_alert:
                # Track resolution time
                resolution_time = (datetime.now(timezone.utc) - resolved_alert.triggered_at).total_seconds() / 60
                
                metrics_service.track_custom_metric(
                    "alert_resolved",
                    value=resolution_time,
                    unit="minutes",
                    alert_type=resolved_alert.type.value,
                    severity=resolved_alert.severity.value
                )
            
            logfire.info(
                "Alert resolved",
                alert_id=alert_id,
                resolved_by=resolved_by
            )
            
        except Exception as e:
            logfire.error("Failed to resolve alert", error=str(e))
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history."""
        try:
            cutoff_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            
            result = await self.db.query(
                f"SELECT * FROM system_alerts WHERE triggered_at > '{cutoff_time}' ORDER BY triggered_at DESC"
            )
            
            return result
        except Exception as e:
            logfire.error("Failed to get alert history", error=str(e))
            return []
    
    def add_custom_rule(self, rule: AlertRule):
        """Add a custom alert rule."""
        self.alert_rules.append(rule)
        logfire.info("Custom alert rule added", rule=rule.name)
    
    def disable_rule(self, rule_name: str):
        """Disable an alert rule."""
        for rule in self.alert_rules:
            if rule.name == rule_name:
                rule.enabled = False
                logfire.info("Alert rule disabled", rule=rule_name)
                break
    
    def enable_rule(self, rule_name: str):
        """Enable an alert rule."""
        for rule in self.alert_rules:
            if rule.name == rule_name:
                rule.enabled = True
                logfire.info("Alert rule enabled", rule=rule_name)
                break
    
    async def _get_recent_metrics(self, metric_type: str, since: datetime) -> List[float]:
        """Get recent metric values from database."""
        try:
            # Query metrics table for recent values
            query = """
            SELECT value FROM metrics 
            WHERE type = $metric_type 
            AND created_at > $since 
            ORDER BY created_at DESC
            """
            
            result = await self.db.query(query, {
                "metric_type": metric_type,
                "since": since.isoformat()
            })
            
            if result:
                return [float(r['value']) for r in result if 'value' in r]
            
        except Exception as e:
            logfire.error("Failed to get metrics", metric_type=metric_type, error=str(e))
        
        return []
    
    async def _count_metrics(self, metric_type: str, since: datetime) -> int:
        """Count occurrences of a metric since a given time."""
        try:
            # Query metrics count
            query = """
            SELECT count() as total FROM metrics 
            WHERE type = $metric_type 
            AND created_at > $since 
            GROUP BY total
            """
            
            result = await self.db.query(query, {
                "metric_type": metric_type,
                "since": since.isoformat()
            })
            
            if result and len(result) > 0:
                return result[0].get('total', 0)
            
        except Exception as e:
            logfire.error("Failed to count metrics", metric_type=metric_type, error=str(e))
        
        return 0
    
    async def _count_overdue_alerts(self) -> int:
        """Count patient alerts that are overdue."""
        try:
            # Query for unresolved alerts older than 24 hours
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
            
            query = """
            SELECT count() as total FROM patient_alerts 
            WHERE status = 'active' 
            AND created_at < $cutoff 
            GROUP BY total
            """
            
            result = await self.db.query(query, {"cutoff": cutoff})
            
            if result and len(result) > 0:
                return result[0].get('total', 0)
            
        except Exception as e:
            logfire.error("Failed to count overdue alerts", error=str(e))
        
        return 0
    
    async def _count_high_risk_patients(self, since: datetime) -> int:
        """Count high risk patients added since a given time."""
        try:
            query = """
            SELECT count() as total FROM patient 
            WHERE risk_level = 'High' 
            AND created_at > $since 
            GROUP BY total
            """
            
            result = await self.db.query(query, {"since": since.isoformat()})
            
            if result and len(result) > 0:
                return result[0].get('total', 0)
            
        except Exception as e:
            logfire.error("Failed to count high risk patients", error=str(e))
        
        return 0
    
    async def _count_phi_violations(self, since: datetime) -> int:
        """Count PHI access violations."""
        try:
            # Query audit logs for unauthorized PHI access
            query = """
            SELECT count() as total FROM audit_logs 
            WHERE action = 'UNAUTHORIZED_PHI_ACCESS' 
            AND created_at > $since 
            GROUP BY total
            """
            
            result = await self.db.query(query, {"since": since.isoformat()})
            
            if result and len(result) > 0:
                return result[0].get('total', 0)
            
        except Exception as e:
            logfire.error("Failed to count PHI violations", error=str(e))
        
        return 0
    
    async def record_metric(self, metric_type: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record a metric value for alert checking."""
        try:
            await self.db.create(
                "metrics",
                {
                    "type": metric_type,
                    "value": value,
                    "metadata": metadata or {},
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            )
        except Exception as e:
            logfire.error("Failed to record metric", metric_type=metric_type, error=str(e))


# Singleton instance
alerting_service = AlertingService()