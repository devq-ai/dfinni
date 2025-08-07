export default function ClerkTest() {
  return (
    <div className="p-8 bg-white text-black">
      <h1 className="text-2xl font-bold mb-4">Clerk Test Page</h1>
      <p>This page has a white background to ensure visibility.</p>
      <p>Publishable Key: {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}</p>
      <div className="mt-4">
        <a href="/sign-in" className="text-blue-600 underline">Go to Sign In</a>
      </div>
    </div>
  );
}