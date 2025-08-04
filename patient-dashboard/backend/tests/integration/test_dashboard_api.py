"""
Integration tests for dashboard API endpoints
Per Production Proposal: Add Logfire instrumentation to all test cases
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime, timedelta
import logfire

from app.main import app
from app.models.analytics import DashboardMetrics, TimeSeriesData
from app.models.user import UserResponse


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.dashboard
class TestDashboardAPI:
    """Test dashboard API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_current_user(self):
        """Mock current user dependency."""
        user = UserResponse(
            id="user:123",
            email="provider@example.com",
            first_name="Test",
            last_name="Provider",
            role="provider",
            is_active=True,
            password_reset_required=False,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        with patch('app.api.v1.dashboard.get_current_user') as mock:
            mock.return_value = user
            yield user
    
    @pytest.fixture
    def mock_analytics_service(self):
        """Mock analytics service."""
        with patch('app.api.v1.dashboard.analytics_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_patient_service(self):
        """Mock patient service."""
        with patch('app.api.v1.dashboard.patient_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_alert_service(self):
        """Mock alert service."""
        with patch('app.api.v1.dashboard.alert_service') as mock:
            yield mock
    
    def test_get_dashboard_metrics(self, client, auth_headers, mock_current_user, mock_analytics_service):
        """Test getting dashboard metrics."""
        logfire.info("Testing dashboard metrics retrieval", test_case="get_dashboard_metrics")
        
        # Mock service response
        mock_analytics_service.get_dashboard_metrics.return_value = DashboardMetrics(
            total_patients=150,
            active_patients=120,
            alerts_today=15,
            critical_alerts=3,
            patient_growth=12.5,
            adherence_rate=85.2,
            appointments_today=8,
            pending_tasks=5
        )
        
        response = client.get(
            "/api/v1/dashboard/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_patients"] == 150
        assert data["active_patients"] == 120
        assert data["alerts_today"] == 15
        assert data["critical_alerts"] == 3
        assert data["patient_growth"] == 12.5
        
        logfire.info("Dashboard metrics retrieved successfully", 
                    total_patients=150, 
                    active_patients=120,
                    alerts_today=15)
    
    def test_get_patient_overview(self, client, auth_headers, mock_current_user, mock_patient_service):
        """Test getting patient overview data."""
        logfire.info("Testing patient overview retrieval", test_case="get_patient_overview")
        
        # Mock service response
        mock_patient_service.get_patient_overview.return_value = {
            "by_status": {
                "active": 120,
                "inactive": 25,
                "inquiry": 5
            },
            "by_risk_level": {
                "low": 80,
                "medium": 50,
                "high": 20
            },
            "recent_additions": [
                {
                    "id": "patient:1",
                    "name": "John Doe",
                    "added_date": "2024-01-15"
                }
            ]
        }
        
        response = client.get(
            "/api/v1/dashboard/patients/overview",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["by_status"]["active"] == 120
        assert data["by_risk_level"]["high"] == 20
        assert len(data["recent_additions"]) == 1
        
        logfire.info("Patient overview retrieved successfully",
                    active_patients=120,
                    high_risk_patients=20)
    
    def test_get_alerts_overview(self, client, auth_headers, mock_current_user, mock_alert_service):
        """Test getting alerts overview."""
        logfire.info("Testing alerts overview retrieval", test_case="get_alerts_overview")
        
        # Mock service response
        mock_alert_service.get_alerts_overview.return_value = {
            "total_active": 25,
            "by_severity": {
                "critical": 3,
                "high": 10,
                "medium": 8,
                "low": 4
            },
            "by_type": {
                "medication": 12,
                "appointment": 8,
                "vitals": 3,
                "lab_result": 2
            },
            "recent_alerts": [
                {
                    "id": "alert:1",
                    "title": "Medication Non-Adherence",
                    "severity": "high",
                    "created_at": "2024-01-15T10:00:00Z"
                }
            ]
        }
        
        response = client.get(
            "/api/v1/dashboard/alerts/overview",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_active"] == 25
        assert data["by_severity"]["critical"] == 3
        assert data["by_type"]["medication"] == 12
        
        logfire.info("Alerts overview retrieved successfully",
                    total_active=25,
                    critical_alerts=3)
    
    def test_get_time_series_data(self, client, auth_headers, mock_current_user, mock_analytics_service):
        """Test getting time series data."""
        logfire.info("Testing time series data retrieval", test_case="get_time_series_data")
        
        # Mock service response
        mock_analytics_service.get_time_series_data.return_value = [
            TimeSeriesData(date="2024-01-01", value=100, label="Patients"),
            TimeSeriesData(date="2024-01-02", value=105, label="Patients"),
            TimeSeriesData(date="2024-01-03", value=110, label="Patients"),
            TimeSeriesData(date="2024-01-04", value=108, label="Patients"),
            TimeSeriesData(date="2024-01-05", value=115, label="Patients")
        ]
        
        response = client.get(
            "/api/v1/dashboard/analytics/time-series",
            headers=auth_headers,
            params={
                "metric": "patient_count",
                "start_date": "2024-01-01",
                "end_date": "2024-01-05",
                "granularity": "daily"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert data[0]["date"] == "2024-01-01"
        assert data[0]["value"] == 100
        assert data[-1]["value"] == 115
        
        logfire.info("Time series data retrieved successfully",
                    metric="patient_count",
                    data_points=5)
    
    def test_get_adherence_trends(self, client, auth_headers, mock_current_user, mock_analytics_service):
        """Test getting medication adherence trends."""
        logfire.info("Testing adherence trends retrieval", test_case="get_adherence_trends")
        
        # Mock service response
        mock_analytics_service.get_adherence_trends.return_value = [
            {
                "week": "2024-W01",
                "average_adherence": 82.5,
                "patient_count": 145
            },
            {
                "week": "2024-W02",
                "average_adherence": 84.2,
                "patient_count": 148
            }
        ]
        
        response = client.get(
            "/api/v1/dashboard/analytics/adherence-trends",
            headers=auth_headers,
            params={"weeks": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["average_adherence"] == 82.5
        assert data[1]["average_adherence"] == 84.2
        
        logfire.info("Adherence trends retrieved successfully",
                    weeks_retrieved=2,
                    latest_adherence=84.2)
    
    def test_get_provider_stats(self, client, auth_headers, mock_current_user, mock_analytics_service):
        """Test getting provider statistics."""
        logfire.info("Testing provider statistics retrieval", test_case="get_provider_stats")
        
        # Mock service response
        mock_analytics_service.get_provider_performance_metrics.return_value = {
            "total_patients": 45,
            "average_response_time": 2.5,
            "alerts_resolved": 120,
            "patient_satisfaction": 4.5,
            "adherence_improvement": 8.2,
            "monthly_trend": {
                "patients": "+5",
                "satisfaction": "+0.2",
                "response_time": "-0.5"
            }
        }
        
        response = client.get(
            "/api/v1/dashboard/provider/stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_patients"] == 45
        assert data["average_response_time"] == 2.5
        assert data["patient_satisfaction"] == 4.5
        
        logfire.info("Provider statistics retrieved successfully",
                    total_patients=45,
                    satisfaction=4.5)
    
    def test_get_recent_activities(self, client, auth_headers, mock_current_user, mock_analytics_service):
        """Test getting recent activities."""
        logfire.info("Testing recent activities retrieval", test_case="get_recent_activities")
        
        # Mock service response
        mock_analytics_service.get_recent_activities.return_value = [
            {
                "id": "activity:1",
                "type": "patient_added",
                "description": "New patient John Doe added",
                "timestamp": "2024-01-15T10:00:00Z",
                "user": "Dr. Smith"
            },
            {
                "id": "activity:2",
                "type": "alert_resolved",
                "description": "High priority alert resolved",
                "timestamp": "2024-01-15T09:30:00Z",
                "user": "Dr. Johnson"
            }
        ]
        
        response = client.get(
            "/api/v1/dashboard/activities/recent",
            headers=auth_headers,
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["type"] == "patient_added"
        assert data[1]["type"] == "alert_resolved"
        
        logfire.info("Recent activities retrieved successfully", activity_count=2)
    
    def test_get_system_health(self, client, auth_headers, mock_current_user, mock_analytics_service):
        """Test getting system health metrics."""
        logfire.info("Testing system health metrics retrieval", test_case="get_system_health")
        
        # Mock service response
        mock_analytics_service.get_system_health_metrics.return_value = {
            "status": "healthy",
            "uptime_percentage": 99.9,
            "api_performance": {
                "avg_response_time": 125.5,
                "p95_response_time": 250.0,
                "error_rate": 0.02
            },
            "database_health": {
                "status": "healthy",
                "avg_query_time": 15.2,
                "connection_pool_usage": 0.45
            },
            "active_users": 25,
            "last_check": "2024-01-15T12:00:00Z"
        }
        
        response = client.get(
            "/api/v1/dashboard/system/health",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["uptime_percentage"] == 99.9
        assert data["api_performance"]["error_rate"] == 0.02
        
        logfire.info("System health metrics retrieved successfully",
                    status="healthy",
                    uptime=99.9)
    
    def test_export_dashboard_data(self, client, auth_headers, mock_current_user, mock_analytics_service):
        """Test exporting dashboard data."""
        logfire.info("Testing dashboard data export", test_case="export_dashboard_data")
        
        # Mock service response
        mock_analytics_service.export_analytics_data.return_value = {
            "filename": "dashboard_export_20240115.csv",
            "data": "date,metric,value\n2024-01-01,patients,100\n2024-01-02,patients,105",
            "format": "csv",
            "size": 1024
        }
        
        response = client.post(
            "/api/v1/dashboard/export",
            headers=auth_headers,
            json={
                "metrics": ["patients", "adherence", "alerts"],
                "format": "csv",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"].endswith(".csv")
        assert data["format"] == "csv"
        assert "data" in data
        
        logfire.info("Dashboard data exported successfully", format="csv")
    
    def test_get_dashboard_widgets(self, client, auth_headers, mock_current_user):
        """Test getting dashboard widget configuration."""
        logfire.info("Testing dashboard widgets retrieval", test_case="get_dashboard_widgets")
        response = client.get(
            "/api/v1/dashboard/widgets",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "widgets" in data
        assert len(data["widgets"]) > 0
        
        # Verify widget structure
        widget = data["widgets"][0]
        assert "id" in widget
        assert "type" in widget
        assert "title" in widget
        assert "position" in widget
        
        logfire.info("Dashboard widgets retrieved successfully", widget_count=len(data["widgets"]))
    
    def test_update_dashboard_layout(self, client, auth_headers, mock_current_user):
        """Test updating dashboard layout."""
        logfire.info("Testing dashboard layout update", test_case="update_dashboard_layout")
        layout_data = {
            "layout": [
                {
                    "widget_id": "metrics_overview",
                    "position": {"x": 0, "y": 0, "w": 12, "h": 4}
                },
                {
                    "widget_id": "patient_chart",
                    "position": {"x": 0, "y": 4, "w": 6, "h": 6}
                },
                {
                    "widget_id": "alerts_list",
                    "position": {"x": 6, "y": 4, "w": 6, "h": 6}
                }
            ]
        }
        
        response = client.put(
            "/api/v1/dashboard/layout",
            headers=auth_headers,
            json=layout_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Dashboard layout updated successfully"
        
        logfire.info("Dashboard layout updated successfully", widgets_updated=3)
    
    def test_get_dashboard_unauthorized(self, client):
        """Test accessing dashboard without authentication."""
        logfire.info("Testing unauthorized dashboard access", test_case="get_dashboard_unauthorized")
        
        response = client.get("/api/v1/dashboard/metrics")
        assert response.status_code == 401
        
        logfire.info("Unauthorized access properly rejected")