# Cloudflare Worker Environment Setup

## Finding Your Worker URL

1. Go to Cloudflare Dashboard > Workers & Pages
2. Click on "devq-ai-app" 
3. You'll see the Worker URL at the top (something like `https://devq-ai-app.YOUR-SUBDOMAIN.workers.dev`)

## Setting Environment Variables

### Via Cloudflare Dashboard:

1. In the Worker page, go to **Settings** > **Variables**
2. Add these environment variables:

**Plain text variables:**
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = `pk_live_...` (your actual key)
- `NEXT_PUBLIC_CLERK_SIGN_IN_URL` = `/sign-in`
- `NEXT_PUBLIC_CLERK_SIGN_UP_URL` = `/sign-up`
- `NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL` = `/dashboard`
- `NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL` = `/dashboard`
- `NEXT_PUBLIC_API_URL` = `https://api.devq.ai`

**Encrypted variables:**
- `CLERK_SECRET_KEY` = `sk_live_...` (your actual secret key)

3. Click "Save and Deploy"

### Via Command Line:

```bash
# Set plain text variables
npx wrangler secret put NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
# (paste your pk_live_... key when prompted)

# Set encrypted secret
npx wrangler secret put CLERK_SECRET_KEY
# (paste your sk_live_... key when prompted)
```

## Verifying It Works

1. Visit your Worker URL directly to test
2. You should see the app load with proper styling
3. The Sign In/Sign Up buttons should work with Clerk

## Setting Up Custom Domain (devq.ai)

Once the Worker is working at the workers.dev URL:

1. The route is already configured in wrangler.toml for `devq.ai/*`
2. You need to ensure your DNS points devq.ai to Cloudflare (orange cloud on)
3. The Worker will automatically handle requests to devq.ai

## Current Issues

The environment variables are currently set as literals:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` = `"$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"` (wrong)
- `CLERK_SECRET_KEY` = `"$CLERK_SECRET_KEY"` (wrong)

These need to be replaced with your actual Clerk keys.