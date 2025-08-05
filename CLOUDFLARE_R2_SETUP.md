## Cloudflare R2 Setup for OpenNext

### Background

OpenNext for Cloudflare uses R2 for incremental cache storage when configured with `r2IncrementalCache`. This is documented in:
- https://opennext.js.org/cloudflare/former-releases/0.5/caching (shows KV was used in older versions)
- Current version uses R2 as shown in your `open-next.config.ts`

### Steps to Fix Deployment

#### 1. Create R2 Bucket

```bash
# Create the R2 bucket (run locally with your API token)
export CLOUDFLARE_API_TOKEN=your_token
npx wrangler r2 bucket create devq-ai-cache
```

#### 2. Update API Token Permissions

Go to https://dash.cloudflare.com/profile/api-tokens and ensure your token has:

**Account Permissions:**

- Workers Scripts: Edit
- Workers R2 Storage: Edit  
- Workers Routes: Edit

**Zone Permissions (for devq.ai):**

- Workers Routes: Edit
- Zone: Read

#### 3. Update GitHub Secrets

Update `CLOUDFLARE_API_TOKEN` in your GitHub repository settings with the new token.

#### 4. Wrangler Configuration

The wrangler.toml has been updated to include:
```toml
[[r2_buckets]]
binding = "NEXT_CACHE_R2"
bucket_name = "devq-ai-cache"
```

This binding name `NEXT_CACHE_R2` is expected by OpenNext's R2 incremental cache implementation.

### Why the KV Error?

The error mentioning KV namespaces is misleading. It occurs because:
- 1. Wrangler attempts to check various storage types during deployment
- 2. Without proper R2 permissions, it fails at the KV check
- 3. The actual requirement is R2 storage, not KV

### References

- R2 Buckets: https://developers.cloudflare.com/r2/get-started/
- KV Namespaces (not needed here): https://developers.cloudflare.com/kv/concepts/kv-namespaces/
- OpenNext Issue #502: https://github.com/opennextjs/opennextjs-cloudflare/issues/502