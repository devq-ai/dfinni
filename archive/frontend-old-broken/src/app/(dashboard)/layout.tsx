'use client'

import { Suspense, lazy, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { performanceMonitor, measureRouteChange } from '@/lib/performance'
import { logger } from '@/lib/logfire'

// Lazy load heavy components
const Header = lazy(() => import('@/components/layout/header').then(mod => ({
  default: mod.Header
})))

const Sidebar = lazy(() => import('@/components/layout/sidebar').then(mod => ({
  default: mod.Sidebar
})))

// Loading fallbacks
const HeaderSkeleton = () => (
  <div className="h-16 bg-zinc-900 border-b border-zinc-800 animate-pulse" />
)

const SidebarSkeleton = () => (
  <div className="w-64 h-full bg-zinc-900 border-r border-zinc-800 animate-pulse" />
)

const ContentSkeleton = () => (
  <div className="flex-1 p-6">
    <div className="space-y-4">
      <div className="h-8 w-1/3 bg-zinc-800 rounded animate-pulse" />
      <div className="h-64 bg-zinc-800 rounded animate-pulse" />
    </div>
  </div>
)

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()

  useEffect(() => {
    // Track route changes
    measureRouteChange(pathname)
    
    // Temporarily disable performance reporting to prevent crashes
    // const timer = setTimeout(() => {
    //   if (performanceMonitor) {
    //     performanceMonitor.reportToLogfire()
    //   }
    // }, 3000)
    
    // return () => clearTimeout(timer)
  }, [pathname])

  useEffect(() => {
    logger.componentMount('DashboardLayout')
    
    // Set up performance monitoring
    if (performanceMonitor) {
      // Temporarily disable periodic reporting
      // const interval = setInterval(() => {
      //   performanceMonitor.reportToLogfire()
      // }, 30000)
      
      return () => {
        // clearInterval(interval)
        logger.componentUnmount('DashboardLayout')
      }
    }
  }, [])

  return (
    <div className="flex h-screen bg-zinc-950">
      {/* Sidebar */}
      <Suspense fallback={<SidebarSkeleton />}>
        <Sidebar />
      </Suspense>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Suspense fallback={<HeaderSkeleton />}>
          <Header />
        </Suspense>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-zinc-950">
          <Suspense fallback={<ContentSkeleton />}>
            {children}
          </Suspense>
        </main>
      </div>
    </div>
  )
}