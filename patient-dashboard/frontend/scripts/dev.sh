#!/bin/bash
# Created: 2025-08-05T22:35:00-06:00
# Development startup script

echo "🚀 Starting PFINNI Dashboard in DEVELOPMENT mode..."

# Load development environment
export NODE_ENV=development
export NEXT_PUBLIC_ENV=development

# Use development env file
if [ -f .env.development ]; then
  echo "✅ Loading .env.development"
  export $(cat .env.development | grep -v '^#' | xargs)
else
  echo "⚠️  .env.development not found, using .env"
fi

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8001 | xargs kill -9 2>/dev/null

# Start the development server
echo "🎯 Starting Next.js development server on port 3000..."
npm run dev