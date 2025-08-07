import { defineCloudflareConfig } from "@opennextjs/cloudflare";

export default defineCloudflareConfig({
  // Use default KV-based incremental cache
  // The basePath is handled in next.config.mjs
});