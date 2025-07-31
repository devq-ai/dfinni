#!/usr/bin/env python3
"""
Check users in the database
"""
import asyncio
import httpx
import json

# SurrealDB connection details
SURREAL_URL = "http://localhost:8000"
SURREAL_USER = "root"
SURREAL_PASS = "root"
NAMESPACE = "healthcare"
DATABASE = "patient_dashboard"

async def execute_query(query: str):
    """Execute a SurrealDB query"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SURREAL_URL}/sql",
            headers={
                "Accept": "application/json"
            },
            auth=(SURREAL_USER, SURREAL_PASS),
            content=query
        )
        return response.json()

async def main():
    print("Checking users in database...")
    
    # Query all users
    result = await execute_query(f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM user;")
    print(f"\nAll users: {json.dumps(result, indent=2)}")
    
    # Query specific user
    result = await execute_query(f"USE NS {NAMESPACE} DB {DATABASE}; SELECT * FROM user WHERE email = 'dion@devq.ai';")
    print(f"\nQuery for dion@devq.ai: {json.dumps(result, indent=2)}")
    
    # Also check different query format
    result = await execute_query(f"USE NS {NAMESPACE} DB {DATABASE}; SELECT email, password_hash FROM user;")
    print(f"\nEmails and password hashes: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())