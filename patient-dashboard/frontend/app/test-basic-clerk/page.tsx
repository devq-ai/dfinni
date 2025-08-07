'use client';

export default function TestBasicClerk() {
  return (
    <div className="p-8 bg-white text-black min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Basic Clerk Test</h1>
      <p>If you can see this text, the page is rendering.</p>
      
      <div className="mt-4 p-4 bg-gray-100 rounded">
        <p>Environment check:</p>
        <ul className="list-disc list-inside">
          <li>NODE_ENV: {process.env.NODE_ENV}</li>
          <li>Clerk Key exists: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ? 'Yes' : 'No'}</li>
          <li>Key value: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}</li>
        </ul>
      </div>
      
      <div className="mt-8">
        <p className="mb-4">Now testing basic Clerk import:</p>
        <SignInButton />
      </div>
    </div>
  );
}

// Import after component to isolate any import errors
import { SignInButton } from "@clerk/nextjs";