'use client';

import { useEffect, useState } from 'react';

export default function DiagnosticPage() {
  const [diagnostics, setDiagnostics] = useState<{
    location: string;
    pathname: string;
    basePath: string;
    clerkPublishableKey: string;
    envVars: Record<string, string | undefined>;
    windowObject: boolean;
    documentObject: boolean;
    clerkLoaded: boolean;
    errors: string[];
  }>({
    location: '',
    pathname: '',
    basePath: '',
    clerkPublishableKey: '',
    envVars: {},
    windowObject: false,
    documentObject: false,
    clerkLoaded: false,
    errors: []
  });

  useEffect(() => {
    try {
      const diag: typeof diagnostics = {
        location: window.location.href,
        pathname: window.location.pathname,
        basePath: (window as any).__NEXT_DATA__?.basePath || 'not set',
        clerkPublishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || 'not set',
        envVars: {
          NODE_ENV: process.env.NODE_ENV,
          NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
          NEXT_PUBLIC_CLERK_SIGN_IN_URL: process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL,
          NEXT_PUBLIC_CLERK_SIGN_UP_URL: process.env.NEXT_PUBLIC_CLERK_SIGN_UP_URL,
        },
        windowObject: typeof window !== 'undefined',
        documentObject: typeof document !== 'undefined',
        clerkLoaded: !!(window as any).Clerk,
        errors: []
      };

      // Check if Clerk script is in DOM
      const clerkScript = document.querySelector('script[src*="clerk"]');
      if (clerkScript) {
        diag.errors.push(`Clerk script found: ${clerkScript.getAttribute('src')}`);
      } else {
        diag.errors.push('No Clerk script found in DOM');
      }

      setDiagnostics(diag);
    } catch (error: any) {
      setDiagnostics(prev => ({
        ...prev,
        errors: [...prev.errors, error.message]
      }));
    }
  }, []);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Cloudflare Deployment Diagnostics</h1>
      
      <div className="space-y-4">
        <section className="bg-gray-100 p-4 rounded">
          <h2 className="font-bold mb-2">Location Info</h2>
          <pre className="text-sm overflow-auto">
{JSON.stringify({
  location: diagnostics.location,
  pathname: diagnostics.pathname,
  basePath: diagnostics.basePath
}, null, 2)}
          </pre>
        </section>

        <section className="bg-gray-100 p-4 rounded">
          <h2 className="font-bold mb-2">Environment Variables</h2>
          <pre className="text-sm overflow-auto">
{JSON.stringify({
  clerkPublishableKey: diagnostics.clerkPublishableKey,
  ...diagnostics.envVars
}, null, 2)}
          </pre>
        </section>

        <section className="bg-gray-100 p-4 rounded">
          <h2 className="font-bold mb-2">Runtime Checks</h2>
          <pre className="text-sm overflow-auto">
{JSON.stringify({
  windowObject: diagnostics.windowObject,
  documentObject: diagnostics.documentObject,
  clerkLoaded: diagnostics.clerkLoaded
}, null, 2)}
          </pre>
        </section>

        {diagnostics.errors.length > 0 && (
          <section className="bg-red-100 p-4 rounded">
            <h2 className="font-bold mb-2">Errors/Warnings</h2>
            <ul className="list-disc list-inside">
              {diagnostics.errors.map((error, i) => (
                <li key={i} className="text-sm">{error}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}