'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { logger } from '@/lib/logger'

interface User {
  id: string
  email: string
  name?: string
  role: 'admin' | 'provider' | 'staff'
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check for existing auth on mount
    const checkAuth = () => {
      const authToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('auth-token='))
        ?.split('=')[1]

      if (authToken) {
        // For demo, create a mock user
        setUser({
          id: '1',
          email: 'demo@example.com',
          name: 'Demo User',
          role: 'provider'
        })
      }
      setIsLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      logger.info('Login attempt', { email })
      
      // For demo, accept any credentials
      const mockUser: User = {
        id: '1',
        email,
        name: email.split('@')[0],
        role: 'provider'
      }
      
      // Set cookie
      document.cookie = `auth-token=demo-token; path=/; max-age=86400`
      
      setUser(mockUser)
      logger.info('Login successful', { userId: mockUser.id })
      
      router.push('/dashboard')
    } catch (error) {
      logger.error('Login failed', error)
      throw error
    }
  }

  const logout = () => {
    // Clear cookie
    document.cookie = 'auth-token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT'
    setUser(null)
    router.push('/login')
    logger.info('User logged out')
  }

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      login,
      logout,
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}