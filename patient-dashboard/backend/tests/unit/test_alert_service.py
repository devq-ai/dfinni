"""
Unit tests for AlertService
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.services.alert_service import AlertService
from app.models.alert import (
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertType,
    AlertSeverity,
    AlertStatus
)


@pytest.mark.unit
@pytest.mark.alerts
class TestAlertService:
    """Test cases for AlertService."""
    
    @pytest.fixture
    def alert_service(self, mock_db):
        """Create alert service instance with mocked database."""
        service = AlertService()
        service.db = mock_db
        return service
    
    @pytest.fixture
    def sample_alert_data(self):
        """Sample alert data for testing."""
        return {
            "patient_id": "patient:123",
            "type": AlertType.MEDICATION,
            "severity": AlertSeverity.HIGH,
            "title": "Medication Non-Adherence",
            "description": "Patient missed 3 consecutive doses",
            "triggered_by": "system",
            "requires_action": True,
            "metadata": {
                "medication": "Lisinopril",
                "missed_doses": 3,
                "last_taken": "2024-01-12"
            }
        }
    
    @pytest.mark.asyncio
    async def test_create_alert_success(self, alert_service, sample_alert_data, mock_db):
        """Test successful alert creation."""
        # Mock database response
        mock_db.create.return_value = [{
            "id": "alert:456",
            **sample_alert_data,
            "status": AlertStatus.ACTIVE,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
        }]
        
        alert_create = AlertCreate(**sample_alert_data)
        result = await alert_service.create_alert(alert_create)
        
        assert result.id == "alert:456"
        assert result.patient_id == sample_alert_data["patient_id"]
        assert result.type == AlertType.MEDICATION
        assert result.severity == AlertSeverity.HIGH
        assert result.status == AlertStatus.ACTIVE
        
        # Verify database call
        mock_db.create.assert_called_once()
        
        # Verify notification was triggered
        with patch.object(alert_service, 'notification_service') as mock_notif:
            await alert_service.create_alert(alert_create)
            mock_notif.send_alert_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_critical_alert_escalation(self, alert_service, sample_alert_data, mock_db):
        """Test critical alert escalation."""
        # Make it a critical alert
        sample_alert_data["severity"] = AlertSeverity.CRITICAL
        
        mock_db.create.return_value = [{
            "id": "alert:789",
            **sample_alert_data,
            "status": AlertStatus.ACTIVE,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
        }]
        
        with patch.object(alert_service, 'escalation_service') as mock_escalation:
            alert_create = AlertCreate(**sample_alert_data)
            result = await alert_service.create_alert(alert_create)
            
            assert result.severity == AlertSeverity.CRITICAL
            # Verify escalation was triggered for critical alert
            mock_escalation.escalate_critical_alert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_alert_by_id_found(self, alert_service, sample_alert_data, mock_db):
        """Test getting alert by ID when found."""
        alert_id = "alert:456"
        
        mock_db.select.return_value = [{
            "id": alert_id,
            **sample_alert_data,
            "status": AlertStatus.ACTIVE,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
        }]
        
        result = await alert_service.get_alert(alert_id)
        
        assert result is not None
        assert result.id == alert_id
        assert result.patient_id == sample_alert_data["patient_id"]
        
        mock_db.select.assert_called_once_with(alert_id)
    
    @pytest.mark.asyncio
    async def test_get_alert_by_id_not_found(self, alert_service, mock_db):
        """Test getting alert by ID when not found."""
        mock_db.select.return_value = []
        
        result = await alert_service.get_alert("alert:999")
        
        assert result is None
        mock_db.select.assert_called_once_with("alert:999")
    
    @pytest.mark.asyncio
    async def test_get_alerts_for_patient(self, alert_service, mock_db):
        """Test getting alerts for a specific patient."""
        patient_id = "patient:123"
        
        mock_db.query.return_value = [
            {
                "id": "alert:1",
                "patient_id": patient_id,
                "type": AlertType.MEDICATION,
                "severity": AlertSeverity.HIGH,
                "status": AlertStatus.ACTIVE
            },
            {
                "id": "alert:2",
                "patient_id": patient_id,
                "type": AlertType.APPOINTMENT,
                "severity": AlertSeverity.MEDIUM,
                "status": AlertStatus.ACTIVE
            }
        ]
        
        result = await alert_service.get_alerts_for_patient(
            patient_id,
            status=AlertStatus.ACTIVE
        )
        
        assert len(result) == 2
        assert all(alert.patient_id == patient_id for alert in result)
        assert result[0].id == "alert:1"
        assert result[1].id == "alert:2"
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, alert_service, sample_alert_data, mock_db):
        """Test acknowledging an alert."""
        alert_id = "alert:456"
        user_id = "user:provider123"
        
        # Mock getting the alert
        mock_db.select.return_value = [{
            "id": alert_id,
            **sample_alert_data,
            "status": AlertStatus.ACTIVE,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
        }]
        
        # Mock update
        mock_db.update.return_value = [{
            "id": alert_id,
            **sample_alert_data,
            "status": AlertStatus.ACKNOWLEDGED,
            "acknowledged_by": user_id,
            "acknowledged_at": "2024-01-15T11:00:00Z",
            "updated_at": "2024-01-15T11:00:00Z"
        }]
        
        result = await alert_service.acknowledge_alert(alert_id, user_id)
        
        assert result is not None
        assert result.status == AlertStatus.ACKNOWLEDGED
        assert result.acknowledged_by == user_id
        assert result.acknowledged_at is not None
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, alert_service, sample_alert_data, mock_db):
        """Test resolving an alert."""
        alert_id = "alert:456"
        user_id = "user:provider123"
        resolution_notes = "Patient contacted, medication schedule adjusted"
        
        # Mock getting the alert
        mock_db.select.return_value = [{
            "id": alert_id,
            **sample_alert_data,
            "status": AlertStatus.ACKNOWLEDGED,
            "acknowledged_by": user_id,
            "acknowledged_at": "2024-01-15T11:00:00Z"
        }]
        
        # Mock update
        mock_db.update.return_value = [{
            "id": alert_id,
            **sample_alert_data,
            "status": AlertStatus.RESOLVED,
            "resolved_by": user_id,
            "resolved_at": "2024-01-15T12:00:00Z",
            "resolution_notes": resolution_notes
        }]
        
        result = await alert_service.resolve_alert(
            alert_id,
            user_id,
            resolution_notes
        )
        
        assert result is not None
        assert result.status == AlertStatus.RESOLVED
        assert result.resolved_by == user_id
        assert result.resolution_notes == resolution_notes
    
    @pytest.mark.asyncio
    async def test_snooze_alert(self, alert_service, sample_alert_data, mock_db):
        """Test snoozing an alert."""
        alert_id = "alert:456"
        user_id = "user:provider123"
        snooze_until = datetime.utcnow() + timedelta(hours=24)
        
        # Mock getting the alert
        mock_db.select.return_value = [{
            "id": alert_id,
            **sample_alert_data,
            "status": AlertStatus.ACTIVE
        }]
        
        # Mock update
        mock_db.update.return_value = [{
            "id": alert_id,
            **sample_alert_data,
            "status": AlertStatus.SNOOZED,
            "snoozed_by": user_id,
            "snoozed_until": snooze_until.isoformat()
        }]
        
        result = await alert_service.snooze_alert(
            alert_id,
            user_id,
            snooze_until
        )
        
        assert result is not None
        assert result.status == AlertStatus.SNOOZED
        assert result.snoozed_by == user_id
        assert result.snoozed_until is not None
    
    @pytest.mark.asyncio
    async def test_get_active_alerts_count(self, alert_service, mock_db):
        """Test getting count of active alerts."""
        mock_db.query.return_value = [{"count": 25}]
        
        result = await alert_service.get_active_alerts_count()
        
        assert result == 25
        mock_db.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_alerts_by_severity(self, alert_service, mock_db):
        """Test getting alerts grouped by severity."""
        mock_db.query.return_value = [
            {"severity": "critical", "count": 3},
            {"severity": "high", "count": 10},
            {"severity": "medium", "count": 15},
            {"severity": "low", "count": 5}
        ]
        
        result = await alert_service.get_alerts_by_severity()
        
        assert isinstance(result, dict)
        assert result["critical"] == 3
        assert result["high"] == 10
        assert result["medium"] == 15
        assert result["low"] == 5
    
    @pytest.mark.asyncio
    async def test_auto_resolve_old_alerts(self, alert_service, mock_db):
        """Test auto-resolving old alerts."""
        # Mock finding old alerts
        mock_db.query.return_value = [
            {"id": "alert:1"},
            {"id": "alert:2"},
            {"id": "alert:3"}
        ]
        
        # Mock bulk update
        mock_db.query.return_value = [{"updated": 3}]
        
        result = await alert_service.auto_resolve_old_alerts(days_old=30)
        
        assert result["resolved_count"] == 3
        # Verify query was called to find and update old alerts
        assert mock_db.query.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_create_alert_rule(self, alert_service, mock_db):
        """Test creating an alert rule."""
        rule_data = {
            "name": "High Blood Pressure Alert",
            "condition": "blood_pressure.systolic > 140",
            "type": AlertType.VITALS,
            "severity": AlertSeverity.HIGH,
            "enabled": True
        }
        
        mock_db.create.return_value = [{
            "id": "alert_rule:123",
            **rule_data,
            "created_at": "2024-01-15T10:00:00Z"
        }]
        
        result = await alert_service.create_alert_rule(rule_data)
        
        assert result["id"] == "alert_rule:123"
        assert result["name"] == rule_data["name"]
        assert result["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_evaluate_alert_rules(self, alert_service, mock_db):
        """Test evaluating alert rules for a patient."""
        patient_id = "patient:123"
        
        # Mock getting patient data and rules
        with patch.object(alert_service, 'rule_engine') as mock_engine:
            mock_engine.evaluate_patient.return_value = [
                {
                    "rule_id": "rule:1",
                    "triggered": True,
                    "alert_data": {
                        "type": AlertType.MEDICATION,
                        "severity": AlertSeverity.HIGH,
                        "title": "Medication adherence below threshold"
                    }
                }
            ]
            
            # Mock alert creation
            mock_db.create.return_value = [{
                "id": "alert:new",
                "patient_id": patient_id,
                "type": AlertType.MEDICATION
            }]
            
            result = await alert_service.evaluate_alert_rules(patient_id)
            
            assert len(result["triggered_alerts"]) == 1
            assert result["rules_evaluated"] > 0
    
    @pytest.mark.asyncio
    async def test_get_alert_history(self, alert_service, mock_db):
        """Test getting alert history for a patient."""
        patient_id = "patient:123"
        
        mock_db.query.return_value = [
            {
                "id": "alert:1",
                "created_at": "2024-01-01T10:00:00Z",
                "type": AlertType.MEDICATION,
                "status": AlertStatus.RESOLVED
            },
            {
                "id": "alert:2",
                "created_at": "2024-01-10T10:00:00Z",
                "type": AlertType.APPOINTMENT,
                "status": AlertStatus.RESOLVED
            }
        ]
        
        result = await alert_service.get_alert_history(
            patient_id,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        assert len(result) == 2
        assert result[0]["id"] == "alert:1"
        assert result[1]["id"] == "alert:2"