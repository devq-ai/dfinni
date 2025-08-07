# 🚀 DEPLOY NOW - Fix Blank Page Issue

The current live site is using the OLD build that tries to load Clerk from `clerk.devq.ai` (which doesn't exist).
The NEW build uses `clean-stang-14-51.clerk.accounts.dev` (which works).

## Option 1: Deploy via Cloudflare Dashboard (EASIEST)

1. Go to: https://dash.cloudflare.com
2. Navigate to: Workers & Pages
3. Find: `pfinni-dashboard-demo` 
4. Click: "Upload" or "Deploy"
5. Upload: The `pfinni-deployment.tar.gz` file created in this directory
   OR upload the `.open-next` directory

## Option 2: Deploy via Wrangler CLI

1. Get your Cloudflare API Token:
   - Go to: https://dash.cloudflare.com/profile/api-tokens
   - Create token with "Edit Workers" permission
   
2. Run deployment:
```bash
cd patient-dashboard/frontend
export CLOUDFLARE_API_TOKEN=your_token_here
export CLOUDFLARE_ACCOUNT_ID=your_account_id_here
npx wrangler deploy --config wrangler.toml
```

## Option 3: Deploy via GitHub Actions

1. Add secrets to your GitHub repository:
   - Go to: Settings → Secrets → Actions
   - Add: `CLOUDFLARE_API_TOKEN`
   - Add: `CLOUDFLARE_ACCOUNT_ID`

2. Push to trigger deployment:
```bash
git add -A
git commit -m "Fix Clerk domain - use working test instance"
git push origin main
```

## What Will Happen

After deployment, https://devq.ai/pfinni/sign-in will:
- ✅ Load Clerk JS from `clean-stang-14-51.clerk.accounts.dev`
- ✅ Show the sign-in page instead of blank screen
- ✅ All CSS/JS assets will load correctly

## Current Issue

The site shows blank because it's trying to load:
❌ https://clerk.devq.ai/npm/@clerk/clerk-js@5/dist/clerk.browser.js (doesn't exist)

After deployment it will load:
✅ https://clean-stang-14-51.clerk.accounts.dev/npm/@clerk/clerk-js@5/dist/clerk.browser.js (works!)

## Verify Deployment Success

After deploying, run:
```bash
curl -s https://devq.ai/pfinni/sign-in | grep -o 'clerk[^"]*\.dev'
```

Should show: `clean-stang-14-51.clerk.accounts.dev`
NOT: `clerk.devq.ai`