#!/bin/bash

# MCP HTTP Bridge Startup Script
# Starts the HTTP bridge server that proxies to Zed MCP servers

set -e

# Configuration
BRIDGE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BRIDGE_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PID_FILE="$BRIDGE_DIR/bridge.pid"
LOG_FILE="$BRIDGE_DIR/bridge.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if bridge is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    fi
    return 1  # Not running
}

# Setup virtual environment
setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo_info "Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi

    echo_info "Installing dependencies..."
    "$VENV_DIR/bin/pip" install -r "$BRIDGE_DIR/requirements.txt" --quiet
}

# Start the bridge
start_bridge() {
    if check_running; then
        echo_warn "MCP HTTP Bridge is already running (PID: $(cat "$PID_FILE"))"
        return 0
    fi

    echo_info "Setting up environment..."
    setup_venv

    echo_info "Starting MCP HTTP Bridge..."

    # Load environment variables from pfinni/.env
    if [ -f "$BRIDGE_DIR/../.env" ]; then
        export $(grep -v '^#' "$BRIDGE_DIR/../.env" | xargs)
    fi

    # Start the bridge in background
    cd "$BRIDGE_DIR"
    nohup "$PYTHON_BIN" mcp_http_bridge.py > "$LOG_FILE" 2>&1 &
    local pid=$!

    # Save PID
    echo "$pid" > "$PID_FILE"

    # Wait a moment to check if it started successfully
    sleep 2
    if ps -p "$pid" > /dev/null 2>&1; then
        echo_info "MCP HTTP Bridge started successfully (PID: $pid)"
        echo_info "Server running at: http://localhost:8001"
        echo_info "API docs at: http://localhost:8001/docs"
        echo_info "Log file: $LOG_FILE"
    else
        echo_error "Failed to start MCP HTTP Bridge"
        cat "$LOG_FILE" | tail -20
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop the bridge
stop_bridge() {
    if ! check_running; then
        echo_warn "MCP HTTP Bridge is not running"
        return 0
    fi

    local pid=$(cat "$PID_FILE")
    echo_info "Stopping MCP HTTP Bridge (PID: $pid)..."

    kill "$pid"

    # Wait for process to stop
    local count=0
    while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done

    if ps -p "$pid" > /dev/null 2>&1; then
        echo_warn "Process didn't stop gracefully, force killing..."
        kill -9 "$pid"
    fi

    rm -f "$PID_FILE"
    echo_info "MCP HTTP Bridge stopped"
}

# Show status
status_bridge() {
    if check_running; then
        local pid=$(cat "$PID_FILE")
        echo_info "MCP HTTP Bridge is running (PID: $pid)"
        echo_info "Server URL: http://localhost:8001"

        # Test if server is responding
        if command -v curl >/dev/null 2>&1; then
            if curl -s http://localhost:8001/ > /dev/null; then
                echo_info "Server is responding"
            else
                echo_warn "Server process running but not responding"
            fi
        fi
    else
        echo_warn "MCP HTTP Bridge is not running"
    fi
}

# Show logs
logs_bridge() {
    if [ -f "$LOG_FILE" ]; then
        echo_info "Showing last 50 lines of log file:"
        tail -50 "$LOG_FILE"
    else
        echo_warn "No log file found"
    fi
}

# Test the bridge
test_bridge() {
    if ! check_running; then
        echo_error "Bridge is not running. Start it first with: $0 start"
        return 1
    fi

    echo_info "Testing MCP HTTP Bridge..."

    # Test health endpoint
    if command -v curl >/dev/null 2>&1; then
        echo_info "Testing health endpoint..."
        curl -s http://localhost:8001/ | python3 -m json.tool

        echo_info "Testing servers list..."
        curl -s http://localhost:8001/servers | python3 -m json.tool

        echo_info "Testing sequential thinking tools..."
        curl -s http://localhost:8001/servers/sequential_thinking/tools | python3 -m json.tool
    else
        echo_warn "curl not available, cannot test endpoints"
    fi
}

# Main command handling
case "$1" in
    start)
        start_bridge
        ;;
    stop)
        stop_bridge
        ;;
    restart)
        stop_bridge
        sleep 1
        start_bridge
        ;;
    status)
        status_bridge
        ;;
    logs)
        logs_bridge
        ;;
    test)
        test_bridge
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the MCP HTTP Bridge"
        echo "  stop    - Stop the MCP HTTP Bridge"
        echo "  restart - Restart the MCP HTTP Bridge"
        echo "  status  - Show bridge status"
        echo "  logs    - Show recent log entries"
        echo "  test    - Test bridge endpoints"
        echo ""
        echo "The bridge will be available at http://localhost:8001"
        echo "API documentation at http://localhost:8001/docs"
        exit 1
        ;;
esac
