'use client'

import { useState, useEffect } from 'react'
import { useWebSocketContext } from '@/contexts/websocket-context'
import { logger } from '@/lib/logfire'
import { Bell, AlertCircle, AlertTriangle, Info, X, ExternalLink } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'
import { Button } from '@/components/ui/Button'

export interface Alert {
  id: string
  type: 'critical' | 'warning' | 'info' | 'success'
  title: string
  message: string
  patientId?: string
  patientName?: string
  source: string
  read: boolean
  resolved: boolean
  createdAt: string
  expiresAt?: string
  actions?: {
    label: string
    href?: string
    onClick?: () => void
  }[]
}

interface RealTimeAlertsProps {
  maxAlerts?: number
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
  className?: string
}

export function RealTimeAlerts({ 
  maxAlerts = 5, 
  position = 'top-right',
  className 
}: RealTimeAlertsProps) {
  const { isConnected } = useWebSocketContext()
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isMinimized, setIsMinimized] = useState(false)

  useEffect(() => {
    const handleNewAlert = (event: CustomEvent<Alert>) => {
      logger.userAction('real_time_alert_received', { 
        alertId: event.detail.id,
        type: event.detail.type 
      })
      
      setAlerts(prev => {
        const newAlerts = [event.detail, ...prev]
        // Keep only the most recent alerts
        return newAlerts.slice(0, maxAlerts)
      })

      // Auto-dismiss info alerts after 10 seconds
      if (event.detail.type === 'info') {
        setTimeout(() => {
          dismissAlert(event.detail.id)
        }, 10000)
      }
    }

    window.addEventListener('new-alert', handleNewAlert as EventListener)
    return () => {
      window.removeEventListener('new-alert', handleNewAlert as EventListener)
    }
  }, [maxAlerts])

  const dismissAlert = (alertId: string) => {
    logger.userAction('dismiss_alert', { alertId })
    setAlerts(prev => prev.filter(alert => alert.id !== alertId))
  }

  const markAsRead = (alertId: string) => {
    logger.userAction('mark_alert_read', { alertId })
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId ? { ...alert, read: true } : alert
      )
    )
  }

  const getAlertIcon = (type: Alert['type']) => {
    switch (type) {
      case 'critical':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'info':
        return <Info className="h-5 w-5 text-blue-500" />
      case 'success':
        return <Bell className="h-5 w-5 text-green-500" />
    }
  }

  const getAlertStyles = (type: Alert['type']) => {
    switch (type) {
      case 'critical':
        return 'border-red-500/50 bg-red-500/10'
      case 'warning':
        return 'border-yellow-500/50 bg-yellow-500/10'
      case 'info':
        return 'border-blue-500/50 bg-blue-500/10'
      case 'success':
        return 'border-green-500/50 bg-green-500/10'
    }
  }

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
  }

  if (!isConnected || alerts.length === 0) {
    return null
  }

  const unreadCount = alerts.filter(a => !a.read).length

  return (
    <div
      className={cn(
        'fixed z-50 w-96 max-w-[calc(100vw-2rem)]',
        positionClasses[position],
        className
      )}
    >
      {/* Header */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-t-lg p-3 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bell className="h-4 w-4 text-zinc-400" />
          <span className="text-sm font-medium text-zinc-100">
            Real-time Alerts
          </span>
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white text-xs rounded-full px-2 py-0.5">
              {unreadCount}
            </span>
          )}
        </div>
        <button
          onClick={() => setIsMinimized(!isMinimized)}
          className="text-zinc-400 hover:text-zinc-100"
        >
          {isMinimized ? '▼' : '▲'}
        </button>
      </div>

      {/* Alerts Container */}
      {!isMinimized && (
        <div className="bg-zinc-950 border-x border-b border-zinc-800 rounded-b-lg max-h-96 overflow-y-auto">
          {alerts.map((alert, index) => (
            <div
              key={alert.id}
              className={cn(
                'p-4 border-b border-zinc-800 last:border-b-0 transition-all',
                !alert.read && 'bg-zinc-900/50',
                index === 0 && 'animate-slide-in'
              )}
              onClick={() => !alert.read && markAsRead(alert.id)}
            >
              <div className="flex items-start space-x-3">
                {getAlertIcon(alert.type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className={cn(
                        'text-sm font-medium text-zinc-100',
                        !alert.read && 'font-semibold'
                      )}>
                        {alert.title}
                      </h4>
                      <p className="text-xs text-zinc-400 mt-1">
                        {alert.message}
                      </p>
                      {alert.patientName && (
                        <p className="text-xs text-zinc-500 mt-1">
                          Patient: {alert.patientName}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        dismissAlert(alert.id)
                      }}
                      className="text-zinc-500 hover:text-zinc-300"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-zinc-500">
                      {formatDistanceToNow(new Date(alert.createdAt), { 
                        addSuffix: true 
                      })}
                    </span>
                    {alert.actions && alert.actions.length > 0 && (
                      <div className="flex items-center space-x-2">
                        {alert.actions.map((action, idx) => (
                          <Button
                            key={idx}
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              action.onClick?.()
                              logger.userAction('alert_action_clicked', {
                                alertId: alert.id,
                                action: action.label
                              })
                            }}
                            className="h-6 px-2 text-xs"
                          >
                            {action.label}
                            {action.href && <ExternalLink className="ml-1 h-3 w-3" />}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Alert type indicator */}
              <div className={cn(
                'absolute left-0 top-0 bottom-0 w-1',
                getAlertStyles(alert.type).replace('border-', 'bg-').replace('/50', '')
              )} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}