"""
Alerts API endpoints.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.database.connection import get_database
from app.api.v1.auth import get_current_user
from app.models.user import UserResponse
import json

router = APIRouter()

class Alert(BaseModel):
    id: Optional[str] = None
    type: str  # critical, warning, info, success
    title: str
    message: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    source: str
    read: bool = False
    resolved: bool = False
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None

class AlertStats(BaseModel):
    total: int
    unread: int
    critical: int
    pending_action: int

class AlertsResponse(BaseModel):
    alerts: List[Alert]
    stats: AlertStats

@router.get("", response_model=dict)
async def get_alerts(
    type: Optional[str] = Query(None, description="Filter by alert type"),
    status: Optional[str] = Query(None, description="Filter by status (read/unread/resolved/pending)"),
    search: Optional[str] = Query(None, description="Search in title and message"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get alerts for the current user with optional filters."""
    try:
        # Build query
        query_parts = ["SELECT * FROM alert WHERE user_id = $user_id"]
        params = {"user_id": current_user.id}
        
        if type and type != "all":
            query_parts.append("AND type = $type")
            params["type"] = type
            
        if status:
            if status == "unread":
                query_parts.append("AND read = false")
            elif status == "read":
                query_parts.append("AND read = true")
            elif status == "resolved":
                query_parts.append("AND resolved = true")
            elif status == "pending":
                query_parts.append("AND resolved = false")
                
        if search:
            query_parts.append("AND (title CONTAINS $search OR message CONTAINS $search)")
            params["search"] = search
            
        # Add ordering and pagination
        query_parts.append("ORDER BY created_at DESC")
        query_parts.append(f"LIMIT {limit} START {offset}")
        
        query = " ".join(query_parts)
        
        # Execute query
        result = await db.query(query, params)
        alerts = []
        
        for record in result:
            alert_data = json.loads(record.text) if hasattr(record, 'text') else record
            alert = Alert(**alert_data)
            alerts.append(alert)
        
        # Get stats
        stats_query = """
            LET total = (SELECT count() FROM alert WHERE user_id = $user_id GROUP ALL)[0].count;
            LET unread = (SELECT count() FROM alert WHERE user_id = $user_id AND read = false GROUP ALL)[0].count;
            LET critical = (SELECT count() FROM alert WHERE user_id = $user_id AND type = 'critical' GROUP ALL)[0].count;
            LET pending = (SELECT count() FROM alert WHERE user_id = $user_id AND resolved = false GROUP ALL)[0].count;
            RETURN {
                total: total ?? 0,
                unread: unread ?? 0,
                critical: critical ?? 0,
                pending_action: pending ?? 0
            };
        """
        
        stats_result = await db.query(stats_query, {"user_id": current_user.id})
        stats_data = json.loads(stats_result[0].text) if stats_result and hasattr(stats_result[0], 'text') else {
            "total": 0,
            "unread": 0,
            "critical": 0,
            "pending_action": 0
        }
        stats = AlertStats(**stats_data[0] if isinstance(stats_data, list) else stats_data)
        
        return {
            "status": "success",
            "data": {
                "alerts": [alert.dict() for alert in alerts],
                "stats": stats.dict()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=dict)
async def create_alert(
    alert: Alert,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Create a new alert."""
    try:
        # Set alert metadata
        alert.user_id = current_user.id
        alert.created_at = datetime.utcnow()
        if not alert.expires_at:
            # Default expiry is 7 days for non-critical alerts
            if alert.type == "critical":
                alert.expires_at = datetime.utcnow() + timedelta(days=30)
            else:
                alert.expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Create alert in database
        query = """
            CREATE alert CONTENT {
                type: $type,
                title: $title,
                message: $message,
                patient_id: $patient_id,
                patient_name: $patient_name,
                source: $source,
                read: $read,
                resolved: $resolved,
                created_at: $created_at,
                expires_at: $expires_at,
                user_id: $user_id
            };
        """
        
        result = await db.query(query, alert.dict())
        created_alert = json.loads(result[0].text) if hasattr(result[0], 'text') else result[0]
        
        return {
            "status": "success",
            "data": created_alert
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{alert_id}", response_model=dict)
async def update_alert(
    alert_id: str,
    read: Optional[bool] = None,
    resolved: Optional[bool] = None,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Update an alert's read or resolved status."""
    try:
        # Check if alert exists and belongs to user
        check_query = "SELECT * FROM $alert_id WHERE user_id = $user_id"
        check_result = await db.query(check_query, {
            "alert_id": f"alert:{alert_id}",
            "user_id": current_user.id
        })
        
        if not check_result:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Build update query
        updates = []
        params = {"alert_id": f"alert:{alert_id}"}
        
        if read is not None:
            updates.append("read = $read")
            params["read"] = read
            
        if resolved is not None:
            updates.append("resolved = $resolved")
            params["resolved"] = resolved
            
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        update_query = f"UPDATE $alert_id SET {', '.join(updates)}"
        await db.query(update_query, params)
        
        return {
            "status": "success",
            "message": "Alert updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{alert_id}", response_model=dict)
async def delete_alert(
    alert_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Delete an alert."""
    try:
        # Check if alert exists and belongs to user
        check_query = "SELECT * FROM $alert_id WHERE user_id = $user_id"
        check_result = await db.query(check_query, {
            "alert_id": f"alert:{alert_id}",
            "user_id": current_user.id
        })
        
        if not check_result:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Delete alert
        delete_query = "DELETE $alert_id"
        await db.query(delete_query, {"alert_id": f"alert:{alert_id}"})
        
        return {
            "status": "success",
            "message": "Alert deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mark-all-read", response_model=dict)
async def mark_all_alerts_read(
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Mark all alerts as read for the current user."""
    try:
        query = "UPDATE alert SET read = true WHERE user_id = $user_id AND read = false"
        await db.query(query, {"user_id": current_user.id})
        
        return {
            "status": "success",
            "message": "All alerts marked as read"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))