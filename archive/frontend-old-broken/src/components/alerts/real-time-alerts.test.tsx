import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { RealTimeAlerts, type Alert } from './real-time-alerts'
import { MockWebSocketProvider } from '@/test/websocket-test-utils'

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

// Mock toast
vi.mock('@/lib/toast', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  },
}))

// Mock date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn((date) => '2 minutes ago'),
}))

describe('RealTimeAlerts', () => {
  const mockAlert: Alert = {
    id: '1',
    type: 'warning',
    title: 'Test Alert',
    message: 'This is a test alert',
    patientId: 'patient-123',
    patientName: 'John Doe',
    source: 'System',
    read: false,
    resolved: false,
    createdAt: new Date().toISOString(),
    actions: [
      {
        label: 'View Details',
        onClick: vi.fn(),
      },
    ],
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders nothing when not connected', () => {
    const { container } = render(
      <MockWebSocketProvider value={{ isConnected: false }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    expect(container.firstChild).toBeNull()
  })

  it('renders alerts when connected', async () => {
    // Simulate receiving an alert
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    // Dispatch alert event
    const alertEvent = new CustomEvent('new-alert', { detail: mockAlert })
    window.dispatchEvent(alertEvent)

    await waitFor(() => {
      expect(screen.getByText('Test Alert')).toBeInTheDocument()
    })
    
    expect(screen.getByText('This is a test alert')).toBeInTheDocument()
    expect(screen.getByText('Patient: John Doe')).toBeInTheDocument()
  })

  it('displays alert type icons correctly', async () => {
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    // Test different alert types
    const alertTypes: Alert['type'][] = ['critical', 'warning', 'info', 'success']
    
    alertTypes.forEach((type, index) => {
      const alert: Alert = {
        ...mockAlert,
        id: `alert-${index}`,
        type,
        title: `${type} Alert`,
      }
      
      const event = new CustomEvent('new-alert', { detail: alert })
      window.dispatchEvent(event)
    })

    await waitFor(() => {
      expect(screen.getByText('critical Alert')).toBeInTheDocument()
      expect(screen.getByText('warning Alert')).toBeInTheDocument()
      expect(screen.getByText('info Alert')).toBeInTheDocument()
      expect(screen.getByText('success Alert')).toBeInTheDocument()
    })
  })

  it('limits number of alerts displayed', async () => {
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts maxAlerts={3} />
      </MockWebSocketProvider>
    )

    // Send 5 alerts
    for (let i = 0; i < 5; i++) {
      const alert: Alert = {
        ...mockAlert,
        id: `alert-${i}`,
        title: `Alert ${i}`,
      }
      const event = new CustomEvent('new-alert', { detail: alert })
      window.dispatchEvent(event)
    }

    await waitFor(() => {
      // Should only show the 3 most recent
      expect(screen.getByText('Alert 4')).toBeInTheDocument()
      expect(screen.getByText('Alert 3')).toBeInTheDocument()
      expect(screen.getByText('Alert 2')).toBeInTheDocument()
    })
    
    expect(screen.queryByText('Alert 1')).not.toBeInTheDocument()
    expect(screen.queryByText('Alert 0')).not.toBeInTheDocument()
  })

  it('auto-dismisses info alerts after 10 seconds', async () => {
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    const infoAlert: Alert = {
      ...mockAlert,
      type: 'info',
      title: 'Info Alert',
    }

    const event = new CustomEvent('new-alert', { detail: infoAlert })
    window.dispatchEvent(event)

    await waitFor(() => {
      expect(screen.getByText('Info Alert')).toBeInTheDocument()
    })

    // Advance timers by 10 seconds
    await vi.advanceTimersByTimeAsync(10000)

    await waitFor(() => {
      expect(screen.queryByText('Info Alert')).not.toBeInTheDocument()
    }, { timeout: 2000 })
  })

  it('dismisses alert when X button clicked', async () => {
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    const event = new CustomEvent('new-alert', { detail: mockAlert })
    window.dispatchEvent(event)

    await waitFor(() => {
      expect(screen.getByText('Test Alert')).toBeInTheDocument()
    })

    // Find and click the dismiss button
    const dismissButtons = screen.getAllByRole('button')
    const dismissButton = dismissButtons.find(btn => btn.querySelector('svg'))
    fireEvent.click(dismissButton!)

    await waitFor(() => {
      expect(screen.queryByText('Test Alert')).not.toBeInTheDocument()
    })
  })

  it('marks alert as read when clicked', async () => {
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    const event = new CustomEvent('new-alert', { detail: mockAlert })
    window.dispatchEvent(event)

    await waitFor(() => {
      expect(screen.getByText('Test Alert')).toBeInTheDocument()
    })

    const alertElement = screen.getByText('Test Alert').closest('div[class*="border-b"]')
    expect(alertElement).toHaveClass('bg-zinc-900/50')

    fireEvent.click(alertElement!)

    // The alert should no longer have the unread background
    await waitFor(() => {
      expect(alertElement).not.toHaveClass('bg-zinc-900/50')
    })
  })

  it('executes alert actions when clicked', async () => {
    const mockAction = vi.fn()
    const alertWithAction: Alert = {
      ...mockAlert,
      actions: [
        {
          label: 'Test Action',
          onClick: mockAction,
        },
      ],
    }

    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    const event = new CustomEvent('new-alert', { detail: alertWithAction })
    window.dispatchEvent(event)

    await waitFor(() => {
      expect(screen.getByText('Test Action')).toBeInTheDocument()
    })

    const actionButton = screen.getByText('Test Action')
    fireEvent.click(actionButton)

    expect(mockAction).toHaveBeenCalled()
  })

  it('toggles minimize state', async () => {
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    const event = new CustomEvent('new-alert', { detail: mockAlert })
    window.dispatchEvent(event)

    await waitFor(() => {
      // Initially expanded
      expect(screen.getByText('Test Alert')).toBeInTheDocument()
    })

    // Find minimize button
    const minimizeButton = screen.getByText('▲')
    fireEvent.click(minimizeButton)

    // Should be minimized
    await waitFor(() => {
      expect(screen.queryByText('Test Alert')).not.toBeInTheDocument()
      expect(screen.getByText('▼')).toBeInTheDocument()
    })

    // Expand again
    fireEvent.click(screen.getByText('▼'))
    
    await waitFor(() => {
      expect(screen.getByText('Test Alert')).toBeInTheDocument()
    })
  })

  it('shows unread count badge', async () => {
    render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts />
      </MockWebSocketProvider>
    )

    // Send multiple unread alerts
    for (let i = 0; i < 3; i++) {
      const alert: Alert = {
        ...mockAlert,
        id: `alert-${i}`,
        read: false,
      }
      const event = new CustomEvent('new-alert', { detail: alert })
      window.dispatchEvent(event)
    }

    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument()
    })
  })

  it('respects position prop', async () => {
    const positions = [
      { position: 'top-right' as const, class: 'top-4 right-4' },
      { position: 'top-left' as const, class: 'top-4 left-4' },
      { position: 'bottom-right' as const, class: 'bottom-4 right-4' },
      { position: 'bottom-left' as const, class: 'bottom-4 left-4' },
    ]

    for (const { position, class: expectedClass } of positions) {
      const { container, unmount } = render(
        <MockWebSocketProvider value={{ isConnected: true }}>
          <RealTimeAlerts position={position} />
        </MockWebSocketProvider>
      )

      const event = new CustomEvent('new-alert', { detail: { ...mockAlert, id: `alert-${position}` } })
      window.dispatchEvent(event)

      await waitFor(() => {
        const alertContainer = container.firstChild
        expect(alertContainer).toHaveClass(expectedClass)
      })

      unmount()
    }
  })

  it('applies custom className', async () => {
    const { container } = render(
      <MockWebSocketProvider value={{ isConnected: true }}>
        <RealTimeAlerts className="custom-class" />
      </MockWebSocketProvider>
    )

    const event = new CustomEvent('new-alert', { detail: mockAlert })
    window.dispatchEvent(event)

    await waitFor(() => {
      expect(container.firstChild).toHaveClass('custom-class')
    })
  })
})