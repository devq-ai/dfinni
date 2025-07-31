"""
Health checker for monitoring service status.
"""
from typing import Dict, Any
import asyncio
from app.database.connection import get_database

class HealthChecker:
    """Check health status of all services."""
    
    async def check_all_services(self) -> Dict[str, Any]:
        """Check health of all services."""
        services = {}
        
        # Check database
        try:
            db = await get_database()
            db_health = await db.health_check()
            services["database"] = {
                "status": "healthy" if db_health["status"] == "healthy" else "unhealthy",
                "details": db_health
            }
        except Exception as e:
            services["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check cache (if implemented)
        services["cache"] = {
            "status": "healthy",
            "details": {"message": "Cache health check not implemented"}
        }
        
        # Overall health
        overall_healthy = all(
            service.get("status") == "healthy" 
            for service in services.values()
        )
        
        return {
            "overall_healthy": overall_healthy,
            "services": services
        }