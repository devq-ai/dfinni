# GitHub Secret Update Required

The deployment is using the wrong Clerk publishable key. The debug page shows:
- Current key: `pk_live_Y2xlcmsuZGV2cS5haSQ` (expects clerk.devq.ai domain)
- Needed key: `pk_test_bGVuaWVudC1zdG9yay00NS5jbGVyay5hY2NvdW50cy5kZXYk`

## Action Required:

1. Go to https://github.com/devq-ai/dfinni/settings/secrets/actions
2. Check if there's a secret named `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
3. If it exists, update it to: `pk_test_bGVuaWVudC1zdG9yay00NS5jbGVyay5hY2NvdW50cy5kZXYk`
4. If it doesn't exist, the issue might be in the wrangler deployment

## Alternative: Force Override in Deployment

If you can't update the GitHub secret, we can force the correct key in the wrangler.toml file.