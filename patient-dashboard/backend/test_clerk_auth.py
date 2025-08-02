#!/usr/bin/env python3
"""Test Clerk authentication directly"""

import asyncio
import httpx
from datetime import datetime

# Your actual Clerk user ID when logged in
# You can find this in the browser console by running: 
# await window.Clerk.user.id

async def test_auth():
    """Test authentication with backend"""
    
    # First, let's check if the backend is running
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8001/health")
            print(f"Backend health check: {response.status_code}")
        except Exception as e:
            print(f"Backend not reachable: {e}")
            return
    
    # Now let's test without auth
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8001/api/v1/dashboard/stats")
        print(f"\nWithout auth - Status: {response.status_code}")
        print(f"Response: {response.text}")
    
    # Test with a dummy token to see the error
    headers = {
        "Authorization": "Bearer dummy_token"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8001/api/v1/dashboard/stats",
            headers=headers
        )
        print(f"\nWith dummy token - Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    print("Testing Clerk Authentication")
    print("=" * 50)
    asyncio.run(test_auth())
    
    print("\n\nTo get your actual Clerk token:")
    print("1. Open browser console (F12)")
    print("2. Run: await window.Clerk.session.getToken()")
    print("3. Copy the token and test with it")