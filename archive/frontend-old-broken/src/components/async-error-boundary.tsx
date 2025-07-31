'use client'

import { Suspense, ReactNode } from 'react'
import { ErrorBoundary } from './error-boundary'

interface AsyncErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  loadingFallback?: ReactNode
  onError?: (error: Error, errorInfo: any) => void
}

export function AsyncErrorBoundary({
  children,
  fallback,
  loadingFallback,
  onError
}: AsyncErrorBoundaryProps) {
  return (
    <ErrorBoundary fallback={fallback} onError={onError}>
      <Suspense fallback={loadingFallback || <DefaultLoadingFallback />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  )
}

function DefaultLoadingFallback() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="flex items-center space-x-3">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        <p className="text-zinc-400">Loading...</p>
      </div>
    </div>
  )
}