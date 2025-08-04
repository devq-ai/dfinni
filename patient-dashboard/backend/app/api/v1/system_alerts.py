"""
System alerts API endpoints for monitoring and alerting.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.v1.auth import get_current_user
from app.models.user import UserResponse, UserRole
from app.services.alerting_service import alerting_service, Alert, AlertRule, AlertSeverity, AlertType

router = APIRouter()


class AlertAcknowledgeRequest(BaseModel):
    """Request to acknowledge an alert."""
    alert_id: str


class AlertResolveRequest(BaseModel):
    """Request to resolve an alert."""
    alert_id: str


class CustomAlertRule(BaseModel):
    """Request to create a custom alert rule."""
    name: str
    type: AlertType
    severity: AlertSeverity
    condition: dict
    threshold: float
    time_window_minutes: int = 5
    description: str


@router.get("/active", response_model=List[Alert])
async def get_active_alerts(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all active system alerts."""
    # Only admins and providers can view system alerts
    if current_user.role not in [UserRole.ADMIN, UserRole.PROVIDER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view system alerts"
        )
    
    return await alerting_service.get_active_alerts()


@router.get("/history")
async def get_alert_history(
    hours: int = 24,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get alert history for the specified time period."""
    # Only admins and providers can view alert history
    if current_user.role not in [UserRole.ADMIN, UserRole.PROVIDER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view alert history"
        )
    
    return await alerting_service.get_alert_history(hours)


@router.post("/acknowledge")
async def acknowledge_alert(
    request: AlertAcknowledgeRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Acknowledge an active alert."""
    # Only admins and providers can acknowledge alerts
    if current_user.role not in [UserRole.ADMIN, UserRole.PROVIDER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to acknowledge alerts"
        )
    
    await alerting_service.acknowledge_alert(
        alert_id=request.alert_id,
        acknowledged_by=current_user.id
    )
    
    return {"message": "Alert acknowledged successfully"}


@router.post("/resolve")
async def resolve_alert(
    request: AlertResolveRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """Resolve an active alert."""
    # Only admins and providers can resolve alerts
    if current_user.role not in [UserRole.ADMIN, UserRole.PROVIDER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to resolve alerts"
        )
    
    await alerting_service.resolve_alert(
        alert_id=request.alert_id,
        resolved_by=current_user.id
    )
    
    return {"message": "Alert resolved successfully"}


@router.post("/rules", status_code=status.HTTP_201_CREATED)
async def create_custom_alert_rule(
    rule: CustomAlertRule,
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a custom alert rule (admin only)."""
    # Only admins can create custom alert rules
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create alert rules"
        )
    
    alert_rule = AlertRule(
        name=rule.name,
        type=rule.type,
        severity=rule.severity,
        condition=rule.condition,
        threshold=rule.threshold,
        time_window_minutes=rule.time_window_minutes,
        description=rule.description
    )
    
    alerting_service.add_custom_rule(alert_rule)
    
    return {"message": "Alert rule created successfully", "rule_name": rule.name}


@router.put("/rules/{rule_name}/disable")
async def disable_alert_rule(
    rule_name: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Disable an alert rule (admin only)."""
    # Only admins can disable alert rules
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can disable alert rules"
        )
    
    alerting_service.disable_rule(rule_name)
    
    return {"message": f"Alert rule '{rule_name}' disabled successfully"}


@router.put("/rules/{rule_name}/enable")
async def enable_alert_rule(
    rule_name: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """Enable an alert rule (admin only)."""
    # Only admins can enable alert rules
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can enable alert rules"
        )
    
    alerting_service.enable_rule(rule_name)
    
    return {"message": f"Alert rule '{rule_name}' enabled successfully"}


@router.get("/rules")
async def get_alert_rules(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all configured alert rules."""
    # Only admins can view alert rules
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view alert rules"
        )
    
    return [
        {
            "name": rule.name,
            "type": rule.type.value,
            "severity": rule.severity.value,
            "threshold": rule.threshold,
            "time_window_minutes": rule.time_window_minutes,
            "description": rule.description,
            "enabled": rule.enabled
        }
        for rule in alerting_service.alert_rules
    ]