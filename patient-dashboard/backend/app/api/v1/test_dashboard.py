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
    # Return mock data directly for now
    current = {
        "totalPatients": 20,
        "activePatients": 9,
        "highRiskPatients": 3,
        "appointmentsToday": 0
    }
    
    previous = {
        "totalPatients": 18,
        "activePatients": 8,
        "highRiskPatients": 2,
        "appointmentsToday": 0
    }
    
    trends = {
        "totalPatients": {"value": "+11.1%", "isUp": True},
        "activePatients": {"value": "+12.5%", "isUp": True},
        "highRiskPatients": {"value": "+50.0%", "isUp": True},
        "appointmentsToday": {"value": "0%", "isUp": True}
    }
    
    # Log to Logfire for testing
    try:
        logfire.info(
            "test_dashboard_stats_mock",
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