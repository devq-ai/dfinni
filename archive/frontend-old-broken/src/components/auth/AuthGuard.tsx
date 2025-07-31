'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuthStore } from '@/stores/auth-store'
import { logger } from '@/lib/logfire'

interface AuthGuardProps {
  children: React.ReactNode
  requiredRoles?: string[]
  fallbackUrl?: string
}

export function AuthGuard({ 
  children, 
  requiredRoles = [], 
  fallbackUrl = '/login' 
}: AuthGuardProps) {
  const router = useRouter()
  const pathname = usePathname()
  const { isAuthenticated, user, isLoading, refreshUser } = useAuthStore()

  useEffect(() => {
    logger.componentMount('AuthGuard', { 
      pathname, 
      requiredRoles,
      isAuthenticated 
    })

    // Check authentication on mount
    if (!isAuthenticated && !isLoading) {
      refreshUser()
    }

    return () => {
      logger.componentUnmount('AuthGuard')
    }
  }, [pathname])

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        logger.userAction('auth_guard_redirect', {
          reason: 'not_authenticated',
          from: pathname,
          to: fallbackUrl
        })
        
        const redirectUrl = `${fallbackUrl}?from=${encodeURIComponent(pathname)}`
        router.push(redirectUrl)
      } else if (requiredRoles.length > 0 && user) {
        const hasRequiredRole = requiredRoles.includes(user.role)
        
        if (!hasRequiredRole) {
          logger.userAction('auth_guard_redirect', {
            reason: 'insufficient_role',
            userRole: user.role,
            requiredRoles,
            from: pathname,
            to: '/dashboard'
          })
          
          router.push('/dashboard')
        }
      }
    }
  }, [isAuthenticated, isLoading, user, pathname, requiredRoles, fallbackUrl, router])

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-zinc-400">Loading...</p>
        </div>
      </div>
    )
  }

  // Don't render children if not authenticated
  if (!isAuthenticated) {
    return null
  }

  // Don't render children if role requirements not met
  if (requiredRoles.length > 0 && user && !requiredRoles.includes(user.role)) {
    return null
  }

  return <>{children}</>
}