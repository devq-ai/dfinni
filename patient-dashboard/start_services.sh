#!/bin/bash
# Updated: 2025-07-31T13:30:00-06:00
# Start all services for Patient Dashboard

echo "🚀 Starting Patient Dashboard Services..."
echo "========================================"

# Start SurrealDB
echo "1. Starting SurrealDB on port 8000..."
surreal start --user root --pass root --bind 0.0.0.0:8000 memory > /tmp/surrealdb.log 2>&1 &
sleep 3

# Check if SurrealDB started
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ SurrealDB started successfully"
else
    echo "   ❌ Failed to start SurrealDB"
    echo "   Check /tmp/surrealdb.log for details"
fi

# Start Backend API
echo "2. Starting Backend API on port 8001..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > /tmp/backend.log 2>&1 &
cd ..
sleep 3

# Check if Backend started
if curl -s http://localhost:8001/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend API started successfully"
else
    echo "   ❌ Failed to start Backend API"
    echo "   Check /tmp/backend.log for details"
fi

# Start Frontend
echo "3. Starting Frontend on port 3000..."
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
cd ..
sleep 5

# Check if Frontend started
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend started successfully"
else
    echo "   ❌ Failed to start Frontend"
    echo "   Check /tmp/frontend.log for details"
fi

echo ""
echo "========================================"
echo "📋 Service URLs:"
echo "   Frontend:    http://localhost:3000"
echo "   API Docs:    http://localhost:8001/docs"
echo "   SurrealDB:   ws://localhost:8000/rpc"
echo ""
echo "📝 Logs:"
echo "   SurrealDB:   /tmp/surrealdb.log"
echo "   Backend:     /tmp/backend.log"
echo "   Frontend:    /tmp/frontend.log"
echo ""
echo "To stop all services, run: ./stop_services.sh"
echo "========================================"