import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useWebSocket } from './use-websocket'
import { useAuthStore } from '@/stores/auth-store'
import { WebSocketManager } from '@/lib/websocket'

// Mock dependencies
vi.mock('@/stores/auth-store', () => ({
  useAuthStore: vi.fn(),
}))

vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

// Create WebSocketManager mock at module level
const mockWebSocketManager = {
  connect: vi.fn(),
  disconnect: vi.fn(),
  send: vi.fn(),
  isConnected: vi.fn().mockReturnValue(false),
  getState: vi.fn().mockReturnValue('disconnected'),
}

vi.mock('@/lib/websocket', () => {
  return {
    WebSocketManager: vi.fn().mockImplementation(() => mockWebSocketManager),
  }
})

describe('useWebSocket', () => {
  const mockUser = {
    id: '123',
    email: 'test@example.com',
    name: 'Test User',
  }

  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    
    vi.mocked(useAuthStore).mockReturnValue({
      user: mockUser,
      isAuthenticated: true,
    } as any)
  })

  it('initializes with disconnected state', () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }))

    expect(result.current.isConnected).toBe(false)
    expect(result.current.connectionState).toBe('disconnected')
  })

  it('auto-connects when authenticated', async () => {
    localStorage.setItem('auth_token', 'test-token')
    
    const { result } = renderHook(() => useWebSocket({ autoConnect: true }))

    await act(async () => {
      // Give effect time to run
      await new Promise(resolve => setTimeout(resolve, 0))
    })

    expect(result.current.connectionState).toBe('connecting')
  })

  it('does not connect when not authenticated', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: null,
      isAuthenticated: false,
    } as any)

    const { result } = renderHook(() => useWebSocket({ autoConnect: true }))

    act(() => {
      result.current.connect()
    })

    expect(result.current.connectionState).toBe('disconnected')
  })

  it('handles manual connect and disconnect', () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: false }))

    act(() => {
      result.current.connect()
    })

    expect(result.current.connectionState).toBe('connecting')

    act(() => {
      result.current.disconnect()
    })

    expect(result.current.connectionState).toBe('disconnected')
  })

  it('calls onMessage callback when message received', () => {
    const onMessage = vi.fn()
    let messageHandler: any
    
    // Capture the onMessage handler during initialization
    vi.mocked(WebSocketManager).mockImplementation((config: any) => {
      messageHandler = config.onMessage
      return mockWebSocketManager
    })

    renderHook(() => useWebSocket({ onMessage, autoConnect: true }))

    const testMessage = {
      type: 'patient_status_update' as const,
      data: { test: 'data' },
      timestamp: new Date().toISOString(),
    }

    act(() => {
      messageHandler(testMessage)
    })

    expect(onMessage).toHaveBeenCalledWith(testMessage)
  })

  it('calls lifecycle callbacks', () => {
    const onConnect = vi.fn()
    const onDisconnect = vi.fn()
    const onError = vi.fn()
    
    let connectHandler: any
    let disconnectHandler: any
    let errorHandler: any
    
    // Capture the lifecycle handlers during initialization
    vi.mocked(WebSocketManager).mockImplementation((config: any) => {
      connectHandler = config.onConnect
      disconnectHandler = config.onDisconnect
      errorHandler = config.onError
      return mockWebSocketManager
    })

    const { result } = renderHook(() => useWebSocket({
      onConnect,
      onDisconnect,
      onError,
      autoConnect: true,
    }))

    // Mock the state getters for the correct state transitions
    mockWebSocketManager.isConnected.mockReturnValue(true)
    mockWebSocketManager.getState.mockReturnValue('connected')
    
    act(() => {
      connectHandler()
    })
    expect(onConnect).toHaveBeenCalled()
    expect(result.current.connectionState).toBe('connected')

    // Mock disconnect state
    mockWebSocketManager.isConnected.mockReturnValue(false)
    mockWebSocketManager.getState.mockReturnValue('disconnected')
    
    act(() => {
      disconnectHandler()
    })
    expect(onDisconnect).toHaveBeenCalled()
    expect(result.current.connectionState).toBe('disconnected')

    const error = new Event('error')
    act(() => {
      errorHandler(error)
    })
    expect(onError).toHaveBeenCalledWith(error)
  })

  it('reconnects on auth token change', () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: true }))

    // Simulate storage event
    act(() => {
      const event = new StorageEvent('storage', {
        key: 'auth_token',
        newValue: 'new-token',
        oldValue: 'old-token',
      })
      window.dispatchEvent(event)
    })

    // Should trigger reconnect
    expect(result.current.connectionState).toBe('disconnected')
  })

  it('sends messages through WebSocket manager', () => {
    const { result } = renderHook(() => useWebSocket({ autoConnect: true }))

    const message = {
      type: 'patient_status_update' as const,
      data: { test: 'data' },
      timestamp: new Date().toISOString(),
    }

    act(() => {
      result.current.send(message)
    })

    expect(mockWebSocketManager.send).toHaveBeenCalledWith(message)
  })
})