#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' /Users/dionedge/devqai/.env | xargs)

# Navigate to backend directory
cd "$(dirname "$0")/.."

# Start the backend server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload