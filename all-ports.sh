#!/bin/bash

# Get all listening ports (including those on all interfaces)
lsof -iTCP -sTCP:LISTEN -P -n | while read line; do
    # Extract port number from the address field
    port=$(echo "$line" | awk '{print $9}' | grep -oE '[0-9]+$')
    
    # Skip if no valid port
    if [[ -z "$port" ]] || ! [[ "$port" =~ ^[0-9]+$ ]]; then
        continue
    fi    
    # Add to our list
    echo "$port"
done | sort -nu | while read port; do
    # Get the listening process for this port
    pid=$(lsof -iTCP:$port -sTCP:LISTEN -t | head -1)
    if [[ -n "$pid" ]]; then
        process=$(ps -p $pid -o comm= 2>/dev/null | xargs basename 2>/dev/null)
        # Check if it's accessible on localhost
        if lsof -i:$port | grep -qE '(127\.0\.0\.1|localhost|\*)'; then
            # Process is listening, so it's running
            printf "Port %-6s - PID: %-7s - Process: %-20s - Status: Running\n" "$port" "$pid" "$process"
        fi
    fi
done