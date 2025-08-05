## Deployment Strategy: Cloudflare + Local SurrealDB

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  GitHub Repo    │────▶│ GitHub Actions   │────▶│  Cloudflare     │
│                 │     │ (Build & Deploy) │     │  Pages/Workers  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Mac Studio     │◀────│ Cloudflare       │◀────│  User Browser   │
│  (SurrealDB)    │     │ Tunnel           │     │  devq.ai        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## Requirements
### Local Network Settings
- The good news is that Cloudflare Tunnel abstracts away most networking complexities:
    - 1. Tunnel handles NAT: Your router's NAT doesn't matter
    - 2. No port forwarding needed: Tunnel creates  utbound connection
    - 3. IP changes don't break it: Tunnel reconnects automatically
    - 4. IPv4/IPv6 agnostic: Tunnel works with both
- Best Practices for Your Setup
    - 1. Keep DHCP with manual address: This is ideal for your setup
    - 2. Don't expose services directly: Let Cloudflare Tunnel handle it
    - 3. Monitor tunnel status: Add to your monitoring cloudflared lared tunnel info
    - 4. Test failover:
    ```
    # Test what happens when network drops
    sudo ifconfig en0 down
    sleep 10
    sudo ifconfig en0 up
    # Tunnel should auto-reconnect
    ```
### 1. Domain & DNS
- [x] Domain: devq.ai (already purchased)
- [ ] Cloudflare account (free tier)
- [ ] Domain added to Cloudflare DNS
### 2. Local Mac Studio
- [x] SurrealDB installed
- [ ] Cloudflared installed (`brew install cloudflare/cloudflare/cloudflared`)
- [ ] Static storage location for database
- [ ] Startup scripts for auto-launch
### 3. GitHub Repository
- [x] Source code repository
- [ ] GitHub Actions enabled
- [ ] Secrets configured
### 4. Cloudflare Services
- [ ] Cloudflare Pages for frontend
- [ ] Cloudflare Workers for backend API
- [ ] Cloudflare Tunnel for SurrealDB connection

## Step-by-Step Implementation
### Phase 1: Cloudflare Setup
#### 1.1 Add Domain to Cloudflare
```bash
# Sign up at cloudflare.com
# Add devq.ai domain
# Update nameservers at your registrar to Cloudflare's
```
#### 1.2 Get API Tokens
- 1. Go to Cloudflare Dashboard → My Profile → API Tokens
- 2. Create Token → Custom Token with permissions:
   - Account: Cloudflare Pages:Edit
   - Account: Cloudflare Workers Scripts:Edit
   - Zone: DNS:Edit for devq.ai

### Phase 2: Local SurrealDB Setup

#### 2.1 Install and Configure SurrealDB
```bash
# Install SurrealDB
brew install surrealdb/tap/surreal

# Create data directory
mkdir -p ~/surrealdb/patient-dashboard

# Create startup script
cat > ~/surrealdb/start-surreal.sh << 'EOF'
#!/bin/bash
surreal start \
  --user root \
  --pass root \
  --bind 0.0.0.0:8000 \
  file://~/surrealdb/patient-dashboard/data.db
EOF

chmod +x ~/surrealdb/start-surreal.sh
```
#### 2.2 Setup Cloudflare Tunnel
```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared
# Login to Cloudflare
cloudflared tunnel login
# Create tunnel
cloudflared tunnel create patient-dashboard-db
# Get tunnel ID (save this!)
cloudflared tunnel list
# Create config file
cat > ~/.cloudflared/config.yml << EOF
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /Users dionedge/.cloudflared/<YOUR-TUNNEL-ID>.json
ingress:
  - hostname: db.devq.ai
    service: ws://localhost:8000
    originRequest:
      noTLSVerify: true
  - service: http_status:404
EOF
# Create DNS record
cloudflared tunnel route dns patient-dashboard-db db.devq.ai
```
#### 2.3 Auto-start Services
```bash
# Create LaunchAgent for SurrealDB
cat > ~/Library/LaunchAgents/com.devqai.surrealdb.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devqai.surrealdb</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/dionedge/surrealdb/start-surreal.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/surrealdb.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/surrealdb.error.log</string>
</dict>
</plist>
EOF
# Create LaunchAgent for Cloudflare Tunnel
cat > ~/Library/LaunchAgents/com.devqai.cloudflared.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devqai.cloudflared</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF
# Load services
launchctl load ~/Library/LaunchAgents/com.devqai.surrealdb.plist
launchctl load ~/Library/LaunchAgents/com.devqai.cloudflared.plist
```
### Phase 3: Code Updates
#### 3.1 Update Backend Configuration
```python
# patient-dashboard/backend/app/config/settings.py
import os
class Settings(BaseSettings):
    # Update database URL for production
    DATABASE_URL: str = Field(
        default="ws://localhost:8000/rpc",
        env="DATABASE_URL"
    )    
    @property
    def database_url_production(self):
        if self.ENVIRONMENT == "production":
            return "wss://db.devq.ai/rpc"
        return self.DATABASE_URL
```
#### 3.2 Update Frontend Configuration
```typescript
// patient-dashboard/frontend/lib/config.ts
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://api.devq.ai' 
    : 'http://localhost:8001')
```
#### 3.3 Create Health Check Endpoint
```python
# patient-dashboard/backend/app/api/v1/health.py
from fastapi import APIRouter, Response
from app.database.connection import get_database
import asyncio
router = APIRouter()
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db = await get_database()
        # SurrealDB doesn't have a ping, so we'll do a simple query
        result = await asyncio.wait_for(
            db.query("SELECT 1"),
            timeout=5.0
        )       
        return {
            "status": "online",
            "database": "connected",
            "services": {
                "api": "healthy",
                "database": "healthy"
            }
        }
    except asyncio.TimeoutError:
        return Response(
            content='{"status":"offline","database":"timeout"}',
            status_code=503,
            media_type="application/json"
        )
    except Exception as e:
        return Response(
            content=f'{{"status":"offline","database":"error","error":"{str(e)}"}}',
            status_code=503,
            media_type="application/json"
        )
```
### Phase 4: GitHub Actions
#### 4.1 Create Deployment Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - 'patient-dashboard/'
      - '.github/workflows/deploy.yml'
env:
  NODE_VERSION: '20'
  PYTHON_VERSION: '3.12'
jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}          
      - name: Install dependencies
        working-directory: patient-dashboard/frontend
        run: npm ci        
      - name: Build frontend
        working-directory: patient-dashboard/frontend
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: https://api.devq.ai
          NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: ${{ secrets.CLERK_PUBLISHABLE_KEY }}          
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: patient-dashboard
          directory: patient-dashboard/frontend/out
          gitHubToken: ${{ secrets.GITHUB_TOKEN }}
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4      
      - name: Create wrangler.toml
        working-directory: patient-dashboard/backend
        run: |
          cat > wrangler.toml << EOF
          name = "patient-dashboard-api"
          main = "worker.js"
          compatibility_date = "2024-01-01"          
          [vars]
          DATABASE_URL = "wss://db.devq.ai/rpc"
          ENVIRONMENT = "production"          
          [[routes]]
          pattern = "api.devq.ai/*"
          zone_name = "devq.ai"
          EOF          
      - name: Deploy to Cloudflare Workers
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          workingDirectory: patient-dashboard/backend
          secrets: |
            CLERK_SECRET_KEY
            LOGFIRE_TOKEN
```
#### 4.2 Add GitHub Secrets
```bash
# Required secrets in GitHub:
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY
LOGFIRE_TOKEN
```
### Phase 5: DNS Configuration
- In Cloudflare DNS for devq.ai:
```
Type    Name    Content                     Proxy   TTL
A       @       192.0.2.1                   Yes     Auto
CNAME   www     patient-dashboard.pages.dev Yes     Auto
CNAME   api     patient-dashboard.workers.dev Yes    Auto
CNAME   db      <tunnel-id>.cfargotunnel.com Yes    Auto
```
### Phase 6: Update README
```markdown
# Patient Dashboard Demo
<div align="center">
[![Demo Status](https://img.shields.io/endpoint?url=https://api.devq.ai/health&query=$.status&label=Demo%20Status&color=green)](https://devq.ai)
<a href="https://devq.ai">
  <img src="https://img.shields.io/badge/🚀_Launch_Patient_Dashboard-00A3E0?style=for-the-badge&labelColor=000000" alt="Launch Demo">
</a>
</div>
## Demo Access
- URL: [https://devq.ai](https://devq.ai)
- Login: demo@devq.ai / DemoPass123
- Status: Check the badge above
> If the demo is offline, the database server may be temporarily unavailable.
```

## Potential Problems & Solutions
### Problem 1: Mac Studio Offline
- Issue: Demo fails when Mac is off/sleeping
- Solution: 
- Enable "Prevent automatic sleeping" in Energy Saver
- Use `caffeinate -i` to prevent sleep
- Consider UPS for power outages
- Add monitoring alerts
### Problem 2: Dynamic IP Changes
- Issue: Home IP might change
- Solution: Cloudflare Tunnel handles this automatically
### Problem 3: SurrealDB Connection Drops
- Issue: WebSocket connections timeout
- Solution:
```python
# Add connection retry logic
async def get_database_with_retry(retries=3):
    for i in range(retries):
        try:
            return await get_database()
        except Exception as e:
            if i == retries - 1:
                raise
            await asyncio.sleep(1 * (i + 1))
```
### Problem 4: Cloudflare Workers Limitations
- Issue: 10ms CPU time limit, 128MB memory
- Solution: 
- Optimize API responses
- Move heavy processing to background jobs
- Use Cloudflare Workers Paid plan if needed
### Problem 5: CORS Issues
- Issue: Cross-origin requests blocked
- Solution:
```python
# Ensure CORS headers in Workers
headers = {
    'Access-Control-Allow-Origin': 'https://devq.ai',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}
```
### Problem 6: Database Backups
- Issue: Local data loss risk
- Solution:
```bash
# Add to crontab
0 2 * * * /Users/dionedge/surrealdb/backup.sh
# backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
surreal export --conn http://localhost:8000 \
  --user root --pass root \
  --ns patient_dashboard --db patient_dashboard \
  > ~/backups/patient_dashboard_$DATE.sql
# Upload to cloud storage
rclone copy ~/backups/ gdrive:patient-dashboard-backups/
```

## Monitoring & Maintenance
### 1. Setup Monitoring
```bash
# Use UptimeRobot or similar
- Monitor: https://api.devq.ai/health
- Alert: Email/SMS if down
```
### 2. Log Aggregation
```python
# All logs go to Logfire
logfire.configure(
    service_name='patient-dashboard-demo',
    environment='production'
)
```
### 3. Regular Maintenance
- Weekly: Check logs for errors
- Monthly: Update dependencies
- Quarterly: Security audit

## Cost Analysis
### Monthly Costs
- Cloudflare: $0 (Free tier)
- Domain: ~$1/month (annual)
- Mac Studio Power: ~$5-10/month
- Internet: (existing cost)
- Total: ~$6-11/month
### Comparison
- Cloud hosting: $20-100/month
- Savings: $15-90/month

## Security Considerations
- 1. Tunnel Security: Only SurrealDB exposed through tunnel
- 2. Authentication: Clerk handles all auth
- 3. API Security: Rate limiting on Cloudflare
- 4. Database: Local = physical security
- 5. Backups: Encrypted cloud backups
