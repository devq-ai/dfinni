"""
Analytics API endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.database.connection import get_database
from app.api.v1.auth import get_current_user
from app.models.user import UserResponse
from datetime import datetime, timedelta
import json

router = APIRouter()

@router.get("", response_model=dict)
async def get_analytics(
    range: str = Query("30d", description="Time range: 7d, 30d, 90d, 1y"),
    current_user: UserResponse = Depends(get_current_user),
    db=Depends(get_database)
):
    """Get analytics data for the specified time range."""
    try:
        # For MVP, return mock data
        # In production, this would aggregate real data from the database
        
        analytics_data = {
            "patient_growth": {
                "current_month": 156,
                "previous_month": 142,
                "growth_rate": 9.86
            },
            "engagement_metrics": {
                "avg_session_duration": 12.5,
                "total_sessions": 3842,
                "active_users_rate": 78.5
            },
            "health_outcomes": {
                "improved": 89,
                "stable": 45,
                "declined": 22
            },
            "risk_distribution": {
                "low": 98,
                "medium": 47,
                "high": 11
            },
            "monthly_trends": [
                {"month": "Jan", "new_patients": 45, "active_patients": 412, "churned_patients": 8},
                {"month": "Feb", "new_patients": 52, "active_patients": 438, "churned_patients": 12},
                {"month": "Mar", "new_patients": 48, "active_patients": 465, "churned_patients": 10},
                {"month": "Apr", "new_patients": 61, "active_patients": 489, "churned_patients": 15},
                {"month": "May", "new_patients": 58, "active_patients": 512, "churned_patients": 9},
                {"month": "Jun", "new_patients": 67, "active_patients": 548, "churned_patients": 11}
            ]
        }
        
        # Adjust data based on time range
        if range == "7d":
            # Show only last week's data
            analytics_data["monthly_trends"] = analytics_data["monthly_trends"][-1:]
            analytics_data["patient_growth"]["growth_rate"] = 2.3
        elif range == "90d":
            # Show last 3 months
            analytics_data["monthly_trends"] = analytics_data["monthly_trends"][-3:]
        elif range == "1y":
            # Show all data
            pass
        
        return {
            "status": "success",
            "data": analytics_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))