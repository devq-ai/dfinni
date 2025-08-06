'use client'

import { useAuth, useClerk } from '@clerk/nextjs'

export default function DebugClerkPage() {
  const { isLoaded, userId, sessionId } = useAuth()
  const clerk = useClerk()

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Clerk Debug Info</h1>
      
      <div className="space-y-4 font-mono text-sm">
        <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded">
          <h2 className="font-bold mb-2">Auth State:</h2>
          <p>Is Loaded: {isLoaded ? 'Yes' : 'No'}</p>
          <p>User ID: {userId || 'None'}</p>
          <p>Session ID: {sessionId || 'None'}</p>
        </div>

        <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded">
          <h2 className="font-bold mb-2">Clerk Instance:</h2>
          <p>Clerk Loaded: {clerk ? 'Yes' : 'No'}</p>
          <p>Publishable Key: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.substring(0, 20)}...</p>
          <p>Sign In URL: {process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL}</p>
        </div>

        <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded">
          <h2 className="font-bold mb-2">Build Info:</h2>
          <p>NODE_ENV: {process.env.NODE_ENV}</p>
          <p>API URL: {process.env.NEXT_PUBLIC_API_URL}</p>
        </div>

        <div className="mt-8">
          <a href="/sign-in" className="inline-block px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Go to Sign In
          </a>
        </div>
      </div>
    </div>
  )
}