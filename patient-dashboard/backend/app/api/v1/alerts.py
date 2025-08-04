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
        # Debug log for successful authentication
        logfire.info(
            "Alerts API accessed successfully",
            user_id=current_user.id,
            user_email=current_user.email,
            clerk_user_id=getattr(current_user, 'clerk_user_id', 'N/A')
        )
        
        # Build query based on filters
        query_parts = ["SELECT * FROM alert"]
        where_clauses = []
        params = {}
        
        # Apply status filter
        if status:
            if status == 'new':
                where_clauses.append("status = 'active'")
            elif status == 'read':
                where_clauses.append("read = true")
            elif status == 'unread':
                where_clauses.append("(read = false OR read = null)")
            elif status == 'resolved':
                where_clauses.append("status = 'resolved'")
            elif status == 'pending':
                where_clauses.append("requires_action = true")
        
        # Apply type filter
        if type:
            where_clauses.append("type = $type")
            params['type'] = type
        
        # Apply search filter
        if search:
            where_clauses.append("(title CONTAINS $search OR description CONTAINS $search)")
            params['search'] = search
        
        # Combine where clauses
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        # Add ordering and pagination
        query_parts.append("ORDER BY created_at DESC")
        query_parts.append(f"LIMIT {limit} START {offset}")
        
        # Execute query
        query = " ".join(query_parts)
        alerts_result = await db.execute(query, params)
        
        # Convert results to Alert objects
        alerts = []
        if alerts_result:
            for alert_data in alerts_result:
                # Map database fields to API model
                alert = Alert(
                    id=str(alert_data.get('id', '')).split(':')[-1] if alert_data.get('id') else None,
                    type=alert_data.get('type', 'unknown'),
                    title=alert_data.get('title', ''),
                    message=alert_data.get('description', ''),
                    patient_id=alert_data.get('patient_id'),
                    patient_name=alert_data.get('patient_name'),
                    source=alert_data.get('triggered_by', 'system'),
                    read=alert_data.get('read', False),
                    resolved=alert_data.get('status') == 'resolved',
                    created_at=alert_data.get('created_at'),
                    expires_at=alert_data.get('expires_at'),
                    user_id=alert_data.get('user_id')
                )
                alerts.append(alert)
        
        # Get stats from database
        stats_queries = {
            'total': "SELECT count() as count FROM alert GROUP ALL",
            'unread': "SELECT count() as count FROM alert WHERE (read = false OR read = null) GROUP ALL",
            'critical': "SELECT count() as count FROM alert WHERE severity = 'critical' GROUP ALL",
            'pending_action': "SELECT count() as count FROM alert WHERE requires_action = true GROUP ALL"
        }
        
        stats_results = {}
        for stat_name, stat_query in stats_queries.items():
            result = await db.execute(stat_query)
            if result and len(result) > 0:
                stats_results[stat_name] = result[0].get('count', 0)
            else:
                stats_results[stat_name] = 0
        
        stats = AlertStats(
            total=stats_results['total'],
            unread=stats_results['unread'],
            critical=stats_results['critical'],
            pending_action=stats_results['pending_action']
        )
        
        return {
            "status": "success",
            "data": {
                "alerts": [alert.dict() for alert in alerts],
                "stats": stats.dict()
            }
        }
        
    except Exception as e:
        logfire.error(f"Error in get_alerts: {str(e)}")
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