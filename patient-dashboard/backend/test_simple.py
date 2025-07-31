#!/usr/bin/env python3
"""Simple test to check if server is working"""

import requests

try:
    response = requests.get("http://localhost:8001/health", timeout=5)
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Server not responding: {e}")