#!/bin/bash
# Load environment variables and run the backend

# Source the .env file
export $(grep -v '^#' /Users/dionedge/devqai/pfinni/.env | xargs)

# Ensure logfire token is set
export LOGFIRE_TOKEN="${LOGFIRE_WRITE_TOKEN:-$LOGFIRE_TOKEN}"

# Run the command passed as arguments
exec "$@"