'use client';

import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            PFINNI Patient Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Sign in to access your dashboard
          </p>
        </div>
        <SignIn 
          path="/sign-in"
          routing="path"
          signUpUrl="/sign-up"
          afterSignInUrl="/dashboard"
          appearance={{
            elements: {
              rootBox: "mx-auto",
              card: "bg-white dark:bg-gray-800 shadow-xl border border-gray-200 dark:border-gray-700",
              headerTitle: "text-gray-900 dark:text-gray-100",
              headerSubtitle: "text-gray-600 dark:text-gray-400",
              socialButtonsBlockButton: "bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600",
              formFieldLabel: "text-gray-700 dark:text-gray-300",
              formFieldInput: "bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100",
              footerActionLink: "text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
            }
          }}
        />
      </div>
    </div>
  );
}