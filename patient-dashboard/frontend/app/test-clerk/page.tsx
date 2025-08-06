export default function TestClerkPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Clerk Environment Test</h1>
      <pre className="bg-gray-100 p-4 rounded">
        {JSON.stringify({
          NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
          NEXT_PUBLIC_CLERK_SIGN_IN_URL: process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL,
          NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
        }, null, 2)}
      </pre>
    </div>
  )
}