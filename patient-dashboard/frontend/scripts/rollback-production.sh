#!/bin/bash
# Created: 2025-08-05T22:45:00-06:00
# Emergency rollback script for production

set -e

echo "🚨 PRODUCTION ROLLBACK SCRIPT 🚨"
echo "================================"
echo ""

# Confirmation
if [ "$1" != "--confirm" ]; then
    echo "This will rollback the production deployment!"
    echo ""
    echo "To proceed, run: $0 --confirm"
    exit 1
fi

echo "⏮️  Initiating rollback..."

# Rollback Cloudflare Workers deployment
wrangler rollback --env production --config wrangler.production.toml

# Log the rollback
ROLLBACK_ID=$(date +%Y%m%d%H%M%S)
echo "{
  \"rollback_id\": \"$ROLLBACK_ID\",
  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
  \"rolled_back_by\": \"$(git config user.name)\",
  \"reason\": \"$2\"
}" > .rollback-$ROLLBACK_ID.json

echo ""
echo "✅ Rollback complete!"
echo ""
echo "Next steps:"
echo "1. Verify site is working: https://devq.ai"
echo "2. Check Logfire for errors"
echo "3. Create incident report"
echo "4. Investigate root cause"

# Send notification (customize as needed)
# curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/HERE \
#   -H 'Content-type: application/json' \
#   -d "{\"text\":\"🚨 Production rollback executed by $(git config user.name)\"}"