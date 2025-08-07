# Clerk Custom Domain Setup for clerk.devq.ai

## Option 1: Set up Custom Domain (Recommended)

1. **Add DNS Record in Cloudflare**:
   - Type: CNAME
   - Name: clerk
   - Target: frontend-api.clerk.services
   - Proxy status: Proxied (orange cloud ON)

2. **Configure in Clerk Dashboard**:
   - Go to https://dashboard.clerk.com
   - Navigate to Settings → Domains
   - Add custom domain: clerk.devq.ai
   - Wait for SSL provisioning (5-30 minutes)

## Option 2: Use Standard Clerk Domain

Change the publishable key in wrangler.pfinni.toml:
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY = "pk_test_Y2xlYW4tc3RhbmctMTQtNTEuY2xlcmsuYWNjb3VudHMuZGV2JA"
```

This uses the test environment at: clean-stang-14-51.clerk.accounts.dev

## Current Issue

The publishable key `pk_live_Y2xlcmsuZGV2cS5haSQ` expects clerk.devq.ai to exist.
Without this DNS record, Clerk JavaScript cannot load, causing a blank page.