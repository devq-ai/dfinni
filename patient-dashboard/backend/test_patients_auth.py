#!/usr/bin/env python3
"""Test patient endpoints with authentication"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api/v1"

async def test_patient_endpoints():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # Login first
        print("1. Testing login...")
        login_data = {
            "username": "admin@example.com",
            "password": "Admin123!",
            "grant_type": "password"
        }
        response = await client.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Access token obtained: {token_data['access_token'][:20]}...")
            
            # Set up headers with token
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}",
                "Content-Type": "application/json"
            }
            
            # Test current user
            print("\n2. Testing current user...")
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"Current user response: {response.status_code}")
            if response.status_code == 200:
                print(f"Current user: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Error: {response.text}")
            
            # List patients
            print("\n3. Testing list patients...")
            response = await client.get(f"{BASE_URL}/patients", headers=headers)
            print(f"List patients response: {response.status_code}")
            if response.status_code == 200:
                print(f"Patients: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Error: {response.text}")
            
            # Create a test patient
            print("\n4. Testing create patient...")
            patient_data = {
                "first_name": "Test",
                "last_name": "Patient",
                "date_of_birth": "1990-01-01",
                "email": "test.patient@example.com",
                "phone": "5551234567",
                "ssn": "123456789",
                "address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "state": "CA",
                    "zip_code": "90210"
                },
                "insurance": {
                    "member_id": "MEM789",
                    "company": "Test Insurance Co",
                    "plan_type": "PPO",
                    "group_number": "GRP456",
                    "effective_date": "2024-01-01"
                },
                "status": "Active",
                "risk_level": "Low"
            }
            response = await client.post(f"{BASE_URL}/patients", headers=headers, json=patient_data)
            print(f"Create patient response: {response.status_code}")
            if response.status_code == 200:
                created_patient = response.json()
                print(f"Created patient: {json.dumps(created_patient, indent=2)}")
                
                # Get the created patient
                patient_id = created_patient.get('id')
                if patient_id:
                    print(f"\n5. Testing get patient {patient_id}...")
                    response = await client.get(f"{BASE_URL}/patients/{patient_id}", headers=headers)
                    print(f"Get patient response: {response.status_code}")
                    if response.status_code == 200:
                        print(f"Patient details: {json.dumps(response.json(), indent=2)}")
                    else:
                        print(f"Error: {response.text}")
            else:
                print(f"Error: {response.text}")
            
            # Test search
            print("\n6. Testing patient search...")
            response = await client.get(
                f"{BASE_URL}/patients?search=test",
                headers=headers
            )
            print(f"Search response: {response.status_code}")
            if response.status_code == 200:
                print(f"Search results: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"Error: {response.text}")
        else:
            print(f"Login failed: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_patient_endpoints())