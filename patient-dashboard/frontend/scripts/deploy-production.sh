#!/bin/bash
# Created: 2025-08-05T22:45:00-06:00
# Production deployment script with safety checks

set -e  # Exit on error

echo "🚨 PRODUCTION DEPLOYMENT SCRIPT 🚨"
echo "=================================="
echo ""

# Safety checks
if [ "$1" != "--confirm" ]; then
    echo "⚠️  WARNING: This will deploy to PRODUCTION!"
    echo ""
    echo "Pre-deployment checklist:"
    echo "[ ] Have you tested in staging?"
    echo "[ ] Are all tests passing?"
    echo "[ ] Is the rollback procedure clear?"
    echo "[ ] Do you have production credentials?"
    echo ""
    echo "To proceed, run: $0 --confirm"
    exit 1
fi

# Environment check
if [ ! -f ".env.production" ]; then
    echo "❌ ERROR: .env.production not found!"
    echo "Create it from .env.production.example with real values"
    exit 1
fi

echo "✅ Loading production environment..."
export NODE_ENV=production
export $(cat .env.production | grep -v '^#' | xargs)

# Run tests first
echo "🧪 Running tests..."
npm test || {
    echo "❌ Tests failed! Aborting deployment."
    exit 1
}

# Run linting
echo "🔍 Running lint..."
npm run lint || {
    echo "❌ Linting failed! Aborting deployment."
    exit 1
}

# Build for production
echo "🔨 Building for production..."
npm run build || {
    echo "❌ Build failed! Aborting deployment."
    exit 1
}

# Build for Cloudflare
echo "☁️  Building for Cloudflare Workers..."
npx @opennextjs/cloudflare build || {
    echo "❌ Cloudflare build failed! Aborting deployment."
    exit 1
}

# Create deployment record
DEPLOYMENT_ID=$(date +%Y%m%d%H%M%S)
echo "📝 Creating deployment record: $DEPLOYMENT_ID"
echo "{
  \"id\": \"$DEPLOYMENT_ID\",
  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
  \"git_commit\": \"$(git rev-parse HEAD)\",
  \"git_branch\": \"$(git branch --show-current)\",
  \"deployed_by\": \"$(git config user.name)\"
}" > .deployment-$DEPLOYMENT_ID.json

# Deploy to Cloudflare
echo "🚀 Deploying to Cloudflare Workers..."
wrangler deploy --env production --config wrangler.production.toml || {
    echo "❌ Deployment failed!"
    echo "Run rollback if needed: wrangler rollback --env production"
    exit 1
}

# Set secrets (only if changed)
echo "🔐 Updating secrets..."
echo "$CLERK_SECRET_KEY" | wrangler secret put CLERK_SECRET_KEY --env production --config wrangler.production.toml

# Verify deployment
echo "✨ Verifying deployment..."
sleep 5  # Wait for deployment to propagate

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://devq.ai/api/health)
if [ "$HEALTH_CHECK" != "200" ]; then
    echo "❌ Health check failed! Status: $HEALTH_CHECK"
    echo "Consider rolling back: wrangler rollback --env production"
    exit 1
fi

echo ""
echo "✅ PRODUCTION DEPLOYMENT SUCCESSFUL!"
echo "=================================="
echo "Deployment ID: $DEPLOYMENT_ID"
echo "URL: https://devq.ai"
echo ""
echo "Post-deployment checklist:"
echo "[ ] Check https://devq.ai loads correctly"
echo "[ ] Verify sign-in works"
echo "[ ] Monitor Logfire for errors"
echo "[ ] Check Cloudflare Analytics"
echo ""
echo "If issues arise, rollback with:"
echo "wrangler rollback --env production --config wrangler.production.toml"