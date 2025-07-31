import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { AuthGuard } from './AuthGuard'
import { useAuthStore } from '@/stores/auth-store'
import { useRouter, usePathname } from 'next/navigation'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
  usePathname: vi.fn(),
}))

// Mock the auth store
vi.mock('@/stores/auth-store', () => ({
  useAuthStore: vi.fn(),
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    componentMount: vi.fn(),
    componentUnmount: vi.fn(),
    userAction: vi.fn(),
  },
}))

describe('AuthGuard', () => {
  const mockPush = vi.fn()
  const mockRefreshUser = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
    vi.mocked(usePathname).mockReturnValue('/dashboard')
  })

  it('shows loading state when auth is loading', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: false,
      user: null,
      isLoading: true,
      refreshUser: mockRefreshUser,
    } as any)

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    )

    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('renders children when authenticated', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', email: 'test@example.com', role: 'provider' },
      isLoading: false,
      refreshUser: mockRefreshUser,
    } as any)

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    )

    expect(screen.getByText('Protected Content')).toBeInTheDocument()
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('redirects to login when not authenticated', async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: false,
      user: null,
      isLoading: false,
      refreshUser: mockRefreshUser,
    } as any)

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    )

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login?from=%2Fdashboard')
    })
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('redirects to custom fallback URL when provided', async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: false,
      user: null,
      isLoading: false,
      refreshUser: mockRefreshUser,
    } as any)

    render(
      <AuthGuard fallbackUrl="/custom-login">
        <div>Protected Content</div>
      </AuthGuard>
    )

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/custom-login?from=%2Fdashboard')
    })
  })

  it('allows access when user has required role', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', email: 'admin@example.com', role: 'admin' },
      isLoading: false,
      refreshUser: mockRefreshUser,
    } as any)

    render(
      <AuthGuard requiredRoles={['admin', 'audit']}>
        <div>Admin Content</div>
      </AuthGuard>
    )

    expect(screen.getByText('Admin Content')).toBeInTheDocument()
    expect(mockPush).not.toHaveBeenCalled()
  })

  it('redirects when user lacks required role', async () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', email: 'user@example.com', role: 'provider' },
      isLoading: false,
      refreshUser: mockRefreshUser,
    } as any)

    render(
      <AuthGuard requiredRoles={['admin']}>
        <div>Admin Content</div>
      </AuthGuard>
    )

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard')
    })
    expect(screen.queryByText('Admin Content')).not.toBeInTheDocument()
  })

  it('calls refreshUser when not authenticated on mount', () => {
    vi.mocked(useAuthStore).mockReturnValue({
      isAuthenticated: false,
      user: null,
      isLoading: false,
      refreshUser: mockRefreshUser,
    } as any)

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    )

    expect(mockRefreshUser).toHaveBeenCalled()
  })
})