#!/bin/bash
# Created: 2025-08-09T15:10:00-06:00
# Update Cloudflare tunnel to point to PRD backend on port 8002

echo "Updating Cloudflare tunnel configuration..."
echo "The tunnel should point to http://localhost:8002 for production backend"
echo ""
echo "Manual steps required:"
echo "1. Stop current cloudflared process: pkill -f cloudflared"
echo "2. Update tunnel configuration to point to localhost:8002"
echo "3. Restart cloudflared tunnel"
echo ""
echo "Or use this command if you have the tunnel config file:"
echo "cloudflared tunnel run --url http://localhost:8002"