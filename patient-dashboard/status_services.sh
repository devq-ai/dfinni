#!/bin/bash
# Updated: 2025-07-31T13:30:00-06:00
# Check status of all services

echo "📊 Patient Dashboard Service Status"
echo "========================================"

# Check SurrealDB
echo -n "1. SurrealDB (port 8000):     "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check Backend API
echo -n "2. Backend API (port 8001):   "
if curl -s http://localhost:8001/api/v1/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

# Check Frontend
echo -n "3. Frontend (port 3000):      "
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

echo "========================================"

# Show running processes
echo ""
echo "📋 Running Processes:"
echo "-------------------"

# Check for SurrealDB process
if pgrep -f surreal > /dev/null; then
    echo "SurrealDB:"
    ps aux | grep -E "surreal.*8000" | grep -v grep | head -1
fi

# Check for Backend process
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo ""
    echo "Backend API:"
    ps aux | grep -E "uvicorn.*app.main:app" | grep -v grep | head -1
fi

# Check for Frontend process
if pgrep -f "next dev" > /dev/null; then
    echo ""
    echo "Frontend:"
    ps aux | grep -E "next dev" | grep -v grep | head -1
fi

echo ""