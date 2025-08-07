#!/bin/bash
# Start Development Environment Script

echo "🚀 Starting PFINNI Development Environment..."

# Check if development env file exists
if [ ! -f .env.development ]; then
    echo "❌ Error: .env.development file not found!"
    exit 1
fi

# Load development environment variables
export $(cat .env.development | grep -v '^#' | xargs)

# Stop any existing dev containers
echo "🛑 Stopping existing development containers..."
docker-compose -f docker-compose.dev.yml down

# Start development services
echo "🏗️  Building and starting development services..."
docker-compose -f docker-compose.dev.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "✅ Development services status:"
docker-compose -f docker-compose.dev.yml ps

echo "🎉 Development environment is ready!"
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend API: http://localhost:8001"
echo "📍 SurrealDB: http://localhost:8000"
echo ""
echo "📝 Logs: docker-compose -f docker-compose.dev.yml logs -f"