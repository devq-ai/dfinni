#!/bin/bash
# Build script for Cloudflare deployment with forced Clerk configuration

echo "=== Building for Cloudflare with correct Clerk configuration ==="

# Force the correct Clerk test keys
export NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="pk_test_bGVuaWVudC1zdG9yay00NS5jbGVyay5hY2NvdW50cy5kZXYk"
export NEXT_PUBLIC_CLERK_DOMAIN="lenient-stork-45.clerk.accounts.dev"

# Unset any conflicting variables
unset CLERK_PUBLISHABLE_KEY
unset CLERK_SECRET_KEY

echo "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}"
echo "NEXT_PUBLIC_CLERK_DOMAIN=${NEXT_PUBLIC_CLERK_DOMAIN}"

# Build with OpenNext
npx @opennextjs/cloudflare build