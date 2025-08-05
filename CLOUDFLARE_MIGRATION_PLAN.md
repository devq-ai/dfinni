# Cloudflare Migration Plan for PFINNI Dashboard

## Executive Summary

This document outlines the migration plan from the current deployment strategy to Cloudflare Pages using `@opennextjs/cloudflare` with full Node.js runtime support and Clerk authentication.

## Pre-flight Checklist

- [x] Next.js version 15.4.5 (✓ Above 15.2.4 security requirement)
- [x] Middleware file at root level (`middleware.ts`)
- [x] Clerk authentication configured
- [ ] Cloudflare account with Workers paid plan (10MB limit recommended)
- [ ] Environment variables ready:
  - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - `CLERK_SECRET_KEY`
  - `CLOUDFLARE_API_TOKEN`
  - `CLOUDFLARE_ACCOUNT_ID`

## Key Findings

### 1. Runtime Support
- **Documentation**: https://opennext.js.org/cloudflare
- **@opennextjs/cloudflare** supports full Node.js runtime (not just Edge runtime)
- Supports Next.js 14 (latest minor) and all versions of Next.js 15
- Requires `nodejs_compat` flag and compatibility date `2024-09-23` or later

### 2. Clerk Authentication Compatibility
- **Documentation**: https://clerk.com/docs/references/sdk/backend-only
- **Community Proof**: https://dev.to/yinks/implementing-authorization-with-clerk-in-a-trpc-app-running-on-a-cloudflare-worker-4li5
- Clerk is compatible using `@clerk/backend` package
- Requires environment variables for API keys
- Works with both server and client-side authentication

### 3. Current App Requirements
Based on codebase analysis:
- Uses `@clerk/nextjs/server` for server-side auth (`auth()`, `currentUser()`)
- Uses `@clerk/nextjs` for client-side auth (`useAuth()`, `useUser()`)
- Has middleware for route protection
- Passes JWT tokens to backend API

## Migration Steps

### Step 1: Install Dependencies
```bash
npm install @opennextjs/cloudflare@latest
npm install --save-dev wrangler@latest
```
**Source**: https://opennext.js.org/cloudflare/get-started

### Step 2: Create Wrangler Configuration
Create `wrangler.jsonc` in frontend directory:
```json
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "main": ".open-next/worker.js",
  "name": "pfinni-dashboard",
  "compatibility_date": "2024-12-30",
  "compatibility_flags": [
    "nodejs_compat",
    "global_fetch_strictly_public"
  ],
  "assets": {
    "directory": ".open-next/assets",
    "binding": "ASSETS"
  },
  "vars": {
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
    "CLERK_SECRET_KEY": "$CLERK_SECRET_KEY",
    "NEXT_PUBLIC_CLERK_SIGN_IN_URL": "/sign-in",
    "NEXT_PUBLIC_CLERK_SIGN_UP_URL": "/sign-up",
    "NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL": "/dashboard",
    "NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL": "/dashboard",
    "NEXT_PUBLIC_API_URL": "https://api.devq.ai"
  }
}
```
**Source**: https://opennext.js.org/cloudflare/get-started

### Step 3: Create OpenNext Configuration
Create `open-next.config.ts`:
```typescript
import { defineCloudflareConfig } from "@opennextjs/cloudflare";

export default defineCloudflareConfig({
  // Enable incremental cache using R2 for ISR/SSG
  incrementalCache: "r2-incremental-cache",
});
```
**Source**: https://opennext.js.org/cloudflare/get-started

### Step 4: Add Development Variables
Create `.dev.vars`:
```
NEXTJS_ENV=development
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_dev_publishable_key
CLERK_SECRET_KEY=your_dev_secret_key
```
**Source**: https://opennext.js.org/cloudflare/get-started

### Step 5: Update package.json Scripts
```json
{
  "scripts": {
    "dev": "next dev --turbopack",
    "build": "next build",
    "build:worker": "npx @opennextjs/cloudflare build",
    "preview": "npm run build:worker && wrangler pages dev",
    "deploy": "npm run build:worker && wrangler pages deploy",
    "start": "next start",
    "lint": "next lint"
  }
}
```
**Source**: https://opennext.js.org/cloudflare/get-started

### Step 6: Add Static Asset Headers
Create `public/_headers`:
```
/_next/static/*
  Cache-Control: public,max-age=31536000,immutable

/_next/image/*
  Cache-Control: public,max-age=31536000,immutable

/fonts/*
  Cache-Control: public,max-age=31536000,immutable
```
**Source**: https://opennext.js.org/cloudflare/get-started

### Step 7: Environment Variable Configuration
For production deployment, set secrets using Wrangler:
```bash
# Set Clerk secrets
wrangler secret put CLERK_SECRET_KEY --env production
wrangler secret put NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY --env production
```
**Source**: https://developers.cloudflare.com/workers/configuration/secrets/

### Step 8: Update GitHub Actions Workflow
Update `.github/workflows/deploy-cloudflare.yml`:
```yaml
name: Deploy to Cloudflare Pages

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
          cache: 'npm'
          cache-dependency-path: patient-dashboard/frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: patient-dashboard/frontend
        run: npm ci
      
      - name: Build application
        working-directory: patient-dashboard/frontend
        run: |
          npm run build
          npx @opennextjs/cloudflare build
        env:
          NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: ${{ secrets.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY }}
          NEXT_PUBLIC_API_URL: https://api.devq.ai
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          command: pages deploy .open-next/assets --project-name=pfinni-dashboard
          workingDirectory: patient-dashboard/frontend
```

## Critical Considerations

### 1. Middleware Compatibility
- Next.js middleware works with `@opennextjs/cloudflare`
- Source: https://opennext.js.org/cloudflare (Supported Features section)
- **CRITICAL**: Known issue with Clerk middleware detection (GitHub Issue #524)
  - Error: "Clerk: auth() was called but Clerk can't detect usage of clerkMiddleware()"
  - Solution: Deploy using `opennextjs-cloudflare deploy` or Wrangler directly
  - Source: https://github.com/opennextjs/opennextjs-cloudflare/issues/524

### 2. Security Vulnerability (CVE-2025-29927)
- **CRITICAL**: Ensure Next.js version 15.2.4 or later
- Vulnerability affects authentication middleware
- Source: https://clerk.com/blog/cve-2025-29927

### 3. Worker Size Limits
- Free plan: 3 MiB compressed
- Paid plan: 10 MiB compressed
- Source: https://opennext.js.org/cloudflare

### 4. Authentication Flow
- Server-side: `auth()` from `@clerk/nextjs/server` works with Node.js runtime
- Client-side: Standard Clerk components work as expected
- API calls: JWT tokens passed via Authorization header

### 5. Known Limitations
- Node Middleware (introduced in Next.js 15.2) not yet supported
- Source: https://opennext.js.org/cloudflare
- **Beta Status**: @opennextjs/cloudflare is in 1.0-beta as of 2025
- Source: https://blog.cloudflare.com/deploying-nextjs-apps-to-cloudflare-workers-with-the-opennext-adapter/

## Testing Strategy

### 1. Local Testing
```bash
cd patient-dashboard/frontend
npm run build:worker
npm run preview
```

### 2. Staging Deployment
Deploy to a staging project first:
```bash
wrangler pages deploy .open-next/assets --project-name=pfinni-staging
```

### 3. Verification Checklist
- [ ] Homepage loads
- [ ] Sign in/up works
- [ ] Protected routes redirect correctly
- [ ] API calls authenticate properly
- [ ] Static assets load with proper caching
- [ ] Middleware executes correctly

## Troubleshooting

### Build Error: page_client-reference-manifest.js ENOENT
If you encounter "ENOENT: no such file or directory" for `page_client-reference-manifest.js`:

**Solution**: Remove any redirect-only pages in route groups:
```bash
rm app/(dashboard)/page.tsx  # If it only contains redirects
```

This error occurs when route groups have pages that only perform redirects. The build process expects certain manifest files that aren't generated for these pages.

### Clerk Middleware Detection Error
If you encounter "Clerk: auth() was called but Clerk can't detect usage of clerkMiddleware()":

1. **Verify middleware file location**:
   - Must be at `middleware.ts` (not in `src/` directory)
   - Source: Clerk documentation requires middleware at root

2. **Check deployment command**:
   ```bash
   # Use this
   npx opennextjs-cloudflare deploy
   # OR
   wrangler pages deploy .open-next/assets
   
   # NOT this
   npm run deploy
   ```

3. **Verify environment variables**:
   - Ensure all Clerk env vars are set in Cloudflare dashboard
   - Check `.dev.vars` for local development

4. **Middleware matcher configuration**:
   - Ensure matcher includes all necessary routes
   - Current config should work as-is

### Build Size Issues
If build exceeds size limits:
1. Check bundle size with `npm run analyze`
2. Consider code splitting
3. Remove unused dependencies

### Wrangler Configuration Warning
Add `pages_build_output_dir` to `wrangler.jsonc` to avoid warnings:
```json
"pages_build_output_dir": ".open-next/assets"
```

## Rollback Plan

If issues arise:
1. Keep current Vercel/other deployment active
2. Update DNS only after full verification
3. Can instantly rollback by updating DNS

## References

1. **@opennextjs/cloudflare Documentation**: https://opennext.js.org/cloudflare
2. **Clerk Backend SDK**: https://clerk.com/docs/references/sdk/backend-only
3. **Cloudflare Workers Node.js Compatibility**: https://developers.cloudflare.com/workers/runtime-apis/nodejs/
4. **Community Implementation**: https://dev.to/yinks/implementing-authorization-with-clerk-in-a-trpc-app-running-on-a-cloudflare-worker-4li5
5. **Cloudflare Pages Functions**: https://developers.cloudflare.com/pages/functions/
6. **Wrangler Configuration**: https://developers.cloudflare.com/workers/wrangler/configuration/