#!/bin/bash
# Created: 2025-08-05T22:45:00-06:00
# Staging deployment script for testing production builds

set -e  # Exit on error

echo "🧪 STAGING DEPLOYMENT SCRIPT 🧪"
echo "=============================="
echo ""

# Use production build with staging URLs
export NODE_ENV=production
export NEXT_PUBLIC_ENV=staging

# Check for staging env file
if [ -f ".env.staging" ]; then
    echo "✅ Loading .env.staging"
    export $(cat .env.staging | grep -v '^#' | xargs)
else
    echo "⚠️  No .env.staging found, using production config with staging URLs"
    if [ -f ".env.production" ]; then
        export $(cat .env.production | grep -v '^#' | xargs)
    fi
fi

# Override with staging URLs
export NEXT_PUBLIC_API_URL="https://staging-api.devq.ai"
export FRONTEND_URL="https://staging.devq.ai"

# Build for production (same as prod build)
echo "🔨 Building production bundle for staging..."
npm run build

# Build for Cloudflare
echo "☁️  Building for Cloudflare Workers..."
npx @opennextjs/cloudflare build

# Deploy to staging
echo "🚀 Deploying to staging..."
wrangler pages deploy .open-next/assets \
    --project-name=pfinni-staging \
    --branch=staging \
    --commit-hash=$(git rev-parse HEAD)

# Get deployment URL
DEPLOYMENT_URL=$(wrangler pages deployment list --project-name=pfinni-staging | head -2 | tail -1 | awk '{print $4}')

echo ""
echo "✅ STAGING DEPLOYMENT COMPLETE!"
echo "=============================="
echo "URL: $DEPLOYMENT_URL"
echo "Custom domain: https://staging.devq.ai"
echo ""
echo "Test the following:"
echo "[ ] Homepage loads"
echo "[ ] Sign-in works"
echo "[ ] Dashboard accessible"
echo "[ ] API calls succeed"
echo "[ ] No DEV MODE indicator"
echo ""
echo "If tests pass, deploy to production with:"
echo "./scripts/deploy-production.sh --confirm"