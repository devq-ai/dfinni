'use client';

import { useClerk } from '@clerk/nextjs';
import { useEffect, useState } from 'react';

export default function ClerkDebugPage() {
  const clerk = useClerk();
  const [debugInfo, setDebugInfo] = useState<any>({});

  useEffect(() => {
    const info = {
      loaded: clerk.loaded,
      publishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
      domain: process.env.NEXT_PUBLIC_CLERK_DOMAIN,
      signInUrl: process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL,
      version: clerk.version,
      frontendApi: clerk.frontendApi,
    };
    setDebugInfo(info);
  }, [clerk]);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Clerk Debug Information</h1>
      <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-auto">
        {JSON.stringify(debugInfo, null, 2)}
      </pre>
      <div className="mt-4">
        <p>Window location: {typeof window !== 'undefined' ? window.location.href : 'N/A'}</p>
      </div>
    </div>
  );
}