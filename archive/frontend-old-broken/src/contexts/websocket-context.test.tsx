import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, renderHook, waitFor } from '@testing-library/react'
import { WebSocketProvider, useWebSocketContext, WebSocketContext } from './websocket-context'
import { useWebSocket } from '@/hooks/use-websocket'
import { usePatientStore } from '@/stores/patient-store'
import { useDashboardStore } from '@/stores/dashboard-store'
import type { WebSocketMessage } from '@/lib/websocket'

// Mock dependencies
vi.mock('@/hooks/use-websocket', () => ({
  useWebSocket: vi.fn(),
}))

vi.mock('@/stores/patient-store', () => ({
  usePatientStore: vi.fn(),
}))

vi.mock('@/stores/dashboard-store', () => ({
  useDashboardStore: vi.fn(),
}))

vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

vi.mock('@/lib/toast', () => ({
  toast: {
    success: vi.fn(),
    warning: vi.fn(),
    error: vi.fn(),
  },
}))

describe('WebSocketContext', () => {
  const mockWebSocketReturn = {
    isConnected: false,
    connectionState: 'disconnected' as const,
    connect: vi.fn(),
    disconnect: vi.fn(),
    send: vi.fn(),
    lastMessage: null,
  }

  const mockFetchPatients = vi.fn()
  const mockUpdatePatient = vi.fn()
  const mockFetchActivities = vi.fn()
  const mockFetchMetrics = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(useWebSocket).mockReturnValue(mockWebSocketReturn)
    
    vi.mocked(usePatientStore).mockReturnValue({
      fetchPatients: mockFetchPatients,
      updatePatient: mockUpdatePatient,
    } as any)

    vi.mocked(useDashboardStore).mockReturnValue({
      fetchActivities: mockFetchActivities,
      fetchMetrics: mockFetchMetrics,
    } as any)
  })

  it('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    expect(() => {
      renderHook(() => useWebSocketContext())
    }).toThrow('useWebSocketContext must be used within WebSocketProvider')
    
    consoleSpy.mockRestore()
  })

  it('provides WebSocket context to children', () => {
    const { result } = renderHook(() => useWebSocketContext(), {
      wrapper: ({ children }) => <WebSocketProvider>{children}</WebSocketProvider>,
    })

    expect(result.current).toBeDefined()
    expect(result.current.isConnected).toBe(false)
    expect(result.current.connectionState).toBe('disconnected')
    expect(result.current.connect).toBeDefined()
    expect(result.current.disconnect).toBeDefined()
    expect(result.current.send).toBeDefined()
    expect(result.current.subscribeToPatientUpdates).toBeDefined()
    expect(result.current.unsubscribeFromPatientUpdates).toBeDefined()
    expect(result.current.subscribeToAlerts).toBeDefined()
    expect(result.current.unsubscribeFromAlerts).toBeDefined()
  })

  it('subscribes to alerts on connection', async () => {
    let onConnectCallback: (() => void) | undefined

    vi.mocked(useWebSocket).mockImplementation((config) => {
      onConnectCallback = config?.onConnect
      return mockWebSocketReturn
    })

    render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    // Trigger onConnect
    onConnectCallback?.()

    await waitFor(() => {
      expect(mockWebSocketReturn.send).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'subscribe',
          data: {
            channel: 'alerts',
          },
        })
      )
    })
  })

  it('handles patient status update messages', async () => {
    let onMessageCallback: ((message: WebSocketMessage) => void) | undefined

    vi.mocked(useWebSocket).mockImplementation((config) => {
      onMessageCallback = config?.onMessage
      return mockWebSocketReturn
    })

    render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    const statusUpdateMessage: WebSocketMessage = {
      type: 'patient_status_update',
      data: {
        patientId: '123',
        status: 'Active',
        oldStatus: 'Inquiry',
        patientName: 'John Doe',
      },
      timestamp: new Date().toISOString(),
    }

    // Trigger message handler
    onMessageCallback?.(statusUpdateMessage)

    await waitFor(() => {
      expect(mockUpdatePatient).toHaveBeenCalledWith('123', { status: 'Active' })
      expect(mockFetchPatients).toHaveBeenCalled()
    })

    // Check if custom event was dispatched
    const eventHandler = vi.fn()
    window.addEventListener('patient-status-update' as any, eventHandler)
    
    onMessageCallback?.(statusUpdateMessage)
    
    await waitFor(() => {
      expect(eventHandler).toHaveBeenCalled()
    })
    
    window.removeEventListener('patient-status-update' as any, eventHandler)
  })

  it('handles new alert messages', async () => {
    let onMessageCallback: ((message: WebSocketMessage) => void) | undefined

    vi.mocked(useWebSocket).mockImplementation((config) => {
      onMessageCallback = config?.onMessage
      return mockWebSocketReturn
    })

    render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    const alertMessage: WebSocketMessage = {
      type: 'new_alert',
      data: {
        id: 'alert-123',
        type: 'warning',
        title: 'Test Alert',
        message: 'This is a test',
      },
      timestamp: new Date().toISOString(),
    }

    // Add event listener
    const eventHandler = vi.fn()
    window.addEventListener('new-alert' as any, eventHandler)

    // Trigger message handler
    onMessageCallback?.(alertMessage)

    await waitFor(() => {
      expect(eventHandler).toHaveBeenCalledWith(
        expect.objectContaining({
          detail: alertMessage.data,
        })
      )
    })

    window.removeEventListener('new-alert' as any, eventHandler)
  })

  it('handles new activity messages', async () => {
    let onMessageCallback: ((message: WebSocketMessage) => void) | undefined

    vi.mocked(useWebSocket).mockImplementation((config) => {
      onMessageCallback = config?.onMessage
      return mockWebSocketReturn
    })

    render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    const activityMessage: WebSocketMessage = {
      type: 'new_activity',
      data: {
        id: 'activity-123',
        type: 'patient_update',
        message: 'Patient status changed',
      },
      timestamp: new Date().toISOString(),
    }

    // Trigger message handler
    onMessageCallback?.(activityMessage)

    await waitFor(() => {
      expect(mockFetchActivities).toHaveBeenCalled()
      expect(mockFetchMetrics).toHaveBeenCalled()
    })
  })

  it('subscribes to patient updates', () => {
    const { result } = renderHook(() => useWebSocketContext(), {
      wrapper: ({ children }) => <WebSocketProvider>{children}</WebSocketProvider>,
    })

    result.current.subscribeToPatientUpdates('patient-123')

    expect(mockWebSocketReturn.send).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'subscribe',
        data: {
          channel: 'patient_updates',
          patientId: 'patient-123',
        },
      })
    )
  })

  it('unsubscribes from patient updates', () => {
    const { result } = renderHook(() => useWebSocketContext(), {
      wrapper: ({ children }) => <WebSocketProvider>{children}</WebSocketProvider>,
    })

    result.current.unsubscribeFromPatientUpdates('patient-123')

    expect(mockWebSocketReturn.send).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'unsubscribe',
        data: {
          channel: 'patient_updates',
          patientId: 'patient-123',
        },
      })
    )
  })

  it('subscribes to alerts channel', () => {
    const { result } = renderHook(() => useWebSocketContext(), {
      wrapper: ({ children }) => <WebSocketProvider>{children}</WebSocketProvider>,
    })

    result.current.subscribeToAlerts()

    expect(mockWebSocketReturn.send).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'subscribe',
        data: {
          channel: 'alerts',
        },
      })
    )
  })

  it('unsubscribes from alerts channel', () => {
    const { result } = renderHook(() => useWebSocketContext(), {
      wrapper: ({ children }) => <WebSocketProvider>{children}</WebSocketProvider>,
    })

    result.current.unsubscribeFromAlerts()

    expect(mockWebSocketReturn.send).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'unsubscribe',
        data: {
          channel: 'alerts',
        },
      })
    )
  })

  it('unsubscribes from alerts on unmount when connected', () => {
    vi.mocked(useWebSocket).mockReturnValue({
      ...mockWebSocketReturn,
      isConnected: true,
    })

    const { unmount } = render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    unmount()

    expect(mockWebSocketReturn.send).toHaveBeenCalledWith(
      expect.objectContaining({
        type: 'unsubscribe',
        data: {
          channel: 'alerts',
        },
      })
    )
  })

  it('shows success toast on connection', async () => {
    let onConnectCallback: (() => void) | undefined

    vi.mocked(useWebSocket).mockImplementation((config) => {
      onConnectCallback = config?.onConnect
      return mockWebSocketReturn
    })

    const { toast } = await import('@/lib/toast')

    render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    onConnectCallback?.()

    expect(toast.success).toHaveBeenCalledWith('Real-time updates connected')
  })

  it('shows warning toast on disconnection', async () => {
    let onDisconnectCallback: (() => void) | undefined

    vi.mocked(useWebSocket).mockImplementation((config) => {
      onDisconnectCallback = config?.onDisconnect
      return mockWebSocketReturn
    })

    const { toast } = await import('@/lib/toast')

    render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    onDisconnectCallback?.()

    expect(toast.warning).toHaveBeenCalledWith('Real-time updates disconnected')
  })

  it('logs errors from WebSocket', async () => {
    let onErrorCallback: ((error: Event) => void) | undefined

    vi.mocked(useWebSocket).mockImplementation((config) => {
      onErrorCallback = config?.onError
      return mockWebSocketReturn
    })

    const { logger } = await import('@/lib/logfire')

    render(
      <WebSocketProvider>
        <div>Test</div>
      </WebSocketProvider>
    )

    const error = new Event('error')
    onErrorCallback?.(error)

    expect(logger.error).toHaveBeenCalledWith('WebSocket error in provider', error)
  })
})