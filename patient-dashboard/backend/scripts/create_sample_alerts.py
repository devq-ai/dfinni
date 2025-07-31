"""
Create sample alerts in the database for testing.
"""
import asyncio
from datetime import datetime, timedelta, timezone
import httpx
import json

# SurrealDB connection details
SURREAL_URL = "http://localhost:8000"
SURREAL_USER = "root"
SURREAL_PASS = "root"
NAMESPACE = "healthcare"
DATABASE = "patient_dashboard"

async def execute_query(query: str):
    """Execute a SurrealDB query using HTTP API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SURREAL_URL}/sql",
            auth=(SURREAL_USER, SURREAL_PASS),
            headers={
                "NS": NAMESPACE,
                "DB": DATABASE,
                "Accept": "application/json"
            },
            content=query
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed: {response.text}")

async def create_sample_alerts():
    """Create sample alerts in the database."""
    try:
        print("Creating sample alerts...")
        
        # Get users to assign alerts to
        result = await execute_query(f"USE NS {NAMESPACE} DB {DATABASE}; SELECT id FROM user;")
        
        if result and isinstance(result, list) and len(result) > 1:
            # The second result contains the SELECT query results
            users = result[1].get('result', [])
        else:
            users = []
        
        if not users:
            print("No users found. Please create users first.")
            return
        
        # Sample alerts for each user
        alert_templates = [
            {
                "type": "critical",
                "title": "Critical Health Alert",
                "message": "Patient John Doe showing signs of rapid deterioration. Immediate medical attention required.",
                "patient_id": "patient:john123",
                "patient_name": "John Doe",
                "source": "AI Health Monitor",
                "read": False,
                "resolved": False,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=30),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=1)
            },
            {
                "type": "warning",
                "title": "Medication Non-Compliance",
                "message": "Sarah Smith has missed 3 consecutive medication doses. Follow-up recommended.",
                "patient_id": "patient:sarah456",
                "patient_name": "Sarah Smith",
                "source": "Medication Tracker",
                "read": False,
                "resolved": False,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=2),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
            },
            {
                "type": "info",
                "title": "Appointment Reminder",
                "message": "5 patients have appointments scheduled for tomorrow. Review schedule.",
                "source": "Scheduling System",
                "read": True,
                "resolved": False,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=4),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=1)
            },
            {
                "type": "warning",
                "title": "High Risk Pattern Detected",
                "message": "Multiple patients showing similar symptoms. Potential outbreak alert.",
                "source": "Pattern Recognition AI",
                "read": False,
                "resolved": False,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=6),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=3)
            },
            {
                "type": "success",
                "title": "Treatment Success",
                "message": "Michael Johnson treatment plan completed successfully. All health markers improved.",
                "patient_id": "patient:michael789",
                "patient_name": "Michael Johnson",
                "source": "Treatment Monitor",
                "read": True,
                "resolved": True,
                "created_at": datetime.now(timezone.utc) - timedelta(hours=12),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=30)
            },
            {
                "type": "critical",
                "title": "Emergency Room Visit",
                "message": "Patient Emma Wilson admitted to ER with severe symptoms. Immediate review required.",
                "patient_id": "patient:emma012",
                "patient_name": "Emma Wilson",
                "source": "Hospital Integration",
                "read": False,
                "resolved": False,
                "created_at": datetime.now(timezone.utc) - timedelta(minutes=15),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=12)
            },
            {
                "type": "info",
                "title": "Weekly Report Available",
                "message": "Your weekly patient summary report is now available for review.",
                "source": "Reporting System",
                "read": False,
                "resolved": False,
                "created_at": datetime.now(timezone.utc) - timedelta(days=1),
                "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
            }
        ]
        
        # Create alerts for each user
        created_count = 0
        for user in users:
            user_id = user['id']
            print(f"\nCreating alerts for user: {user_id}")
            
            for alert in alert_templates:
                # Create alert with user_id
                alert_data = alert.copy()
                alert_data['user_id'] = user_id
                
                # Format datetime objects
                alert_data['created_at'] = alert_data['created_at'].isoformat() + 'Z'
                alert_data['expires_at'] = alert_data['expires_at'].isoformat() + 'Z'
                
                # Build query
                fields = []
                for key, value in alert_data.items():
                    if isinstance(value, str):
                        fields.append(f"{key} = '{value}'")
                    elif isinstance(value, bool):
                        fields.append(f"{key} = {str(value).lower()}")
                    else:
                        fields.append(f"{key} = {value}")
                
                query = f"USE NS {NAMESPACE} DB {DATABASE}; CREATE alert SET {', '.join(fields)};"
                
                try:
                    result = await execute_query(query)
                    created_count += 1
                    print(f"  ✓ Created {alert['type']} alert: {alert['title']}")
                except Exception as e:
                    print(f"  ✗ Error creating alert: {e}")
        
        print(f"\n✅ Successfully created {created_count} alerts")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_sample_alerts())