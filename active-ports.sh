#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
GRAY='\033[0;90m'
NC='\033[0m'

echo "=== ALL Active Localhost Ports ==="
echo ""

# First, get unique ports and their PIDs
declare -a ports_info

# Get all listening ports
while IFS= read -r line; do
    # Extract port
    port=$(echo "$line" | awk '{print $9}' | grep -oE '[0-9]+$')
    
    # Skip if no valid port
    if [[ -z "$port" ]] || ! [[ "$port" =~ ^[0-9]+$ ]]; then
        continue
    fi
    
    # Get PID for this port
    pid=$(lsof -ti:$port | head -1)
    
    # Skip if no PID
    if [[ -z "$pid" ]]; then
        continue
    fi
    
    # Get process name and command
    process_name=$(ps -p $pid -o comm= 2>/dev/null | xargs basename 2>/dev/null || echo "Unknown")
    full_cmd=$(ps -p $pid -o args= 2>/dev/null | cut -c1-50 || echo "Unknown")
    
    # Store the info
    ports_info+=("$port|$pid|$process_name|$full_cmd")
    
done < <(lsof -iTCP -sTCP:LISTEN -P -n | grep -E '(127\.0\.0\.1|::1)')

# Sort and display unique ports
printf "%s\n" "${ports_info[@]}" | sort -u -t'|' -k1,1n | while IFS='|' read -r port pid process cmd; do
    # Color code by port range
    if [[ $port -lt 1024 ]]; then
        color=$YELLOW  # System ports
    else
        color=$GREEN   # User ports
    fi
    
    printf "${color}%-6s${NC} | PID: %-7s | %-25s | ${GRAY}%s${NC}\n" \
           "$port" "$pid" "$process" "$cmd"
done

echo ""
echo "Total active localhost ports: ${#ports_info[@]}"
echo ""
echo "${YELLOW}Yellow${NC} = System ports (< 1024)"
echo "${GREEN}Green${NC} = User ports (>= 1024)"