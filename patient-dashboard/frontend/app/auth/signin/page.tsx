'use client';

import { useEffect } from 'react';

export default function SimpleSignIn() {
  useEffect(() => {
    // Redirect to Clerk sign-in after a brief moment
    const timer = setTimeout(() => {
      window.location.href = '/pfinni/sign-in';
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          PFINNI Patient Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Redirecting to sign in...
        </p>
        <div className="mt-8">
          <a 
            href="/pfinni/sign-in" 
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Sign In
          </a>
        </div>
      </div>
    </div>
  );
}