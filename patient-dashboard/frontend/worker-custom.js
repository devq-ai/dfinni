// Custom worker to handle basePath and URL encoding issues
import originalWorker from './.open-next/worker.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    console.log('Incoming request:', url.pathname);
    console.log('ASSETS available:', !!env.ASSETS);
    
    // Handle static asset requests with URL decoding
    if (url.pathname.startsWith('/pfinni/_next/') || 
        url.pathname.startsWith('/pfinni/favicon.ico') ||
        url.pathname.endsWith('.css') ||
        url.pathname.endsWith('.js') ||
        url.pathname.endsWith('.woff2')) {
      
      try {
        // First try the original URL
        console.log('Trying original path:', url.pathname);
        let assetResponse = await env.ASSETS.fetch(request);
        console.log('Original path response:', assetResponse.status);
        
        // If not found and URL contains encoded characters, try decoding
        if (assetResponse.status === 404 && url.pathname.includes('%')) {
          const decodedPath = decodeURIComponent(url.pathname);
          console.log('Trying decoded path:', decodedPath);
          const decodedUrl = new URL(decodedPath, request.url);
          const decodedRequest = new Request(decodedUrl, request);
          assetResponse = await env.ASSETS.fetch(decodedRequest);
          console.log('Decoded path response:', assetResponse.status);
        }
        
        // If still not found, try without the /pfinni prefix for _next assets
        if (assetResponse.status === 404 && url.pathname.startsWith('/pfinni/_next/')) {
          const pathWithoutPrefix = url.pathname.replace('/pfinni/', '/');
          console.log('Trying without prefix:', pathWithoutPrefix);
          const noPrefixUrl = new URL(pathWithoutPrefix, request.url);
          const noPrefixRequest = new Request(noPrefixUrl, request);
          assetResponse = await env.ASSETS.fetch(noPrefixRequest);
          console.log('No prefix response:', assetResponse.status);
        }
        
        if (assetResponse.status !== 404) {
          console.log('Serving asset:', url.pathname, 'status:', assetResponse.status);
          return assetResponse;
        } else {
          console.log('Asset not found after all attempts:', url.pathname);
        }
      } catch (e) {
        console.error('Asset fetch error:', e);
      }
    }
    
    // For all other requests, use the original worker
    console.log('Forwarding to original worker:', url.pathname);
    return originalWorker.fetch(request, env, ctx);
  }
};