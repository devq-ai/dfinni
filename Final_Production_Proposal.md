# Patient Dashboard
**Pfinni Dashboard Specific Requirements**
- Add these to Part A. Final Production Proposal
```
#### Unit Tests Improvement
- Patient CRUD operations
- Dashboard statistics calculations
- Alert management
- Provider operations
#### E2E Backend Tests
- Sign up → Login → Create Patient → View Dashboard
- Alert creation and resolution flow
- Provider assignment workflow
#### Playwright Implementation
- Patient management (CRUD operations)
- Dashboard data display
- Real-time updates
- Error handling
#### Component Testing
- PatientForm validation
- Dashboard cards data display
### HIPAA COMPLIANCE
#### Audit Logging Enhancement
- Patient data anonymization for logs
#### Data Protection
- Add patient data export compliance
```
## A. Final Production Proposal
Comprehensive production readiness proposal for the Patient Management Dashboard, focusing on testing, monitoring, security, and deployment optimizations while adhering to best practices.
### Environment Configuration
- Single .env file in root directory (/Users/dionedge/devqai/)
- No .env.local or environment variations
- All services reference the single .env file with correct filepath
### Testing Philosophy
- Test all critical operations (authentication, data operations, API endpoints)
- Enable Logfire logging in all tests for observability
- Never disable testing or logging - maintain visibility
- Focus on root cause analysis, not workarounds
### Code Creation & Maintenance
- DO NOT guess when it comes to writing or refactoring code and find the CORRECT solution the technical source documentation
- Prioritize refactoring existing files over creating new ones
- No tech debt creation - solve problems properly
- Understand errors fully before implementing fixes
### Backend Testing Enhancement
#### Unit Tests Improvement
- Enhance existing test files in `/backend/tests/unit/`
- Add Logfire instrumentation to all test cases
- Cover critical paths:
  - Authentication flow (Clerk JWT verification)
#### Integration Tests
- Enhance `/backend/tests/integration/` tests
- Test full API request/response cycles
- Include authentication headers in all tests
- Verify database state changes
- Log all test operations to Logfire
#### E2E Backend Tests
- Enhance `/backend/tests/e2e/` workflows
- Test complete user journeys:
  - Sign up → Login → Create Patient → View Dashboard
### Frontend Testing Framework (New)
#### Playwright Implementation
- Add Playwright for E2E testing
- Test critical user flows:
  - Authentication (Clerk sign-in/sign-up)
#### Component Testing
- Use Vitest for component testing
- Test all critical components:
  - Authentication components
  - Error boundaries
#### Visual Regression Testing
- Implement Playwright visual comparisons
- Ensure dark theme consistency
- Validate responsive design
### Authentication & Authorization
#### Enhance Clerk Integration
- Add rate limiting to auth endpoints
- Implement session management best practices
- Add MFA support configuration
- Enhanced JWT validation with claims verification
#### API Security
- Add request signing for sensitive operations
- Implement field-level encryption for PII
- Enhanced CORS configuration for production
- API versioning strategy
#### Audit Logging Enhancement
- Ensure all data access is logged via Logfire
- Implement log retention policies (7 years)
- Add data access reports generation
#### Data Protection
- Implement encryption at rest for SurrealDB
- Add data backup and recovery procedures
- Implement data retention policies
### Backend Optimizations
#### Database Query Optimization
- Add indexes for common query patterns
- Implement query result caching
- Optimize N+1 query issues
- Add database connection pooling
- SurrealDB is the primary database
- SQLite is the application datase when specified
#### API Response Optimization
- Implement response compression
- Add pagination for all list endpoints
- Implement field selection (GraphQL-like)
- Add response caching headers
### Frontend Optimizations
#### Bundle Size Reduction
- Implement code splitting
- Lazy load heavy components
- Optimize image loading
- Remove unused dependencies
#### Runtime Performance
- Implement React.memo for expensive components
- Add virtual scrolling for patient lists
- Optimize re-renders with proper state management
- Implement service worker for offline support
### Enhanced Logfire Integration
#### Structured Logging
- Add correlation IDs to all requests
- Implement distributed tracing
- Add custom metrics for business KPIs
- Create alerting rules for critical events
#### Performance Monitoring
- Add API endpoint latency tracking
- Monitor database query performance
- Track frontend Core Web Vitals
- Set up performance budgets
### Health Monitoring
#### Service Health Checks
- Enhance existing health endpoints
- Add dependency health checks
- Implement circuit breakers
- Add automated recovery procedures
### DevOps & Deployment
#### Containerization
- Create multi-stage Dockerfiles
- Implement security scanning
- Optimize image sizes
- Add health checks to containers
#### CI/CD Pipeline
- Create GitHub Issues usign GH CLI for Roadmap (New or Enhanve Features, Technical Debt) on GitHub Projects
- Automated testing on PR
- Security scanning (SAST/DAST)
- Automated deployment to staging
- Production deployment with approval
### Documentation & Maintenance
- Generate from FastAPI automatically
- Add example requests/responses
- Document error codes
- Include authentication flows
- Create Runbooks documenting procedutes for primary system troubleshooting steps and project (idiosyncratic) issues

---

## B. Deployment
### Operations Manual
- Step-by-step deployment guide
- Rollback procedures
- Monitoring setup guide
- Troubleshooting playbook
### Deployment Strategy: Cloudflare + Local SurrealDB
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
# Demo Access
- URL: [https://devq.ai](https://devq.ai)
- Login: demo@devq.ai / DemoPass123
- Status: Check the badge above
> If the demo is offline, the database server may be temporarily unavailable.
```
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
### Monthly Costs
- Cloudflare: $0 (Free tier)
- Domain: ~$1/month (annual)
- Mac Studio Power: ~$5-10/month
- Internet: (existing cost)
- Total: ~$6-11/month
### Comparison
- Cloud hosting: $20-100/month
- Savings: $15-90/month
### Security Considerations
- 1. Tunnel Security: Only SurrealDB exposed through tunnel
- 2. Authentication: Clerk handles all auth
- 3. API Security: Rate limiting on Cloudflare
- 4. Database: Local = physical security
- 5. Backups: Encrypted cloud backups
### Phase 1: Critical Security & Testing (4 Hours)
1. Implement Playwright E2E tests for authentication
2. Add Logfire to all critical operations
3. Enhance Clerk JWT validation
4. Implement audit logging for all data access
### Phase 2: Performance & Monitoring (4 Hours)
1. Optimize database queries with indexes
2. Implement response caching
3. Add comprehensive Logfire metrics
4. Set up alerting rules
### Phase 3: DevOps & Deployment (4 Hours)
1. Create production Dockerfiles
2. Set up CI/CD pipelines
3. Implement Kubernetes configs
4. Create deployment documentation
### Phase 4: Advanced Features (4 Hours)
1. Implement visual regression testing
2. Add advanced security features
3. Optimize frontend performance
4. Complete HIPAA compliance checklist
### Completed Features
- Modern patient management dashboard with authentication
- Dark mode theme applied (#0f0f0f, #141414, #3e3e3e)
- Full patient data management with all required fields
- Patient status workflow (inquiry, onboarding, active, churned, urgent)
- 20 XML files in X12 271 Healthcare Eligibility Response format
- FastAPI backend with RESTful endpoints
- Next.js 15 frontend with TypeScript
- Clerk authentication integration
- SurrealDB database integration
- Alert system with severity levels
- Provider management system
- Search & filtering capabilities
### Technical Stack
- Backend: FastAPI, Python
- Frontend: Next.js 15, TypeScript, Shadcn UI
- Database: SurrealDB
- Authentication: Clerk
- Monitoring: Logfire
- Container: Docker (docker-compose.yml exists)
### Immediate Optimization Opportunities
- 1. Testing Gap: No frontend tests exist - Playwright implementation critical
- 2. Backend Tests: Exist but need Logfire integration
- 3. Production Dockerfiles: Missing from backend/frontend directories
- 4. CI/CD: No GitHub Actions workflows present
- 5. Security: Clerk integration exists but needs hardening
- 6. Monitoring: Logfire configured but needs enhancement
- 7. Documentation: Basic README exists, needs expansion

---

## C. Style Guide
### Cyber & Pastel Design System Style Guide
A comprehensive design system featuring two distinctive palettes with modern typography for digital interfaces.
### Table of Contents
- [Color Palettes](#color-palettes)
- [Typography System](#typography-system)
- [Implementation Guide](#implementation-guide)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
### Color Palettes
#### Cyber Black Palette
Perfect for: Gaming interfaces, tech dashboards, cyberpunk themes, high-energy digital experiences
##### Base Colors
| Color Name | Hex Code | Usage |
|------------|----------|--------|
| Void Black | `#000000` | Primary background, deep shadows, maximum contrast base |
| Carbon Black | `#0a0a0a` | Secondary background, subtle elevation |
| Cyber Gray | `#1a1a1a` | Card backgrounds, modal overlays |
| Pure White | `#ffffff` | Primary text, high contrast elements |
##### Accent Colors
| Color Name | Hex Code | Usage |
|------------|----------|--------|
| Matrix Green | `#00ff00` | Success states, online status, completion |
| Neon Pink | `#ff0080` | Error states, critical alerts, danger |
| Electric Cyan | `#00ffff` | Processing states, loading, active elements |
| Laser Yellow | `#ffff00` | Warning states, caution, pending actions |
##### CSS Variables
```css
:root {
  /* Cyber Black Palette */
  --cyber-void-black: #000000;
  --cyber-carbon-black: #0a0a0a;
  --cyber-gray: #1a1a1a;
  --cyber-white: #ffffff;
  --cyber-matrix-green: #00ff00;
  --cyber-neon-pink: #ff0080;
  --cyber-electric-cyan: #00ffff;
  --cyber-laser-yellow: #ffff00;
}
```
#### Pastel Black Palette
Perfect for: Mobile apps, productivity tools, wellness apps, modern websites, professional interfaces
##### Base Colors
| Color Name | Hex Code | Usage |
|------------|----------|--------|
| Midnight Black | `#000000` | Primary background, deep contrast foundation |
| Charcoal | `#0f0f0f` | Secondary surfaces, subtle depth |
| Soft Gray | `#1e1e1e` | Card backgrounds, gentle elevation |
| Soft White | `#f8f8f8` | Primary text, comfortable reading |
##### Accent Colors
| Color Name | Hex Code | Usage |
|------------|----------|--------|
| Mint Green | `#a8e6a3` | Success states, positive feedback, completion |
| Blush Pink | `#ffb3ba` | Error states, gentle warnings, attention |
| Sky Blue | `#b3e5fc` | Processing states, information, calm activity |
| Cream Yellow | `#fff9c4` | Warning states, caution, pending review |
##### CSS Variables
```css
:root {
  /* Pastel Black Palette */
  --pastel-midnight-black: #000000;
  --pastel-charcoal: #0f0f0f;
  --pastel-soft-gray: #1e1e1e;
  --pastel-soft-white: #f8f8f8;
  --pastel-mint-green: #a8e6a3;
  --pastel-blush-pink: #ffb3ba;
  --pastel-sky-blue: #b3e5fc;
  --pastel-cream-yellow: #fff9c4;
}
```
### Typography System
#### Font Selection
- UI Font: Inter Nerd Font - Clean, modern, highly readable
- Monospace Font: Space Mono Nerd Font - Unique personality, perfect for code
#### Font Stack Definition
```css
:root {
  /* Font Stacks */
  --font-ui: 'Inter', 'Inter Nerd Font', 'Segoe UI', 'Roboto', sans-serif;
  --font-mono: 'Space Mono', 'Space Mono Nerd Font', 'JetBrains Mono', monospace;  
  /* Font Weights */
  --font-light: 300;
  --font-regular: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;  
  /* Font Sizes */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  --text-4xl: 2.25rem;   /* 36px */
}
```
#### Font Loading
##### CDN Method (Fallback)
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
```
##### Self-Hosted Method (Recommended)
```css
@font-face {
  font-family: 'Inter Nerd Font';
  src: url('./fonts/InterNerdFont-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}
@font-face {
  font-family: 'Space Mono Nerd Font';
  src: url('./fonts/SpaceMonoNerdFont-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
}
```
#### Typography Scale
| Size | Rem | Pixels | Usage |
|------|-----|---------|--------|
| XS | 0.75rem | 12px | Tiny details, footnotes |
| SM | 0.875rem | 14px | Small labels, metadata |
| Base | 1rem | 16px | Body text, regular content |
| LG | 1.125rem | 18px | Subheadings, emphasis |
| XL | 1.25rem | 20px | Card titles, section headers |
| 2XL | 1.5rem | 24px | Page titles, main headings |
| 3XL | 1.875rem | 30px | Display headings |
| 4XL | 2.25rem | 36px | Hero text, major displays |
### Implementation Guide
#### Semantic CSS Classes
```css
/* Font Families */
.font-ui { font-family: var(--font-ui); }
.font-mono { font-family: var(--font-mono); }
/* Font Weights */
.weight-light { font-weight: var(--font-light); }
.weight-regular { font-weight: var(--font-regular); }
.weight-medium { font-weight: var(--font-medium); }
.weight-semibold { font-weight: var(--font-semibold); }
.weight-bold { font-weight: var(--font-bold); }
/* Font Sizes */
.text-xs { font-size: var(--text-xs); }
.text-sm { font-size: var(--text-sm); }
.text-base { font-size: var(--text-base); }
.text-lg { font-size: var(--text-lg); }
.text-xl { font-size: var(--text-xl); }
.text-2xl { font-size: var(--text-2xl); }
.text-3xl { font-size: var(--text-3xl); }
.text-4xl { font-size: var(--text-4xl); }
/* Component Classes */
.heading { 
  font-family: var(--font-ui); 
  font-weight: var(--font-semibold); 
}
.body-text { 
  font-family: var(--font-ui); 
  font-weight: var(--font-regular); 
}
.code-block { 
  font-family: var(--font-mono); 
  font-weight: var(--font-regular); 
}
.terminal { 
  font-family: var(--font-mono); 
  background: var(--cyber-carbon-black); 
  color: var(--cyber-white); 
}
```
#### Color Utility Classes
```css
/* Cyber Theme */
.cyber-bg-primary { background-color: var(--cyber-void-black); }
.cyber-bg-secondary { background-color: var(--cyber-carbon-black); }
.cyber-bg-surface { background-color: var(--cyber-gray); }
.cyber-text-primary { color: var(--cyber-white); }
.cyber-text-success { color: var(--cyber-matrix-green); }
.cyber-text-error { color: var(--cyber-neon-pink); }
.cyber-text-warning { color: var(--cyber-laser-yellow); }
.cyber-text-info { color: var(--cyber-electric-cyan); }
/* Pastel Theme */
.pastel-bg-primary { background-color: var(--pastel-midnight-black); }
.pastel-bg-secondary { background-color: var(--pastel-charcoal); }
.pastel-bg-surface { background-color: var(--pastel-soft-gray); }
.pastel-text-primary { color: var(--pastel-soft-white); }
.pastel-text-success { color: var(--pastel-mint-green); }
.pastel-text-error { color: var(--pastel-blush-pink); }
.pastel-text-warning { color: var(--pastel-cream-yellow); }
.pastel-text-info { color: var(--pastel-sky-blue); }
```
### Usage Examples
#### Status Indicators
##### Cyber Theme
```html
<!-- Online Status -->
<div class="status-indicator">
  <span class="status-dot" style="background: var(--cyber-matrix-green);"></span>
  <span class="font-ui text-sm cyber-text-primary">System Online</span>
</div>
<!-- Error Status -->
<div class="status-indicator">
  <span class="status-dot" style="background: var(--cyber-neon-pink);"></span>
  <span class="font-ui text-sm cyber-text-primary">Connection Failed</span>
</div>
<!-- Processing Status -->
<div class="status-indicator">
  <span class="status-dot" style="background: var(--cyber-electric-cyan);"></span>
  <span class="font-ui text-sm cyber-text-primary">Processing...</span>
</div>
```
###### Pastel Theme
```html
<!-- Success Status -->
<div class="status-indicator">
  <span class="status-dot" style="background: var(--pastel-mint-green);"></span>
  <span class="font-ui text-sm pastel-text-primary">Task Complete</span>
</div>
<!-- Warning Status -->
<div class="status-indicator">
  <span class="status-dot" style="background: var(--pastel-cream-yellow);"></span>
  <span class="font-ui text-sm pastel-text-primary">Needs Review</span>
</div>
```
#### Button Components
##### Cyber Theme Buttons
```html
<!-- Success Button -->
<button class="btn cyber-success">
  <span class="font-ui text-sm weight-medium">Execute Command</span>
</button>
<!-- Error Button -->
<button class="btn cyber-error">
  <span class="font-ui text-sm weight-medium">Terminate Process</span>
</button>
<!-- Info Button -->
<button class="btn cyber-info">
  <span class="font-ui text-sm weight-medium">Scan System</span>
</button>
```
```css
.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.cyber-success {
  background: var(--cyber-matrix-green);
  color: var(--cyber-void-black);
}
.cyber-error {
  background: var(--cyber-neon-pink);
  color: var(--cyber-white);
}
.cyber-info {
  background: var(--cyber-electric-cyan);
  color: var(--cyber-void-black);
}
```
#### Terminal/Code Blocks
##### Cyber Terminal
```html
<div class="terminal-window">
  <div class="terminal-header">
    <span class="font-mono text-sm weight-bold cyber-text-info">SYSTEM TERMINAL</span>
  </div>
  <div class="terminal-content">
    <div class="font-mono text-sm cyber-text-info">$ system.status --verbose</div>
    <div class="font-mono text-sm cyber-text-success">✓ Connection established</div>
    <div class="font-mono text-sm cyber-text-warning">⚠ Memory usage: 84%</div>
    <div class="font-mono text-sm cyber-text-error">✗ Critical error detected</div>
  </div>
</div>
```
#### Card Components
##### Pastel Card
```html
<div class="card pastel-theme">
  <div class="card-header">
    <h3 class="font-ui text-xl weight-semibold pastel-text-primary">
      Project Status
    </h3>
  </div>
  <div class="card-body">
    <p class="font-ui text-base weight-regular pastel-text-primary">
      Your project is running smoothly with no issues detected.
    </p>
    <div class="status-grid">
      <div class="status-item">
        <span class="font-ui text-sm weight-medium pastel-text-success">
          ✓ All systems operational
        </span>
      </div>
    </div>
  </div>
</div>
```
### Best Practices
#### Color Usage Guidelines
##### Cyber Theme
- Use high contrast for maximum visibility
- Neon accents sparingly - they should pop, not overwhelm
- Matrix Green for positive actions and success states
- Neon Pink for critical errors and destructive actions
- Electric Cyan for interactive elements and processing states
- Laser Yellow for warnings and caution states
##### Pastel Theme
- Maintain readability with sufficient contrast
- Soft accents should feel gentle and non-intrusive
- Mint Green for positive feedback and completion
- Blush Pink for gentle errors and attention
- Sky Blue for information and calm interactions
- Cream Yellow for subtle warnings
#### Typography Guidelines
##### Font Selection
- Inter Nerd Font for all UI elements, buttons, headings, and body text
- Space Mono Nerd Font for code, terminal output, data display, and technical content
- Never mix more than two font families in a single interface
##### Hierarchy
- 1. Display Text (3XL-4XL, Bold) - Hero sections, major headings
- 2. Headings (XL-2XL, Semibold) - Section titles, card headers
- 3. Body Text (Base-LG, Regular) - Main content, descriptions
- 4. Small Text (SM-XS, Medium) - Labels, metadata, captions
##### Line Height
- Display Text: 1.1-1.2
- Headings: 1.2-1.3
- Body Text: 1.4-1.6
- Code/Terminal: 1.4
#### Accessibility Considerations
##### Color Contrast
- Cyber Theme: High contrast ratios (7:1 or higher)
- Pastel Theme: Maintain WCAG AA compliance (4.5:1 minimum)
- Never rely on color alone for important information
#### Font Accessibility
- Minimum 16px for body text
- Maximum line length of 75 characters
- Sufficient spacing between interactive elements (44px minimum)
#### Implementation Tips
##### Performance
- Load fonts efficiently using font-display: swap
- Preload critical fonts for faster rendering
- Use system fonts as fallbacks
##### Maintenance
- Use CSS custom properties for easy theme switching
- Document color meanings and usage contexts
- Test both themes in different lighting conditions
##### Responsiveness
- Scale typography appropriately for different screen sizes
- Adjust contrast for different viewing environments
- Test on various devices and browsers
### File Structure
```
styles/
├── tokens/
│   ├── colors.css          # Color variables
│   ├── typography.css      # Font and text variables
│   └── spacing.css         # Spacing and layout variables
├── components/
│   ├── buttons.css         # Button styles
│   ├── cards.css           # Card components
│   ├── forms.css           # Form elements
│   └── status.css          # Status indicators
├── themes/
│   ├── cyber.css           # Cyber theme overrides
│   └── pastel.css          # Pastel theme overrides
└── main.css               # Main stylesheet
```
### Resources
#### Font Downloads
- Inter Nerd Font: [Nerd Fonts Repository](https://github.com/ryanoasis/nerd-fonts)
- Space Mono Nerd Font: [Nerd Fonts Repository](https://github.com/ryanoasis/nerd-fonts)
#### Color Tools
- Contrast Checker: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Accessibility: [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
#### Browser Support
- CSS Custom Properties: IE11+ (with polyfill)
- Font Loading: All modern browsers
- Fallback Fonts: Ensure graceful degradation

---

## D. Best Practices
- **ALAWYS ASK ME QUESTIONS IF CLARIFICATION WOULD HELP**
### Single .env File Rule
- **Location**: `/Users/dionedge/devqai/.env` (root directory only)
- **Never create**: `.env.local`, `.env.development`, or any variations
- All services reference the single .env file with correct filepath
- Use absolute paths when loading environment variables
```python
# Correct
from dotenv import load_dotenv
load_dotenv('/Users/dionedge/devqai/.env')

# Wrong
load_dotenv('.env.local')  # Don't create variations
```
### Port Management
#### Before Starting Services
Always check what's running to avoid conflicts:
```bash
# Run from ~/devqai/pfinni_dashboard
./all-ports.sh
```
Common services:
- Port 3000: Frontend (Next.js)
- Port 8000: SurrealDB
- Port 8001: Backend API (FastAPI)
#### Troubleshooting Workflow
- 1. Check active ports first: `./all-ports.sh`
- 2. Identify the service by PID and process name
- 3. Only restart if actually needed
- 4. Never blindly kill processes without checking
### Logging with Logfire
#### Configuration
- **Project URL**: https://logfire-us.pydantic.dev/devq-ai/pfinni
- **Tokens**: Set in root .env file
  - `LOGFIRE_TOKEN`
  - `LOGFIRE_WRITE_TOKEN`
  - `LOGFIRE_READ_TOKEN`
#### Implementation Pattern
Always use try-except-else pattern with Logfire logging:
```python
import logfire
# Configure once at startup
logfire.configure(
    token=os.getenv('LOGFIRE_TOKEN'),
    service_name='pfinni-backend',
    environment=os.getenv('ENVIRONMENT', 'development')
)
# Usage pattern
try:
    # Operation
    result = await db.query("SELECT * FROM patients")
    logfire.info("Query successful", rows=len(result))
except Exception as e:
    # Log error with context
    logfire.error(
        "Database query failed",
        error=str(e),
        query="SELECT * FROM patients",
        exc_info=True
    )
    raise
else:
    # Log success metrics
    logfire.info(
        "Operation completed",
        duration_ms=elapsed_time,
        result_count=len(result)
    )
```
#### Critical Operations to Log
- Authentication attempts
- Database operations
- API requests/responses
- Error conditions
- Performance metrics
### Testing with Pytest
```
backend/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── conftest.py
└── pytest.ini
```
#### Best Practices
```python
# Always use fixtures for setup
@pytest.fixture
async def test_db():
    db = await get_test_database()
    yield db
    await db.cleanup()
# Log test operations
def test_patient_creation(test_db):
    logfire.info("Starting patient creation test")
    try:
        patient = create_patient(test_db, test_data)
        assert patient.id is not None
    except Exception as e:
        logfire.error("Test failed", error=str(e))
        raise
```
#### Run Tests
```bash
# All tests with coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_patient_service.py -v
```
### FastAPI Best Practices
#### Project Structure
```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import logfire
app = FastAPI(title="Patient Dashboard API")
# Dependency injection
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user = await verify_token(token)
        logfire.info("User authenticated", user_id=user.id)
        return user
    except Exception as e:
        logfire.error("Authentication failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
# Endpoint with logging
@app.post("/patients")
async def create_patient(
    patient: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    logfire.info("Creating patient", user_id=current_user.id)
    try:
        result = await db.create_patient(patient)
        return result
    except Exception as e:
        logfire.error("Patient creation failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
```
### FastMCP Integration
#### Server Setup // TOBE UPDATED BY DION EDGE
<!-- ```python
from fastmcp import FastMCP
mcp = FastMCP("patient-dashboard")
@mcp.tool()
async def get_patient_data(patient_id: str) -> dict:
    """Retrieve patient data by ID"""
    try:
        # Implementation
        logfire.info("MCP tool called", tool="get_patient_data", patient_id=patient_id)
        return result
    except Exception as e:
        logfire.error("MCP tool failed", tool="get_patient_data", error=str(e))
        raise
``` -->
### SurrealDB Best Practices
#### Connection Management
```python
from surrealdb import AsyncSurrealDB
async def get_database():
    db = AsyncSurrealDB("ws://localhost:8000/rpc")
    try:
        await db.connect()
        await db.use("patient_dashboard", "patient_dashboard")
        await db.signin({"user": "root", "pass": "root"})
        logfire.info("Database connected")
        return db
    except Exception as e:
        logfire.error("Database connection failed", error=str(e))
        raise
# Query pattern
async def get_patients(db: AsyncSurrealDB):
    try:
        result = await db.query("SELECT * FROM patient WHERE status = 'active'")
        logfire.info("Query executed", rows=len(result))
        return result
    except Exception as e:
        logfire.error("Query failed", error=str(e))
        raise
```
#### Important Notes
- SurrealDB doesn't support `count()` - fetch all and count in Python
- Use proper indexes for performance
- Always close connections in finally blocks
### Pydantic AI Integration
#### Model Definition
```python
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class Patient(BaseModel):
    id: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: datetime
    status: Literal["inquiry", "onboarding", "active", "churned", "urgent"]
    @validator('date_of_birth')
    def validate_age(cls, v):
        if v > datetime.now():
            raise ValueError('Date of birth cannot be in the future')
        return v
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```
### Ptolemies MCP Registry
#### Configuration // TO BE UPDATED BY DION EDGE
<!-- ```python
# In MCP server configuration
{
    "mcpServers": {
        "patient-dashboard": {
            "command": "uvx",
            "args": ["--from", "patient-dashboard-mcp", "run"],
            "env": {
                "DATABASE_URL": "ws://localhost:8000/rpc"
            }
        }
    }
}
``` -->
### Clerk Authentication
#### Backend Setup
```python
from clerk_backend_api import Clerk
#clerk = Clerk(api_key=os.getenv("CLERK_SECRET_KEY"))
async def verify_clerk_token(token: str):
    try:
        # Verify JWT
        claims = clerk.verify_token(token)
        logfire.info("Token verified", user_id=claims.get("sub"))
        return claims
    except Exception as e:
        logfire.error("Token verification failed", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
```
#### Frontend Setup
```typescript
// In middleware.ts
import { clerkMiddleware } from '@clerk/nextjs/server'
export default clerkMiddleware({
  publicRoutes: ['/'],
  afterAuth(auth, req) {
    console.log('Auth status:', auth.userId)
  }
})
// In components
import { useAuth } from '@clerk/nextjs'
export function useAuthHeaders() {
  const { getToken } = useAuth()
  return async () => {
    const token = await getToken()
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }
}
```
### Next.js + Shadcn + Tailwind CSS + Anime.js
#### Component Structure
```typescript
// Use Shadcn components with Tailwind
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import anime from 'animejs'
import { useEffect, useRef } from 'react'
export function PatientCard({ patient }: { patient: Patient }) {
  const cardRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    // Anime.js animation on mount
    anime({
      targets: cardRef.current,
      translateY: [20, 0],
      opacity: [0, 1],
      duration: 500,
      easing: 'easeOutExpo'
    })
  }, [])
  return (
    <Card ref={cardRef} className="p-6 bg-[#141414] border-[#3e3e3e]">
      <h3 className="text-lg font-semibold">{patient.name}</h3>
      <Button variant="outline" className="mt-4">
        View Details
      </Button>
    </Card>
  )
}
```
#### Dark Theme Colors
- Background: `#0f0f0f`
- Card background: `#141414`
- Borders: `#3e3e3e`
#### Animation Best Practices
```typescript
// Stagger animations for lists
useEffect(() => {
  anime({
    targets: '.patient-item',
    translateX: [-20, 0],
    opacity: [0, 1],
    delay: anime.stagger(100),
    duration: 600,
    easing: 'easeOutQuad'
  })
}, [patients])
```
#### Error Handling
- 1. Always understand root cause - no workarounds
- 2. Fix problems properly - no mock data or stubs
- 3. Log errors with full context
- 4. Test error conditions
#### Code Organization
- 1. Prioritize refactoring over new files
- 2. Follow existing patterns in codebase
- 3. Keep components small and focused
- 4. Use TypeScript for type safety
### Testing Requirements
- 1. Test all critical paths
- 2. Include Logfire logging in tests
- 3. Never disable tests or logging
- 4. Maintain test coverage above 80%
### Security
- 1. Never hardcode credentials
- 2. Use Clerk for all authentication
- 3. Validate all inputs with Pydantic
- 4. Log security events to Logfire
### Start Services
```bash
# Check what's running
./all-ports.sh
# Start backend
cd patient-dashboard/backend
./start_server.sh
# Start frontend
cd patient-dashboard/frontend
npm run dev
# Start SurrealDB
surreal start --user root --pass root file://data
```
### Debug Issues
- 1. Check logs in Logfire: https://logfire-us.pydantic.dev/devq-ai/pfinni
- 2. Run `./all-ports.sh` to verify services
- 3. Check `.env` file location and values
- 4. Review error logs with proper context
### Deploy Checklist
- [ ] All tests passing
- [ ] Logfire configured for production
- [ ] Environment variables set
- [ ] Clerk production keys configured
- [ ] Database migrations complete
- [ ] Security scan passed

## CLI Tools in Go and Charm.sh
### Not Required for Pfinni Dashboard
Building modern CLI tools in Go has been revolutionized by the Charm libraries, which provide elegant terminal UI components and patterns. The DevGen CLI demonstrates how to create professional, interactive command-line applications that feel more like desktop apps than traditional terminal tools.
### Core Charm Libraries
#### Bubbletea - The Foundation
The foundation for building terminal apps with The Elm Architecture:
```go
type model struct {
    servers []Server
    cursor  int
}
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "j", "down":
            m.cursor++
        case "k", "up":
            m.cursor--
        case "enter":
            m.servers[m.cursor].Toggle()
        }
    }
    return m, nil
}
```
#### Lipgloss - Terminal Styling
CSS-like styling for beautiful terminal output:
```go
var (
    titleStyle = lipgloss.NewStyle().
        Bold(true).
        Foreground(lipgloss.Color("#FF10F0")).
        MarginBottom(1)
    
    activeStyle = lipgloss.NewStyle().
        Foreground(lipgloss.Color("#39FF14"))
)
```
#### Bubbles - Pre-built Components
Ready-to-use UI components like spinners, progress bars, and text inputs:
```go
spinner := spinner.New()
spinner.Spinner = spinner.Dot
spinner.Style = lipgloss.NewStyle().Foreground(lipgloss.Color("#00FFFF"))
```
### Building Interactive Dashboards
The DevGen dashboard shows real-time MCP server status with interactive controls:
```go
func (m dashboardModel) View() string {
    s := titleStyle.Render("🚀 DevGen MCP Server Dashboard\n")
    for i, server := range m.servers {
        cursor := " "
        if m.cursor == i {
            cursor = ">"
        }
        status := "inactive"
        style := inactiveStyle
        if server.Active {
            status = "active"
            style = activeStyle
        }
        s += fmt.Sprintf("%s %s %-30s %s\n",
            cursor,
            server.Emoji,
            server.Name,
            style.Render(status))
    }
    return s
}
```
### Command Structure with Cobra
Organize commands hierarchically with aliases for better UX:
```go
var dashboardCmd = &cobra.Command{
    Use:     "dashboard",
    Aliases: []string{"dash", "d"},
    Short:   "Launch interactive server dashboard",
    Run: func(cmd *cobra.Command, args []string) {
        p := tea.NewProgram(initialModel())
        if _, err := p.Run(); err != nil {
            fmt.Printf("Error: %v\n", err)
            os.Exit(1)
        }
    },
}
```
### SSH Server Integration
Enable remote access with Charm's Wish library:

```go
s, err := wish.NewServer(
    wish.WithAddress(fmt.Sprintf("%s:%d", sshHost, sshPort)),
    wish.WithHostKeyPath(".ssh/devgen_host_key"),
    wish.WithPasswordAuth(func(ctx ssh.Context, password string) bool {
        return password == "demo" || password == "devq"
    }),
    wish.WithMiddleware(
        bubbletea.Middleware(teaHandler),
        logging.Middleware(),
    ),
)
```
### Best Practices from DevGen
#### 1. Category Organization
Group related functionality with visual indicators:
```go
categories := map[string]string{
    "knowledge":     "🧠",
    "development":   "⚡",
    "web":          "🌐",
    "database":     "💾",
}
```
#### 2. Responsive Design
Handle terminal resizing gracefully:
```go
case tea.WindowSizeMsg:
    m.width = msg.Width
    m.height = msg.Height
```
#### 3. Error Handling
Provide clear, actionable error messages:
```go
if err != nil {
    return fmt.Errorf("%s Configuration not found. Try: %s",
        errorStyle.Render("✗"),
        codeStyle.Render("devgen --config /path/to/config.json"))
}
```
#### 4. Configuration Discovery
Search multiple locations intelligently:
```go
searchPaths := []string{
    "./mcp_status.json",
    "../mcp_status.json",
    "/Users/dionedge/devqai/machina/mcp_status.json",
}
```
#### 5. Cross-Platform Building
Use Make targets for consistency:
```makefile
cross-compile:
    GOOS=darwin GOARCH=amd64 go build -o build/devgen-darwin-amd64
    GOOS=linux GOARCH=amd64 go build -o build/devgen-linux-amd64
    GOOS=windows GOARCH=amd64 go build -o build/devgen-windows-amd64.exe
```
### Example: Building a Simple Interactive CLI
Here's a minimal example combining these concepts:
```go
package main
import (
    "fmt"
    "os"
    
    tea "github.com/charmbracelet/bubbletea"
    "github.com/charmbracelet/lipgloss"
)
type model struct {
    choices  []string
    cursor   int
    selected map[int]struct{}
}
var (
    selectedStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("212"))
    cursorStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("86"))
)
func main() {
    p := tea.NewProgram(initialModel())
    if _, err := p.Run(); err != nil {
        fmt.Printf("Error: %v", err)
        os.Exit(1)
    }
}
func initialModel() model {
    return model{
        choices:  []string{"Docker", "Kubernetes", "Terraform", "Ansible"},
        selected: make(map[int]struct{}),
    }
}
func (m model) Init() tea.Cmd {
    return nil
}
func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "ctrl+c", "q":
            return m, tea.Quit
        case "up", "k":
            if m.cursor > 0 {
                m.cursor--
            }
        case "down", "j":
            if m.cursor < len(m.choices)-1 {
                m.cursor++
            }
        case "enter", " ":
            _, ok := m.selected[m.cursor]
            if ok {
                delete(m.selected, m.cursor)
            } else {
                m.selected[m.cursor] = struct{}{}
            }
        }
    }
    return m, nil
}
func (m model) View() string {
    s := "What tools do you use?\n\n"
    for i, choice := range m.choices {
        cursor := " "
        if m.cursor == i {
            cursor = cursorStyle.Render(">")
        }
        checked := " "
        if _, ok := m.selected[i]; ok {
            checked = selectedStyle.Render("x")
        }
        s += fmt.Sprintf("%s [%s] %s\n", cursor, checked, choice)
    }
    s += "\nPress q to quit.\n"
    return s
}
```
### Resources
- Charm.sh: [https://charm.sh](https://charm.sh) - The home of all Charm libraries
- Bubbletea: [https://github.com/charmbracelet/bubbletea](https://github.com/charmbracelet/bubbletea) - The functional framework
- Lipgloss: [https://github.com/charmbracelet/lipgloss](https://github.com/charmbracelet/lipgloss) - Style definitions
- Bubbles: [https://github.com/charmbracelet/bubbles](https://github.com/charmbracelet/bubbles) - TUI components
- DevGen CLI: [https://github.com/devq-ai/devgen-cli](https://github.com/devq-ai/devgen-cli) - Full implementation example

The combination of Go's performance and Charm's elegant UI libraries enables CLI tools that are both powerful and delightful to use, as demonstrated by DevGen's interactive dashboard and comprehensive feature set.