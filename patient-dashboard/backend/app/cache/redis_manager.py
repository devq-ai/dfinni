# Updated: 2025-07-27T12:58:15-05:00
"""
Redis Cache Configuration and Urgent Alert System
Handles real-time caching and immediate alert processing
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from app.config.settings import get_settings

# Get settings
settings = get_settings()


class RedisManager:
    """Redis connection and operation manager"""

    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis_password = settings.REDIS_PASSWORD
        self.cache_ttl = settings.CACHE_TTL
        self.pool: Optional[ConnectionPool] = None
        self.redis_client: Optional[Redis] = None

    async def initialize(self):
        """Initialize Redis connection pool"""
        self.pool = ConnectionPool.from_url(
            self.redis_url,
            password=self.redis_password,
            max_connections=20,
            retry_on_timeout=True,
            decode_responses=True,
        )
        self.redis_client = Redis(connection_pool=self.pool)

        # Test connection
        await self.redis_client.ping()

    async def close(self):
        """Close Redis connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.pool:
            await self.pool.disconnect()

    def get_client(self) -> Redis:
        """Get Redis client instance"""
        if not self.redis_client:
            raise RuntimeError("Redis client not initialized")
        return self.redis_client


# Global Redis manager instance
redis_manager = RedisManager()


class CacheKeys:
    """Redis cache key patterns"""

    # Patient data caching
    PATIENT_PREFIX = "patient:"
    PATIENT_LIST = "patients:list"
    PATIENT_SEARCH = "patients:search:"
    PATIENT_STATUS = "patient:status:"

    # Urgent alerts
    URGENT_ALERTS = "alerts:urgent"
    ALERT_QUEUE = "alerts:queue"
    ALERT_PROCESSING = "alerts:processing"

    # Insurance data
    INSURANCE_ELIGIBILITY = "insurance:eligibility:"
    INSURANCE_CACHE = "insurance:cache:"

    # User sessions
    USER_SESSION = "session:"
    USER_PERMISSIONS = "permissions:"

    # Real-time notifications
    NOTIFICATION_QUEUE = "notifications:queue"
    WEBSOCKET_CONNECTIONS = "websocket:connections"

    # Birthday alerts
    BIRTHDAY_ALERTS = "alerts:birthdays:"

    # System status
    SYSTEM_HEALTH = "system:health"
    API_RATE_LIMITS = "ratelimit:"


class UrgentAlertCache:
    """Handles urgent alerts and real-time notifications via Redis"""

    def __init__(self):
        self.redis = redis_manager.get_client()

    async def cache_urgent_alert(self, alert_data: Dict[str, Any]) -> str:
        """Cache urgent alert with immediate expiration"""
        alert_id = f"urgent_{datetime.utcnow().timestamp()}"

        # Store in urgent alerts set with short TTL (1 hour)
        alert_key = f"{CacheKeys.URGENT_ALERTS}:{alert_id}"

        await self.redis.hset(
            alert_key,
            mapping={
                "id": alert_id,
                "patient_id": alert_data["patient_id"],
                "alert_type": alert_data["alert_type"],
                "priority": "URGENT",
                "message": alert_data["message"],
                "created_at": datetime.utcnow().isoformat(),
                "status": "PENDING",
                "data": json.dumps(alert_data.get("data", {})),
            }
        )

        # Set TTL for urgent alerts (1 hour)
        await self.redis.expire(alert_key, 3600)

        # Add to urgent alerts queue for immediate processing
        await self.redis.lpush(CacheKeys.ALERT_QUEUE, alert_id)

        # Publish to real-time channel
        await self.redis.publish(
            f"urgent_alerts:{alert_data['patient_id']}",
            json.dumps({
                "alert_id": alert_id,
                "type": "URGENT_ALERT",
                "patient_id": alert_data["patient_id"],
                "message": alert_data["message"],
                "timestamp": datetime.utcnow().isoformat(),
            })
        )

        return alert_id

    async def get_urgent_alerts(self, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all urgent alerts, optionally filtered by patient"""
        pattern = f"{CacheKeys.URGENT_ALERTS}:*"
        alert_keys = await self.redis.keys(pattern)

        alerts = []
        for key in alert_keys:
            alert_data = await self.redis.hgetall(key)
            if alert_data and (not patient_id or alert_data.get("patient_id") == patient_id):
                alert_data["data"] = json.loads(alert_data.get("data", "{}"))
                alerts.append(alert_data)

        # Sort by created_at desc
        alerts.sort(key=lambda x: x["created_at"], reverse=True)
        return alerts

    async def mark_alert_processed(self, alert_id: str) -> bool:
        """Mark urgent alert as processed"""
        alert_key = f"{CacheKeys.URGENT_ALERTS}:{alert_id}"

        result = await self.redis.hset(
            alert_key,
            "status", "PROCESSED",
            "processed_at", datetime.utcnow().isoformat()
        )

        # Remove from processing queue
        await self.redis.lrem(CacheKeys.ALERT_QUEUE, 1, alert_id)

        return bool(result)

    async def get_pending_urgent_alerts(self) -> List[str]:
        """Get list of pending urgent alert IDs"""
        return await self.redis.lrange(CacheKeys.ALERT_QUEUE, 0, -1)


class PatientCache:
    """Patient data caching for performance optimization"""

    def __init__(self):
        self.redis = redis_manager.get_client()
        self.default_ttl = settings.CACHE_TTL

    async def cache_patient(self, patient_id: str, patient_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache patient data"""
        cache_key = f"{CacheKeys.PATIENT_PREFIX}{patient_id}"

        # Cache patient data as hash
        await self.redis.hset(
            cache_key,
            mapping={
                "id": patient_data["id"],
                "first_name": patient_data["first_name"],
                "last_name": patient_data["last_name"],
                "status": patient_data["status"],
                "insurance_company": patient_data.get("insurance_company", ""),
                "last_updated": datetime.utcnow().isoformat(),
                "data": json.dumps(patient_data),
            }
        )

        # Set TTL
        ttl = ttl or self.default_ttl
        await self.redis.expire(cache_key, ttl)

        # Add to patient list cache
        await self.redis.sadd(CacheKeys.PATIENT_LIST, patient_id)

        return True

    async def get_cached_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get cached patient data"""
        cache_key = f"{CacheKeys.PATIENT_PREFIX}{patient_id}"

        cached_data = await self.redis.hgetall(cache_key)
        if not cached_data:
            return None

        try:
            patient_data = json.loads(cached_data["data"])
            return patient_data
        except (KeyError, json.JSONDecodeError):
            return None

    async def invalidate_patient_cache(self, patient_id: str) -> bool:
        """Invalidate patient cache (used for urgent updates)"""
        cache_key = f"{CacheKeys.PATIENT_PREFIX}{patient_id}"

        # Delete patient cache
        await self.redis.delete(cache_key)

        # Remove from patient list
        await self.redis.srem(CacheKeys.PATIENT_LIST, patient_id)

        # Clear related search caches
        search_pattern = f"{CacheKeys.PATIENT_SEARCH}*"
        search_keys = await self.redis.keys(search_pattern)
        if search_keys:
            await self.redis.delete(*search_keys)

        return True

    async def cache_patient_status_change(self, patient_id: str, old_status: str, new_status: str, urgent: bool = False):
        """Cache patient status change for real-time updates"""
        status_key = f"{CacheKeys.PATIENT_STATUS}{patient_id}"

        status_change = {
            "patient_id": patient_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.utcnow().isoformat(),
            "urgent": urgent,
        }

        # Cache status change
        await self.redis.hset(
            status_key,
            mapping=status_change
        )

        # Short TTL for status changes (30 minutes)
        await self.redis.expire(status_key, 1800)

        # If urgent, trigger immediate alert
        if urgent or new_status == "URGENT":
            alert_cache = UrgentAlertCache()
            await alert_cache.cache_urgent_alert({
                "patient_id": patient_id,
                "alert_type": "STATUS_CHANGE",
                "message": f"Patient status changed from {old_status} to {new_status}",
                "data": status_change,
            })


class InsuranceCache:
    """Insurance eligibility data caching"""

    def __init__(self):
        self.redis = redis_manager.get_client()

    async def cache_eligibility_response(self, member_id: str, eligibility_data: Dict[str, Any]) -> bool:
        """Cache insurance eligibility response"""
        cache_key = f"{CacheKeys.INSURANCE_ELIGIBILITY}{member_id}"

        await self.redis.hset(
            cache_key,
            mapping={
                "member_id": member_id,
                "status": eligibility_data["status"],
                "insurance_company": eligibility_data["insurance_company"],
                "cached_at": datetime.utcnow().isoformat(),
                "data": json.dumps(eligibility_data),
            }
        )

        # Cache eligibility for 1 hour (insurance data changes frequently)
        await self.redis.expire(cache_key, 3600)

        return True

    async def get_cached_eligibility(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get cached eligibility data"""
        cache_key = f"{CacheKeys.INSURANCE_ELIGIBILITY}{member_id}"

        cached_data = await self.redis.hgetall(cache_key)
        if not cached_data:
            return None

        try:
            return json.loads(cached_data["data"])
        except (KeyError, json.JSONDecodeError):
            return None


class RealTimeNotifications:
    """Real-time notification system using Redis pub/sub"""

    def __init__(self):
        self.redis = redis_manager.get_client()

    async def publish_patient_update(self, patient_id: str, update_type: str, data: Dict[str, Any]):
        """Publish real-time patient update"""
        message = {
            "type": update_type,
            "patient_id": patient_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        # Publish to patient-specific channel
        await self.redis.publish(f"patient_updates:{patient_id}", json.dumps(message))

        # Publish to general updates channel
        await self.redis.publish("patient_updates", json.dumps(message))

    async def publish_urgent_notification(self, notification_data: Dict[str, Any]):
        """Publish urgent notification to all connected clients"""
        message = {
            "type": "URGENT_NOTIFICATION",
            "priority": "HIGH",
            "timestamp": datetime.utcnow().isoformat(),
            **notification_data,
        }

        await self.redis.publish("urgent_notifications", json.dumps(message))

    async def subscribe_to_patient_updates(self, patient_id: str):
        """Subscribe to patient-specific updates"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f"patient_updates:{patient_id}")
        return pubsub

    async def subscribe_to_urgent_notifications(self):
        """Subscribe to urgent notifications"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("urgent_notifications")
        return pubsub


# Global cache instances
urgent_alert_cache = UrgentAlertCache()
patient_cache = PatientCache()
insurance_cache = InsuranceCache()
real_time_notifications = RealTimeNotifications()


# Utility functions
async def initialize_redis():
    """Initialize Redis connections"""
    await redis_manager.initialize()


async def close_redis():
    """Close Redis connections"""
    await redis_manager.close()


async def cache_patient_with_urgent_check(patient_data: Dict[str, Any]) -> bool:
    """Cache patient and check for urgent status changes"""
    patient_id = patient_data["id"]
    new_status = patient_data["status"]

    # Check if patient exists in cache
    cached_patient = await patient_cache.get_cached_patient(patient_id)

    if cached_patient:
        old_status = cached_patient.get("status")

        # Check for urgent status changes
        urgent_statuses = ["URGENT", "CRITICAL", "EMERGENCY"]
        is_urgent = (
            new_status in urgent_statuses or
            (old_status != new_status and new_status == "Churned")
        )

        if old_status != new_status:
            await patient_cache.cache_patient_status_change(
                patient_id, old_status, new_status, urgent=is_urgent
            )

            # Publish real-time update
            await real_time_notifications.publish_patient_update(
                patient_id,
                "STATUS_CHANGE",
                {
                    "old_status": old_status,
                    "new_status": new_status,
                    "urgent": is_urgent,
                }
            )

    # Cache updated patient data
    await patient_cache.cache_patient(patient_id, patient_data)

    return True
