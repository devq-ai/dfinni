'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to dashboard
    router.push('/dashboard')
  }, [router])

  return (
    <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-zinc-100 mb-4">
          Patient Management Dashboard
        </h1>
        <p className="text-zinc-400">Redirecting to dashboard...</p>
      </div>
    </div>
  )
}
