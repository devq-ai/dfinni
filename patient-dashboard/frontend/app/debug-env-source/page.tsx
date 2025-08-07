export default function DebugEnvSourcePage() {
  // Check all possible sources
  const sources = {
    processEnv: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
    nodeEnv: process.env.NODE_ENV,
    allEnvKeys: Object.keys(process.env).filter(k => k.includes('CLERK')).join(', '),
  };
  
  return (
    <div className="p-8 max-w-4xl mx-auto font-mono text-sm">
      <h1 className="text-2xl font-bold mb-4">Environment Debug</h1>
      <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-auto">
{JSON.stringify(sources, null, 2)}
      </pre>
      <div className="mt-4 p-4 bg-red-100 dark:bg-red-900 rounded">
        <p className="font-bold">Looking for source of:</p>
        <p>pk_live_Y2xlcmsuZGV2cS5haSQ</p>
      </div>
      <div className="mt-4">
        <p>Build timestamp: {new Date().toISOString()}</p>
      </div>
    </div>
  );
}