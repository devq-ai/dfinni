#!/bin/bash
# Created: 2025-08-05T22:35:00-06:00
# Production build script

echo "🏭 Building PFINNI Dashboard for PRODUCTION..."

# Set production environment
export NODE_ENV=production
export NEXT_PUBLIC_ENV=production

# Use production env file
if [ -f .env.production ]; then
  echo "✅ Loading .env.production"
  export $(cat .env.production | grep -v '^#' | xargs)
else
  echo "❌ ERROR: .env.production not found!"
  echo "Please create .env.production with production values"
  exit 1
fi

# Build for production
echo "🔨 Building production bundle..."
npm run build

# Build for Cloudflare if needed
if [ "$1" == "--cloudflare" ]; then
  echo "☁️  Building for Cloudflare Workers..."
  npm run build:worker
fi

echo "✅ Production build complete!"