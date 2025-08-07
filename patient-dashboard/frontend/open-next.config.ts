import { defineCloudflareConfig } from "@opennextjs/cloudflare";

export default defineCloudflareConfig({
  // Configure for basePath deployment
  basePath: '/pfinni',
  assetPrefix: '/pfinni',
  
  // Ensure static assets are served correctly
  routes: {
    // Handle static assets
    "/_next/static/*": { type: "static" },
    "/pfinni/_next/static/*": { type: "static" },
    "/_next/image/*": { type: "static" },
    "/pfinni/_next/image/*": { type: "static" },
  },
});