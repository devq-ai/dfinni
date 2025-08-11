#!/bin/bash
# PFINNI Dashboard - Quick Local Start Script
# This script starts all services needed for local development

echo "🚀 Starting PFINNI Dashboard Services..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Step 1: Check and start SurrealDB
echo -e "${YELLOW}1. Checking SurrealDB...${NC}"
if check_port 8000; then
    echo -e "${GREEN}✓ SurrealDB is already running on port 8000${NC}"
else
    echo "Starting SurrealDB..."
    surreal start --log debug --user root --pass root memory --bind 0.0.0.0:8000 > surrealdb.log 2>&1 &
    sleep 3
    if check_port 8000; then
        echo -e "${GREEN}✓ SurrealDB started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start SurrealDB${NC}"
        exit 1
    fi
fi

# Step 2: Start Backend
echo -e "${YELLOW}2. Starting Backend API...${NC}"
if check_port 8001; then
    echo -e "${RED}✗ Port 8001 is already in use. Killing existing process...${NC}"
    kill -9 $(lsof -ti:8001) 2>/dev/null
    sleep 2
fi

cd patient-dashboard/backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -q -r requirements.txt

# Start backend with all required environment variables
PFINNI_SURREALDB_URL=ws://localhost:8000/rpc \
PFINNI_SURREALDB_DATABASE=patient_dashboard_dev \
PFINNI_SURREALDB_NAMESPACE=patient_dashboard_dev \
PFINNI_SURREALDB_USERNAME=root \
PFINNI_SURREALDB_PASSWORD=root \
PFINNI_SECRET_KEY=dev-secret-key \
PFINNI_JWT_SECRET_KEY=dev-jwt-key \
PFINNI_ENCRYPTION_KEY=dev-encryption-key \
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 > backend.log 2>&1 &

sleep 5
if check_port 8001; then
    echo -e "${GREEN}✓ Backend API started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start Backend API${NC}"
    echo "Check backend.log for errors"
    exit 1
fi

cd ../..

# Step 3: Start Frontend
echo -e "${YELLOW}3. Starting Frontend...${NC}"
cd patient-dashboard/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend
npm run dev > frontend.log 2>&1 &

sleep 5
if check_port 3000; then
    echo -e "${GREEN}✓ Frontend started successfully${NC}"
else
    echo -e "${RED}✗ Failed to start Frontend${NC}"
    echo "Check frontend.log for errors"
    exit 1
fi

cd ../..

# Success message
echo -e "\n${GREEN}🎉 All services started successfully!${NC}"
echo -e "\n📍 Access Points:"
echo -e "   Frontend:    ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend API: ${GREEN}http://localhost:8001${NC}"
echo -e "   API Docs:    ${GREEN}http://localhost:8001/docs${NC}"
echo -e "\n📧 Demo Login:"
echo -e "   Email:    demo@user.com"
echo -e "   Password: DemoUser2025!Secure"
echo -e "\n💡 To stop all services, run: ${YELLOW}./STOP_LOCAL.sh${NC}"
echo -e "\n📝 Logs are available in:"
echo -e "   - surrealdb.log"
echo -e "   - patient-dashboard/backend/backend.log"
echo -e "   - patient-dashboard/frontend/frontend.log"