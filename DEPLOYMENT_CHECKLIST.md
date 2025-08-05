# 🚀 PFINNI Dashboard Deployment Checklist

## Overview
This checklist guides you through deploying the PFINNI Patient Dashboard to production using Cloudflare (frontend/backend) and your local Mac Studio (database).

**Architecture**: GitHub → Cloudflare Pages/Workers → Cloudflare Tunnel → Mac Studio SurrealDB

---

## Phase 1: Domain & DNS Setup (You Must Do First)

### 1.1 Create Cloudflare Account
- [X] Go to https://cloudflare.com and sign up for free account
- [X] Verify your email address [dion@devq.ai]
### 1.2 Add Domain to Cloudflare
- [X] Click "Add a Site" in Cloudflare dashboard [dashboard.devqi.ai]
- [X] Enter `devq.ai` as your domain
- [X] Select the FREE plan
- [X] Copy the two nameservers Cloudflare provides [ harley.ns.cloudflare.com, ulla.ns.cloudflare.com ]

### 1.3 Update GoDaddy Nameservers
- [X] Log into your GoDaddy account
- [X] Go to Domain Settings for devq.ai
- [X] Change nameservers from GoDaddy to Cloudflare's nameservers
- [X] Save changes (propagation takes 24-48 hours, but we can continue setup)

### 1.4 Get Cloudflare Credentials
- [X] In Cloudflare: Go to My Profile → API Tokens
- [X] Create Token → Custom Token with permissions:
  - [X] Account: Cloudflare Pages:Edit
  - [X] Account: Cloudflare Workers Scripts:Edit 
  - [X] Zone: DNS:Edit for devq.ai
- [X] Save the API Token securely (you'll need it for GitHub)`2NbDZwsYbzH_iEPCF-LmK_tDAD3qHEDdRVNQMMJz`
- [X] Get your Account ID from the Cloudflare dashboard right sidebar
- [X] Save the Account ID (you'll need it for GitHub)
4
---

## Phase 2: External Services Setup (You Must Do)

### 2.1 Production Clerk Keys
- [X] Log into your Clerk Dashboard
- [X] Create a production instance (or switch to production)
- [X] Add `devq.ai` as an allowed domain
- [X] Copy the production `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`=`pk_live_Y2xlcmsuZGV2cS5haSQ`
- [X] Copy the production `CLERK_SECRET_KEY`=`sk_live_7t98vEqf307GvF2aaMGrx4ODmh9SRK4Qju6xDxn4dD`

### 2.2 GitHub Repository Secrets
- [X] Go to your GitHub repository settings
- [X] Navigate to Settings → Secrets and variables → Actions
- [ ] Add the following secrets: 
Is this a Respostory or Envionment Secret or Variable
  - [ ] `CLOUDFLARE_API_TOKEN` (from step 1.4)
  - [ ] `CLOUDFLARE_ACCOUNT_ID` (from step 1.4)
  - [ ] `CLERK_PUBLISHABLE_KEY` (from step 2.1)
  - [ ] `CLERK_SECRET_KEY` (from step 2.1)
  - [ ] `LOGFIRE_TOKEN` (from your Logfire dashboard)

---

## Phase 3: Mac Studio Database Setup (We Do Together) [WHAT DIRECTORY]

### 3.1 Install Required Software
```bash
# Install Cloudflare Tunnel
brew install cloudflare/cloudflare/cloudflared

# Verify SurrealDB is installed
surreal version
2.3.3 for macos on aarch64
```

### 3.2 Create Data Directory Structure
```bash
# Create directory for database files
mkdir -p ~/surrealdb/patient-dashboard

# Create directory for scripts
mkdir -p ~/surrealdb/scripts
```

### 3.3 Create SurrealDB Startup Script
```bash
cat > ~/surrealdb/scripts/start-surreal.sh << 'EOF'
#!/bin/bash
# SurrealDB startup script for PFINNI Dashboard

echo "Starting SurrealDB for Patient Dashboard..."
surreal start \
  --user root \
  --pass $SURREAL_PASS \
  --bind 0.0.0.0:8000 \
  file://~/surrealdb/patient-dashboard/data.db
EOF

chmod +x ~/surrealdb/scripts/start-surreal.sh
```

### 3.4 Cloudflare Tunnel Authentication (You Must Do)
```bash
# Login to Cloudflare (opens browser)
cloudflared tunnel login

# This saves credentials to ~/.cloudflared/
```

### 3.5 Create Cloudflare Tunnel
```bash
# Create the tunnel
cloudflared tunnel create patient-dashboard-db

# Save the Tunnel ID that's displayed!
# It will look like: 6ff42ae2-765d-4adf-8112-31c55c1551ef

# List tunnels to confirm
cloudflared tunnel list
```

### 3.6 Configure Tunnel
```bash
# Create config file (replace <YOUR-TUNNEL-ID> with actual ID)
cat > ~/.cloudflared/config.yml << EOF
tunnel: <YOUR-TUNNEL-ID>
credentials-file: /Users/dionedge/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: db.devq.ai
    service: ws://localhost:8000
    originRequest:
      noTLSVerify: true
  - service: http_status:404
EOF
```

### 3.7 Create DNS Record for Tunnel
```bash
# This creates a CNAME record in Cloudflare
cloudflared tunnel route dns patient-dashboard-db db.devq.ai
```

### 3.8 Setup Auto-Start Services
```bash
# Create SurrealDB LaunchAgent
cat > ~/Library/LaunchAgents/com.devqai.surrealdb.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.devqai.surrealdb</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/dionedge/surrealdb/scripts/start-surreal.sh</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>SURREAL_PASS</key>
        <string>your-secure-password-here</string>
    </dict>
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

# Create Cloudflare Tunnel LaunchAgent
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
    <key>StandardOutPath</key>
    <string>/tmp/cloudflared.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/cloudflared.error.log</string>
</dict>
</plist>
EOF

# Load the services
launchctl load ~/Library/LaunchAgents/com.devqai.surrealdb.plist
launchctl load ~/Library/LaunchAgents/com.devqai.cloudflared.plist
```

### 3.9 Configure Mac to Stay Awake
- [ ] System Preferences → Energy Saver
- [ ] Check "Prevent your Mac from automatically sleeping when the display is off"
- [ ] Set "Turn display off after" to Never (or longer period)

---

## Phase 4: Code Updates (We Do Together)

### 4.1 Update Backend Configuration
- [ ] Modify `patient-dashboard/backend/app/core/config.py` for production database URL
- [ ] Add production environment detection
- [ ] Update to use `wss://db.devq.ai/rpc` in production

### 4.2 Update Frontend Configuration  
- [ ] Modify `patient-dashboard/frontend/lib/api/config.ts`
- [ ] Set production API URL to `https://api.devq.ai`

### 4.3 Create Health Check Endpoint
- [ ] Add `/api/v1/health` endpoint to backend
- [ ] Include database connectivity check
- [ ] Return appropriate status codes

### 4.4 Create GitHub Actions Workflow
- [ ] Create `.github/workflows/deploy.yml`
- [ ] Configure frontend deployment to Cloudflare Pages
- [ ] Configure backend deployment to Cloudflare Workers

### 4.5 Create Worker Configuration
- [ ] Create `wrangler.toml` in backend directory
- [ ] Configure for Cloudflare Workers deployment

---

## Phase 5: DNS Configuration (You Do in Cloudflare)

### 5.1 Add DNS Records
Once nameservers have propagated (check with `dig devq.ai`):

- [ ] In Cloudflare DNS settings, add:
  ```
  Type    Name    Content                         Proxy   TTL
  A       @       192.0.2.1                      ✓       Auto
  CNAME   www     patient-dashboard.pages.dev    ✓       Auto  
  CNAME   api     patient-dashboard.workers.dev  ✓       Auto
  CNAME   db      <tunnel-id>.cfargotunnel.com  ✓       Auto
  ```

---

## Phase 6: Initial Deployment (We Do Together)

### 6.1 Test Local Setup
```bash
# Check if services are running
launchctl list | grep devqai

# Check SurrealDB
curl http://localhost:8000/health

# Check tunnel
curl https://db.devq.ai/health
```

### 6.2 Load Initial Data
```bash
cd patient-dashboard/backend
python scripts/load_production_data.py
```

### 6.3 Trigger GitHub Deployment
- [ ] Push code to main branch
- [ ] Monitor GitHub Actions for successful deployment
- [ ] Check Cloudflare Pages deployment
- [ ] Check Cloudflare Workers deployment

### 6.4 Verify Production
- [ ] Visit https://devq.ai - should see login page
- [ ] Check https://api.devq.ai/health - should return healthy
- [ ] Test login with production credentials
- [ ] Verify data loads correctly

---

## Phase 7: Monitoring & Backup Setup (Optional but Recommended)

### 7.1 Setup Monitoring (You Do)
- [ ] Create UptimeRobot account (free)
- [ ] Add monitor for https://api.devq.ai/health
- [ ] Set up email/SMS alerts

### 7.2 Create Backup System
```bash
# Create backup script
cat > ~/surrealdb/scripts/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/surrealdb/backups
mkdir -p $BACKUP_DIR

echo "Backing up Patient Dashboard database..."
surreal export --conn http://localhost:8000 \
  --user root --pass $SURREAL_PASS \
  --ns healthcare --db patient_dashboard \
  > $BACKUP_DIR/patient_dashboard_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
echo "Backup completed: patient_dashboard_$DATE.sql"
EOF

chmod +x ~/surrealdb/scripts/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /Users/dionedge/surrealdb/scripts/backup.sh") | crontab -
```

---

## 🎉 Deployment Complete!

### Access Points
- **Production Site**: https://devq.ai
- **API Documentation**: https://api.devq.ai/docs
- **Health Check**: https://api.devq.ai/health
- **Database** (via tunnel): wss://db.devq.ai/rpc

### Default Login
- Email: `admin@example.com`
- Password: `Admin123!`

### Troubleshooting Commands
```bash
# Check service status
launchctl list | grep devqai

# View logs
tail -f /tmp/surrealdb.log
tail -f /tmp/cloudflared.log

# Restart services
launchctl unload ~/Library/LaunchAgents/com.devqai.surrealdb.plist
launchctl load ~/Library/LaunchAgents/com.devqai.surrealdb.plist
```

---

## Notes
- DNS propagation can take 24-48 hours
- First deployment may take longer due to Cloudflare provisioning
- Monitor logs during first 24 hours for any issues
- Keep your Cloudflare API token and database password secure