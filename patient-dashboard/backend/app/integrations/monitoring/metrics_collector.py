"""
Metrics collector for Prometheus-compatible metrics.
"""
from typing import Dict, Any
import time

class MetricsCollector:
    """Collect and format metrics for monitoring."""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        uptime = time.time() - self.start_time
        
        metrics = []
        
        # Basic metrics
        metrics.append("# HELP pfinni_uptime_seconds Application uptime in seconds")
        metrics.append("# TYPE pfinni_uptime_seconds gauge")
        metrics.append(f"pfinni_uptime_seconds {uptime}")
        
        metrics.append("# HELP pfinni_health_status Application health status")
        metrics.append("# TYPE pfinni_health_status gauge")
        metrics.append("pfinni_health_status 1")
        
        return "\n".join(metrics)