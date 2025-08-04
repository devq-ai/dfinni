#!/bin/bash
# Setup Cloudflare Tunnel for Patient Dashboard

set -e

echo "🚀 Setting up Cloudflare Tunnel for Patient Dashboard"

# Check if cloudflared is installed
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared is not installed. Please install it first:"
    echo "   brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

# Variables
TUNNEL_NAME="pfinni-dashboard"
FRONTEND_DOMAIN="patient-dashboard.memorial-hc.com"
API_DOMAIN="api.patient-dashboard.memorial-hc.com"

# Check if already logged in
if ! cloudflared tunnel list &> /dev/null; then
    echo "📝 Please login to Cloudflare:"
    cloudflared tunnel login
fi

# Check if tunnel already exists
if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
    echo "⚠️  Tunnel '$TUNNEL_NAME' already exists"
    read -p "Do you want to delete and recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cloudflared tunnel delete "$TUNNEL_NAME"
    else
        echo "Using existing tunnel"
        TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
    fi
fi

# Create tunnel if it doesn't exist
if [ -z "$TUNNEL_ID" ]; then
    echo "🔧 Creating tunnel '$TUNNEL_NAME'..."
    cloudflared tunnel create "$TUNNEL_NAME"
    TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
fi

echo "✅ Tunnel ID: $TUNNEL_ID"

# Create config directory if it doesn't exist
mkdir -p ~/.cloudflared

# Copy and update config file
echo "📄 Creating tunnel configuration..."
cp cloudflare-config.yml ~/.cloudflared/config.yml
sed -i.bak "s/<TUNNEL_ID>/$TUNNEL_ID/g" ~/.cloudflared/config.yml
rm ~/.cloudflared/config.yml.bak

# Create DNS routes
echo "🌐 Creating DNS routes..."
cloudflared tunnel route dns "$TUNNEL_NAME" "$FRONTEND_DOMAIN" || echo "Route may already exist"
cloudflared tunnel route dns "$TUNNEL_NAME" "$API_DOMAIN" || echo "Route may already exist"

# Create systemd service (Linux) or LaunchAgent (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🍎 Setting up LaunchAgent for macOS..."
    
    PLIST_FILE="$HOME/Library/LaunchAgents/com.cloudflare.pfinni-dashboard.plist"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cloudflare.pfinni-dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
        <string>$TUNNEL_NAME</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/cloudflared.err</string>
    <key>StandardOutPath</key>
    <string>/tmp/cloudflared.out</string>
</dict>
</plist>
EOF
    
    launchctl load "$PLIST_FILE"
    echo "✅ LaunchAgent created and loaded"
else
    # Linux
    echo "🐧 Setting up systemd service for Linux..."
    sudo cloudflared service install
    echo "✅ Systemd service installed"
fi

echo ""
echo "🎉 Cloudflare Tunnel setup complete!"
echo ""
echo "📋 Summary:"
echo "   - Tunnel Name: $TUNNEL_NAME"
echo "   - Tunnel ID: $TUNNEL_ID"
echo "   - Frontend URL: https://$FRONTEND_DOMAIN"
echo "   - API URL: https://$API_DOMAIN"
echo ""
echo "🚀 To start the tunnel manually:"
echo "   cloudflared tunnel run $TUNNEL_NAME"
echo ""
echo "📊 To check tunnel status:"
echo "   cloudflared tunnel info $TUNNEL_NAME"
echo ""
echo "🛑 To stop the tunnel service:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   launchctl unload $HOME/Library/LaunchAgents/com.cloudflare.pfinni-dashboard.plist"
else
    echo "   sudo systemctl stop cloudflared"
fi