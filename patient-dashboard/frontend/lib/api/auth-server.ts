import { auth } from '@clerk/nextjs/server'

// Server-side function to get auth headers
export async function getServerAuthHeaders(): Promise<HeadersInit> {
  const { getToken } = await auth()
  const token = await getToken()
  
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}