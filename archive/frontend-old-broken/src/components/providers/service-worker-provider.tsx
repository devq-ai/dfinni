'use client'

import { useEffect } from 'react'
import { logger } from '@/lib/logfire'

export function ServiceWorkerProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      // Only register in production
      if (process.env.NODE_ENV === 'production') {
        registerServiceWorker()
      }
    }
  }, [])

  const registerServiceWorker = async () => {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      })

      logger.info('Service Worker registered', {
        scope: registration.scope,
        state: registration.active?.state
      })

      // Check for updates periodically
      setInterval(() => {
        registration.update()
      }, 60 * 60 * 1000) // Check every hour

      // Handle updates
      registration.addEventListener('updatefound', () => {
        const newWorker = registration.installing
        if (newWorker) {
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'activated') {
              logger.info('Service Worker updated')
              // Optionally show update notification to user
            }
          })
        }
      })
    } catch (error) {
      logger.error('Service Worker registration failed', error)
    }
  }

  return <>{children}</>
}