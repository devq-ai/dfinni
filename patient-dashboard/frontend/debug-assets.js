// Simple worker to debug asset serving
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Only handle specific test paths for debugging
    if (url.pathname === '/pfinni/debug-assets') {
      const testPaths = [
        '/pfinni/_next/static/chunks/webpack-e881b77b05179a22.js',
        'pfinni/_next/static/chunks/webpack-e881b77b05179a22.js',
        '/_next/static/chunks/webpack-e881b77b05179a22.js',
        '_next/static/chunks/webpack-e881b77b05179a22.js',
        './pfinni/_next/static/chunks/webpack-e881b77b05179a22.js'
      ];
      
      const results = [];
      
      for (const path of testPaths) {
        try {
          const testUrl = new URL(path, 'https://example.com');
          const testRequest = new Request(testUrl, { method: 'GET' });
          const response = await env.ASSETS.fetch(testRequest);
          results.push({
            path,
            status: response.status,
            headers: Object.fromEntries(response.headers.entries())
          });
        } catch (e) {
          results.push({
            path,
            error: e.message
          });
        }
      }
      
      return new Response(JSON.stringify({
        assetsAvailable: !!env.ASSETS,
        results
      }, null, 2), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // For all other requests, return 404
    return new Response('Not Found', { status: 404 });
  }
};