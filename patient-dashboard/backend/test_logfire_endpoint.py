#!/usr/bin/env python3
"""Test script to generate Logfire logs."""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8001"

print("Testing Logfire logging...")

# Test health endpoint
print("\n1. Testing health endpoint:")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test login endpoint
print("\n2. Testing login endpoint:")
login_data = {
    "username": "demo@example.com",
    "password": "password123"
}
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    data=login_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    token = response.json()["access_token"]
    print("Login successful!")
    
    # Test authenticated endpoint
    print("\n3. Testing dashboard stats endpoint:")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/dashboard/stats", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test patients endpoint
    print("\n4. Testing patients endpoint:")
    response = requests.get(f"{BASE_URL}/api/v1/patients", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Number of patients: {len(response.json())}")

print("\n✅ Test complete! Check Logfire at: https://logfire-us.pydantic.dev/devq-ai/pfinni")