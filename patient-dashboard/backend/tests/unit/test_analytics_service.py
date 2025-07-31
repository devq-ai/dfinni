"""
Unit tests for AnalyticsService
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import List, Dict

from app.services.analytics_service import AnalyticsService
from app.models.analytics import (
    DashboardMetrics,
    PatientMetrics,
    TimeSeriesData,
    MetricTrend
)


@pytest.mark.unit
@pytest.mark.analytics
class TestAnalyticsService:
    """Test cases for AnalyticsService."""
    
    @pytest.fixture
    def analytics_service(self, mock_db):
        """Create analytics service instance with mocked database."""
        service = AnalyticsService()
        service.db = mock_db
        return service
    
    @pytest.mark.asyncio
    async def test_get_dashboard_metrics(self, analytics_service, mock_db):
        """Test getting dashboard metrics."""
        # Mock database responses
        mock_db.query.side_effect = [
            # Total patients
            [{"count": 150}],
            # Active patients
            [{"count": 120}],
            # Alerts today
            [{"count": 15}],
            # Critical alerts
            [{"count": 3}],
            # Patient growth
            [{"growth_percentage": 12.5}]
        ]
        
        result = await analytics_service.get_dashboard_metrics("user:123")
        
        assert isinstance(result, DashboardMetrics)
        assert result.total_patients == 150
        assert result.active_patients == 120
        assert result.alerts_today == 15
        assert result.critical_alerts == 3
        assert result.patient_growth == 12.5
        
        # Verify all queries were made
        assert mock_db.query.call_count == 5
    
    @pytest.mark.asyncio
    async def test_get_patient_metrics(self, analytics_service, mock_db):
        """Test getting patient-specific metrics."""
        patient_id = "patient:123"
        
        # Mock database responses
        mock_db.query.side_effect = [
            # Adherence rate
            [{"adherence_rate": 85.5}],
            # Risk score
            [{"risk_score": 0.25}],
            # Last visit
            [{"last_visit": "2024-01-15T10:00:00Z"}],
            # Upcoming appointments
            [{"count": 2}],
            # Active medications
            [{"count": 5}],
            # Recent alerts
            [{"count": 1}]
        ]
        
        result = await analytics_service.get_patient_metrics(patient_id)
        
        assert isinstance(result, PatientMetrics)
        assert result.patient_id == patient_id
        assert result.adherence_rate == 85.5
        assert result.risk_score == 0.25
        assert result.last_visit == "2024-01-15T10:00:00Z"
        assert result.upcoming_appointments == 2
        assert result.active_medications == 5
        assert result.recent_alerts == 1
    
    @pytest.mark.asyncio
    async def test_get_time_series_data(self, analytics_service, mock_db):
        """Test getting time series data."""
        # Mock database response
        mock_db.query.return_value = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 105},
            {"date": "2024-01-03", "value": 110},
            {"date": "2024-01-04", "value": 108},
            {"date": "2024-01-05", "value": 115}
        ]
        
        result = await analytics_service.get_time_series_data(
            metric="patient_count",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 5),
            granularity="daily"
        )
        
        assert isinstance(result, list)
        assert len(result) == 5
        assert all(isinstance(item, TimeSeriesData) for item in result)
        assert result[0].date == "2024-01-01"
        assert result[0].value == 100
        assert result[-1].value == 115
    
    @pytest.mark.asyncio
    async def test_get_patient_risk_distribution(self, analytics_service, mock_db):
        """Test getting patient risk distribution."""
        # Mock database response
        mock_db.query.return_value = [
            {"risk_level": "low", "count": 80, "percentage": 53.3},
            {"risk_level": "medium", "count": 50, "percentage": 33.3},
            {"risk_level": "high", "count": 20, "percentage": 13.3}
        ]
        
        result = await analytics_service.get_patient_risk_distribution()
        
        assert isinstance(result, dict)
        assert "low" in result
        assert "medium" in result
        assert "high" in result
        assert result["low"]["count"] == 80
        assert result["low"]["percentage"] == 53.3
        assert sum(r["count"] for r in result.values()) == 150
    
    @pytest.mark.asyncio
    async def test_get_adherence_trends(self, analytics_service, mock_db):
        """Test getting medication adherence trends."""
        # Mock database response
        mock_db.query.return_value = [
            {
                "week": "2024-W01",
                "average_adherence": 82.5,
                "patient_count": 145
            },
            {
                "week": "2024-W02",
                "average_adherence": 84.2,
                "patient_count": 148
            },
            {
                "week": "2024-W03",
                "average_adherence": 83.8,
                "patient_count": 150
            },
            {
                "week": "2024-W04",
                "average_adherence": 85.1,
                "patient_count": 150
            }
        ]
        
        result = await analytics_service.get_adherence_trends(weeks=4)
        
        assert isinstance(result, list)
        assert len(result) == 4
        assert result[0]["week"] == "2024-W01"
        assert result[0]["average_adherence"] == 82.5
        assert result[-1]["average_adherence"] == 85.1
    
    @pytest.mark.asyncio
    async def test_get_alert_statistics(self, analytics_service, mock_db):
        """Test getting alert statistics."""
        # Mock database response
        mock_db.query.return_value = [
            {
                "type": "medication",
                "severity": "high",
                "count": 15,
                "resolved": 10,
                "pending": 5
            },
            {
                "type": "appointment",
                "severity": "medium",
                "count": 25,
                "resolved": 20,
                "pending": 5
            },
            {
                "type": "lab_result",
                "severity": "high",
                "count": 8,
                "resolved": 5,
                "pending": 3
            }
        ]
        
        result = await analytics_service.get_alert_statistics(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        assert isinstance(result, dict)
        assert "by_type" in result
        assert "by_severity" in result
        assert "total" in result
        assert result["total"]["count"] == 48
        assert result["total"]["resolved"] == 35
        assert result["total"]["pending"] == 13
    
    @pytest.mark.asyncio
    async def test_calculate_metric_trend(self, analytics_service):
        """Test metric trend calculation."""
        data_points = [
            {"date": "2024-01-01", "value": 100},
            {"date": "2024-01-02", "value": 105},
            {"date": "2024-01-03", "value": 103},
            {"date": "2024-01-04", "value": 108},
            {"date": "2024-01-05", "value": 110}
        ]
        
        result = analytics_service.calculate_metric_trend(data_points)
        
        assert isinstance(result, MetricTrend)
        assert result.direction == "up"  # Overall upward trend
        assert result.percentage_change == 10.0  # 10% increase from 100 to 110
        assert result.trend_strength > 0  # Positive correlation
    
    @pytest.mark.asyncio
    async def test_get_provider_performance_metrics(self, analytics_service, mock_db):
        """Test getting provider performance metrics."""
        provider_id = "user:provider123"
        
        # Mock database response
        mock_db.query.return_value = [
            {
                "total_patients": 45,
                "average_response_time": 2.5,  # hours
                "alerts_resolved": 120,
                "patient_satisfaction": 4.5,
                "adherence_improvement": 8.2
            }
        ]
        
        result = await analytics_service.get_provider_performance_metrics(provider_id)
        
        assert isinstance(result, dict)
        assert result["total_patients"] == 45
        assert result["average_response_time"] == 2.5
        assert result["alerts_resolved"] == 120
        assert result["patient_satisfaction"] == 4.5
        assert result["adherence_improvement"] == 8.2
    
    @pytest.mark.asyncio
    async def test_get_system_health_metrics(self, analytics_service, mock_db):
        """Test getting system health metrics."""
        # Mock various system metrics
        mock_db.query.side_effect = [
            # API response times
            [{"avg_response_time": 125.5, "p95_response_time": 250.0}],
            # Error rate
            [{"error_rate": 0.02}],  # 2% error rate
            # Active users
            [{"active_users": 25}],
            # Database performance
            [{"avg_query_time": 15.2}]
        ]
        
        result = await analytics_service.get_system_health_metrics()
        
        assert isinstance(result, dict)
        assert result["api_performance"]["avg_response_time"] == 125.5
        assert result["api_performance"]["p95_response_time"] == 250.0
        assert result["error_rate"] == 0.02
        assert result["active_users"] == 25
        assert result["database_performance"]["avg_query_time"] == 15.2
    
    @pytest.mark.asyncio
    async def test_generate_analytics_report(self, analytics_service, mock_db):
        """Test generating comprehensive analytics report."""
        # Mock multiple database calls for report generation
        mock_db.query.side_effect = [
            # Summary metrics
            [{"total_patients": 150, "active_patients": 120}],
            # Top insights
            [
                {"insight": "15% increase in medication adherence"},
                {"insight": "20% reduction in high-risk patients"},
                {"insight": "30% faster alert response time"}
            ],
            # Recommendations
            [
                {"recommendation": "Focus on patients with adherence < 70%"},
                {"recommendation": "Schedule follow-ups for high-risk patients"}
            ]
        ]
        
        result = await analytics_service.generate_analytics_report(
            report_type="monthly",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        assert isinstance(result, dict)
        assert "summary" in result
        assert "insights" in result
        assert "recommendations" in result
        assert result["summary"]["total_patients"] == 150
        assert len(result["insights"]) == 3
        assert len(result["recommendations"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_predictive_analytics(self, analytics_service, mock_db):
        """Test predictive analytics functionality."""
        patient_id = "patient:123"
        
        # Mock ML model predictions
        with patch('app.services.analytics_service.ml_predictor') as mock_predictor:
            mock_predictor.predict_risk.return_value = {
                "risk_score": 0.75,
                "risk_factors": [
                    "Missed medications",
                    "No recent visits",
                    "Abnormal lab results"
                ],
                "confidence": 0.85
            }
            
            mock_predictor.predict_adherence.return_value = {
                "predicted_adherence": 65.5,
                "trend": "declining",
                "intervention_recommended": True
            }
            
            result = await analytics_service.get_predictive_analytics(patient_id)
            
            assert isinstance(result, dict)
            assert result["risk_prediction"]["risk_score"] == 0.75
            assert len(result["risk_prediction"]["risk_factors"]) == 3
            assert result["adherence_prediction"]["predicted_adherence"] == 65.5
            assert result["adherence_prediction"]["intervention_recommended"] is True
    
    @pytest.mark.asyncio
    async def test_export_analytics_data(self, analytics_service, mock_db):
        """Test exporting analytics data."""
        # Mock data retrieval
        mock_db.query.return_value = [
            {"date": "2024-01-01", "metric": "patients", "value": 100},
            {"date": "2024-01-02", "metric": "patients", "value": 105}
        ]
        
        result = await analytics_service.export_analytics_data(
            metrics=["patients", "adherence"],
            format="csv",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31)
        )
        
        assert isinstance(result, dict)
        assert "filename" in result
        assert "data" in result
        assert result["filename"].endswith(".csv")
        assert len(result["data"]) > 0