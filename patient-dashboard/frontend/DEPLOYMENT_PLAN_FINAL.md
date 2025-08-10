# PFINNI Dashboard Deployment Plan - FINAL CONFIGURATION

## Overview
Deploy Next.js app with Clerk authentication to Cloudflare Workers at https://devq.ai/pfinni

## 1. CLERK CONFIGURATION

### Option A: Custom Domain (clerk.devq.ai)
1. **Clerk Dashboard Settings**:
   - Add custom domain: `clerk.devq.ai`
   - Instance: Production
   - Publishable Key: `<YOUR_CLERK_PUBLISHABLE_KEY>` (encodes clerk.devq.ai)

2. **Required DNS (in Cloudflare)**:
   ```
   Type: CNAME
   Name: clerk
   Target: frontend-api.clerk.services
   Proxy: ON (orange cloud)
   ```

### Option B: Standard Clerk Domain (IMMEDIATE SOLUTION)
1. **Use Test Instance**:
   - Domain: clean-stang-14-51.clerk.accounts.dev
   - Publishable Key: `pk_test_Y2xlYW4tc3RhbmctMTQtNTEuY2xlcmsuYWNjb3VudHMuZGV2JA`
   - No DNS setup required

## 2. CLOUDFLARE CONFIGURATION

### wrangler.toml (CORRECT VERSION)
```toml
name = "pfinni-dashboard-demo"
main = ".open-next/worker.js"
compatibility_date = "2024-12-30"
compatibility_flags = ["nodejs_compat"]

[assets]
directory = ".open-next/assets"
binding = "ASSETS"

[[kv_namespaces]]
binding = "NEXT_CACHE_WORKERS_KV"
id = "3e3333eba2c34b5193271f6f51dd811f"

[[routes]]
pattern = "devq.ai/pfinni/*"
zone_name = "devq.ai"

[vars]
NEXT_PUBLIC_API_URL = "https://api.devq.ai"
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = "pk_test_Y2xlYW4tc3RhbmctMTQtNTEuY2xlcmsuYWNjb3VudHMuZGV2JA"
NEXT_PUBLIC_CLERK_SIGN_IN_URL = "/pfinni/sign-in"
NEXT_PUBLIC_CLERK_SIGN_UP_URL = "/pfinni/sign-up"
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL = "/pfinni/dashboard"
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL = "/pfinni/dashboard"
```

### Cloudflare Secrets (via Dashboard or CLI)
```bash
npx wrangler secret put CLERK_SECRET_KEY
# Enter: sk_test_XXXXX (from Clerk dashboard)

npx wrangler secret put DATABASE_URL
# Enter: postgres://username:password@host:5432/dbname
```

## 3. GITHUB ACTIONS CONFIGURATION

### Repository Secrets Required:
```
CLOUDFLARE_API_TOKEN    # Create at https://dash.cloudflare.com/profile/api-tokens
CLOUDFLARE_ACCOUNT_ID   # From Cloudflare dashboard
CLERK_SECRET_KEY        # From Clerk dashboard (sk_test_XXX or sk_live_XXX)
DATABASE_URL            # PostgreSQL connection string
```

### .github/workflows/deploy-pfinni.yml
```yaml
name: Deploy PFINNI to Cloudflare

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: |
          cd patient-dashboard/frontend
          npm ci
          
      - name: Build for Cloudflare
        run: |
          cd patient-dashboard/frontend
          npx @opennextjs/cloudflare@latest build
        env:
          NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: ${{ vars.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY }}
          
      - name: Deploy to Cloudflare
        run: |
          cd patient-dashboard/frontend
          npx wrangler deploy --config wrangler.toml
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

## 4. NEXT.JS CONFIGURATION

### next.config.mjs
```javascript
const nextConfig = {
  basePath: '/pfinni',
  assetPrefix: '/pfinni',
  // ... rest of config
};
```

### Environment Variables (.env.production)
```
NEXT_PUBLIC_API_URL=https://api.devq.ai
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_Y2xlYW4tc3RhbmctMTQtNTEuY2xlcmsuYWNjb3VudHMuZGV2JA
```

## 5. BUILD & DEPLOY COMMANDS

### Local Build & Test
```bash
# Clean build
rm -rf .next .open-next

# Build for Cloudflare
npx @opennextjs/cloudflare@latest build

# Deploy
npx wrangler deploy --config wrangler.toml
```

## 6. TROUBLESHOOTING CHECKLIST

✅ Assets loading (CSS/JS files return 200)
✅ Clerk JS loads from correct domain
✅ Environment variables are set
✅ Secrets are configured in Cloudflare
✅ basePath is consistent (/pfinni)
✅ Routes pattern matches deployment

## 7. CURRENT ISSUES & FIXES

1. **Blank Page**: Clerk JS trying to load from non-existent clerk.devq.ai
   - **Fix**: Either add DNS record OR use test key

2. **Static Assets 404**: Using deprecated [site] configuration
   - **Fix**: Use [assets] with binding = "ASSETS"

3. **Multiple wrangler.toml files**: Confusion about which to use
   - **Fix**: Use only wrangler.toml for production

## IMMEDIATE ACTION ITEMS

1. Choose Clerk option (A or B above)
2. Update wrangler.toml with correct configuration
3. Add required secrets to Cloudflare
4. Deploy using the commands in section 5
5. Verify at https://devq.ai/pfinni/sign-in