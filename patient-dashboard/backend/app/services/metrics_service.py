"""
Comprehensive Logfire metrics service for monitoring and observability.
Per Production Proposal Phase 2: Add comprehensive Logfire metrics
"""
import time
import logfire
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timezone
import asyncio
from contextlib import asynccontextmanager

from app.config.settings import get_settings
from app.models.user import UserRole

settings = get_settings()


class MetricsService:
    """Service for comprehensive application metrics using Logfire."""
    
    def __init__(self):
        self.service_name = "pfinni-patient-dashboard"
        self.initialized = False
        
    def initialize(self):
        """Initialize metrics service."""
        if not self.initialized:
            # Don't reconfigure logfire - it's already configured in logging.py
            self.initialized = True
            logfire.info("Metrics service initialized", environment=settings.ENVIRONMENT)
    
    # Business Metrics
    
    def track_patient_created(self, patient_id: str, created_by: str, **kwargs):
        """Track new patient creation."""
        logfire.info(
            "patient.created",
            patient_id=patient_id,
            created_by=created_by,
            metric_type="business",
            **kwargs
        )
    
    def track_patient_updated(self, patient_id: str, updated_by: str, fields_changed: list, **kwargs):
        """Track patient update."""
        logfire.info(
            "patient.updated",
            patient_id=patient_id,
            updated_by=updated_by,
            fields_changed=fields_changed,
            fields_count=len(fields_changed),
            metric_type="business",
            **kwargs
        )
    
    def track_patient_status_change(self, patient_id: str, old_status: str, new_status: str, changed_by: str, **kwargs):
        """Track patient status transitions."""
        logfire.info(
            "patient.status_changed",
            patient_id=patient_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            metric_type="business",
            **kwargs
        )
    
    def track_alert_created(self, alert_id: str, patient_id: str, severity: str, alert_type: str, **kwargs):
        """Track alert creation."""
        logfire.info(
            "alert.created",
            alert_id=alert_id,
            patient_id=patient_id,
            severity=severity,
            alert_type=alert_type,
            metric_type="business",
            **kwargs
        )
    
    def track_alert_resolved(self, alert_id: str, resolved_by: str, resolution_time_hours: float, **kwargs):
        """Track alert resolution."""
        logfire.info(
            "alert.resolved",
            alert_id=alert_id,
            resolved_by=resolved_by,
            resolution_time_hours=resolution_time_hours,
            metric_type="business",
            **kwargs
        )
    
    def track_user_login(self, user_id: str, user_role: str, auth_method: str = "internal", **kwargs):
        """Track user login."""
        logfire.info(
            "user.login",
            user_id=user_id,
            user_role=user_role,
            auth_method=auth_method,
            metric_type="business",
            **kwargs
        )
    
    def track_user_logout(self, user_id: str, session_duration_minutes: float, **kwargs):
        """Track user logout."""
        logfire.info(
            "user.logout",
            user_id=user_id,
            session_duration_minutes=session_duration_minutes,
            metric_type="business",
            **kwargs
        )
    
    # Performance Metrics
    
    @asynccontextmanager
    async def track_database_query(self, query_type: str, table: str):
        """Track database query performance."""
        start_time = time.time()
        try:
            with logfire.span(
                "database.query",
                query_type=query_type,
                table=table,
                metric_type="performance"
            ):
                yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            logfire.info(
                "database.query.completed",
                query_type=query_type,
                table=table,
                duration_ms=duration_ms,
                metric_type="performance"
            )
    
    def track_api_request(self, method: str, path: str, status_code: int, duration_ms: float, **kwargs):
        """Track API request metrics."""
        logfire.info(
            "api.request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            success=(200 <= status_code < 400),
            metric_type="performance",
            **kwargs
        )
        
        # Record metrics for alerting
        asyncio.create_task(self._record_metric_async("api_request", 1))
        asyncio.create_task(self._record_metric_async("api_request_duration", duration_ms))
        if status_code >= 500:
            asyncio.create_task(self._record_metric_async("api_request_error", 1))
    
    def track_cache_operation(self, operation: str, key: str, hit: bool, duration_ms: float):
        """Track cache operations."""
        logfire.info(
            "cache.operation",
            operation=operation,
            key=key,
            hit=hit,
            duration_ms=duration_ms,
            metric_type="performance"
        )
    
    def track_external_api_call(self, service: str, endpoint: str, status_code: int, duration_ms: float, **kwargs):
        """Track external API calls."""
        logfire.info(
            "external_api.call",
            service=service,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            success=(200 <= status_code < 400),
            metric_type="performance",
            **kwargs
        )
    
    # Error Metrics
    
    def track_error(self, error_type: str, error_message: str, user_id: Optional[str] = None, **kwargs):
        """Track application errors."""
        logfire.error(
            "application.error",
            error_type=error_type,
            error_message=error_message,
            user_id=user_id,
            metric_type="error",
            **kwargs
        )
    
    def track_validation_error(self, field: str, value: Any, error: str, **kwargs):
        """Track validation errors."""
        logfire.warning(
            "validation.error",
            field=field,
            value_type=type(value).__name__,
            error=error,
            metric_type="error",
            **kwargs
        )
    
    def track_auth_failure(self, reason: str, email: Optional[str] = None, ip_address: Optional[str] = None, **kwargs):
        """Track authentication failures."""
        logfire.warning(
            "auth.failure",
            reason=reason,
            email=email,
            ip_address=ip_address,
            metric_type="security",
            **kwargs
        )
        
        # Record for alerting
        asyncio.create_task(self._record_metric_async("auth_failure", 1))
        if reason == "unauthorized":
            asyncio.create_task(self._record_metric_async("auth_unauthorized", 1))
    
    # System Metrics
    
    def track_background_job(self, job_name: str, status: str, duration_seconds: float, **kwargs):
        """Track background job execution."""
        logfire.info(
            "background_job.completed",
            job_name=job_name,
            status=status,
            duration_seconds=duration_seconds,
            success=(status == "success"),
            metric_type="system",
            **kwargs
        )
    
    def track_health_check(self, component: str, status: str, response_time_ms: float, **kwargs):
        """Track health check results."""
        logfire.info(
            "health_check",
            component=component,
            status=status,
            response_time_ms=response_time_ms,
            healthy=(status == "healthy"),
            metric_type="system",
            **kwargs
        )
    
    # HIPAA Compliance Metrics
    
    def track_phi_access(self, user_id: str, patient_id: str, access_type: str, fields_accessed: list, **kwargs):
        """Track PHI (Protected Health Information) access for HIPAA compliance."""
        logfire.info(
            "phi.access",
            user_id=user_id,
            patient_id=patient_id,
            access_type=access_type,
            fields_accessed=fields_accessed,
            fields_count=len(fields_accessed),
            metric_type="compliance",
            **kwargs
        )
    
    def track_data_export(self, user_id: str, export_type: str, record_count: int, **kwargs):
        """Track data exports for compliance."""
        logfire.info(
            "data.export",
            user_id=user_id,
            export_type=export_type,
            record_count=record_count,
            metric_type="compliance",
            **kwargs
        )
    
    # Decorators for automatic metric tracking
    
    def track_endpoint(self, endpoint_name: str):
        """Decorator to track endpoint performance."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    with logfire.span(f"endpoint.{endpoint_name}"):
                        result = await func(*args, **kwargs)
                        duration_ms = (time.time() - start_time) * 1000
                        logfire.info(
                            "endpoint.completed",
                            endpoint=endpoint_name,
                            duration_ms=duration_ms,
                            success=True,
                            metric_type="performance"
                        )
                        return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    logfire.error(
                        "endpoint.failed",
                        endpoint=endpoint_name,
                        duration_ms=duration_ms,
                        error=str(e),
                        metric_type="error"
                    )
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    with logfire.span(f"endpoint.{endpoint_name}"):
                        result = func(*args, **kwargs)
                        duration_ms = (time.time() - start_time) * 1000
                        logfire.info(
                            "endpoint.completed",
                            endpoint=endpoint_name,
                            duration_ms=duration_ms,
                            success=True,
                            metric_type="performance"
                        )
                        return result
                except Exception as e:
                    duration_ms = (time.time() - start_time) * 1000
                    logfire.error(
                        "endpoint.failed",
                        endpoint=endpoint_name,
                        duration_ms=duration_ms,
                        error=str(e),
                        metric_type="error"
                    )
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    def track_service_method(self, service_name: str, method_name: str):
        """Decorator to track service method performance."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with logfire.span(f"service.{service_name}.{method_name}"):
                    return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with logfire.span(f"service.{service_name}.{method_name}"):
                    return func(*args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    # Custom metrics
    
    def track_custom_metric(self, metric_name: str, value: float, unit: str = "count", **tags):
        """Track custom business metrics."""
        logfire.info(
            f"custom.{metric_name}",
            value=value,
            unit=unit,
            metric_type="custom",
            **tags
        )
    
    # Dashboard-specific metrics
    
    def track_dashboard_load(self, user_id: str, load_time_ms: float, widget_count: int, **kwargs):
        """Track dashboard load performance."""
        logfire.info(
            "dashboard.load",
            user_id=user_id,
            load_time_ms=load_time_ms,
            widget_count=widget_count,
            metric_type="performance",
            **kwargs
        )
    
    def track_real_time_update(self, update_type: str, latency_ms: float, **kwargs):
        """Track real-time update latency."""
        logfire.info(
            "realtime.update",
            update_type=update_type,
            latency_ms=latency_ms,
            metric_type="performance",
            **kwargs
        )
    
    async def _record_metric_async(self, metric_type: str, value: float, metadata: Optional[Dict[str, Any]] = None):
        """Record metric to database for alerting."""
        try:
            # Import here to avoid circular dependency
            from app.services.alerting_service import alerting_service
            
            # Record metric if alerting service is initialized
            if hasattr(alerting_service, 'db') and alerting_service.db:
                await alerting_service.record_metric(metric_type, value, metadata)
        except Exception as e:
            # Don't fail if metric recording fails
            logfire.debug("Failed to record metric for alerting", error=str(e))
    
    @asynccontextmanager
    async def track_database_query_with_metrics(self, query_type: str, table: str):
        """Enhanced database query tracking with metrics recording."""
        start_time = time.time()
        try:
            with logfire.span(
                "database.query",
                query_type=query_type,
                table=table,
                metric_type="performance"
            ):
                yield
        finally:
            duration_ms = (time.time() - start_time) * 1000
            logfire.info(
                "database.query.completed",
                query_type=query_type,
                table=table,
                duration_ms=duration_ms,
                metric_type="performance"
            )
            # Record for alerting
            await self._record_metric_async("database_query_duration", duration_ms, {"table": table})


# Singleton instance
metrics_service = MetricsService()

# Don't initialize on import - let main.py handle it after logging is configured