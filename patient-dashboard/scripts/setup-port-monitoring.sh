#!/bin/bash

# Setup script for port monitoring solutions

echo "Patient Dashboard Port Monitoring Setup"
echo "======================================"
echo ""
echo "This script will set up port monitoring for your development environment."
echo ""

# Create aliases for easy access
SHELL_RC="$HOME/.zshrc"
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

echo "Adding aliases to $SHELL_RC..."

# Add aliases if they don't exist
if ! grep -q "alias ports=" "$SHELL_RC"; then
    cat >> "$SHELL_RC" << 'EOF'

# Patient Dashboard Port Management
alias ports='/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/scripts/port-manager.sh status'
alias ports-start='/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/scripts/port-manager.sh start'
alias ports-stop='/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/scripts/port-manager.sh stop'
alias ports-monitor='/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/scripts/port-manager.sh monitor'
alias service-dashboard='python3 /Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/scripts/service-dashboard.py'

# Quick port check function
whats-on-port() {
    if [ -z "$1" ]; then
        echo "Usage: whats-on-port <port_number>"
        return 1
    fi
    lsof -i :$1
}

# Kill process on port
kill-port() {
    if [ -z "$1" ]; then
        echo "Usage: kill-port <port_number>"
        return 1
    fi
    lsof -ti:$1 | xargs kill -9
}
EOF
    echo "✓ Aliases added"
else
    echo "✓ Aliases already exist"
fi

# Create a launch agent for continuous monitoring (optional)
LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
LAUNCH_AGENT_PLIST="$LAUNCH_AGENT_DIR/com.patientdashboard.portmonitor.plist"

mkdir -p "$LAUNCH_AGENT_DIR"

cat > "$LAUNCH_AGENT_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.patientdashboard.portmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/dionedge/devqai/pfinni_dashboard/patient-dashboard/scripts/service-dashboard.py</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/portmonitor.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/portmonitor.error.log</string>
</dict>
</plist>
EOF

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Available commands:"
echo "  ports           - Show status of all services"
echo "  ports-start     - Start all services"
echo "  ports-stop      - Stop all services"
echo "  ports-monitor   - Continuous monitoring"
echo "  service-dashboard - Web-based dashboard (http://localhost:8888)"
echo "  whats-on-port <port> - Check what's running on a specific port"
echo "  kill-port <port>     - Kill process on a specific port"
echo ""
echo "To use the service dashboard as a background service:"
echo "  launchctl load $LAUNCH_AGENT_PLIST"
echo ""
echo "Please run: source $SHELL_RC"
echo "Or restart your terminal to use the new commands."