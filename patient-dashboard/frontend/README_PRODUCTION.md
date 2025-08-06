# PFINNI Dashboard - Production Deployment Guide
Created: 2025-08-05T22:45:00-06:00

## ⚠️ PRODUCTION ENVIRONMENT - HANDLE WITH CARE ⚠️

This guide covers deploying and managing the PFINNI Dashboard in production. All operations here affect REAL USERS and REAL DATA.

## Pre-Deployment Checklist

### 1. Environment Verification
- [ ] **NO DEV MODE INDICATOR** should be visible
- [ ] Verify `NODE_ENV=production`
- [ ] Confirm using production Clerk instance (pk_live_...)
- [ ] Check all API endpoints point to production URLs
- [ ] Ensure Logfire is set to production project

### 2. Security Checklist
- [ ] All secrets stored in GitHub Secrets or Cloudflare environment
- [ ] No hardcoded API keys in code
- [ ] CORS configured for production domains only
- [ ] Rate limiting enabled
- [ ] Security headers configured

### 3. Code Quality
- [ ] All tests passing (`npm test`)
- [ ] No console.log statements in production code
- [ ] TypeScript build succeeds without errors
- [ ] Lint passes (`npm run lint`)

## Production Environment Setup

### Required Environment Variables

Create `.env.production` (NEVER commit this file):

```bash
# Clerk Production Keys (from Clerk Dashboard - Production Instance)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_YOUR_REAL_KEY_HERE
CLERK_SECRET_KEY=sk_live_YOUR_REAL_SECRET_HERE

# Production URLs
NEXT_PUBLIC_API_URL=https://api.devq.ai
DATABASE_URL=https://db.devq.ai:8001
FRONTEND_URL=https://devq.ai

# Production Settings
NODE_ENV=production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=ERROR

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Production Database
DATABASE_NAME=patient_dashboard
DATABASE_NAMESPACE=patient_dashboard

# Logfire Production
LOGFIRE_ENVIRONMENT=production
LOGFIRE_PROJECT_NAME=pfinni
LOGFIRE_TOKEN=pylf_v1_us_YOUR_PRODUCTION_TOKEN
```

## Deployment Methods

### Method 1: GitHub Actions (Recommended)

The repository is configured with automatic deployment via GitHub Actions.

**Trigger Production Deployment:**
```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Push to main triggers automatic deployment
git push origin main
```

**GitHub Secrets Required:**
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLERK_SECRET_KEY` (production)
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (set as variable)

### Method 2: Manual Cloudflare Deployment

```bash
# 1. Build for production
npm run build:prod

# 2. Deploy to Cloudflare Workers
wrangler deploy --env production

# 3. Set secrets
wrangler secret put CLERK_SECRET_KEY --env production
```

### Method 3: Direct Cloudflare Pages

```bash
# Build and deploy
npm run build:worker:prod
npx @opennextjs/cloudflare deploy
```

## Production Configuration Files

### wrangler.toml (Production Section)
```toml
[env.production]
name = "pfinni-dashboard-production"
routes = [
  { pattern = "devq.ai/*", zone_name = "devq.ai" },
  { pattern = "www.devq.ai/*", zone_name = "devq.ai" }
]

[env.production.vars]
NEXT_PUBLIC_API_URL = "https://api.devq.ai"
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = "pk_live_..."
# Add other public vars here

# Secrets must be set via wrangler CLI or dashboard
```

### Cloudflare Configuration

1. **DNS Settings**
   ```
   Type  Name    Content
   A     @       192.0.2.1 (Cloudflare proxy)
   A     www     192.0.2.1 (Cloudflare proxy)
   A     api     Your-Backend-IP (Cloudflare proxy)
   ```

2. **Page Rules**
   - Cache Level: Standard
   - SSL: Full (Strict)
   - Always Use HTTPS: On

3. **Workers Routes**
   - `devq.ai/*` → pfinni-dashboard-production
   - `api.devq.ai/*` → pfinni-api-production

## Monitoring & Maintenance

### 1. Health Checks

**Frontend Health:**
```bash
curl https://devq.ai/api/health
```

**Backend Health:**
```bash
curl https://api.devq.ai/health
```

### 2. Logfire Monitoring

Production logs: https://logfire-us.pydantic.dev/devq-ai/pfinni

Key metrics to monitor:
- Error rate
- Response times
- API failures
- Authentication issues

### 3. Clerk Dashboard

Monitor authentication: https://dashboard.clerk.com

Check:
- Active users
- Failed login attempts
- Webhook deliveries
- Rate limits

## Emergency Procedures

### Rolling Back Deployment

```bash
# Via Cloudflare Dashboard
1. Go to Workers & Pages
2. Select pfinni-dashboard-production
3. Click "Deployments" tab
4. Select previous stable deployment
5. Click "Rollback"

# Via CLI
wrangler rollback --env production
```

### Disabling Site (Emergency)

```bash
# Create maintenance page
wrangler pages publish maintenance.html --project-name=pfinni-dashboard-production

# Or via Cloudflare Dashboard
1. Create "Under Maintenance" page rule
2. Set forwarding URL to maintenance page
```

### Debug Production Issues

⚠️ **NEVER enable DEBUG mode in production!**

Instead:
1. Check Logfire for errors
2. Use Cloudflare Analytics
3. Monitor Clerk logs
4. Test in staging environment

## Production Commands Reference

### Build Commands
```bash
# Full production build
npm run build:prod

# Analyze bundle size
ANALYZE=true npm run build:prod

# Build for Cloudflare
npm run build:worker:prod
```

### Deployment Commands
```bash
# Deploy via GitHub (push to main)
git push origin main

# Manual deploy to Cloudflare
wrangler deploy --env production

# Deploy to staging first
npm run deploy:staging
```

### Secret Management
```bash
# Set Clerk secret
wrangler secret put CLERK_SECRET_KEY --env production

# List secrets (names only)
wrangler secret list --env production

# Delete secret
wrangler secret delete SECRET_NAME --env production
```

## Post-Deployment Verification

### 1. Functional Tests
- [ ] Can access homepage (https://devq.ai)
- [ ] Sign in works with production account
- [ ] Dashboard loads correctly
- [ ] API calls succeed
- [ ] No DEV MODE indicator visible

### 2. Security Tests
- [ ] HTTPS enforced
- [ ] Security headers present
- [ ] CORS properly configured
- [ ] Rate limiting active

### 3. Performance Tests
- [ ] Page load time < 3 seconds
- [ ] Time to Interactive < 5 seconds
- [ ] Lighthouse score > 80

## Rollback Procedures

If issues detected after deployment:

1. **Immediate Rollback**
   ```bash
   # Cloudflare Dashboard > Workers & Pages > Rollback
   # Or
   wrangler rollback --env production
   ```

2. **Notify Team**
   - Post in #production-incidents channel
   - Create incident report
   - Update status page

3. **Root Cause Analysis**
   - Review deployment logs
   - Check error rates in Logfire
   - Analyze what changed

## Security Reminders

### NEVER DO THIS IN PRODUCTION:
- ❌ Enable DEBUG mode
- ❌ Log sensitive data
- ❌ Disable authentication
- ❌ Use test/development keys
- ❌ Expose internal APIs
- ❌ Disable rate limiting
- ❌ Commit secrets to git

### ALWAYS DO THIS:
- ✅ Test in staging first
- ✅ Monitor after deployment
- ✅ Have rollback plan ready
- ✅ Check security headers
- ✅ Verify HTTPS everywhere
- ✅ Keep secrets in secure storage
- ✅ Document all changes

## Production Support

### Monitoring Dashboard
- Cloudflare: https://dash.cloudflare.com
- Logfire: https://logfire-us.pydantic.dev/devq-ai/pfinni
- Clerk: https://dashboard.clerk.com

### Alert Channels
- PagerDuty: Production errors
- Slack: #production-alerts
- Email: ops@devq.ai

### On-Call Procedures
1. Check Logfire for errors
2. Verify all services are up
3. Check recent deployments
4. Rollback if necessary
5. Document incident

## Staging Environment

Always test in staging before production:

```bash
# Deploy to staging
npm run deploy:staging

# Staging URL
https://staging.devq.ai

# Uses same production build but different URL
```

## Questions?

**Before deploying to production:**
1. Have you tested in staging?
2. Is the rollback procedure clear?
3. Are monitoring alerts configured?
4. Do you have production access credentials?

**If unsure, DO NOT DEPLOY. Ask for help first.**

Remember: **Production affects real users. Measure twice, deploy once.**