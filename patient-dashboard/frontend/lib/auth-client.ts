import { useAuth } from '@clerk/nextjs'

export function useAuthHeaders() {
  const { getToken } = useAuth()
  
  return async (): Promise<HeadersInit> => {
    const token = await getToken()
    
    return {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    }
  }
}