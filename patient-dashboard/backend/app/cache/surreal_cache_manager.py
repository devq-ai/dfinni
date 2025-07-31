# Updated: 2025-07-27T12:58:15-05:00
"""
SurrealDB Cache Manager and Urgent Alert System
Replaces Redis with SurrealDB for caching and real-time operations
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from surrealdb import Surreal as AsyncSurreal

from app.config.settings import get_settings

# Get settings
settings = get_settings()


class SurrealCacheManager:
    """SurrealDB connection and cache operation manager"""

    def __init__(self):
        self.cache_config = settings.cache_config
        self.cache_client: Optional[AsyncSurreal] = None

    async def initialize(self):
        """Initialize SurrealDB cache connection"""
        self.cache_client = AsyncSurreal(self.cache_config["url"])
        await self.cache_client.connect()
        # Skip signin - use namespace/database directly
        await self.cache_client.use(
            self.cache_config["namespace"],
            self.cache_config["database"]
        )

        # Create cache tables if they don't exist
        await self._setup_cache_schema()

    async def close(self):
        """Close SurrealDB cache connection"""
        if self.cache_client:
            await self.cache_client.close()

    async def _setup_cache_schema(self):
        """Setup cache-specific tables and indexes"""

        # Cache entries table with TTL
        await self.cache_client.query("""
            DEFINE TABLE cache_entry SCHEMAFULL;
            DEFINE FIELD key ON cache_entry TYPE string;
            DEFINE FIELD value ON cache_entry TYPE object;
            DEFINE FIELD expires_at ON cache_entry TYPE datetime;
            DEFINE FIELD created_at ON cache_entry TYPE datetime DEFAULT time::now();
            DEFINE INDEX cache_key ON cache_entry COLUMNS key UNIQUE;
            DEFINE INDEX cache_expires ON cache_entry COLUMNS expires_at;
        """)

        # Urgent alerts table
        await self.cache_client.query("""
            DEFINE TABLE urgent_alert SCHEMAFULL;
            DEFINE FIELD alert_id ON urgent_alert TYPE string;
            DEFINE FIELD patient_id ON urgent_alert TYPE string;
            DEFINE FIELD alert_type ON urgent_alert TYPE string;
            DEFINE FIELD priority ON urgent_alert TYPE string DEFAULT "URGENT";
            DEFINE FIELD message ON urgent_alert TYPE string;
            DEFINE FIELD status ON urgent_alert TYPE string DEFAULT "PENDING";
            DEFINE FIELD data ON urgent_alert TYPE object;
            DEFINE FIELD created_at ON urgent_alert TYPE datetime DEFAULT time::now();
            DEFINE FIELD expires_at ON urgent_alert TYPE datetime;
            DEFINE INDEX alert_patient ON urgent_alert COLUMNS patient_id;
            DEFINE INDEX alert_status ON urgent_alert COLUMNS status;
        """)

        # Job queue table
        await self.cache_client.query("""
            DEFINE TABLE job_queue SCHEMAFULL;
            DEFINE FIELD job_id ON job_queue TYPE string;
            DEFINE FIELD job_type ON job_queue TYPE string;
            DEFINE FIELD payload ON job_queue TYPE object;
            DEFINE FIELD status ON job_queue TYPE string DEFAULT "PENDING";
            DEFINE FIELD priority ON job_queue TYPE number DEFAULT 0;
            DEFINE FIELD scheduled_at ON job_queue TYPE datetime;
            DEFINE FIELD created_at ON job_queue TYPE datetime DEFAULT time::now();
            DEFINE FIELD attempts ON job_queue TYPE number DEFAULT 0;
            DEFINE FIELD max_attempts ON job_queue TYPE number DEFAULT 3;
            DEFINE INDEX job_status ON job_queue COLUMNS status;
            DEFINE INDEX job_scheduled ON job_queue COLUMNS scheduled_at;
        """)

        # Real-time subscriptions table
        await self.cache_client.query("""
            DEFINE TABLE live_subscription SCHEMAFULL;
            DEFINE FIELD subscription_id ON live_subscription TYPE string;
            DEFINE FIELD user_id ON live_subscription TYPE string;
            DEFINE FIELD channel ON live_subscription TYPE string;
            DEFINE FIELD filters ON live_subscription TYPE object;
            DEFINE FIELD created_at ON live_subscription TYPE datetime DEFAULT time::now();
            DEFINE INDEX sub_user ON live_subscription COLUMNS user_id;
            DEFINE INDEX sub_channel ON live_subscription COLUMNS channel;
        """)

    def get_client(self) -> AsyncSurreal:
        """Get SurrealDB cache client instance"""
        if not self.cache_client:
            raise RuntimeError("SurrealDB cache client not initialized")
        return self.cache_client


# Global SurrealDB cache manager instance
surreal_cache_manager = SurrealCacheManager()


class UrgentAlertCache:
    """Handles urgent alerts using SurrealDB real-time capabilities"""

    def __init__(self):
        self.db = surreal_cache_manager.get_client()

    async def cache_urgent_alert(self, alert_data: Dict[str, Any]) -> str:
        """Cache urgent alert with SurrealDB"""
        alert_id = f"urgent_{int(datetime.utcnow().timestamp() * 1000)}"
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Create urgent alert record
        result = await self.db.create("urgent_alert", {
            "alert_id": alert_id,
            "patient_id": alert_data["patient_id"],
            "alert_type": alert_data["alert_type"],
            "priority": "URGENT",
            "message": alert_data["message"],
            "status": "PENDING",
            "data": alert_data.get("data", {}),
            "expires_at": expires_at.isoformat(),
        })

        # Add to job queue for immediate processing
        await self.db.create("job_queue", {
            "job_id": f"process_alert_{alert_id}",
            "job_type": "process_urgent_alert",
            "payload": {"alert_id": alert_id},
            "priority": 100,  # Highest priority
            "scheduled_at": datetime.utcnow().isoformat(),
        })

        return alert_id

    async def get_urgent_alerts(self, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all urgent alerts, optionally filtered by patient"""
        query = """
            SELECT * FROM urgent_alert
            WHERE expires_at > time::now()
            AND status != "PROCESSED"
        """

        if patient_id:
            query += f" AND patient_id = '{patient_id}'"

        query += " ORDER BY created_at DESC"

        result = await self.db.query(query)
        return result[0]["result"] if result and result[0]["result"] else []

    async def mark_alert_processed(self, alert_id: str) -> bool:
        """Mark urgent alert as processed"""
        result = await self.db.query(f"""
            UPDATE urgent_alert
            SET status = "PROCESSED", processed_at = time::now()
            WHERE alert_id = '{alert_id}'
        """)

        return len(result[0]["result"]) > 0 if result and result[0]["result"] else False

    async def get_pending_urgent_alerts(self) -> List[Dict[str, Any]]:
        """Get list of pending urgent alerts"""
        result = await self.db.query("""
            SELECT * FROM urgent_alert
            WHERE status = "PENDING"
            AND expires_at > time::now()
            ORDER BY created_at ASC
        """)

        return result[0]["result"] if result and result[0]["result"] else []


class PatientCache:
    """Patient data caching using SurrealDB with TTL"""

    def __init__(self):
        self.db = surreal_cache_manager.get_client()
        self.default_ttl = settings.CACHE_TTL

    async def cache_patient(self, patient_id: str, patient_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache patient data with TTL"""
        ttl = ttl or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        # Cache patient data
        cache_key = f"patient:{patient_id}"

        await self.db.query(f"""
            DELETE cache_entry WHERE key = '{cache_key}';
            CREATE cache_entry SET
                key = '{cache_key}',
                value = {json.dumps(patient_data)},
                expires_at = '{expires_at.isoformat()}';
        """)

        return True

    async def get_cached_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get cached patient data if not expired"""
        cache_key = f"patient:{patient_id}"

        result = await self.db.query(f"""
            SELECT value FROM cache_entry
            WHERE key = '{cache_key}'
            AND expires_at > time::now()
        """)

        if result and result[0]["result"]:
            return result[0]["result"][0]["value"]

        return None

    async def invalidate_patient_cache(self, patient_id: str) -> bool:
        """Invalidate patient cache (used for urgent updates)"""
        cache_key = f"patient:{patient_id}"

        result = await self.db.query(f"""
            DELETE cache_entry WHERE key = '{cache_key}';
        """)

        # Also clear related search caches
        await self.db.query("""
            DELETE cache_entry WHERE key ~ "patient_search:*";
        """)

        return True

    async def cache_patient_status_change(self, patient_id: str, old_status: str, new_status: str, urgent: bool = False):
        """Cache patient status change and trigger real-time updates"""

        # If urgent or status is URGENT, trigger immediate alert
        if urgent or new_status in ["URGENT", "CRITICAL", "EMERGENCY"]:
            alert_cache = UrgentAlertCache()
            await alert_cache.cache_urgent_alert({
                "patient_id": patient_id,
                "alert_type": "STATUS_CHANGE",
                "message": f"Patient status changed from {old_status} to {new_status}",
                "data": {
                    "old_status": old_status,
                    "new_status": new_status,
                    "urgent": urgent,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            })

        # Invalidate patient cache to force refresh
        await self.invalidate_patient_cache(patient_id)


class InsuranceCache:
    """Insurance eligibility data caching using SurrealDB"""

    def __init__(self):
        self.db = surreal_cache_manager.get_client()

    async def cache_eligibility_response(self, member_id: str, eligibility_data: Dict[str, Any]) -> bool:
        """Cache insurance eligibility response"""
        cache_key = f"insurance:eligibility:{member_id}"
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour TTL

        await self.db.query(f"""
            DELETE cache_entry WHERE key = '{cache_key}';
            CREATE cache_entry SET
                key = '{cache_key}',
                value = {json.dumps(eligibility_data)},
                expires_at = '{expires_at.isoformat()}';
        """)

        return True

    async def get_cached_eligibility(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Get cached eligibility data if not expired"""
        cache_key = f"insurance:eligibility:{member_id}"

        result = await self.db.query(f"""
            SELECT value FROM cache_entry
            WHERE key = '{cache_key}'
            AND expires_at > time::now()
        """)

        if result and result[0]["result"]:
            return result[0]["result"][0]["value"]

        return None


class RealTimeNotifications:
    """Real-time notification system using SurrealDB LIVE queries"""

    def __init__(self):
        self.db = surreal_cache_manager.get_client()

    async def setup_live_patient_updates(self, user_id: str, patient_id: Optional[str] = None):
        """Setup live query for patient updates"""
        if patient_id:
            # Subscribe to specific patient updates
            live_query = f"""
                LIVE SELECT * FROM urgent_alert
                WHERE patient_id = '{patient_id}'
                AND status = "PENDING"
            """
        else:
            # Subscribe to all urgent alerts
            live_query = """
                LIVE SELECT * FROM urgent_alert
                WHERE status = "PENDING"
            """

        # Execute live query and return subscription ID
        result = await self.db.query(live_query)
        subscription_id = result[0]["result"] if result and result[0]["result"] else None

        if subscription_id:
            # Store subscription info
            await self.db.create("live_subscription", {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "channel": f"patient_updates:{patient_id}" if patient_id else "urgent_notifications",
                "filters": {"patient_id": patient_id} if patient_id else {},
            })

        return subscription_id

    async def publish_patient_update(self, patient_id: str, update_type: str, data: Dict[str, Any]):
        """Publish patient update by creating alert record"""
        await self.db.create("urgent_alert", {
            "alert_id": f"update_{int(datetime.utcnow().timestamp() * 1000)}",
            "patient_id": patient_id,
            "alert_type": update_type,
            "priority": "NORMAL",
            "message": f"Patient {patient_id} updated: {update_type}",
            "data": data,
            "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
        })


class JobQueue:
    """Background job queue using SurrealDB"""

    def __init__(self):
        self.db = surreal_cache_manager.get_client()

    async def enqueue_job(self, job_type: str, payload: Dict[str, Any],
                         priority: int = 0, scheduled_at: Optional[datetime] = None) -> str:
        """Enqueue a background job"""
        job_id = f"{job_type}_{int(datetime.utcnow().timestamp() * 1000)}"
        scheduled_at = scheduled_at or datetime.utcnow()

        await self.db.create("job_queue", {
            "job_id": job_id,
            "job_type": job_type,
            "payload": payload,
            "priority": priority,
            "scheduled_at": scheduled_at.isoformat(),
            "status": "PENDING",
        })

        return job_id

    async def get_pending_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get pending jobs ordered by priority and schedule time"""
        result = await self.db.query(f"""
            SELECT * FROM job_queue
            WHERE status = "PENDING"
            AND scheduled_at <= time::now()
            AND attempts < max_attempts
            ORDER BY priority DESC, scheduled_at ASC
            LIMIT {limit}
        """)

        return result[0]["result"] if result and result[0]["result"] else []

    async def mark_job_completed(self, job_id: str) -> bool:
        """Mark job as completed"""
        result = await self.db.query(f"""
            UPDATE job_queue
            SET status = "COMPLETED", completed_at = time::now()
            WHERE job_id = '{job_id}'
        """)

        return len(result[0]["result"]) > 0 if result and result[0]["result"] else False

    async def mark_job_failed(self, job_id: str, error_message: str) -> bool:
        """Mark job as failed and increment attempts"""
        result = await self.db.query(f"""
            UPDATE job_queue
            SET attempts = attempts + 1,
                error_message = '{error_message}',
                last_attempt = time::now()
            WHERE job_id = '{job_id}'
        """)

        return len(result[0]["result"]) > 0 if result and result[0]["result"] else False


# Global cache instances - will be initialized after cache manager
urgent_alert_cache = None
patient_cache = None
insurance_cache = None
real_time_notifications = None
job_queue = None


# Utility functions
async def initialize_cache():
    """Initialize SurrealDB cache connections"""
    global urgent_alert_cache, patient_cache, insurance_cache, real_time_notifications, job_queue
    
    await surreal_cache_manager.initialize()
    
    # Initialize cache instances after cache manager is ready
    urgent_alert_cache = UrgentAlertCache()
    patient_cache = PatientCache()
    insurance_cache = InsuranceCache()
    real_time_notifications = RealTimeNotifications()
    job_queue = JobQueue()


async def close_cache():
    """Close SurrealDB cache connections"""
    await surreal_cache_manager.close()


async def cleanup_expired_cache():
    """Clean up expired cache entries"""
    db = surreal_cache_manager.get_client()

    # Clean expired cache entries
    await db.query("DELETE cache_entry WHERE expires_at < time::now();")

    # Clean expired alerts
    await db.query("DELETE urgent_alert WHERE expires_at < time::now();")

    # Clean old completed jobs (keep for 24 hours)
    cleanup_time = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    await db.query(f"DELETE job_queue WHERE status = 'COMPLETED' AND completed_at < '{cleanup_time}';")


async def cache_patient_with_urgent_check(patient_data: Dict[str, Any]) -> bool:
    """Cache patient and check for urgent status changes"""
    if not patient_cache:
        raise RuntimeError("Cache not initialized. Call initialize_cache() first.")
        
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
