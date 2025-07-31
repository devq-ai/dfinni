"""
Users API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.database.connection import get_database
from app.api.v1.auth import get_current_user
from app.services.auth_service import AuthService
import bcrypt
from app.models.user import UserResponse
import json

router = APIRouter()
auth_service = AuthService()

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class NotificationSettings(BaseModel):
    email_alerts: bool
    sms_alerts: bool
    push_notifications: bool
    alert_frequency: str
    critical_only: bool

@router.get("/me", response_model=dict)
async def get_current_user_profile(
    current_user: UserResponse = Depends(get_current_user)
):
    """Get current user's profile."""
    return {
        "status": "success",
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "phone": getattr(current_user, 'phone', None),
            "role": current_user.role,
            "created_at": current_user.created_at.isoformat() if hasattr(current_user.created_at, 'isoformat') else str(current_user.created_at)
        }
    }

@router.patch("/me", response_model=dict)
async def update_current_user(
    update_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Update current user's profile."""
    try:
        # Build update query
        updates = []
        params = {"user_id": current_user.id}
        
        if update_data.first_name is not None:
            updates.append("first_name = $first_name")
            params["first_name"] = update_data.first_name
            
        if update_data.last_name is not None:
            updates.append("last_name = $last_name")
            params["last_name"] = update_data.last_name
            
        if update_data.phone is not None:
            updates.append("phone = $phone")
            params["phone"] = update_data.phone
        
        if updates:
            updates.append("updated_at = time::now()")
            query = f"UPDATE $user_id SET {', '.join(updates)}"
            await db.query(query, params)
        
        return {
            "status": "success",
            "message": "Profile updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/me/password", response_model=dict)
async def update_password(
    password_data: PasswordUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Update current user's password."""
    try:
        # Verify current password
        is_valid = await auth_service.verify_password(password_data.current_password, current_user.id)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        new_hash = bcrypt.hashpw(
            password_data.new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        query = """
            UPDATE $user_id SET 
                password_hash = $password_hash,
                password_reset_required = false,
                updated_at = time::now()
        """
        
        await db.query(query, {
            "user_id": current_user.id,
            "password_hash": new_hash
        })
        
        return {
            "status": "success",
            "message": "Password updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/me/notifications", response_model=dict)
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Update notification settings."""
    try:
        # For MVP, we'll store these as user attributes
        query = """
            UPDATE $user_id SET 
                notification_settings = $settings,
                updated_at = time::now()
        """
        
        await db.query(query, {
            "user_id": current_user.id,
            "settings": settings.dict()
        })
        
        return {
            "status": "success",
            "message": "Notification settings updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))