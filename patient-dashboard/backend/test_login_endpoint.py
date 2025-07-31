"""Test the login endpoint directly to see the error"""
import requests
import json

# Test data
login_data = {
    "username": "admin@example.com",
    "password": "password123"
}

# Test the login endpoint
response = requests.post(
    "http://localhost:8001/api/v1/auth/login",
    data=login_data  # Form data for OAuth2
)

print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Response: {response.text}")

# Try with JSON content type
print("\n--- Testing with JSON ---")
response2 = requests.post(
    "http://localhost:8001/api/v1/auth/login",
    json={"username": "admin@example.com", "password": "password123"},
    headers={"Content-Type": "application/json"}
)

print(f"Status Code: {response2.status_code}")
print(f"Response: {response2.text}")

# Check if the server is running
print("\n--- Server Health Check ---")
try:
    health = requests.get("http://localhost:8001/health")
    print(f"Health check: {health.status_code} - {health.text}")
except Exception as e:
    print(f"Health check failed: {e}")
    
# Check API docs
print("\n--- API Documentation ---")
try:
    docs = requests.get("http://localhost:8001/docs")
    print(f"API docs available: {docs.status_code == 200}")
except Exception as e:
    print(f"API docs check failed: {e}")