"""
Alert service for managing patient alerts and notifications
"""
import logfire
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.alert import (
    AlertCreate, AlertUpdate, AlertResponse, AlertInDB,
    AlertType, AlertSeverity, AlertStatus
)
from app.database.connection import get_database
from app.core.exceptions import ResourceNotFoundException

# Configure Logfire
try:
    logfire.configure()
except Exception:
    pass


class AlertService:
    """Service for managing alerts."""
    
    def __init__(self):
        self.notification_service = None  # Will be initialized if needed
        self.escalation_service = None  # Will be initialized if needed
        
    async def create_alert(self, alert_data: AlertCreate) -> AlertResponse:
        """Create a new alert."""
        with logfire.span("create_alert", alert_type=alert_data.type, severity=alert_data.severity):
            db = await get_database()
            
            # Create alert record
            alert_dict = alert_data.model_dump()
            alert_dict['created_at'] = datetime.utcnow()
            alert_dict['updated_at'] = datetime.utcnow()
            alert_dict['status'] = AlertStatus.ACTIVE
            
            result = await db.execute(
                "CREATE alert CONTENT $alert",
                {"alert": alert_dict}
            )
            
            if not result:
                raise Exception("Failed to create alert")
            
            alert = AlertResponse(**result[0])
            
            # Send notification for high/critical alerts
            if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                if self.notification_service:
                    await self.notification_service.send_alert_notification(alert)
                    
            # Escalate critical alerts
            if alert.severity == AlertSeverity.CRITICAL:
                if self.escalation_service:
                    await self.escalation_service.escalate_critical_alert(alert)
            
            logfire.info("Alert created", alert_id=alert.id)
            return alert
    
    async def get_alert(self, alert_id: str) -> Optional[AlertResponse]:
        """Get alert by ID."""
        db = await get_database()
        
        result = await db.execute(
            "SELECT * FROM alert WHERE id = $id",
            {"id": alert_id}
        )
        
        if not result or not result[0]:
            return None
            
        return AlertResponse(**result[0])
    
    async def get_alerts_for_patient(
        self, 
        patient_id: str,
        status: Optional[AlertStatus] = None,
        severity: Optional[AlertSeverity] = None,
        limit: int = 50
    ) -> List[AlertResponse]:
        """Get alerts for a specific patient."""
        db = await get_database()
        
        query = "SELECT * FROM alert WHERE patient_id = $patient_id"
        params = {"patient_id": patient_id}
        
        if status:
            query += " AND status = $status"
            params["status"] = status.value
            
        if severity:
            query += " AND severity = $severity"
            params["severity"] = severity.value
            
        query += " ORDER BY created_at DESC LIMIT $limit"
        params["limit"] = limit
        
        result = await db.execute(query, params)
        
        return [AlertResponse(**alert) for alert in result] if result else []
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> Optional[AlertResponse]:
        """Acknowledge an alert."""
        with logfire.span("acknowledge_alert", alert_id=alert_id):
            alert = await self.get_alert(alert_id)
            if not alert:
                return None
            
            db = await get_database()
            
            update_data = {
                "status": AlertStatus.ACKNOWLEDGED,
                "acknowledged_by": user_id,
                "acknowledged_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.execute(
                "UPDATE alert SET status = $status, acknowledged_by = $acknowledged_by, "
                "acknowledged_at = $acknowledged_at, updated_at = $updated_at WHERE id = $id",
                {"id": alert_id, **update_data}
            )
            
            if not result:
                return None
                
            logfire.info("Alert acknowledged", alert_id=alert_id, user_id=user_id)
            return AlertResponse(**result[0])
    
    async def resolve_alert(
        self, 
        alert_id: str, 
        user_id: str, 
        resolution_notes: Optional[str] = None
    ) -> Optional[AlertResponse]:
        """Resolve an alert."""
        with logfire.span("resolve_alert", alert_id=alert_id):
            alert = await self.get_alert(alert_id)
            if not alert:
                return None
                
            db = await get_database()
            
            update_data = {
                "status": AlertStatus.RESOLVED,
                "resolved_by": user_id,
                "resolved_at": datetime.utcnow(),
                "resolution_notes": resolution_notes,
                "updated_at": datetime.utcnow()
            }
            
            result = await db.execute(
                "UPDATE alert SET status = $status, resolved_by = $resolved_by, "
                "resolved_at = $resolved_at, resolution_notes = $resolution_notes, "
                "updated_at = $updated_at WHERE id = $id",
                {"id": alert_id, **update_data}
            )
            
            if not result:
                return None
                
            logfire.info("Alert resolved", alert_id=alert_id, user_id=user_id)
            return AlertResponse(**result[0])
    
    async def snooze_alert(
        self,
        alert_id: str,
        user_id: str,
        snooze_until: datetime
    ) -> Optional[AlertResponse]:
        """Snooze an alert until a specific time."""
        with logfire.span("snooze_alert", alert_id=alert_id):
            alert = await self.get_alert(alert_id)
            if not alert:
                return None
                
            db = await get_database()
            
            update_data = {
                "status": AlertStatus.SNOOZED,
                "snoozed_by": user_id,
                "snoozed_until": snooze_until,
                "updated_at": datetime.utcnow()
            }
            
            result = await db.execute(
                "UPDATE alert SET status = $status, snoozed_by = $snoozed_by, "
                "snoozed_until = $snoozed_until, updated_at = $updated_at WHERE id = $id",
                {"id": alert_id, **update_data}
            )
            
            if not result:
                return None
                
            logfire.info("Alert snoozed", alert_id=alert_id, until=snooze_until.isoformat())
            return AlertResponse(**result[0])
    
    async def get_active_alerts_count(self, user_id: Optional[str] = None) -> int:
        """Get count of active alerts."""
        db = await get_database()
        
        query = "SELECT count() FROM alert WHERE status = 'active'"
        params = {}
        
        if user_id:
            # Count alerts for patients assigned to this user
            query = """
                SELECT count() FROM alert 
                WHERE status = 'active' 
                AND patient_id IN (
                    SELECT id FROM patient WHERE assigned_provider = $user_id
                )
            """
            params["user_id"] = user_id
            
        result = await db.execute(query, params)
        return result[0]['count'] if result else 0
    
    async def get_alerts_by_severity(self) -> Dict[str, int]:
        """Get alert counts grouped by severity."""
        db = await get_database()
        
        result = await db.execute("""
            SELECT severity, count() as count 
            FROM alert 
            WHERE status = 'active' 
            GROUP BY severity
        """)
        
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        if result:
            for row in result:
                severity_counts[row['severity']] = row['count']
                
        return severity_counts
    
    async def auto_resolve_old_alerts(self, days_old: int = 30) -> Dict[str, Any]:
        """Auto-resolve alerts older than specified days."""
        with logfire.span("auto_resolve_old_alerts", days_old=days_old):
            db = await get_database()
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            result = await db.execute("""
                UPDATE alert 
                SET status = 'resolved', 
                    resolved_at = $now,
                    resolution_notes = 'Auto-resolved due to age',
                    updated_at = $now
                WHERE status IN ('active', 'acknowledged') 
                AND created_at < $cutoff_date
                RETURN count()
            """, {
                "now": datetime.utcnow(),
                "cutoff_date": cutoff_date
            })
            
            resolved_count = result[0]['count'] if result else 0
            
            logfire.info("Auto-resolved old alerts", count=resolved_count)
            return {"resolved_count": resolved_count}
    
    async def get_alerts_overview(self) -> Dict[str, Any]:
        """Get alerts overview for dashboard."""
        db = await get_database()
        
        # Get total active alerts
        total_active = await self.get_active_alerts_count()
        
        # Get by severity
        by_severity = await self.get_alerts_by_severity()
        
        # Get by type
        type_result = await db.execute("""
            SELECT type, count() as count 
            FROM alert 
            WHERE status = 'active' 
            GROUP BY type
        """)
        
        by_type = {}
        if type_result:
            for row in type_result:
                by_type[row['type']] = row['count']
        
        # Get recent alerts
        recent_result = await db.execute("""
            SELECT * FROM alert 
            WHERE status = 'active' 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        recent_alerts = [AlertResponse(**alert) for alert in recent_result] if recent_result else []
        
        return {
            "total_active": total_active,
            "by_severity": by_severity,
            "by_type": by_type,
            "recent_alerts": recent_alerts
        }
    
    async def create_alert_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alert rule."""
        db = await get_database()
        
        rule_data['created_at'] = datetime.utcnow()
        rule_data['updated_at'] = datetime.utcnow()
        
        result = await db.execute(
            "CREATE alert_rule CONTENT $rule",
            {"rule": rule_data}
        )
        
        if not result:
            raise Exception("Failed to create alert rule")
            
        return result[0]
    
    async def evaluate_alert_rules(self, patient_id: str) -> Dict[str, Any]:
        """Evaluate alert rules for a patient."""
        # This would integrate with a rule engine
        # For now, return a mock response
        return {
            "triggered_alerts": [],
            "rules_evaluated": 0
        }
    
    async def get_alert_history(
        self,
        patient_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get alert history for a patient."""
        db = await get_database()
        
        result = await db.execute("""
            SELECT * FROM alert 
            WHERE patient_id = $patient_id 
            AND created_at >= $start_date 
            AND created_at <= $end_date 
            ORDER BY created_at DESC
        """, {
            "patient_id": patient_id,
            "start_date": start_date,
            "end_date": end_date
        })
        
        return result if result else []


# Global service instance
alert_service = AlertService()