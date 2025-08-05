#!/bin/bash

echo "Testing Patient Endpoints"
echo "========================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8001/api/v1"

# First, login to get access token
echo -e "\n1. Logging in to get access token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=Admin123!")

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}Failed to get access token${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}Successfully logged in!${NC}"

# Test listing patients
echo -e "\n2. Testing list patients..."
curl -s -X GET "$BASE_URL/patients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

# Test getting a specific patient (if any exist)
echo -e "\n3. Testing get patient by ID..."
# Try to get patient sarah_anderson
curl -s -X GET "$BASE_URL/patients/sarah_anderson" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

# Test creating a new patient
echo -e "\n4. Testing create patient..."
NEW_PATIENT=$(cat <<EOF
{
  "first_name": "Test",
  "last_name": "Patient",
  "middle_name": "Middle",
  "date_of_birth": "1990-01-01",
  "email": "test.patient@example.com",
  "phone": "512-555-1234",
  "ssn": "123-45-6789",
  "address": {
    "street": "123 Test St",
    "city": "Austin",
    "state": "TX",
    "zip_code": "78701"
  },
  "insurance": {
    "member_id": "TEST123456",
    "company": "Test Insurance Co",
    "plan_type": "PPO",
    "group_number": "TEST001",
    "effective_date": "2025-01-01"
  },
  "status": "Active",
  "risk_level": "Low"
}
EOF
)

CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/patients/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$NEW_PATIENT")

echo "$CREATE_RESPONSE" | python3 -m json.tool

# Extract patient ID if creation was successful
PATIENT_ID=$(echo $CREATE_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', ''))" 2>/dev/null || echo "")

if [ ! -z "$PATIENT_ID" ]; then
    echo -e "${GREEN}Patient created successfully with ID: $PATIENT_ID${NC}"
    
    # Test updating the patient
    echo -e "\n5. Testing update patient..."
    UPDATE_DATA=$(cat <<EOF
{
  "phone": "512-555-9999",
  "status": "Onboarding"
}
EOF
)
    
    curl -s -X PUT "$BASE_URL/patients/$PATIENT_ID" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$UPDATE_DATA" | python3 -m json.tool
    
    # Test adding a note
    echo -e "\n6. Testing add patient note..."
    curl -s -X POST "$BASE_URL/patients/$PATIENT_ID/notes" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{"note": "Test note for patient"}' | python3 -m json.tool
fi

# Test advanced search
echo -e "\n7. Testing advanced search..."
curl -s -X GET "$BASE_URL/patients/search/advanced?first_name=Sarah" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

# Test filtering
echo -e "\n8. Testing filtered list (Active patients)..."
curl -s -X GET "$BASE_URL/patients/?status=Active" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo -e "\n${GREEN}Patient endpoint tests completed!${NC}"