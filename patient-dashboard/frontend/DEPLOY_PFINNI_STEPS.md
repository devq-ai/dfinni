# PFINNI Deployment to devq.ai/pfinni - Next Steps
Created: 2025-08-05T23:25:00-06:00

## Current Status ✅

1. ✅ Next.js configured with basePath: '/pfinni'
2. ✅ Built successfully with OpenNext.js Cloudflare adapter
3. ✅ Created wrangler.pfinni.toml configuration
4. ✅ Set up .dev.vars for secrets
5. ✅ Fixed all build errors

## Build Output Ready

The application is built and ready at:
- Worker: `.open-next/worker.js`
- Assets: `.open-next/assets/`

## What You Need to Do

### 1. Get Cloudflare Credentials

You need to get these from your Cloudflare dashboard:

```bash
# Go to: https://dash.cloudflare.com/profile/api-tokens
# Create a new API token with these permissions:
# - Account: Cloudflare Workers Scripts:Edit
# - Zone: Zone:Edit (for devq.ai)

CLOUDFLARE_API_TOKEN=your_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
```

### 2. Create KV Namespace

Once you have the credentials:

```bash
# Export credentials
export CLOUDFLARE_API_TOKEN=your_token_here
export CLOUDFLARE_ACCOUNT_ID=your_account_id_here

# Create KV namespace
npx wrangler kv namespace create "NEXT_CACHE_WORKERS_KV"

# This will output an ID like:
# id = "abcd1234..."
```

### 3. Update wrangler.pfinni.toml

Add the KV namespace ID:

```toml
[[kv_namespaces]]
binding = "NEXT_CACHE_WORKERS_KV"
id = "YOUR_KV_NAMESPACE_ID_HERE"
```

### 4. Deploy to Cloudflare

```bash
# Deploy the worker
npx wrangler deploy --config wrangler.pfinni.toml

# Set the secret
echo "sk_test_O5DYjIEDAXoKmeqqp7Xg510qi0LVEOPw57c5vgXANe" | npx wrangler secret put CLERK_SECRET_KEY --config wrangler.pfinni.toml
```

### 5. Test the Deployment

Visit: https://devq.ai/pfinni

You should see the PFINNI dashboard login page.

## Important Notes

1. **Database Connection**: The app connects to the REAL patient_dashboard database
2. **Authentication**: Uses Clerk test keys (safe for demo)
3. **API**: Points to production API at https://api.devq.ai
4. **No Mocks**: This is using real data, no placeholders

## File Locations

- Config: `wrangler.pfinni.toml`
- Build output: `.open-next/`
- Environment: `.env.pfinni-demo`
- Secrets: `.dev.vars` (not committed)

## Troubleshooting

If you get 500 errors:
1. Check wrangler tail: `npx wrangler tail --config wrangler.pfinni.toml`
2. Verify the KV namespace is created
3. Ensure CLERK_SECRET_KEY is set as a secret
4. Check that routes are configured correctly

## Summary

The application is fully built and configured. You just need:
1. Cloudflare API credentials
2. Create KV namespace
3. Deploy with wrangler

Everything else is ready to go!