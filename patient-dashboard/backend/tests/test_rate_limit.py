"""
Test rate limiting functionality.
"""
import asyncio
import httpx
import time
from typing import List, Dict


async def test_endpoint(client: httpx.AsyncClient, endpoint: str, headers: Dict = None) -> Dict:
    """Test a single endpoint."""
    try:
        response = await client.get(endpoint, headers=headers)
        return {
            "status": response.status_code,
            "headers": dict(response.headers),
            "endpoint": endpoint
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "endpoint": endpoint
        }


async def test_rate_limits():
    """Test rate limiting on various endpoints."""
    base_url = "http://localhost:8000"
    
    # Test endpoints
    test_cases = [
        {
            "name": "Health endpoint (should not be rate limited)",
            "endpoint": "/health",
            "requests": 20,
            "expect_limited": False
        },
        {
            "name": "Users endpoint",
            "endpoint": "/api/v1/users",
            "requests": 110,  # Over the 100/minute limit
            "expect_limited": True
        },
        {
            "name": "Auth login endpoint (strict limit)",
            "endpoint": "/api/v1/auth/login",
            "requests": 10,  # Should hit the 5/5min limit
            "expect_limited": True
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for test_case in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {test_case['name']}")
            print(f"Endpoint: {test_case['endpoint']}")
            print(f"Requests: {test_case['requests']}")
            print(f"{'='*60}")
            
            results = []
            rate_limited = False
            
            # Send requests
            for i in range(test_case['requests']):
                result = await test_endpoint(client, f"{base_url}{test_case['endpoint']}")
                
                # Check if rate limited
                if result['status'] == 429:
                    rate_limited = True
                    print(f"\nRate limited at request #{i+1}")
                    if 'headers' in result:
                        print(f"Rate limit headers:")
                        for header, value in result['headers'].items():
                            if header.startswith('x-ratelimit'):
                                print(f"  {header}: {value}")
                    break
                
                # Print progress
                if (i + 1) % 10 == 0:
                    print(f"  Sent {i+1} requests...")
                
                results.append(result)
                
                # Small delay to simulate real usage
                await asyncio.sleep(0.1)
            
            # Verify results
            if test_case['expect_limited'] and not rate_limited:
                print(f"❌ FAILED: Expected rate limiting but none occurred")
            elif not test_case['expect_limited'] and rate_limited:
                print(f"❌ FAILED: Unexpected rate limiting")
            else:
                print(f"✅ PASSED: Rate limiting behaved as expected")
            
            # Show summary
            status_counts = {}
            for result in results:
                status = result['status']
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"\nResponse summary:")
            for status, count in status_counts.items():
                print(f"  {status}: {count} requests")
            
            # Wait between test cases
            if rate_limited:
                print(f"\nWaiting 10 seconds before next test...")
                await asyncio.sleep(10)


async def test_rate_limit_headers():
    """Test that rate limit headers are properly set."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("\n" + "="*60)
        print("Testing rate limit headers")
        print("="*60)
        
        # Make a single request
        response = await client.get(f"{base_url}/api/v1/users")
        
        print(f"Status: {response.status_code}")
        print("\nRate limit headers:")
        
        expected_headers = [
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset",
            "x-ratelimit-window"
        ]
        
        for header in expected_headers:
            value = response.headers.get(header)
            if value:
                print(f"  {header}: {value}")
            else:
                print(f"  {header}: NOT FOUND")


async def test_distributed_rate_limiting():
    """Test that rate limiting works across multiple clients."""
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/users"
    
    print("\n" + "="*60)
    print("Testing distributed rate limiting")
    print("="*60)
    
    # Simulate multiple clients with same IP
    async def client_requests(client_id: int, num_requests: int):
        async with httpx.AsyncClient() as client:
            limited = False
            for i in range(num_requests):
                response = await client.get(f"{base_url}{endpoint}")
                if response.status_code == 429:
                    print(f"  Client {client_id}: Rate limited at request {i+1}")
                    limited = True
                    break
            
            if not limited:
                print(f"  Client {client_id}: Completed all {num_requests} requests")
            
            return limited
    
    # Run multiple clients concurrently
    tasks = []
    num_clients = 5
    requests_per_client = 25
    
    print(f"Running {num_clients} clients with {requests_per_client} requests each")
    print(f"Total requests: {num_clients * requests_per_client} (should exceed 100/min limit)")
    
    for i in range(num_clients):
        task = client_requests(i+1, requests_per_client)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    limited_count = sum(1 for r in results if r)
    print(f"\nResults: {limited_count}/{num_clients} clients were rate limited")
    
    if limited_count > 0:
        print("✅ PASSED: Distributed rate limiting is working")
    else:
        print("❌ FAILED: No clients were rate limited")


if __name__ == "__main__":
    print("Rate Limiting Test Suite")
    print("Make sure the backend is running on http://localhost:8000")
    
    asyncio.run(test_rate_limits())
    asyncio.run(test_rate_limit_headers())
    asyncio.run(test_distributed_rate_limiting())