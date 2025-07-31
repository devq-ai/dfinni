#!/bin/bash
# Updated: 2025-07-31T13:30:00-06:00
# Stop all services for Patient Dashboard

echo "🛑 Stopping Patient Dashboard Services..."
echo "========================================"

# Stop Frontend
echo "1. Stopping Frontend..."
pkill -f "next dev" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Frontend stopped"
else
    echo "   ⚠️  Frontend was not running"
fi

# Stop Backend API
echo "2. Stopping Backend API..."
pkill -f "uvicorn app.main:app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ Backend API stopped"
else
    echo "   ⚠️  Backend API was not running"
fi

# Stop SurrealDB
echo "3. Stopping SurrealDB..."
pkill surreal 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ SurrealDB stopped"
else
    echo "   ⚠️  SurrealDB was not running"
fi

echo ""
echo "========================================"
echo "✅ All services stopped"
echo "========================================"