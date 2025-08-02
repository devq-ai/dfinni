import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-[#0f0f0f]">
      <SignUp 
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "bg-white dark:bg-[#141414] shadow-xl",
            headerTitle: "text-gray-900 dark:text-gray-100",
            headerSubtitle: "text-gray-600 dark:text-gray-400",
            socialButtonsBlockButton: "bg-white dark:bg-[#3e3e3e] border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700",
            formFieldLabel: "text-gray-700 dark:text-gray-300",
            formFieldInput: "bg-white dark:bg-[#3e3e3e] border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100",
            footerActionLink: "text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
          }
        }}
        afterSignUpUrl="/dashboard"
        signInUrl="/sign-in"
      />
    </div>
  );
}