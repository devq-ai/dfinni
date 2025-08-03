#!/bin/bash

# Define your services and their expected ports (compatible with older bash)
PORTS="3000 8000 8001 8080 9090 3001"
declare -a PORT_NAMES
PORT_NAMES[3000]="Frontend (Next.js)"
PORT_NAMES[8000]="Backend API (FastAPI)"
PORT_NAMES[8001]="Backend API (Alt)"
PORT_NAMES[8080]="SurrealDB"
PORT_NAMES[9090]="Prometheus"
PORT_NAMES[3001]="Grafana"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Localhost Services Status ==="
echo ""

# Check expected services
echo "PREDEFINED SERVICES (these are what we expect):"
echo "-----------------------------------------------"
for port in $PORTS; do
    service="${PORT_NAMES[$port]}"
    if lsof -ti:$port >/dev/null 2>&1; then
        # Get just the first PID if multiple processes
        pid=$(lsof -ti:$port | head -1)
        # Get the actual process name
        process=$(ps -p $pid -o comm= 2>/dev/null || echo "Unknown")
        echo -e "${GREEN}✓ Running${NC} - Port $port: $service"
        echo "             Actual process: $process (PID: $pid)"
    else
        echo -e "${RED}✗ Stopped${NC} - Port $port: $service"
    fi
done

echo ""
echo "OTHER SERVICES (not in our predefined list):"
echo "-------------------------------------------"

# Find other services on localhost
lsof -iTCP -sTCP:LISTEN -P -n | grep -E '(127\.0\.0\.1|::1)' | awk '{print $9}' | cut -d: -f2 | sort -nu | while read port; do
    # Skip if it's empty or not a number
    if [[ -z "$port" ]] || ! [[ "$port" =~ ^[0-9]+$ ]]; then
        continue
    fi
    
    # Check if this port is NOT in our predefined list
    is_predefined=0
    for p in $PORTS; do
        if [[ "$p" == "$port" ]]; then
            is_predefined=1
            break
        fi
    done
    
    if [[ $is_predefined -eq 0 ]] && [ "$port" -gt 1024 ]; then
        pid=$(lsof -ti:$port | head -1)
        process=$(ps -p $pid -o comm= 2>/dev/null || echo "Unknown")
        echo -e "${YELLOW}? Active${NC} - Port $port: $process (PID: $pid)"
    fi
done

echo ""