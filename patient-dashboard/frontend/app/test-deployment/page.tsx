export default function TestDeploymentPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Test Deployment Page
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          If you can see this, the deployment is working.
        </p>
        <p className="text-sm text-gray-500 mt-4">
          Build time: {new Date().toISOString()}
        </p>
      </div>
    </div>
  );
}