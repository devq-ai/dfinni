#!/bin/bash

# Set Cloudflare API token from environment or prompt
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "Please set CLOUDFLARE_API_TOKEN environment variable first"
    echo "export CLOUDFLARE_API_TOKEN=your-token-here"
    exit 1
fi

# Clerk keys from .env file
CLERK_PUBLISHABLE_KEY="pk_test_bGVuaWVudC1zdG9yay00NS5jbGVyay5hY2NvdW50cy5kZXYk"
CLERK_SECRET_KEY="sk_test_O5DYjIEDAXoKmeqqp7Xg510qi0LVEOPw57c5vgXANe"

echo "Setting Clerk publishable key..."
echo "$CLERK_PUBLISHABLE_KEY" | npx wrangler secret put NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY --name devq-ai-app

echo "Setting Clerk secret key..."
echo "$CLERK_SECRET_KEY" | npx wrangler secret put CLERK_SECRET_KEY --name devq-ai-app

echo "Done! Secrets have been set for the devq-ai-app Worker."
echo ""
echo "To verify, visit your Worker at:"
echo "https://devq-ai-app.YOUR-SUBDOMAIN.workers.dev"
echo ""
echo "Or check in Cloudflare dashboard:"
echo "Workers & Pages > devq-ai-app > Settings > Variables"