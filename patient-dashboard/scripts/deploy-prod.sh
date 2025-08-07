#!/bin/bash
# Deploy to Production Script - Preserves Development Environment

echo "🚀 Deploying PFINNI to Production..."

# Check if production env file exists
if [ ! -f .env.production ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please create .env.production from .env.production.example"
    exit 1
fi

# Verify development is isolated
echo "🔒 Verifying development environment isolation..."
DEV_CONTAINERS=$(docker ps --filter "name=pfinni-.*-dev" --format "{{.Names}}")
if [ ! -z "$DEV_CONTAINERS" ]; then
    echo "✅ Development containers are running separately:"
    echo "$DEV_CONTAINERS"
fi

# Load production environment variables
export $(cat .env.production | grep -v '^#' | xargs)

# Build production images
echo "🏗️  Building production images..."
docker-compose -f docker-compose.prod.yml build

# Deploy to Cloudflare Workers (Frontend)
echo "☁️  Deploying frontend to Cloudflare Workers..."
cd frontend
npm run build
npx wrangler deploy --env production
cd ..

# Start production services locally (for testing)
echo "🎯 Starting production services locally for verification..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Production deployment complete!"
echo "📍 Production Frontend (local test): http://localhost:3100"
echo "📍 Production Backend API (local test): http://localhost:8101"
echo "📍 Production SurrealDB: http://localhost:8100"
echo ""
echo "🔒 Development environment remains at:"
echo "📍 Dev Frontend: http://localhost:3000"
echo "📍 Dev Backend API: http://localhost:8001"
echo "📍 Dev SurrealDB: http://localhost:8000"