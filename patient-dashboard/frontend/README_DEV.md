# PFINNI Dashboard - Development Environment Guide
Created: 2025-08-05T22:40:00-06:00

## Overview

This guide explains how the development environment is completely isolated from production, ensuring safe development without any risk to production data or systems.

## The DEV MODE Indicator

### What is it?
A **bright yellow badge** that appears in the **bottom-left corner** of your browser window when running in development mode.

### What does it look like?
```
[●] DEV MODE (development)
```
- Yellow background with black text
- Pulsing dot animation
- Shows current environment in parentheses
- Fixed position (stays visible while scrolling)

### Where is the code?
- Component: `/components/dev-indicator.tsx`
- Imported in: `/app/layout.tsx`
- Only renders when `NODE_ENV === 'development'`

### Why is it important?
- **Instant visual confirmation** you're not in production
- **Prevents accidents** like testing with real user data
- **Always visible** so you can't forget which environment you're in

## Environment Separation

### Development Environment
```bash
# Uses these files:
.env.development     # Development-specific variables
.env                 # Fallback if .env.development not found

# Key settings:
- Clerk: pk_test_... (Test instance - separate from production)
- API: http://localhost:8001
- Database: patient_dashboard_dev
- Debug: Enabled
- Logfire: Development project
```

### Production Environment
```bash
# Uses these files:
.env.production      # Production variables (create from .env.production.example)

# Key settings:
- Clerk: pk_live_... (Live instance - real users)
- API: https://api.devq.ai
- Database: patient_dashboard
- Debug: Disabled
- Logfire: Production project
```

## Quick Start Commands

### Development
```bash
# Standard development server
npm run dev

# Clean development (recommended) - kills existing processes
npm run dev:clean

# What dev:clean does:
1. Sets NODE_ENV=development
2. Loads .env.development
3. Kills any processes on ports 3000 and 8001
4. Starts fresh Next.js dev server
```

### Production (Local Testing)
```bash
# Build for production
npm run build:prod

# Run production build locally
npm run start:prod

# Build for Cloudflare Workers
npm run build:worker:prod
```

## File Structure

```
frontend/
├── .env                    # Default environment (gitignored)
├── .env.development        # Development environment (gitignored)
├── .env.production         # Production environment (gitignored)
├── .env.production.example # Template for production
├── scripts/
│   ├── dev.sh             # Development startup script
│   └── prod.sh            # Production build script
├── components/
│   └── dev-indicator.tsx  # DEV MODE badge component
├── lib/
│   ├── auth-helpers.ts    # Authentication utilities
│   ├── clerk-config.ts    # Clerk configuration
│   ├── env.ts            # Environment validation
│   └── rate-limit.ts     # Rate limiting
└── README_DEV.md         # This file
```

## Clerk Authentication Separation

### Development (Test Mode)
- **Dashboard**: https://dashboard.clerk.com/apps/[your-dev-app]
- **Users**: Test users only, can be deleted anytime
- **Features**: All features available for testing
- **Webhooks**: Point to localhost or ngrok

### Production (Live Mode)
- **Dashboard**: https://dashboard.clerk.com/apps/[your-prod-app]
- **Users**: Real users with real data
- **Features**: Production features only
- **Webhooks**: Point to production endpoints

## Safety Features

1. **Visual Indicators**
   - Yellow DEV MODE badge in development
   - No badge in production
   - Environment shown in Clerk components

2. **Data Isolation**
   - Separate databases (suffix: _dev)
   - Different API endpoints
   - Isolated user accounts

3. **Configuration Protection**
   - All .env files are gitignored
   - Secrets never committed to git
   - Environment validation with Zod

4. **Middleware Protection**
   - Same auth rules in dev and prod
   - Consistent security headers
   - Rate limiting in both environments

## Common Development Tasks

### Creating a New User
```bash
# In development, use Clerk's test mode
# Go to: https://[your-dev-subdomain].clerk.accounts.dev/sign-up
# Or use the sign-up page at: http://localhost:3000/sign-up
```

### Testing API Endpoints
```bash
# Development API runs on port 8001
curl http://localhost:8001/api/health

# Frontend proxies /api/backend/* to backend
curl http://localhost:3000/api/backend/health
```

### Viewing Logs
```bash
# Frontend logs
npm run dev
# Look for console output in terminal

# Check Logfire (development project)
# https://logfire-us.pydantic.dev/devq-ai/pfinni-dev
```

### Database Access
```bash
# Development database
surreal sql --conn ws://localhost:8000 --ns patient_dashboard_dev --db patient_dashboard_dev

# Never connect to production from development!
```

## Troubleshooting

### "DEV MODE" badge not showing?
1. Check `NODE_ENV`:
   ```bash
   echo $NODE_ENV  # Should output: development
   ```
2. Restart dev server with clean script:
   ```bash
   npm run dev:clean
   ```

### Authentication not working?
1. Verify Clerk keys in `.env.development`
2. Check browser console for Clerk errors
3. Clear cookies and localStorage
4. Ensure you're using test instance URLs

### Can't connect to backend?
1. Ensure backend is running on port 8001
2. Check NEXT_PUBLIC_API_URL in environment
3. Verify proxy configuration in next.config.mjs

### Seeing production data?
1. **STOP IMMEDIATELY**
2. Check all environment variables
3. Ensure correct .env file is loaded
4. Verify database connection string

## Best Practices

### DO ✅
- Always use `npm run dev:clean` to start development
- Keep dev and prod Clerk instances completely separate
- Test with fake data in development
- Check for the DEV MODE badge before testing
- Use descriptive test user names (e.g., "Test Admin User")

### DON'T ❌
- Never copy production .env values to development
- Never use production API keys in development
- Never connect to production database from dev
- Never commit .env files to git
- Never disable the DEV MODE indicator

## Environment Variables Reference

### Required in Development (.env.development)
```bash
# Clerk (Test Instance)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# API Configuration  
NEXT_PUBLIC_API_URL=http://localhost:8001
DATABASE_URL=ws://localhost:8000/rpc

# Development Settings
NODE_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### Required in Production (.env.production)
```bash
# Clerk (Live Instance)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...

# API Configuration
NEXT_PUBLIC_API_URL=https://api.devq.ai
DATABASE_URL=https://db.devq.ai:8001

# Production Settings
NODE_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

## Questions?

If you're unsure which environment you're in:
1. Look for the yellow DEV MODE badge
2. Check the URL (localhost = dev, devq.ai = prod)
3. Run `echo $NODE_ENV` in terminal
4. Check browser console for environment logs

Remember: **When in doubt, check for the yellow badge!**