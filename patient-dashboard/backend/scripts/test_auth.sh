#!/bin/bash

echo "Testing Authentication Endpoints"
echo "================================"

# Base URL
BASE_URL="http://localhost:8001/api/v1"

# Test 1: Register a new user
echo -e "\n1. Testing user registration..."
curl -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "ADMIN"
  }' | jq .

# Test 2: Login with the created user
echo -e "\n2. Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!")

echo "$LOGIN_RESPONSE" | jq .

# Extract the access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$ACCESS_TOKEN" != "null" ]; then
    echo -e "\nAccess token obtained successfully!"
    
    # Test 3: Get current user info
    echo -e "\n3. Testing get current user..."
    curl -X GET "$BASE_URL/auth/me" \
      -H "Authorization: Bearer $ACCESS_TOKEN" | jq .
    
    # Test 4: Test refresh token
    REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.refresh_token')
    echo -e "\n4. Testing token refresh..."
    curl -X POST "$BASE_URL/auth/refresh" \
      -H "Content-Type: application/json" \
      -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" | jq .
else
    echo -e "\nFailed to obtain access token!"
fi