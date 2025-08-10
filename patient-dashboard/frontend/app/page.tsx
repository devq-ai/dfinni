// Last Updated: 2025-08-09T20:12:00-06:00
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()
  
  useEffect(() => {
    router.push('/sign-in')
  }, [router])
  
  return null
}