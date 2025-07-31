'use client'

import { ReactNode, useEffect } from 'react'
import { Sidebar } from './sidebar'
import { Header } from './header'
import { logger } from '@/lib/logfire'
import { cn } from '@/lib/utils'
import { WebSocketProvider } from '@/contexts/websocket-context'
import { RealTimeAlerts } from '@/components/alerts/real-time-alerts'

interface DashboardLayoutProps {
  children: ReactNode
  className?: string
}

export function DashboardLayout({ children, className }: DashboardLayoutProps) {
  useEffect(() => {
    logger.componentMount('DashboardLayout')
    return () => {
      logger.componentUnmount('DashboardLayout')
    }
  }, [])

  return (
    <WebSocketProvider>
      <div className="flex h-screen bg-zinc-950 text-zinc-100">
        {/* Sidebar */}
        <Sidebar />

        {/* Main content area */}
        <div className="flex flex-1 flex-col">
          {/* Header */}
          <Header />

          {/* Main content */}
          <main 
            className={cn(
              "flex-1 overflow-y-auto bg-zinc-950",
              className
            )}
          >
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {children}
            </div>
          </main>
        </div>
      </div>
      
      {/* Real-time Alerts */}
      <RealTimeAlerts position="top-right" />
    </WebSocketProvider>
  )
}