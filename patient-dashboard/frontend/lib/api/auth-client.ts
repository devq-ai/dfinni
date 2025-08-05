import { useAuth } from '@clerk/nextjs'

// Client-side hook to get auth headers
export function useClientAuthHeaders() {
  const { getToken } = useAuth()
  
  return async (): Promise<HeadersInit> => {
    try {
      const token = await getToken()
      
      return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    } catch (error) {
      console.error('Failed to get auth token:', error)
      return {
        'Content-Type': 'application/json'
      }
    }
  }
}