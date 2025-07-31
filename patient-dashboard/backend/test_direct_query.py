#!/usr/bin/env python3
"""Test direct SurrealDB query"""

import asyncio
import httpx
import json
import base64

# SurrealDB connection details
SURREAL_URL = "http://localhost:8000/sql"
SURREAL_USER = "root"
SURREAL_PASS = "root"
NAMESPACE = "patient_dashboard"
DATABASE = "patient_dashboard"

# Create auth header
auth_string = f"{SURREAL_USER}:{SURREAL_PASS}"
auth_bytes = auth_string.encode('utf-8')
auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_b64}",
    "NS": NAMESPACE,
    "DB": DATABASE
}

async def test_queries():
    async with httpx.AsyncClient() as client:
        queries = [
            "USE NS patient_dashboard DB patient_dashboard; SELECT * FROM patient;",
            "USE NS patient_dashboard DB patient_dashboard; SELECT * FROM patient WHERE status != 'Deleted';",
            "USE NS patient_dashboard DB patient_dashboard; INFO FOR TABLE patient;",
            "USE NS patient_dashboard DB patient_dashboard; SELECT count() as total FROM patient GROUP BY total;"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            print("-" * 80)
            
            response = await client.post(SURREAL_URL, headers=headers, data=query)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(test_queries())