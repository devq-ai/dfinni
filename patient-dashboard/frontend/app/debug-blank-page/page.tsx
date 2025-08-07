'use client';

import { useEffect, useState } from 'react';

export default function DebugBlankPage() {
  const [debugInfo, setDebugInfo] = useState<any>({
    loading: true,
    clerkStatus: 'checking...',
    clerkScripts: [],
    networkErrors: [],
    consoleErrors: [],
    dom: {},
    env: {},
    routing: {}
  });

  useEffect(() => {
    const collectDebugInfo = async () => {
      const info: any = {
        loading: false,
        timestamp: new Date().toISOString(),
        clerkStatus: 'checking...',
        clerkScripts: [],
        networkErrors: [],
        consoleErrors: [],
        dom: {},
        env: {},
        routing: {}
      };

      // Check environment
      info.env = {
        NODE_ENV: process.env.NODE_ENV,
        NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ? 'SET' : 'NOT SET',
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
      };

      // Check routing
      info.routing = {
        href: window.location.href,
        pathname: window.location.pathname,
        search: window.location.search,
        origin: window.location.origin,
      };

      // Check DOM for Clerk scripts
      const scripts = Array.from(document.querySelectorAll('script'));
      info.clerkScripts = scripts
        .filter(s => s.src && (s.src.includes('clerk') || s.src.includes('accounts.dev')))
        .map(s => ({
          src: s.src,
          async: s.async,
          defer: s.defer,
          loaded: s.getAttribute('data-loaded') || 'unknown'
        }));

      // Check if Clerk is loaded
      const checkClerk = () => {
        if ((window as any).Clerk) {
          info.clerkStatus = 'Clerk object found';
          info.clerkVersion = (window as any).Clerk.version || 'unknown';
          info.clerkLoaded = true;
        } else {
          info.clerkStatus = 'Clerk object NOT found';
          info.clerkLoaded = false;
        }
      };

      // Try immediately and after a delay
      checkClerk();
      setTimeout(checkClerk, 2000);

      // Check for common DOM issues
      info.dom = {
        bodyClasses: document.body.className,
        htmlClasses: document.documentElement.className,
        rootElement: document.getElementById('__next') ? 'Found' : 'Not found',
        clerkElements: document.querySelectorAll('[class*="clerk"]').length,
        hiddenElements: Array.from(document.querySelectorAll('*'))
          .filter(el => {
            const style = window.getComputedStyle(el);
            return (
              style.display === 'none' || 
              style.visibility === 'hidden' || 
              style.opacity === '0'
            ) && el.id && el.id.includes('clerk');
          })
          .map(el => ({ id: el.id, class: el.className }))
      };

      // Listen for console errors
      const originalError = console.error;
      console.error = (...args) => {
        info.consoleErrors.push(args.join(' '));
        originalError.apply(console, args);
      };

      setDebugInfo(info);

      // Restore console.error after 5 seconds
      setTimeout(() => {
        console.error = originalError;
      }, 5000);
    };

    collectDebugInfo();
  }, []);

  if (debugInfo.loading) {
    return <div className="p-8 bg-white text-black">Loading debug information...</div>;
  }

  return (
    <div className="p-8 bg-white text-black min-h-screen">
      <h1 className="text-2xl font-bold mb-6">Blank Page Debug Information</h1>
      
      <div className="space-y-6">
        <section className="border p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Quick Status</h2>
          <ul className="list-disc list-inside space-y-1">
            <li>Page loaded: ✅</li>
            <li>Clerk Status: {debugInfo.clerkStatus}</li>
            <li>Clerk Scripts Found: {debugInfo.clerkScripts.length > 0 ? '✅' : '❌'}</li>
            <li>Console Errors: {debugInfo.consoleErrors.length > 0 ? `❌ (${debugInfo.consoleErrors.length})` : '✅'}</li>
          </ul>
        </section>

        <section className="border p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Environment</h2>
          <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
{JSON.stringify(debugInfo.env, null, 2)}
          </pre>
        </section>

        <section className="border p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Current Route</h2>
          <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
{JSON.stringify(debugInfo.routing, null, 2)}
          </pre>
        </section>

        <section className="border p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Clerk Scripts</h2>
          {debugInfo.clerkScripts.length > 0 ? (
            <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
{JSON.stringify(debugInfo.clerkScripts, null, 2)}
            </pre>
          ) : (
            <p className="text-red-600">No Clerk scripts found in DOM!</p>
          )}
        </section>

        <section className="border p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">DOM Information</h2>
          <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
{JSON.stringify(debugInfo.dom, null, 2)}
          </pre>
        </section>

        {debugInfo.consoleErrors.length > 0 && (
          <section className="border border-red-500 p-4 rounded">
            <h2 className="text-xl font-semibold mb-2 text-red-600">Console Errors</h2>
            <ul className="list-disc list-inside space-y-1">
              {debugInfo.consoleErrors.map((error: string, i: number) => (
                <li key={i} className="text-sm text-red-600">{error}</li>
              ))}
            </ul>
          </section>
        )}

        <section className="border p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Actions to Debug</h2>
          <div className="space-y-2">
            <p>1. Open browser DevTools and check:</p>
            <ul className="list-disc list-inside ml-4 text-sm">
              <li>Network tab for failed requests (especially to clerk.accounts.dev)</li>
              <li>Console for JavaScript errors</li>
              <li>Elements tab to see if Clerk components are hidden</li>
            </ul>
            <p>2. Test links:</p>
            <ul className="list-disc list-inside ml-4">
              <li><a href="/pfinni/sign-in" className="text-blue-600 underline">Go to /pfinni/sign-in</a></li>
              <li><a href="/sign-in" className="text-blue-600 underline">Go to /sign-in</a></li>
              <li><a href="/pfinni/diagnostic" className="text-blue-600 underline">Go to /pfinni/diagnostic</a></li>
              <li><a href="/diagnostic" className="text-blue-600 underline">Go to /diagnostic</a></li>
            </ul>
          </div>
        </section>
      </div>
    </div>
  );
}