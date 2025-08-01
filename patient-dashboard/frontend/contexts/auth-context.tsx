// Updated: 2025-07-31T12:45:00-06:00
'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { logger } from '@/lib/logger'

interface User {
  id: string
  email: string
  name?: string
  role: 'admin' | 'provider' | 'staff'
  first_name?: string
  last_name?: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check for existing auth on mount
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth-token')
        if (token) {
          // Verify token with backend
          const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          
          if (response.ok) {
            const userData = await response.json()
            setUser({
              id: userData.id,
              email: userData.email,
              name: `${userData.first_name} ${userData.last_name}`,
              first_name: userData.first_name,
              last_name: userData.last_name,
              role: userData.role.toLowerCase() as 'admin' | 'provider' | 'staff'
            })
          } else {
            // Token invalid, clear it
            localStorage.removeItem('auth-token')
          }
        }
      } catch (error) {
        logger.error('Auth check failed', error)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      logger.info('Login attempt', { email })
      
      // Call BetterAuth API
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,
          password: password,
          grant_type: 'password'
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      }

      const data = await response.json()
      
      // Store token
      localStorage.setItem('auth-token', data.access_token)
      if (data.refresh_token) {
        localStorage.setItem('refresh-token', data.refresh_token)
      }
      
      // Get user data
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      })
      
      if (userResponse.ok) {
        const userData = await userResponse.json()
        setUser({
          id: userData.id,
          email: userData.email,
          name: `${userData.first_name} ${userData.last_name}`,
          first_name: userData.first_name,
          last_name: userData.last_name,
          role: userData.role.toLowerCase() as 'admin' | 'provider' | 'staff'
        })
        
        logger.info('Login successful', { userId: userData.id })
        router.push('/dashboard')
      } else {
        throw new Error('Failed to get user data')
      }
    } catch (error) {
      logger.error('Login failed', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      const token = localStorage.getItem('auth-token')
      if (token) {
        // Call logout endpoint
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      }
    } catch (error) {
      logger.error('Logout API call failed', error)
    } finally {
      // Clear local storage
      localStorage.removeItem('auth-token')
      localStorage.removeItem('refresh-token')
      setUser(null)
      router.push('/login')
      logger.info('User logged out')
    }
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