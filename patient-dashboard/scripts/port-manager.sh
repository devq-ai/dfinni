#!/bin/bash

# Port Manager - Service Discovery and Management Tool
# This script helps identify and manage services running on localhost

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display service status
display_services() {
    echo -e "${BLUE}=== Patient Dashboard Service Status ===${NC}"
    echo ""
    
    # Define expected services
    declare -A services=(
        ["3000"]="Frontend (Next.js)"
        ["8000"]="Backend API (FastAPI)"
        ["8001"]="Backend API (FastAPI) - Alternative"
        ["8080"]="SurrealDB"
        ["9090"]="Prometheus"
        ["3001"]="Grafana"
    )
    
    # Check each port
    for port in "${!services[@]}"; do
        service_name="${services[$port]}"
        if lsof -ti:$port >/dev/null 2>&1; then
            pid=$(lsof -ti:$port)
            process=$(ps -p $pid -o comm= 2>/dev/null || echo "Unknown")
            echo -e "${GREEN}✓${NC} Port $port: ${GREEN}$service_name${NC} (PID: $pid, Process: $process)"
        else
            echo -e "${RED}✗${NC} Port $port: ${RED}$service_name${NC} - Not running"
        fi
    done
    
    echo ""
    echo -e "${BLUE}=== Other Active Localhost Services ===${NC}"
    # Find all services on localhost (127.0.0.1 and ::1)
    other_ports=$(lsof -iTCP -sTCP:LISTEN -P -n | grep -E '(127\.0\.0\.1|::1)' | awk '{print $9}' | cut -d: -f2 | sort -nu)
    
    for port in $other_ports; do
        if [[ ! " ${!services[@]} " =~ " ${port} " ]]; then
            pid=$(lsof -ti:$port)
            process=$(ps -p $pid -o comm= 2>/dev/null || echo "Unknown")
            echo -e "${YELLOW}?${NC} Port $port: Unknown service (PID: $pid, Process: $process)"
        fi
    done
}

# Function to start services
start_services() {
    echo -e "${BLUE}Starting Patient Dashboard services...${NC}"
    
    # Start SurrealDB if not running
    if ! lsof -ti:8080 >/dev/null 2>&1; then
        echo "Starting SurrealDB..."
        cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard
        docker-compose up -d surrealdb
    fi
    
    # Start Backend if not running
    if ! lsof -ti:8000 >/dev/null 2>&1 && ! lsof -ti:8001 >/dev/null 2>&1; then
        echo "Starting Backend API..."
        cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/backend
        ./start_server.sh &
        sleep 3
    fi
    
    # Start Frontend if not running
    if ! lsof -ti:3000 >/dev/null 2>&1; then
        echo "Starting Frontend..."
        cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/frontend
        npm run dev &
        sleep 5
    fi
}

# Function to stop services
stop_services() {
    echo -e "${BLUE}Stopping Patient Dashboard services...${NC}"
    
    # Stop Frontend
    if lsof -ti:3000 >/dev/null 2>&1; then
        echo "Stopping Frontend..."
        kill $(lsof -ti:3000) 2>/dev/null
    fi
    
    # Stop Backend
    if lsof -ti:8000 >/dev/null 2>&1; then
        echo "Stopping Backend on 8000..."
        kill $(lsof -ti:8000) 2>/dev/null
    fi
    if lsof -ti:8001 >/dev/null 2>&1; then
        echo "Stopping Backend on 8001..."
        kill $(lsof -ti:8001) 2>/dev/null
    fi
    
    # Stop Docker services
    cd /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard
    docker-compose down
}

# Function to show detailed port info
port_info() {
    local port=$1
    echo -e "${BLUE}=== Detailed info for port $port ===${NC}"
    
    if lsof -ti:$port >/dev/null 2>&1; then
        lsof -i:$port
    else
        echo "No service running on port $port"
    fi
}

# Function to free a port
free_port() {
    local port=$1
    echo -e "${YELLOW}Freeing port $port...${NC}"
    
    if lsof -ti:$port >/dev/null 2>&1; then
        kill $(lsof -ti:$port) 2>/dev/null
        echo -e "${GREEN}Port $port freed${NC}"
    else
        echo "Port $port is already free"
    fi
}

# Main menu
show_menu() {
    echo -e "${BLUE}=== Port Manager ===${NC}"
    echo "1. Show all services"
    echo "2. Start all services"
    echo "3. Stop all services"
    echo "4. Show port details"
    echo "5. Free a specific port"
    echo "6. Continuous monitoring"
    echo "7. Exit"
    echo ""
    read -p "Select an option: " choice
    
    case $choice in
        1) display_services ;;
        2) start_services; sleep 2; display_services ;;
        3) stop_services; sleep 2; display_services ;;
        4) 
            read -p "Enter port number: " port
            port_info $port
            ;;
        5) 
            read -p "Enter port number to free: " port
            free_port $port
            ;;
        6) 
            echo "Starting continuous monitoring (Ctrl+C to stop)..."
            while true; do
                clear
                display_services
                sleep 5
            done
            ;;
        7) exit 0 ;;
        *) echo "Invalid option" ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
    show_menu
}

# Check requirements
if ! command_exists lsof; then
    echo -e "${RED}Error: lsof command not found. Please install it first.${NC}"
    exit 1
fi

# Run based on arguments or show menu
if [ "$1" == "status" ]; then
    display_services
elif [ "$1" == "start" ]; then
    start_services
elif [ "$1" == "stop" ]; then
    stop_services
elif [ "$1" == "monitor" ]; then
    while true; do
        clear
        display_services
        sleep 5
    done
else
    clear
    show_menu
fi