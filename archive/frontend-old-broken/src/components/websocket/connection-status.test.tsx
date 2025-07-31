import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ConnectionStatus } from './connection-status'
import { useWebSocketContext } from '@/contexts/websocket-context'

// Mock the WebSocket context
vi.mock('@/contexts/websocket-context', () => ({
  useWebSocketContext: vi.fn(),
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

describe('ConnectionStatus', () => {
  const mockConnect = vi.fn()
  const mockDisconnect = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows connected state', () => {
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'connected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    render(<ConnectionStatus />)

    expect(screen.getByText('Connected')).toBeInTheDocument()
    expect(screen.getByText('Disconnect')).toBeInTheDocument()
  })

  it('shows connecting state', () => {
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'connecting',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    render(<ConnectionStatus />)

    expect(screen.getByText('Connecting...')).toBeInTheDocument()
    // No connect/disconnect button while connecting
    expect(screen.queryByText('Connect')).not.toBeInTheDocument()
    expect(screen.queryByText('Disconnect')).not.toBeInTheDocument()
  })

  it('shows disconnected state', () => {
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'disconnected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    render(<ConnectionStatus />)

    expect(screen.getByText('Disconnected')).toBeInTheDocument()
    expect(screen.getByText('Connect')).toBeInTheDocument()
  })

  it('handles disconnect action', () => {
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'connected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    render(<ConnectionStatus />)

    fireEvent.click(screen.getByText('Disconnect'))

    expect(mockDisconnect).toHaveBeenCalled()
  })

  it('handles connect action', () => {
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'disconnected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    render(<ConnectionStatus />)

    fireEvent.click(screen.getByText('Connect'))

    expect(mockConnect).toHaveBeenCalled()
  })

  it('hides label when showLabel is false', () => {
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'connected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    const { container } = render(<ConnectionStatus showLabel={false} />)

    expect(screen.queryByText('Connected')).not.toBeInTheDocument()
    // Icon should still be present
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'connected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    const { container } = render(<ConnectionStatus className="custom-class" />)

    expect(container.firstChild).toHaveClass('custom-class')
  })

  it('shows correct styling for each state', () => {
    // Connected state
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'connected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    const { container: connectedContainer } = render(<ConnectionStatus />)
    expect(connectedContainer.firstChild).toHaveClass('bg-green-500/10', 'border-green-500/20')

    // Disconnected state
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'disconnected',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    const { container: disconnectedContainer } = render(<ConnectionStatus />)
    expect(disconnectedContainer.firstChild).toHaveClass('bg-red-500/10', 'border-red-500/20')

    // Connecting state
    vi.mocked(useWebSocketContext).mockReturnValue({
      connectionState: 'connecting',
      connect: mockConnect,
      disconnect: mockDisconnect,
    } as any)

    const { container: connectingContainer } = render(<ConnectionStatus />)
    expect(connectingContainer.firstChild).toHaveClass('bg-yellow-500/10', 'border-yellow-500/20')
  })
})