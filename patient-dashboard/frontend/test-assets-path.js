// Test worker to understand asset path resolution
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Test various asset paths
    if (url.pathname === '/pfinni/test-assets') {
      const tests = [];
      
      // Test paths to try
      const pathsToTest = [
        // What browser requests
        '/pfinni/_next/static/chunks/webpack-e881b77b05179a22.js',
        // Without domain prefix
        '/_next/static/chunks/webpack-e881b77b05179a22.js',
        // Direct path matching file structure
        'pfinni/_next/static/chunks/webpack-e881b77b05179a22.js',
        // With https://assets.local prefix (per docs)
        'https://assets.local/pfinni/_next/static/chunks/webpack-e881b77b05179a22.js',
        'https://assets.local/_next/static/chunks/webpack-e881b77b05179a22.js',
      ];
      
      for (const testPath of pathsToTest) {
        try {
          // Test with URL object
          const testUrl = testPath.startsWith('http') ? testPath : new URL(testPath, 'https://example.com').toString();
          const response = await env.ASSETS.fetch(testUrl);
          tests.push({
            path: testPath,
            urlUsed: testUrl,
            status: response.status,
            contentType: response.headers.get('content-type'),
            contentLength: response.headers.get('content-length')
          });
        } catch (e) {
          tests.push({
            path: testPath,
            error: e.message
          });
        }
      }
      
      return new Response(JSON.stringify({
        requestedPath: url.pathname,
        assetsBinding: !!env.ASSETS,
        tests
      }, null, 2), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // For actual asset requests, log and try to serve
    console.log('Asset request:', url.pathname);
    
    try {
      // Try direct pass-through
      const response = await env.ASSETS.fetch(request);
      console.log('Direct fetch status:', response.status);
      
      if (response.status === 404) {
        // Try with assets.local prefix
        const assetUrl = new URL(url.pathname, 'https://assets.local');
        const assetResponse = await env.ASSETS.fetch(assetUrl);
        console.log('Assets.local fetch status:', assetResponse.status);
        if (assetResponse.status !== 404) {
          return assetResponse;
        }
      }
      
      return response;
    } catch (e) {
      console.error('Asset fetch error:', e);
      return new Response('Asset Error: ' + e.message, { status: 500 });
    }
  }
};