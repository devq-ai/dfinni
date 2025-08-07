export default function StaticTest() {
  return (
    <div className="p-8 bg-white text-black min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Static Test Page</h1>
      <p>This is a static page with no client components.</p>
      <p>Clerk Publishable Key from env: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}</p>
      <a href="/sign-in" className="text-blue-600 underline">Go to Sign In</a>
    </div>
  );
}