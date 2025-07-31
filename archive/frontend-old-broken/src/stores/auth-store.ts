import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { auth, authClient } from '@/lib/auth'
import { logger } from '@/lib/logfire'

interface User {
  id: string
  email: string
  name: string
  role: 'provider' | 'admin' | 'audit'
  createdAt: string
  updatedAt: string
}

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  refreshUser: () => Promise<void>
  clearError: () => void
  hasRole: (role: string) => boolean
  hasAnyRole: (roles: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      isAuthenticated: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          logger.userAction('login_attempt', { email })
          const result = await auth.login(email, password)
          
          if (result.data?.user) {
            const user = {
              id: result.data.user.id,
              email: result.data.user.email,
              name: result.data.user.name || '',
              role: result.data.user.role || 'provider',
              createdAt: result.data.user.createdAt || new Date().toISOString(),
              updatedAt: result.data.user.updatedAt || new Date().toISOString(),
            }
            set({ 
              user, 
              isAuthenticated: true, 
              isLoading: false,
              error: null
            })
            logger.userAction('login_success', { userId: user.id, email: user.email })
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Login failed'
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: errorMessage
          })
          logger.userAction('login_failure', { email, error: errorMessage })
          throw error
        }
      },

      logout: async () => {
        set({ isLoading: true })
        try {
          const userId = get().user?.id
          await auth.logout()
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: null
          })
          logger.userAction('logout_success', { userId })
        } catch (error) {
          set({ isLoading: false })
          logger.userAction('logout_failure', { error })
          throw error
        }
      },

      register: async (email: string, password: string, name: string) => {
        set({ isLoading: true, error: null })
        try {
          logger.userAction('register_attempt', { email, name })
          const result = await auth.register(email, password, name)
          
          if (result.data?.user) {
            const user = {
              id: result.data.user.id,
              email: result.data.user.email,
              name: result.data.user.name || name,
              role: result.data.user.role || 'provider',
              createdAt: result.data.user.createdAt || new Date().toISOString(),
              updatedAt: result.data.user.updatedAt || new Date().toISOString(),
            }
            set({ 
              user, 
              isAuthenticated: true, 
              isLoading: false,
              error: null
            })
            logger.userAction('register_success', { userId: user.id, email: user.email })
          }
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Registration failed'
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false,
            error: errorMessage
          })
          logger.userAction('register_failure', { email, error: errorMessage })
          throw error
        }
      },

      refreshUser: async () => {
        set({ isLoading: true })
        try {
          const session = await auth.getSession()
          if (session?.user) {
            const user = {
              id: session.user.id,
              email: session.user.email,
              name: session.user.name || '',
              role: session.user.role || 'provider',
              createdAt: session.user.createdAt || new Date().toISOString(),
              updatedAt: session.user.updatedAt || new Date().toISOString(),
            }
            set({ 
              user, 
              isAuthenticated: true, 
              isLoading: false 
            })
            logger.userAction('session_refresh_success', { userId: user.id })
          } else {
            set({ 
              user: null, 
              isAuthenticated: false, 
              isLoading: false 
            })
          }
        } catch (error) {
          set({ 
            user: null, 
            isAuthenticated: false, 
            isLoading: false 
          })
          logger.userAction('session_refresh_failure', { error })
        }
      },

      clearError: () => {
        set({ error: null })
      },

      hasRole: (role: string) => {
        const user = get().user
        return user?.role === role
      },

      hasAnyRole: (roles: string[]) => {
        const user = get().user
        return user ? roles.includes(user.role) : false
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
)