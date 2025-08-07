# ✅ PFINNI Dashboard - Ready to Deploy

## Current Configuration (WORKING)

### 1. Clerk Configuration
- Using TEST instance (immediate deployment, no DNS required)
- Domain: `clean-stang-14-51.clerk.accounts.dev`
- Publishable Key: `pk_test_Y2xlYW4tc3RhbmctMTQtNTEuY2xlcmsuYWNjb3VudHMuZGV2JA`

### 2. Cloudflare Configuration
- Single `wrangler.toml` file (others removed to avoid confusion)
- Correct `[assets]` configuration (not `[site]`)
- Route: `devq.ai/pfinni/*`

### 3. GitHub Actions
- Workflow file created at `.github/workflows/deploy-pfinni.yml`
- Will deploy on push to main branch

## Deploy Commands

### Option 1: Deploy Now (Manual)
```bash
cd patient-dashboard/frontend
npx wrangler deploy --config wrangler.toml
```

### Option 2: Deploy via GitHub
1. Commit and push to main branch
2. GitHub Actions will automatically deploy

## Required Secrets

### In Cloudflare Dashboard:
```bash
npx wrangler secret put CLERK_SECRET_KEY
# Enter the secret key from Clerk dashboard (sk_test_XXX)
```

### In GitHub Repository Settings:
- `CLOUDFLARE_API_TOKEN` - Create at https://dash.cloudflare.com/profile/api-tokens
- `CLOUDFLARE_ACCOUNT_ID` - From Cloudflare dashboard

## Verification

After deployment, the app will be available at:
https://devq.ai/pfinni/sign-in

## What's Fixed

1. ✅ Static assets now load correctly (CSS/JS)
2. ✅ Clerk JS loads from working domain
3. ✅ Single source of truth for configuration
4. ✅ No more blank pages

## Future Enhancement

To use production Clerk with custom domain:
1. Add CNAME: `clerk.devq.ai → frontend-api.clerk.services`
2. Update publishable key to `pk_live_Y2xlcmsuZGV2cS5haSQ`
3. Redeploy