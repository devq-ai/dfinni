"""Test dashboard endpoint without authentication for debugging"""
from fastapi import APIRouter
import logfire
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["test"])

@router.get("/test-logfire")
async def test_logfire():
    """Test Logfire logging"""
    import time
    timestamp = time.time()
    
    # Test different log levels with unique identifiers
    logfire.info(
        "LOGFIRE_TEST_INFO", 
        service="pfinni-patient-dashboard", 
        test=True,
        timestamp=timestamp,
        message="This is a test info message"
    )
    
    logfire.warn(
        "LOGFIRE_TEST_WARNING", 
        service="pfinni-patient-dashboard",
        timestamp=timestamp,
        message="This is a test warning message"
    )
    
    logfire.error(
        "LOGFIRE_TEST_ERROR", 
        service="pfinni-patient-dashboard",
        timestamp=timestamp,
        message="This is a test error message (not a real error)"
    )
    
    # Test with span
    with logfire.span("test_logfire_span", timestamp=timestamp):
        logfire.info("Inside test span", timestamp=timestamp)
    
    return {
        "message": "Logfire test completed",
        "timestamp": timestamp,
        "logfire_url": "https://logfire-us.pydantic.dev/devq-ai/pfinni",
        "logs_sent": [
            "LOGFIRE_TEST_INFO",
            "LOGFIRE_TEST_WARNING",
            "LOGFIRE_TEST_ERROR",
            "test_logfire_span"
        ]
    }

@router.get("/test-dashboard-stats", response_model=None)
async def get_test_dashboard_stats():
    """Get dashboard stats without authentication for testing"""
    from app.database.connection import get_database
    
    try:
        # Get actual data from database
        db = await get_database()
        
        # Get all patients
        all_patients_result = await db.execute("SELECT * FROM patient")
        all_patients = []
        if all_patients_result:
            # SurrealDB returns the result directly as a list
            all_patients = all_patients_result
        
        # Count total patients
        total_patients = len(all_patients)
        
        # Count active patients (status = 'active' only)
        active_patients = sum(1 for p in all_patients if p.get('status', '').lower() == 'active')
        
        # Count high risk patients (risk_level = 'High' AND status != 'churned')
        high_risk_patients = sum(1 for p in all_patients 
                                if p.get('risk_level', '') == 'High' 
                                and p.get('status', '').lower() != 'churned')
        
        # Debug logging
        logfire.info(
            "Dashboard stats debug",
            total_records=len(all_patients_result) if all_patients_result else 0,
            total_patients=total_patients,
            active_patients=active_patients,
            high_risk_patients=high_risk_patients,
            statuses=[p.get('status', '') for p in all_patients[:5]] if all_patients else [],
            risk_levels=[p.get('risk_level', '') for p in all_patients[:5]] if all_patients else []
        )
        
        # For now, appointments is 0 as we don't have appointment data
        appointments_today = 0
        
        current = {
            "totalPatients": total_patients,
            "activePatients": active_patients,
            "highRiskPatients": high_risk_patients,
            "appointmentsToday": appointments_today
        }
        
        # Calculate previous values (reduce by 10% for demo)
        previous = {
            "totalPatients": max(0, int(total_patients * 0.9)),
            "activePatients": max(0, int(active_patients * 0.9)),
            "highRiskPatients": max(0, int(high_risk_patients * 0.9)),
            "appointmentsToday": 0
        }
        
        # Calculate trends
        def calculate_trend(current_val, previous_val):
            if previous_val == 0:
                if current_val > 0:
                    return {"value": "+100%", "isUp": True}
                else:
                    return {"value": "0%", "isUp": False}
            
            change = ((current_val - previous_val) / previous_val) * 100
            is_up = change >= 0
            sign = "+" if is_up else ""
            return {"value": f"{sign}{change:.1f}%", "isUp": is_up}
        
        trends = {
            "totalPatients": calculate_trend(current["totalPatients"], previous["totalPatients"]),
            "activePatients": calculate_trend(current["activePatients"], previous["activePatients"]),
            "highRiskPatients": calculate_trend(current["highRiskPatients"], previous["highRiskPatients"]),
            "appointmentsToday": {"value": "0%", "isUp": False}
        }
        
        # Log to Logfire
        try:
            logfire.info(
                "test_dashboard_stats_real",
                current=current,
                service="pfinni-patient-dashboard",
                endpoint="/test-dashboard-stats"
            )
        except:
            pass
        
        return {
            "current": current,
            "previous": previous,
            "trends": trends
        }
        
    except Exception as e:
        # Fallback to some default values if database query fails
        logfire.error(f"Failed to get dashboard stats: {str(e)}")
        
        current = {
            "totalPatients": 0,
            "activePatients": 0,
            "highRiskPatients": 0,
            "appointmentsToday": 0
        }
        
        previous = {
            "totalPatients": 0,
            "activePatients": 0,
            "highRiskPatients": 0,
            "appointmentsToday": 0
        }
        
        trends = {
            "totalPatients": {"value": "0%", "isUp": False},
            "activePatients": {"value": "0%", "isUp": False},
            "highRiskPatients": {"value": "0%", "isUp": False},
            "appointmentsToday": {"value": "0%", "isUp": False}
        }
        
        return {
            "current": current,
            "previous": previous,
            "trends": trends
        }

@router.get("/test-patients", response_model=None)
async def get_test_patients():
    """Get patients data without authentication for testing"""
    from app.database.connection import get_database
    
    try:
        db = await get_database()
        
        # Get first 5 patients
        patients_result = await db.execute("SELECT * FROM patient LIMIT 5")
        
        if patients_result:
            return {
                "status": "success",
                "count": len(patients_result),
                "patients": patients_result
            }
        else:
            return {
                "status": "success",
                "count": 0,
                "patients": []
            }
            
    except Exception as e:
        logfire.error(f"Failed to get test patients: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "patients": []
        }

@router.get("/test-alerts-stats", response_model=None)
async def get_test_alerts_stats():
    """Get alerts stats without authentication for testing"""
    from app.database.connection import get_database
    
    try:
        db = await get_database()
        
        # Get actual alert counts from database
        stats_queries = {
            'total': "SELECT count() as count FROM alert GROUP ALL",
            'unread': "SELECT count() as count FROM alert WHERE (read = false OR read = null) GROUP ALL",
            'critical': "SELECT count() as count FROM alert WHERE severity = 'critical' GROUP ALL",
            'pending_action': "SELECT count() as count FROM alert WHERE requires_action = true GROUP ALL",
            'active': "SELECT count() as count FROM alert WHERE status = 'active' GROUP ALL"
        }
        
        stats_results = {}
        for stat_name, stat_query in stats_queries.items():
            result = await db.execute(stat_query)
            if result and len(result) > 0:
                stats_results[stat_name] = result[0].get('count', 0)
            else:
                stats_results[stat_name] = 0
        
        # Get recent alerts
        alerts_result = await db.execute(
            "SELECT * FROM alert WHERE status = 'active' ORDER BY created_at DESC LIMIT 5"
        )
        
        alerts = []
        if alerts_result:
            for alert_data in alerts_result:
                alerts.append({
                    'id': str(alert_data.get('id', '')).split(':')[-1] if alert_data.get('id') else None,
                    'type': alert_data.get('type', 'unknown'),
                    'severity': alert_data.get('severity', 'medium'),
                    'title': alert_data.get('title', ''),
                    'description': alert_data.get('description', ''),
                    'patient_id': alert_data.get('patient_id'),
                    'patient_name': alert_data.get('patient_name'),
                    'created_at': alert_data.get('created_at').isoformat() if alert_data.get('created_at') else None,
                    'status': alert_data.get('status', 'active')
                })
        
        # Log to Logfire
        logfire.info(
            "test_alerts_stats_real",
            stats=stats_results,
            alerts_count=len(alerts),
            service="pfinni-patient-dashboard",
            endpoint="/test-alerts-stats"
        )
        
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "stats": {
                    "total": stats_results['active'],  # Only count active alerts as "new"
                    "unread": stats_results['unread'],
                    "critical": stats_results['critical'],
                    "pending_action": stats_results['pending_action']
                }
            }
        }
        
    except Exception as e:
        logfire.error(f"Failed to get test alerts stats: {str(e)}")
        return {
            "status": "success",
            "data": {
                "alerts": [],
                "stats": {
                    "total": 0,
                    "unread": 0,
                    "critical": 0,
                    "pending_action": 0
                }
            }
        }