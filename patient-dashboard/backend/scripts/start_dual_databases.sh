#!/bin/bash
# Created: 2025-08-09T15:10:00-06:00
# Script to start both DEV and PRD SurrealDB instances

echo "Starting dual database setup..."

# Kill any existing SurrealDB processes
echo "Stopping existing SurrealDB processes..."
pkill -f surreal

# Wait for processes to stop
sleep 2

# Start DEV database on port 8000
echo "Starting DEV database on port 8000..."
surreal start --log debug --user root --pass root file:dev_database.db --bind 0.0.0.0:8000 &
DEV_PID=$!

# Wait for DEV to start
sleep 3

# Start PRD database on port 8080
echo "Starting PRD database on port 8080..."
surreal start --log debug --user root --pass root file:prd_database.db --bind 0.0.0.0:8080 &
PRD_PID=$!

# Wait for PRD to start
sleep 3

echo "DEV database PID: $DEV_PID (port 8000)"
echo "PRD database PID: $PRD_PID (port 8080)"

echo "Both databases started successfully!"