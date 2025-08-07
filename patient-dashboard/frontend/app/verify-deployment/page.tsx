export default function VerifyDeploymentPage() {
  const deploymentTime = "2025-08-07T03:45:00Z";
  
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Deployment Verification</h1>
      <div className="space-y-4">
        <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded">
          <p className="font-semibold">Expected Values (from Cloudflare dashboard):</p>
          <p className="font-mono text-sm">Key: pk_test_Y2xlYW4tc3RhbmctMTQtNTEuY2xlcmsuYWNjb3VudHMuZGV2JA</p>
          <p className="font-mono text-sm">Domain: clean-stang-14-51.clerk.accounts.dev</p>
        </div>
        
        <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded">
          <p className="font-semibold">Actual Values:</p>
          <p className="font-mono text-sm">Key: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}</p>
          <p className="font-mono text-sm">Domain: {process.env.NEXT_PUBLIC_CLERK_DOMAIN}</p>
        </div>
        
        <div className="p-4 bg-green-100 dark:bg-green-900 rounded">
          <p className="font-semibold">Deployment Info:</p>
          <p className="font-mono text-sm">Last Update: {deploymentTime}</p>
          <p className="font-mono text-sm">Build Time: {new Date().toISOString()}</p>
        </div>
      </div>
    </div>
  );
}