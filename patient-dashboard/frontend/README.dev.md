# Development Environment Setup
Created: 2025-08-05T22:35:00-06:00

## Environment Separation

This project is configured to run completely independently in development and production environments.

### Development Setup

1. **Environment Variables**
   - `.env.development` - Development-specific variables (already created)
   - Uses test Clerk keys that are separate from production
   - Points to localhost APIs

2. **Running Development**
   ```bash
   # Standard development (loads .env by default)
   npm run dev
   
   # Clean development (kills existing processes, loads .env.development)
   npm run dev:clean
   ```

3. **Development Features**
   - Yellow "DEV MODE" indicator in bottom-left corner
   - Source maps enabled
   - Fast refresh enabled
   - API proxy to localhost:8001
   - Development-specific Clerk instance

### Production Setup

1. **Environment Variables**
   - Copy `.env.production.example` to `.env.production`
   - Fill in production values (DO NOT commit this file)
   - Uses production Clerk keys

2. **Building for Production**
   ```bash
   # Build for production
   npm run build:prod
   
   # Build for Cloudflare Workers
   npm run build:worker:prod
   ```

3. **Production Features**
   - No dev indicator
   - Optimized bundle
   - Security headers
   - No source maps

### Key Differences

| Feature | Development | Production |
|---------|------------|------------|
| Clerk Instance | Test (pk_test_...) | Live (pk_live_...) |
| API URL | http://localhost:8001 | https://api.devq.ai |
| Database | patient_dashboard_dev | patient_dashboard |
| Debug Mode | Enabled | Disabled |
| Source Maps | Yes | No |
| Dev Indicator | Visible | Hidden |

### Switching Environments

```bash
# Development
export NODE_ENV=development
npm run dev

# Production (local test)
export NODE_ENV=production
npm run start:prod

# Staging
export NODE_ENV=staging
npm run deploy:staging
```

### Important Notes

1. **Never mix environments** - Development data should never touch production
2. **Separate Clerk instances** - Development uses test keys, production uses live keys
3. **Git ignored files** - All .env files are git ignored for security
4. **Database isolation** - Development uses `_dev` suffix on all databases

### Troubleshooting

If you see production data in development:
1. Check `NODE_ENV` environment variable
2. Verify correct .env file is loaded
3. Clear browser cache and cookies
4. Restart the development server

If authentication fails:
1. Verify Clerk keys match the environment
2. Check middleware configuration
3. Ensure correct redirect URLs