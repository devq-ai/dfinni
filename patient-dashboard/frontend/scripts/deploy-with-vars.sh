#!/bin/bash
# Deployment script with environment variables

# Source production environment if it exists
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
fi

# Build and deploy with variables
npm run build:worker && \
npx wrangler deploy \
  --var NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:"$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY"