#!/usr/bin/env python3
"""Test security headers implementation."""
import requests
import json
from tabulate import tabulate

# Test endpoint
BASE_URL = "http://localhost:8001"

def test_security_headers():
    """Test if security headers are properly set."""
    
    print("Testing Security Headers...")
    print("-" * 80)
    
    # Make a request to the health endpoint
    response = requests.get(f"{BASE_URL}/health")
    
    # Expected security headers
    expected_headers = {
        "Content-Security-Policy": "Expected",
        "Strict-Transport-Security": "Expected", 
        "X-Frame-Options": "Expected",
        "X-Content-Type-Options": "Expected",
        "X-XSS-Protection": "Expected",
        "Referrer-Policy": "Expected",
        "Permissions-Policy": "Expected",
        "X-HIPAA-Compliance": "Expected",
        "X-Data-Classification": "Expected"
    }
    
    # Check headers
    results = []
    for header, expected in expected_headers.items():
        actual = response.headers.get(header, "Missing")
        status = "✅" if actual != "Missing" else "❌"
        results.append([header, status, actual[:50] + "..." if len(str(actual)) > 50 else actual])
    
    # Print results
    print(tabulate(results, headers=["Header", "Status", "Value"], tablefmt="grid"))
    
    # Server header check
    server_header = response.headers.get("Server")
    print(f"\nServer Header: {'❌ Present' if server_header else '✅ Removed'}")
    if server_header:
        print(f"  Value: {server_header}")
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.json()}")

if __name__ == "__main__":
    test_security_headers()