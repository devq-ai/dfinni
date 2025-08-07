'use client';

import { useAuth } from '@clerk/nextjs';

export default function TestClerkStatus() {
  const { isLoaded, userId, sessionId } = useAuth();

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Clerk Status Test</h1>
      <div className="space-y-2">
        <p>Clerk Loaded: {isLoaded ? 'Yes' : 'No'}</p>
        <p>User ID: {userId || 'Not signed in'}</p>
        <p>Session ID: {sessionId || 'No session'}</p>
        <p>Publishable Key: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}</p>
      </div>
    </div>
  );
}