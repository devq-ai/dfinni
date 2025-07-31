import { ReactNode } from 'react'
import { vi } from 'vitest'
import { WebSocketContext } from '@/contexts/websocket-context'
import type { WebSocketContextType } from '@/contexts/websocket-context'

export const mockWebSocketContext: WebSocketContextType = {
  isConnected: false,
  connectionState: 'disconnected',
  connect: vi.fn(),
  disconnect: vi.fn(),
  send: vi.fn(),
  lastMessage: null,
  subscribeToPatientUpdates: vi.fn(),
  unsubscribeFromPatientUpdates: vi.fn(),
  subscribeToAlerts: vi.fn(),
  unsubscribeFromAlerts: vi.fn(),
}

export function MockWebSocketProvider({ 
  children,
  value = mockWebSocketContext 
}: { 
  children: ReactNode
  value?: Partial<WebSocketContextType>
}) {
  return (
    <WebSocketContext.Provider value={{ ...mockWebSocketContext, ...value }}>
      {children}
    </WebSocketContext.Provider>
  )
}