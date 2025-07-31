"""Simple check with exact values"""
import asyncio
from surrealdb import Surreal

async def check():
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    await db.use("patient_dashboard", "patient_dashboard")
    
    # Count all records
    result = await db.query("SELECT * FROM user")
    print(f"Users: {len(result[0]['result']) if result and result[0].get('result') else 0}")
    
    result = await db.query("SELECT * FROM patient")
    print(f"Patients: {len(result[0]['result']) if result and result[0].get('result') else 0}")
    
    await db.close()

asyncio.run(check())