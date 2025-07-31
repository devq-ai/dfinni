'use client'

import { useWebSocketContext } from '@/contexts/websocket-context'
import { cn } from '@/lib/utils'
import { Wifi, WifiOff, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { logger } from '@/lib/logfire'

interface ConnectionStatusProps {
  className?: string
  showLabel?: boolean
}

export function ConnectionStatus({ className, showLabel = true }: ConnectionStatusProps) {
  const { connectionState, connect, disconnect } = useWebSocketContext()

  const handleToggleConnection = () => {
    if (connectionState === 'connected') {
      logger.userAction('manual_disconnect_websocket')
      disconnect()
    } else if (connectionState === 'disconnected') {
      logger.userAction('manual_connect_websocket')
      connect()
    }
  }

  const statusConfig = {
    connected: {
      icon: Wifi,
      label: 'Connected',
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/20',
    },
    connecting: {
      icon: Loader2,
      label: 'Connecting...',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/20',
    },
    disconnected: {
      icon: WifiOff,
      label: 'Disconnected',
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/20',
    },
  }

  const config = statusConfig[connectionState]
  const Icon = config.icon

  return (
    <div
      className={cn(
        'flex items-center space-x-2 px-3 py-1.5 rounded-full border',
        config.bgColor,
        config.borderColor,
        className
      )}
    >
      <Icon
        className={cn(
          'h-4 w-4',
          config.color,
          connectionState === 'connecting' && 'animate-spin'
        )}
      />
      {showLabel && (
        <span className={cn('text-xs font-medium', config.color)}>
          {config.label}
        </span>
      )}
      {connectionState !== 'connecting' && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleToggleConnection}
          className="h-6 px-2 text-xs"
        >
          {connectionState === 'connected' ? 'Disconnect' : 'Connect'}
        </Button>
      )}
    </div>
  )
}