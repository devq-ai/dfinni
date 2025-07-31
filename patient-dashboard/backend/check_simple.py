"""Simple database check without authentication"""
import asyncio
from surrealdb import AsyncSurreal

async def check():
    async with AsyncSurreal("ws://localhost:8000/rpc") as db:
        await db.use("patient_dashboard", "patient_dashboard")
        
        # Count users
        result = await db.query("SELECT * FROM user")
        print(f"Raw user result: {result}")
        
        if result and isinstance(result, list) and len(result) > 0:
            if 'result' in result[0]:
                users = result[0]['result']
                print(f"\nFound {len(users)} users:")
                for user in users:
                    print(f"  - {user.get('email', 'N/A')}")
            else:
                print(f"Unexpected result format: {result[0]}")
        
        # Count patients
        result = await db.query("SELECT * FROM patient")
        print(f"\nRaw patient result: {result}")
        
        if result and isinstance(result, list) and len(result) > 0:
            if 'result' in result[0]:
                patients = result[0]['result']
                print(f"\nFound {len(patients)} patients:")
                for patient in patients:
                    print(f"  - {patient.get('first_name', 'N/A')} {patient.get('last_name', 'N/A')}")

asyncio.run(check())