"""
Analytics models for dashboard metrics and reporting
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MetricType(str, Enum):
    """Types of metrics available"""
    PATIENT_COUNT = "patient_count"
    ADHERENCE_RATE = "adherence_rate"
    ALERT_COUNT = "alert_count"
    APPOINTMENT_COUNT = "appointment_count"
    RISK_SCORE = "risk_score"


class DashboardMetrics(BaseModel):
    """Dashboard overview metrics"""
    total_patients: int = Field(..., description="Total number of patients")
    active_patients: int = Field(..., description="Number of active patients")
    alerts_today: int = Field(..., description="Number of alerts today")
    critical_alerts: int = Field(..., description="Number of critical alerts")
    patient_growth: float = Field(..., description="Patient growth percentage")
    adherence_rate: float = Field(..., description="Average medication adherence rate")
    appointments_today: int = Field(..., description="Number of appointments today")
    pending_tasks: int = Field(..., description="Number of pending tasks")


class TimeSeriesData(BaseModel):
    """Time series data point"""
    date: str = Field(..., description="Date in ISO format")
    value: float = Field(..., description="Metric value")
    label: Optional[str] = Field(None, description="Optional label")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PatientMetrics(BaseModel):
    """Patient-specific metrics"""
    patient_id: str = Field(..., description="Patient ID")
    adherence_rate: float = Field(..., description="Medication adherence rate")
    risk_score: float = Field(..., description="Risk score (0-1)")
    last_visit: Optional[str] = Field(None, description="Last visit date")
    upcoming_appointments: int = Field(0, description="Number of upcoming appointments")
    active_medications: int = Field(0, description="Number of active medications")
    recent_alerts: int = Field(0, description="Number of recent alerts")
    health_score: Optional[float] = Field(None, description="Overall health score")


class MetricTrend(BaseModel):
    """Trend information for a metric"""
    direction: str = Field(..., description="Trend direction: up, down, stable")
    percentage_change: float = Field(..., description="Percentage change")
    trend_strength: float = Field(..., description="Trend strength (0-1)")
    forecast: Optional[List[float]] = Field(None, description="Future predictions")


class AnalyticsReport(BaseModel):
    """Comprehensive analytics report"""
    report_id: str = Field(..., description="Report ID")
    report_type: str = Field(..., description="Type of report")
    generated_at: datetime = Field(..., description="Report generation timestamp")
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    summary: Dict[str, Any] = Field(..., description="Report summary")
    insights: List[str] = Field(..., description="Key insights")
    recommendations: List[str] = Field(..., description="Recommendations")
    data: Dict[str, Any] = Field(..., description="Report data")


class ProviderMetrics(BaseModel):
    """Provider performance metrics"""
    provider_id: str = Field(..., description="Provider ID")
    total_patients: int = Field(..., description="Total patients")
    average_response_time: float = Field(..., description="Average response time in hours")
    alerts_resolved: int = Field(..., description="Number of alerts resolved")
    patient_satisfaction: float = Field(..., description="Patient satisfaction score (0-5)")
    adherence_improvement: float = Field(..., description="Adherence improvement percentage")


class SystemHealthMetrics(BaseModel):
    """System health and performance metrics"""
    status: str = Field(..., description="System status")
    uptime_percentage: float = Field(..., description="Uptime percentage")
    api_performance: Dict[str, float] = Field(..., description="API performance metrics")
    database_health: Dict[str, Any] = Field(..., description="Database health metrics")
    active_users: int = Field(..., description="Number of active users")
    error_rate: float = Field(..., description="Error rate percentage")
    last_check: datetime = Field(..., description="Last health check timestamp")