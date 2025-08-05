# GitHub Secrets Configuration Guide

## Use Repository Secrets (Not Environment or Variables)

### Why Repository Secrets?
- **Secrets** are encrypted and perfect for sensitive data like API keys
- **Repository secrets** are available to all workflows in the repo
- **Variables** are not encrypted (don't use for sensitive data)
- **Environment secrets** are only needed if you have multiple environments

## Step-by-Step Guide

1. Go to your repository: https://github.com/devq-ai/dfinni
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** button

## Add These Repository Secrets

### 1. CLOUDFLARE_API_TOKEN
- **Name**: `CLOUDFLARE_API_TOKEN`
- **Value**: `2NbDZwsYbzH_iEPCF-LmK_tDAD3qHEDdRVNQMMJz`

### 2. CLOUDFLARE_ACCOUNT_ID
- **Name**: `CLOUDFLARE_ACCOUNT_ID`
- **Value**: (the 32-character ID you find using the guide above)

### 3. CLERK_PUBLISHABLE_KEY
- **Name**: `CLERK_PUBLISHABLE_KEY`
- **Value**: `pk_live_Y2xlcmsuZGV2cS5haSQ`

### 4. CLERK_SECRET_KEY
- **Name**: `CLERK_SECRET_KEY`
- **Value**: `sk_live_7t98vEqf307GvF2aaMGrx4ODmh9SRK4Qju6xDxn4dD`

### 5. LOGFIRE_TOKEN
- **Name**: `LOGFIRE_TOKEN`
- **Value**: (from your Logfire dashboard - check your .env file)

## Important Notes
- These are **Repository Secrets**, not Variables
- Once saved, you can't view the values again (only update/delete)
- These will be available to GitHub Actions as `${{ secrets.SECRET_NAME }}`
- Keep these values secure and never commit them to code