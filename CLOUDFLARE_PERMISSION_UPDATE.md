# Cloudflare API Token Permission Update

## Error
```
✘ [ERROR] A request to the Cloudflare API (/accounts/***/storage/kv/namespaces) failed.
Authentication error [code: 10000]
```

## Required Permissions

Even though we're using R2 for caching, wrangler deployment process checks for KV namespaces access. You need to add:

**Account Permissions:**
- Workers KV Storage: Edit (ADD THIS)
- Workers R2 Storage: Edit (already added)
- Workers Scripts: Edit (already have)
- Cloudflare Pages: Edit (already have)

**Zone Permissions (for devq.ai):**
- Workers Routes: Edit (already have)
- DNS Settings: Edit (already have)

## Steps
1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Edit the "pfinni" token
3. Add "Workers KV Storage: Edit" permission
4. Save and update the token in GitHub secrets

## Why Both KV and R2?
During deployment, wrangler performs various checks including KV namespace access, even if your application only uses R2. This is part of the deployment validation process.