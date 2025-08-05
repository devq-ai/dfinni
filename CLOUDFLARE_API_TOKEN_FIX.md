# Cloudflare API Token Permission Fix

## Error
```
✘ [ERROR] A request to the Cloudflare API (/accounts/***/storage/kv/namespaces) failed.
Authentication error [code: 10000]
```

## Root Cause
The Cloudflare API token lacks permissions to access KV namespaces, which OpenNext may use internally even if we're using R2 for caching.

## Solution

### Update API Token Permissions

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Find your existing API token or create a new one
3. Add these permissions:

**Account Permissions:**
- `Workers Scripts:Edit` - Deploy and manage Workers
- `Workers KV Storage:Edit` - Required even if using R2
- `Workers R2 Storage:Edit` - For R2 incremental cache
- `Workers Routes:Edit` - Configure routes

**Zone Permissions (for devq.ai):**
- `Workers Routes:Edit` - Deploy to custom domain
- `Zone:Read` - Read zone configuration

### Alternative: Use All-Permissions Template

1. Create new token using "Edit Cloudflare Workers" template
2. This includes all necessary permissions for Workers deployment

### Update GitHub Secret

After updating the token:
```bash
# In GitHub repository settings
Settings > Secrets and variables > Actions
Update CLOUDFLARE_API_TOKEN with new token
```

## Verification

Test locally first:
```bash
cd patient-dashboard/frontend
export CLOUDFLARE_API_TOKEN=your_new_token
npm run build
npx @opennextjs/cloudflare build
npx wrangler deploy --dry-run
```

## Notes

- OpenNext may create KV namespaces automatically for session storage
- Even if using R2 for caching, KV permissions might be required
- The "Workers Paid" plan provides higher limits (10MB vs 3MB)