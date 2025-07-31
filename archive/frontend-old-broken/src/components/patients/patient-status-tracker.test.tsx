import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { PatientStatusTracker } from './patient-status-tracker'
import { MockWebSocketProvider } from '@/test/websocket-test-utils'
import { usePatientStore } from '@/stores/patient-store'

// Mock stores
vi.mock('@/stores/patient-store', () => ({
  usePatientStore: vi.fn(),
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

// Mock date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => '2 minutes ago'),
}))

describe('PatientStatusTracker', () => {
  const mockPatients = [
    { id: '1', firstName: 'John', lastName: 'Doe' },
    { id: '2', firstName: 'Jane', lastName: 'Smith' },
  ]

  const mockSubscribe = vi.fn()
  const mockUnsubscribe = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usePatientStore).mockReturnValue({
      patients: mockPatients,
    } as any)
  })

  it('renders nothing when not connected', () => {
    const { container } = render(
      <MockWebSocketProvider value={{ isConnected: false }}>
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    expect(container.firstChild).toBeNull()
  })

  it('renders tracker when connected', () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    expect(screen.getByText('Live Status Updates')).toBeInTheDocument()
    expect(screen.getByText('Waiting for status updates...')).toBeInTheDocument()
  })

  it('subscribes to patient updates when connected', () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    expect(mockSubscribe).toHaveBeenCalledTimes(2)
    expect(mockSubscribe).toHaveBeenCalledWith('1')
    expect(mockSubscribe).toHaveBeenCalledWith('2')
  })

  it('unsubscribes on unmount', () => {
    const { unmount } = render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    unmount()

    expect(mockUnsubscribe).toHaveBeenCalledTimes(2)
    expect(mockUnsubscribe).toHaveBeenCalledWith('1')
    expect(mockUnsubscribe).toHaveBeenCalledWith('2')
  })

  it('displays status updates when received', async () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    // Simulate status update event
    const statusUpdate = {
      patientId: '1',
      patientName: 'John Doe',
      oldStatus: 'Active',
      newStatus: 'Churned',
      timestamp: new Date().toISOString(),
    }

    const event = new CustomEvent('patient-status-update', { detail: statusUpdate })
    window.dispatchEvent(event)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Active → Churned')).toBeInTheDocument()
      expect(screen.getByText('2 minutes ago')).toBeInTheDocument()
    })
  })

  it('keeps only the last 10 updates', async () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    // Send 12 status updates
    for (let i = 0; i < 12; i++) {
      const statusUpdate = {
        patientId: `patient-${i}`,
        patientName: `Patient ${i}`,
        oldStatus: 'Active',
        newStatus: 'Churned',
        timestamp: new Date().toISOString(),
      }

      const event = new CustomEvent('patient-status-update', { detail: statusUpdate })
      window.dispatchEvent(event)
    }

    await waitFor(() => {
      // Should show updates 2-11 (most recent 10)
      expect(screen.getByText('Patient 11')).toBeInTheDocument()
      expect(screen.getByText('Patient 2')).toBeInTheDocument()
      expect(screen.queryByText('Patient 1')).not.toBeInTheDocument()
      expect(screen.queryByText('Patient 0')).not.toBeInTheDocument()
    })
  })

  it('highlights most recent update', async () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    // Send first update
    const firstUpdate = {
      patientId: '1',
      patientName: 'First Patient',
      oldStatus: 'Active',
      newStatus: 'Churned',
      timestamp: new Date().toISOString(),
    }
    window.dispatchEvent(new CustomEvent('patient-status-update', { detail: firstUpdate }))

    // Send second update
    const secondUpdate = {
      patientId: '2',
      patientName: 'Second Patient',
      oldStatus: 'Inquiry',
      newStatus: 'Active',
      timestamp: new Date().toISOString(),
    }
    window.dispatchEvent(new CustomEvent('patient-status-update', { detail: secondUpdate }))

    await waitFor(() => {
      const secondUpdateElement = screen.getByText('Second Patient').closest('div')
      expect(secondUpdateElement).toHaveClass('ring-1', 'ring-blue-500/50', 'bg-blue-500/5')
    })
  })

  it('toggles expand/collapse state', () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    expect(screen.getByText('Waiting for status updates...')).toBeInTheDocument()

    // Click hide button
    const hideButton = screen.getByText('Hide')
    fireEvent.click(hideButton)

    expect(screen.queryByText('Waiting for status updates...')).not.toBeInTheDocument()
    expect(screen.getByText('Show')).toBeInTheDocument()

    // Click show button
    fireEvent.click(screen.getByText('Show'))
    expect(screen.getByText('Waiting for status updates...')).toBeInTheDocument()
  })

  it('shows update count in header', async () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    // Initially no count shown
    expect(screen.queryByText('(0)')).not.toBeInTheDocument()

    // Send updates
    for (let i = 0; i < 3; i++) {
      const statusUpdate = {
        patientId: `patient-${i}`,
        patientName: `Patient ${i}`,
        oldStatus: 'Active',
        newStatus: 'Churned',
        timestamp: new Date().toISOString(),
      }
      window.dispatchEvent(new CustomEvent('patient-status-update', { detail: statusUpdate }))
    }

    await waitFor(() => {
      expect(screen.getByText('(3)')).toBeInTheDocument()
    })
  })

  it('shows pulse animation on live icon', () => {
    render(
      <MockWebSocketProvider 
        value={{ 
          isConnected: true,
          subscribeToPatientUpdates: mockSubscribe,
          unsubscribeFromPatientUpdates: mockUnsubscribe,
        }}
      >
        <PatientStatusTracker />
      </MockWebSocketProvider>
    )

    const icon = screen.getByText('Live Status Updates').previousElementSibling
    expect(icon).toHaveClass('animate-pulse')
  })
})