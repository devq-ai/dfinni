"""
Dashboard API endpoints for patient management system.
Provides real-time metrics and analytics for healthcare providers.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
import logging
import logfire

from app.services.analytics_service import AnalyticsService
from app.api.v1.auth import get_current_user
from app.models.user import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["dashboard"])
analytics_service = AnalyticsService()

@router.get("/metrics")
async def get_dashboard_metrics(
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get key dashboard metrics including patient counts by status.
    """
    try:
        try:
            logfire.info("Dashboard metrics requested", user_id=current_user.id)
        except:
            pass
        
        metrics = await analytics_service.get_dashboard_metrics()
        
        try:
            logfire.info("Dashboard metrics retrieved", metrics_count=len(metrics))
        except:
            pass
        return {
            "status": "success",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        try:
            logfire.error("Dashboard metrics error", error=str(e))
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard metrics")


@router.get("/stats")
async def get_dashboard_stats(
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get dashboard statistics with trends.
    """
    try:
        # Get current period stats
        current_stats = await analytics_service.get_dashboard_metrics()
        
        # Calculate previous period stats (mock for now)
        previous_stats = {
            "totalPatients": int(current_stats.get("totalPatients", 0) * 0.9),
            "activePatients": int(current_stats.get("activePatients", 0) * 0.85),
            "highRiskPatients": int(current_stats.get("urgentPatients", 0) * 1.1),
            "appointmentsToday": 0  # Not implemented yet
        }
        
        # Calculate trends
        def calculate_trend(current: int, previous: int) -> Dict[str, Any]:
            if previous == 0:
                value = "+100%" if current > 0 else "0%"
                is_up = current > 0
            else:
                change = ((current - previous) / previous) * 100
                value = f"{change:+.1f}%"
                is_up = change >= 0
            return {"value": value, "isUp": is_up}
        
        current = {
            "totalPatients": current_stats.get("totalPatients", 0),
            "activePatients": current_stats.get("activePatients", 0),
            "highRiskPatients": current_stats.get("urgentPatients", 0),
            "appointmentsToday": 0
        }
        
        trends = {
            "totalPatients": calculate_trend(current["totalPatients"], previous_stats["totalPatients"]),
            "activePatients": calculate_trend(current["activePatients"], previous_stats["activePatients"]),
            "highRiskPatients": calculate_trend(current["highRiskPatients"], previous_stats["highRiskPatients"]),
            "appointmentsToday": {"value": "0%", "isUp": True}
        }
        
        return {
            "current": current,
            "previous": previous_stats,
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard stats")

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get recent patient activity and system events.
    """
    try:
        try:
            logfire.info("Recent activity requested", user_id=current_user.id, limit=limit)
        except:
            pass
        
        activity = await analytics_service.get_recent_activity(limit=limit)
        
        try:
            logfire.info("Recent activity retrieved", activity_count=len(activity))
        except:
            pass
        return {
            "status": "success",
            "data": activity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        try:
            logfire.error("Recent activity error", error=str(e))
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to retrieve recent activity")

@router.get("/alerts-summary")
async def get_alerts_summary(
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get summary of active alerts and notifications.
    """
    try:
        try:
            logfire.info("Alerts summary requested", user_id=current_user.id)
        except:
            pass
        
        alerts = await analytics_service.get_alerts_summary()
        
        try:
            logfire.info("Alerts summary retrieved", alerts_count=len(alerts))
        except:
            pass
        return {
            "status": "success",
            "data": alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts summary: {str(e)}")
        try:
            logfire.error("Alerts summary error", error=str(e))
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts summary")

@router.get("/patient-distribution")
async def get_patient_distribution(
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get patient distribution by status and risk level for charts.
    """
    try:
        try:
            logfire.info("Patient distribution requested", user_id=current_user.id)
        except:
            pass
        
        distribution = await analytics_service.get_patient_distribution()
        
        try:
            logfire.info("Patient distribution retrieved")
        except:
            pass
        return {
            "status": "success",
            "data": distribution,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting patient distribution: {str(e)}")
        try:
            logfire.error("Patient distribution error", error=str(e))
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to retrieve patient distribution")

@router.get("/performance-metrics")
async def get_performance_metrics(
    days: int = 7,
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get system performance metrics over the specified time period.
    """
    try:
        try:
            logfire.info("Performance metrics requested", user_id=current_user.id, days=days)
        except:
            pass
        
        metrics = await analytics_service.get_performance_metrics(days=days)
        
        try:
            logfire.info("Performance metrics retrieved")
        except:
            pass
        return {
            "status": "success",
            "data": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        try:
            logfire.error("Performance metrics error", error=str(e))
        except:
            pass
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")