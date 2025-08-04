"""Test dashboard endpoint without authentication for debugging"""
from fastapi import APIRouter
import logfire
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["test"])
analytics_service = AnalyticsService()

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

@router.get("/test-dashboard-stats")
async def get_test_dashboard_stats():
    """Get dashboard stats without authentication for testing"""
    try:
        # Get current period stats
        current_stats = await analytics_service.get_dashboard_metrics()
        
        # Calculate previous period stats (mock for now)
        previous_stats = {
            "totalPatients": int(current_stats.get("totalPatients", 0) * 0.9),
            "activePatients": int(current_stats.get("activePatients", 0) * 0.85),
            "highRiskPatients": int(current_stats.get("urgentPatients", 0) * 1.1),
            "appointmentsToday": 0
        }
        
        # Calculate trends
        def calculate_trend(current: int, previous: int):
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
        
        # Log to Logfire for testing
        logfire.info(
            "test_dashboard_stats",
            current=current,
            service="pfinni-patient-dashboard",
            endpoint="/test-dashboard-stats"
        )
        
        return {
            "current": current,
            "previous": previous_stats,
            "trends": trends
        }
        
    except Exception as e:
        print(f"Error in test dashboard: {e}")
        return {
            "current": {
                "totalPatients": 20,
                "activePatients": 9,
                "highRiskPatients": 3,
                "appointmentsToday": 0
            },
            "previous": {
                "totalPatients": 18,
                "activePatients": 8,
                "highRiskPatients": 2,
                "appointmentsToday": 0
            },
            "trends": {
                "totalPatients": {"value": "+11.1%", "isUp": True},
                "activePatients": {"value": "+12.5%", "isUp": True},
                "highRiskPatients": {"value": "+50.0%", "isUp": True},
                "appointmentsToday": {"value": "0%", "isUp": True}
            }
        }