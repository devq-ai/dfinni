#!/usr/bin/env python
"""Direct test of SurrealDB using HTTP API"""
import requests
import json
import bcrypt

# Base URL for SurrealDB HTTP API
BASE_URL = "http://localhost:8000"

# Test function
def test_surrealdb():
    # Create test user
    password_hash = bcrypt.hashpw("Test123!".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # SQL endpoint
    response = requests.post(
        f"{BASE_URL}/sql",
        headers={
            "Accept": "application/json",
            "NS": "patient_dashboard",
            "DB": "patient_dashboard"
        },
        data=f"""
            USE NS patient_dashboard DB patient_dashboard;
            CREATE user:test1 SET
                email = 'test1@example.com',
                password_hash = '{password_hash}',
                first_name = 'Test',
                last_name = 'User',
                role = 'ADMIN',
                is_active = true,
                created_at = time::now(),
                updated_at = time::now();
            SELECT * FROM user;
        """
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_surrealdb()