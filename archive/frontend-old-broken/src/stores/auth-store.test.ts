import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useAuthStore } from './auth-store'
import { auth } from '@/lib/auth'

// Mock the auth module
vi.mock('@/lib/auth', () => ({
  auth: {
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    getSession: vi.fn(),
  },
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
    debug: vi.fn(),
    auth: vi.fn(),
  },
}))

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,
    })
    // Clear all mocks
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('successfully logs in a user', async () => {
      const mockUser = {
        id: 'user123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'provider',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      vi.mocked(auth.login).mockResolvedValue({
        data: { user: mockUser },
      } as any)

      const { login } = useAuthStore.getState()
      await login('test@example.com', 'password123')

      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockUser)
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBe(null)
    })

    it('handles login failure', async () => {
      const error = new Error('Invalid credentials')
      vi.mocked(auth.login).mockRejectedValue(error)

      const { login } = useAuthStore.getState()
      
      await expect(login('test@example.com', 'wrong-password')).rejects.toThrow('Invalid credentials')

      const state = useAuthStore.getState()
      expect(state.user).toBe(null)
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBe('Invalid credentials')
    })
  })

  describe('logout', () => {
    it('successfully logs out a user', async () => {
      // Set initial logged-in state
      useAuthStore.setState({
        user: {
          id: 'user123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'provider',
          createdAt: '2025-01-01T00:00:00Z',
          updatedAt: '2025-01-01T00:00:00Z',
        },
        isAuthenticated: true,
      })

      vi.mocked(auth.logout).mockResolvedValue()

      const { logout } = useAuthStore.getState()
      await logout()

      const state = useAuthStore.getState()
      expect(state.user).toBe(null)
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
    })
  })

  describe('register', () => {
    it('successfully registers a new user', async () => {
      const mockUser = {
        id: 'user456',
        email: 'new@example.com',
        name: 'New User',
        role: 'provider',
        createdAt: '2025-01-01T00:00:00Z',
        updatedAt: '2025-01-01T00:00:00Z',
      }

      vi.mocked(auth.register).mockResolvedValue({
        data: { user: mockUser },
      } as any)

      const { register } = useAuthStore.getState()
      await register('new@example.com', 'password123', 'New User')

      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockUser)
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
      expect(state.error).toBe(null)
    })
  })

  describe('refreshUser', () => {
    it('refreshes user session successfully', async () => {
      const mockSession = {
        user: {
          id: 'user123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'admin',
          createdAt: '2025-01-01T00:00:00Z',
          updatedAt: '2025-01-01T00:00:00Z',
        },
      }

      vi.mocked(auth.getSession).mockResolvedValue(mockSession as any)

      const { refreshUser } = useAuthStore.getState()
      await refreshUser()

      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockSession.user)
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
    })

    it('handles session refresh when no session exists', async () => {
      vi.mocked(auth.getSession).mockResolvedValue(null)

      const { refreshUser } = useAuthStore.getState()
      await refreshUser()

      const state = useAuthStore.getState()
      expect(state.user).toBe(null)
      expect(state.isAuthenticated).toBe(false)
      expect(state.isLoading).toBe(false)
    })
  })

  describe('utility methods', () => {
    it('clears error', () => {
      useAuthStore.setState({ error: 'Some error' })
      
      const { clearError } = useAuthStore.getState()
      clearError()

      const state = useAuthStore.getState()
      expect(state.error).toBe(null)
    })

    it('checks user role correctly', () => {
      useAuthStore.setState({
        user: {
          id: 'user123',
          email: 'test@example.com',
          name: 'Test User',
          role: 'admin',
          createdAt: '2025-01-01T00:00:00Z',
          updatedAt: '2025-01-01T00:00:00Z',
        },
      })

      const { hasRole, hasAnyRole } = useAuthStore.getState()
      
      expect(hasRole('admin')).toBe(true)
      expect(hasRole('provider')).toBe(false)
      expect(hasAnyRole(['admin', 'audit'])).toBe(true)
      expect(hasAnyRole(['provider'])).toBe(false)
    })

    it('returns false for role checks when no user', () => {
      const { hasRole, hasAnyRole } = useAuthStore.getState()
      
      expect(hasRole('admin')).toBe(false)
      expect(hasAnyRole(['admin', 'provider'])).toBe(false)
    })
  })
})