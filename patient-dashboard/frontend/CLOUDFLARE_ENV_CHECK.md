# Cloudflare Environment Variable Issue

The deployment is still using `pk_live_Y2xlcmsuZGV2cS5haSQ` even after:
1. Deleting the GitHub secret
2. Setting correct values in wrangler.toml
3. Forcing values in the deployment script

## Possible Sources:

1. **Cloudflare Dashboard Environment Variables**
   - Go to https://dash.cloudflare.com
   - Navigate to Workers & Pages > pfinni-dashboard-demo
   - Check Settings > Environment variables
   - Look for `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
   - DELETE it if found

2. **Cloudflare Pages Environment Variables**
   - If using Pages instead of Workers
   - Check the Pages project settings

3. **Wrangler Secrets**
   - Already checked - only CLERK_SECRET_KEY exists

## Next Steps:

1. Check Cloudflare dashboard for environment variable bindings
2. If found, delete `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
3. Redeploy

The key `pk_live_Y2xlcmsuZGV2cS5haSQ` expects the domain `clerk.devq.ai` which doesn't exist, causing 401 errors.