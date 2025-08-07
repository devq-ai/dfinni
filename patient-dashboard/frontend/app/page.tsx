// Updated: 2025-08-05T22:30:00-06:00
import { SignIn } from '@clerk/nextjs'

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-[#0f0f0f]">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-8 text-gray-900 dark:text-gray-100">
          PFINNI Patient Dashboard
        </h1>
        <SignIn routing="hash" redirectUrl="/dashboard" />
      </div>
    </div>
  )
}