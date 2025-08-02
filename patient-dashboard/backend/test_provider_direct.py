import asyncio
from app.database.connection import get_database

async def test_create_provider():
    db = await get_database()
    
    try:
        # Simple provider data
        provider_data = {
            "id": "test-provider-1",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah@pfinni.com",
            "phone": "555-123-4567",
            "role": "doctor",
            "license_number": "MD123456",
            "department": "Cardiology",
            "status": "active",
            "hire_date": "2015-03-15",
            "assigned_patients": [],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "created_by": "admin",
            "deleted_at": None,
            "deleted_by": None
        }
        
        # Try to create directly
        result = await db.execute(
            "CREATE provider CONTENT $data",
            {"data": provider_data}
        )
        print("Result:", result)
        
        # Try to fetch it back
        fetch_result = await db.execute("SELECT * FROM provider")
        print("All providers:", fetch_result)
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

asyncio.run(test_create_provider())