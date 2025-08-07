export default function TestEnvPage() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Environment Test</h1>
      <div className="space-y-2">
        <p>NODE_ENV: {process.env.NODE_ENV}</p>
        <p>NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}</p>
        <p>NEXT_PUBLIC_CLERK_DOMAIN: {process.env.NEXT_PUBLIC_CLERK_DOMAIN}</p>
        <p>NEXT_PUBLIC_API_URL: {process.env.NEXT_PUBLIC_API_URL}</p>
      </div>
      <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded">
        <p className="font-mono text-sm">
          Build Time: {new Date().toISOString()}
        </p>
      </div>
    </div>
  );
}