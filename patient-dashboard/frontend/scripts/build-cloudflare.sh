#!/bin/bash
# Build script for Cloudflare deployment with forced Clerk configuration

echo "=== Building for Cloudflare with correct Clerk configuration ==="

# Force the correct Clerk test keys
export NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_Y2xlYW4tc3RhbmctMTQtNTEuY2xlcmsuYWNjb3VudHMuZGV2JA"
export NEXT_PUBLIC_CLERK_DOMAIN="clean-stang-14-51.clerk.accounts.dev"

# Unset any conflicting variables
unset CLERK_PUBLISHABLE_KEY
unset CLERK_SECRET_KEY

echo "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}"
echo "NEXT_PUBLIC_CLERK_DOMAIN=${NEXT_PUBLIC_CLERK_DOMAIN}"

# Build with OpenNext
npx @opennextjs/cloudflare build