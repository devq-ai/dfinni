# Last Updated: 2025-08-09T20:12:00-06:00
#!/bin/bash
# Build script for Cloudflare deployment

echo "=== Building for Cloudflare ==="

# Load environment variables from .env.production if they're not already set
if [ -f .env.production ]; then
  export $(grep -v '^#' .env.production | xargs)
fi

# Clerk key should be set via environment variables or CI/CD secrets
# Do not hardcode keys here
if [ -z "$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" ]; then
  echo "WARNING: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY not set"
fi

# Unset any conflicting variables
unset CLERK_PUBLISHABLE_KEY
unset CLERK_SECRET_KEY
unset NEXT_PUBLIC_CLERK_DOMAIN

echo "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}"

# Build with OpenNext
npx @opennextjs/cloudflare build