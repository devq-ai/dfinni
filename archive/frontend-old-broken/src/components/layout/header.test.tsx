import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { Header } from './header'
import { useAuthStore } from '@/stores/auth-store'
import { useRouter } from 'next/navigation'
import { MockWebSocketProvider } from '@/test/websocket-test-utils'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}))

// Mock the auth store
vi.mock('@/stores/auth-store', () => ({
  useAuthStore: vi.fn(),
}))

// Mock child components
vi.mock('./breadcrumb', () => ({
  Breadcrumb: () => <div data-testid="breadcrumb">Breadcrumb</div>,
}))

vi.mock('./theme-toggle', () => ({
  ThemeToggle: () => <div data-testid="theme-toggle">Theme Toggle</div>,
}))

// Mock ConnectionStatus to avoid WebSocket dependency
vi.mock('@/components/websocket/connection-status', () => ({
  ConnectionStatus: () => <div data-testid="connection-status">Connected</div>,
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

describe('Header', () => {
  const mockPush = vi.fn()
  const mockLogout = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(useAuthStore).mockReturnValue({
      user: {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'provider',
      },
      logout: mockLogout,
    } as any)
  })

  it('renders breadcrumb and theme toggle', () => {
    render(
      <MockWebSocketProvider>
        <Header />
      </MockWebSocketProvider>
    )
    
    expect(screen.getByTestId('breadcrumb')).toBeInTheDocument()
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument()
  })

  it('displays user name in dropdown trigger', () => {
    render(
      <MockWebSocketProvider>
        <Header />
      </MockWebSocketProvider>
    )
    
    expect(screen.getByText('Test User')).toBeInTheDocument()
  })

  it('displays user email when name is not available', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: {
        id: '123',
        email: 'test@example.com',
        name: '',
        role: 'provider',
      },
      logout: mockLogout,
    } as any)

    render(
      <MockWebSocketProvider>
        <Header />
      </MockWebSocketProvider>
    )
    
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
  })

  it('displays "User" when no user data is available', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      user: null,
      logout: mockLogout,
    } as any)

    render(
      <MockWebSocketProvider>
        <Header />
      </MockWebSocketProvider>
    )
    
    expect(screen.getByText('User')).toBeInTheDocument()
  })

  it('renders notifications button with indicator', () => {
    render(
      <MockWebSocketProvider>
        <Header />
      </MockWebSocketProvider>
    )
    
    const notificationButton = screen.getByLabelText('View notifications')
    expect(notificationButton).toBeInTheDocument()
    
    // Check for notification indicator (red dot)
    const indicator = notificationButton.querySelector('.bg-red-500')
    expect(indicator).toBeInTheDocument()
  })

  it('navigates to alerts when notifications clicked', () => {
    render(
      <MockWebSocketProvider>
        <Header />
      </MockWebSocketProvider>
    )
    
    const notificationButton = screen.getByLabelText('View notifications')
    fireEvent.click(notificationButton)
    
    expect(mockPush).toHaveBeenCalledWith('/alerts')
  })

  describe('dropdown menu', () => {
    it('renders dropdown trigger', () => {
      render(
        <MockWebSocketProvider>
          <Header />
        </MockWebSocketProvider>
      )
      
      const trigger = screen.getByText('Test User')
      expect(trigger).toBeInTheDocument()
      expect(trigger.closest('button')).toHaveAttribute('aria-haspopup', 'menu')
    })

    it('has correct dropdown trigger attributes', () => {
      render(
        <MockWebSocketProvider>
          <Header />
        </MockWebSocketProvider>
      )
      
      const trigger = screen.getByText('Test User').closest('button')
      expect(trigger).toHaveAttribute('aria-expanded', 'false')
      expect(trigger).toHaveAttribute('data-state', 'closed')
    })
  })

  it('applies custom className', () => {
    const { container } = render(
      <MockWebSocketProvider>
        <Header className="custom-class" />
      </MockWebSocketProvider>
    )
    
    const header = container.querySelector('header.custom-class')
    expect(header).toBeInTheDocument()
  })
})