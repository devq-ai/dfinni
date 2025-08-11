#!/bin/bash
# PFINNI Dashboard - Stop All Local Services

echo "🛑 Stopping PFINNI Dashboard Services..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Stop Frontend (port 3000)
echo -e "${YELLOW}Stopping Frontend...${NC}"
if lsof -ti:3000 >/dev/null 2>&1; then
    kill -9 $(lsof -ti:3000) 2>/dev/null
    echo -e "${GREEN}✓ Frontend stopped${NC}"
else
    echo "Frontend not running"
fi

# Stop Backend (port 8001)
echo -e "${YELLOW}Stopping Backend API...${NC}"
if lsof -ti:8001 >/dev/null 2>&1; then
    kill -9 $(lsof -ti:8001) 2>/dev/null
    echo -e "${GREEN}✓ Backend API stopped${NC}"
else
    echo "Backend API not running"
fi

# Stop SurrealDB (port 8000)
echo -e "${YELLOW}Stopping SurrealDB...${NC}"
if lsof -ti:8000 >/dev/null 2>&1; then
    kill -9 $(lsof -ti:8000) 2>/dev/null
    echo -e "${GREEN}✓ SurrealDB stopped${NC}"
else
    echo "SurrealDB not running"
fi

# Kill any remaining Python/Node processes
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "next dev" 2>/dev/null

echo -e "\n${GREEN}✅ All services stopped${NC}"