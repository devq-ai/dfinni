// Custom wrapper to handle basePath routing for static assets
import workerScript from './.open-next/worker.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Debug logging
    console.log('Request URL:', url.pathname);
    
    // Check if this is a request for static assets
    if (url.pathname.startsWith('/pfinni/_next/') || 
        url.pathname.startsWith('/pfinni/favicon.ico') ||
        url.pathname === '/pfinni/favicon.ico') {
      
      // Try to fetch the asset directly from the ASSETS bucket
      try {
        // Create a new request with the correct path
        const assetUrl = new URL(url.pathname, request.url);
        const assetRequest = new Request(assetUrl, request);
        
        console.log('Fetching asset:', assetUrl.pathname);
        const assetResponse = await env.ASSETS.fetch(assetRequest);
        
        if (assetResponse.status === 200) {
          console.log('Asset found:', assetUrl.pathname);
          return assetResponse;
        } else {
          console.log('Asset not found, status:', assetResponse.status);
        }
      } catch (e) {
        console.error('Asset fetch error:', e);
      }
    }
    
    // For all other requests, use the original worker
    return workerScript.fetch(request, env, ctx);
  }
};