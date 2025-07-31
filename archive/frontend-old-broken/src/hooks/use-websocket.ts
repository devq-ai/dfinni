'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { WebSocketManager, WebSocketMessage, WebSocketConfig } from '@/lib/websocket'
import { useAuthStore } from '@/stores/auth-store'
import { logger } from '@/lib/logfire'

export interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  autoConnect?: boolean
}

export interface UseWebSocketReturn {
  isConnected: boolean
  connectionState: 'connecting' | 'connected' | 'disconnected'
  connect: () => void
  disconnect: () => void
  send: (message: WebSocketMessage) => void
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const { user, isAuthenticated } = useAuthStore()
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const wsManagerRef = useRef<WebSocketManager | null>(null)

  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    autoConnect = true,
  } = options

  // Create WebSocket URL with auth token
  const getWebSocketUrl = useCallback(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = process.env.NEXT_PUBLIC_WS_URL || window.location.host
    const token = localStorage.getItem('auth_token')
    
    return `${wsProtocol}//${host}/ws?token=${token}`
  }, [])

  // Initialize WebSocket connection
  const connect = useCallback(() => {
    if (!isAuthenticated || !user) {
      logger.userAction('websocket_connect_skipped', { reason: 'not_authenticated' })
      return
    }

    if (wsManagerRef.current?.isConnected()) {
      logger.userAction('websocket_already_connected')
      return
    }

    const config: WebSocketConfig = {
      url: getWebSocketUrl(),
      onMessage: (message) => {
        onMessage?.(message)
      },
      onConnect: () => {
        setConnectionState('connected')
        onConnect?.()
      },
      onDisconnect: () => {
        setConnectionState('disconnected')
        onDisconnect?.()
      },
      onError: (error) => {
        onError?.(error)
      },
    }

    setConnectionState('connecting')
    wsManagerRef.current = new WebSocketManager(config)
    wsManagerRef.current.connect()
  }, [isAuthenticated, user, getWebSocketUrl, onMessage, onConnect, onDisconnect, onError])

  // Disconnect WebSocket
  const disconnect = useCallback(() => {
    if (wsManagerRef.current) {
      wsManagerRef.current.disconnect()
      wsManagerRef.current = null
      setConnectionState('disconnected')
    }
  }, [])

  // Send message
  const send = useCallback((message: WebSocketMessage) => {
    if (!wsManagerRef.current) {
      logger.error('Cannot send message: WebSocket not initialized')
      return
    }

    wsManagerRef.current.send(message)
  }, [])

  // Auto-connect when authenticated
  useEffect(() => {
    if (autoConnect && isAuthenticated && user) {
      connect()
    }

    return () => {
      if (wsManagerRef.current) {
        disconnect()
      }
    }
  }, [autoConnect, isAuthenticated, user, connect, disconnect])

  // Reconnect on auth token change
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_token' && e.newValue && wsManagerRef.current) {
        logger.userAction('websocket_reconnect_on_token_change')
        disconnect()
        setTimeout(connect, 100)
      }
    }

    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [connect, disconnect])

  return {
    isConnected: connectionState === 'connected',
    connectionState,
    connect,
    disconnect,
    send,
  }
}