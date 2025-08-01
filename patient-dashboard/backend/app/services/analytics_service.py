"""
Analytics service for dashboard metrics and system performance tracking.
Handles data aggregation, caching, and business intelligence queries.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import logfire
from collections import defaultdict

from app.database.connection import get_database
from app.config.logging import audit_logger

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for analytics and dashboard metrics."""
    
    def __init__(self):
        self.cache_ttl = 300  # 5 minutes cache
        self._cache = {}
        self._cache_timestamps = {}
    
    async def _get_db(self):
        """Get database connection."""
        return await get_database()
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache_timestamps:
            return False
        return (datetime.utcnow() - self._cache_timestamps[key]).seconds < self.cache_ttl
    
    def _cache_result(self, key: str, data: Any) -> Any:
        """Cache result with timestamp."""
        self._cache[key] = data
        self._cache_timestamps[key] = datetime.utcnow()
        return data
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get key dashboard metrics including patient counts by status."""
        cache_key = "dashboard_metrics"
        
        if self._is_cache_valid(cache_key):
            try:
                logfire.info("Returning cached dashboard metrics")
            except:
                pass
            return self._cache[cache_key]
        
        try:
            db = await self._get_db()
            
            # Get patient count by status
            status_query = """
                SELECT status, count() as count 
                FROM patient 
                WHERE status != 'Deleted'
                GROUP BY status
            """
            
            status_result = await db.execute(status_query)
            status_counts = {}
            
            if status_result and status_result[0].get('result'):
                for row in status_result[0]['result']:
                    status_counts[row['status']] = row['count']
            
            # Get patient count by risk level
            risk_query = """
                SELECT risk_level, count() as count 
                FROM patient 
                WHERE status != 'Deleted'
                GROUP BY risk_level
            """
            
            risk_result = await db.execute(risk_query)
            risk_counts = {}
            
            if risk_result and risk_result[0].get('result'):
                for row in risk_result[0]['result']:
                    risk_counts[row['risk_level']] = row['count']
            
            # Get total patient count
            total_query = "SELECT count() as total FROM patient WHERE status != 'Deleted'"
            total_result = await db.execute(total_query)
            total_patients = total_result[0]['result'][0]['total'] if total_result and total_result[0].get('result') else 0
            
            # Get recent registrations (last 30 days)
            recent_query = """
                SELECT count() as recent 
                FROM patient 
                WHERE created_at > (time::now() - 30d) AND status != 'Deleted'
            """
            recent_result = await db.execute(recent_query)
            recent_patients = recent_result[0]['result'][0]['recent'] if recent_result and recent_result[0].get('result') else 0
            
            # Get active alerts count
            alerts_query = "SELECT count() as alerts FROM alert WHERE status = 'ACTIVE'"
            alerts_result = await db.execute(alerts_query)
            active_alerts = alerts_result[0]['result'][0]['alerts'] if alerts_result and alerts_result[0].get('result') else 0
            
            metrics = {
                "total_patients": total_patients,
                "recent_patients_30d": recent_patients,
                "active_alerts": active_alerts,
                "patients_by_status": status_counts,
                "patients_by_risk_level": risk_counts,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            try:
                logfire.info("Dashboard metrics calculated", 
                            total_patients=total_patients, 
                            active_alerts=active_alerts)
            except:
                pass
            
            return self._cache_result(cache_key, metrics)
            
        except Exception as e:
            logger.error(f"Error calculating dashboard metrics: {str(e)}")
            try:
                logfire.error("Dashboard metrics calculation failed", error=str(e))
            except:
                pass
            raise
    
    async def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent patient activity and system events."""
        try:
            db = await self._get_db()
            
            # Get recent audit logs
            audit_query = f"""
                SELECT * FROM audit_log 
                ORDER BY created_at DESC 
                LIMIT {limit}
            """
            
            audit_result = await db.execute(audit_query)
            activities = []
            
            if audit_result and audit_result[0].get('result'):
                for log in audit_result[0]['result']:
                    activities.append({
                        "id": log.get('id'),
                        "type": "audit",
                        "action": log.get('action', 'Unknown'),
                        "resource_type": log.get('resource_type', 'Unknown'),
                        "resource_id": log.get('resource_id'),
                        "user_id": log.get('user_id'),
                        "timestamp": log.get('created_at'),
                        "description": f"{log.get('action', 'Action')} on {log.get('resource_type', 'resource')}"
                    })
            
            # Get recent patient updates
            patient_query = f"""
                SELECT id, first_name, last_name, status, updated_at 
                FROM patient 
                WHERE status != 'Deleted'
                ORDER BY updated_at DESC 
                LIMIT {limit}
            """
            
            patient_result = await db.execute(patient_query)
            
            if patient_result and patient_result[0].get('result'):
                for patient in patient_result[0]['result']:
                    activities.append({
                        "id": f"patient_{patient.get('id')}",
                        "type": "patient_update",
                        "action": "UPDATE",
                        "resource_type": "PATIENT",
                        "resource_id": patient.get('id'),
                        "timestamp": patient.get('updated_at'),
                        "description": f"Patient {patient.get('first_name')} {patient.get('last_name')} status: {patient.get('status')}"
                    })
            
            # Sort by timestamp and limit results
            activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            try:
                logfire.info("Recent activity retrieved", activity_count=len(activities[:limit]))
            except:
                pass
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
            try:
                logfire.error("Recent activity retrieval failed", error=str(e))
            except:
                pass
            raise
    
    async def get_alerts_summary(self) -> List[Dict[str, Any]]:
        """Get summary of active alerts and notifications."""
        try:
            db = await self._get_db()
            
            # Get active alerts
            alerts_query = """
                SELECT * FROM alert 
                WHERE status = 'ACTIVE'
                ORDER BY priority DESC, created_at DESC
                LIMIT 20
            """
            
            alerts_result = await db.execute(alerts_query)
            alerts = []
            
            if alerts_result and alerts_result[0].get('result'):
                for alert in alerts_result[0]['result']:
                    alerts.append({
                        "id": alert.get('id'),
                        "type": alert.get('type', 'GENERAL'),
                        "priority": alert.get('priority', 'MEDIUM'),
                        "title": alert.get('title', 'Alert'),
                        "message": alert.get('message', ''),
                        "patient_id": alert.get('patient_id'),
                        "created_at": alert.get('created_at'),
                        "status": alert.get('status', 'ACTIVE')
                    })
            
            # Get alert counts by type
            count_query = """
                SELECT type, count() as count 
                FROM alert 
                WHERE status = 'ACTIVE'
                GROUP BY type
            """
            
            count_result = await db.execute(count_query)
            alert_counts = {}
            
            if count_result and count_result[0].get('result'):
                for row in count_result[0]['result']:
                    alert_counts[row['type']] = row['count']
            
            summary = {
                "active_alerts": alerts,
                "alert_counts_by_type": alert_counts,
                "total_active": len(alerts)
            }
            
            try:
                logfire.info("Alerts summary retrieved", total_alerts=len(alerts))
            except:
                pass
            return summary
            
        except Exception as e:
            logger.error(f"Error getting alerts summary: {str(e)}")
            try:
                logfire.error("Alerts summary retrieval failed", error=str(e))
            except:
                pass
            raise
    
    async def get_patient_distribution(self) -> Dict[str, Any]:
        """Get patient distribution by status and risk level for charts."""
        cache_key = "patient_distribution"
        
        if self._is_cache_valid(cache_key):
            try:
                logfire.info("Returning cached patient distribution")
            except:
                pass
            return self._cache[cache_key]
        
        try:
            db = await self._get_db()
            
            # Status distribution
            status_query = """
                SELECT status, count() as count 
                FROM patient 
                WHERE status != 'Deleted'
                GROUP BY status
                ORDER BY count DESC
            """
            
            status_result = await db.execute(status_query)
            status_distribution = []
            
            if status_result and status_result[0].get('result'):
                for row in status_result[0]['result']:
                    status_distribution.append({
                        "name": row['status'],
                        "value": row['count']
                    })
            
            # Risk level distribution
            risk_query = """
                SELECT risk_level, count() as count 
                FROM patient 
                WHERE status != 'Deleted'
                GROUP BY risk_level
                ORDER BY count DESC
            """
            
            risk_result = await db.execute(risk_query)
            risk_distribution = []
            
            if risk_result and risk_result[0].get('result'):
                for row in risk_result[0]['result']:
                    risk_distribution.append({
                        "name": row['risk_level'],
                        "value": row['count']
                    })
            
            # Age group distribution (if date_of_birth available)
            age_query = """
                SELECT 
                    CASE 
                        WHEN time::year(time::now()) - time::year(date_of_birth) < 18 THEN 'Under 18'
                        WHEN time::year(time::now()) - time::year(date_of_birth) < 30 THEN '18-29'
                        WHEN time::year(time::now()) - time::year(date_of_birth) < 50 THEN '30-49'
                        WHEN time::year(time::now()) - time::year(date_of_birth) < 65 THEN '50-64'
                        ELSE '65+'
                    END as age_group,
                    count() as count
                FROM patient 
                WHERE status != 'Deleted' AND date_of_birth IS NOT NONE
                GROUP BY age_group
                ORDER BY count DESC
            """
            
            age_result = await db.execute(age_query)
            age_distribution = []
            
            if age_result and age_result[0].get('result'):
                for row in age_result[0]['result']:
                    age_distribution.append({
                        "name": row['age_group'],
                        "value": row['count']
                    })
            
            distribution = {
                "by_status": status_distribution,
                "by_risk_level": risk_distribution,
                "by_age_group": age_distribution,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            try:
                logfire.info("Patient distribution calculated")
            except:
                pass
            return self._cache_result(cache_key, distribution)
            
        except Exception as e:
            logger.error(f"Error calculating patient distribution: {str(e)}")
            try:
                logfire.error("Patient distribution calculation failed", error=str(e))
            except:
                pass
            raise
    
    async def get_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get system performance metrics over the specified time period."""
        try:
            db = await self._get_db()
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Patient registration trend
            trend_query = f"""
                SELECT 
                    time::format(created_at, '%Y-%m-%d') as date,
                    count() as registrations
                FROM patient 
                WHERE created_at >= '{start_date.isoformat()}' 
                    AND created_at <= '{end_date.isoformat()}'
                    AND status != 'Deleted'
                GROUP BY date
                ORDER BY date
            """
            
            trend_result = await db.execute(trend_query)
            registration_trend = []
            
            if trend_result and trend_result[0].get('result'):
                for row in trend_result[0]['result']:
                    registration_trend.append({
                        "date": row['date'],
                        "registrations": row['registrations']
                    })
            
            # Status change activity
            activity_query = f"""
                SELECT 
                    time::format(created_at, '%Y-%m-%d') as date,
                    count() as activities
                FROM audit_log 
                WHERE created_at >= '{start_date.isoformat()}' 
                    AND created_at <= '{end_date.isoformat()}'
                    AND resource_type = 'PATIENT'
                GROUP BY date
                ORDER BY date
            """
            
            activity_result = await db.execute(activity_query)
            activity_trend = []
            
            if activity_result and activity_result[0].get('result'):
                for row in activity_result[0]['result']:
                    activity_trend.append({
                        "date": row['date'],
                        "activities": row['activities']
                    })
            
            metrics = {
                "period_days": days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "registration_trend": registration_trend,
                "activity_trend": activity_trend,
                "total_registrations": sum(item['registrations'] for item in registration_trend),
                "total_activities": sum(item['activities'] for item in activity_trend)
            }
            
            try:
                logfire.info("Performance metrics calculated", 
                            days=days, 
                            registrations=metrics['total_registrations'],
                            activities=metrics['total_activities'])
            except:
                pass
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            try:
                logfire.error("Performance metrics calculation failed", error=str(e))
            except:
                pass
            raise