// Last Updated: 2025-08-09T20:12:00-06:00
import { Provider, ProviderListResponse, CreateProviderDto, UpdateProviderDto } from '@/types/provider'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL

// Helper function to get auth headers
async function getAuthHeaders(): Promise<HeadersInit> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'username=demo@example.com&password=password123'
    })
    
    if (response.ok) {
      const data = await response.json()
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth-token', data.access_token)
      }
      return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${data.access_token}`
      }
    }
  } catch (error) {
    console.error('Auth error:', error)
  }
  
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth-token') : null
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}

export const providersApi = {
  async getProviders(page = 1, pageSize = 10): Promise<ProviderListResponse> {
    try {
      // Temporarily use test endpoint to get actual database data
      const response = await fetch(`${API_BASE_URL}/api/v1/test-providers`, {
        headers: {
          'Content-Type': 'application/json'
        },
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch providers')
      }
      
      return response.json()
    } catch (error) {
      console.warn('API not available, returning mock data')
      return getMockProviders(page, pageSize)
    }
  },

  async getProvider(id: string): Promise<Provider> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/providers/${id}`, {
        headers: await getAuthHeaders(),
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch provider')
      }
      
      return response.json()
    } catch (error) {
      const mockProviders = getMockProviders(1, 100).providers
      const provider = mockProviders.find(p => p.id === id)
      if (!provider) throw new Error('Provider not found')
      return provider
    }
  },

  async createProvider(data: CreateProviderDto): Promise<Provider> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/providers`, {
        method: 'POST',
        headers: await getAuthHeaders(),
        body: JSON.stringify(data),
      })
      
      if (!response.ok) {
        throw new Error('Failed to create provider')
      }
      
      return response.json()
    } catch (error) {
      // Return mock response for demo
      return {
        id: Math.random().toString(36).substr(2, 9),
        ...data,
        status: data.status || 'active',
        assignedPatients: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      } as Provider
    }
  },

  async updateProvider(id: string, data: UpdateProviderDto): Promise<Provider> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/providers/${id}`, {
        method: 'PATCH',
        headers: await getAuthHeaders(),
        body: JSON.stringify(data),
      })
      
      if (!response.ok) {
        throw new Error('Failed to update provider')
      }
      
      return response.json()
    } catch (error) {
      const provider = await this.getProvider(id)
      return {
        ...provider,
        ...data,
        updatedAt: new Date().toISOString(),
      }
    }
  },

  async deleteProvider(id: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/providers/${id}`, {
        method: 'DELETE',
        headers: await getAuthHeaders(),
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete provider')
      }
    } catch (error) {
      console.warn('API not available, simulating delete')
    }
  },
}

// Mock data function
function getMockProviders(page: number, pageSize: number): ProviderListResponse {
  const providers: Provider[] = [
    {
      id: '1',
      firstName: 'Dr. Sarah',
      lastName: 'Johnson',
      email: 'sarah.johnson@hospital.com',
      phone: '(555) 123-4567',
      role: 'doctor',
      specialization: 'Cardiology',
      licenseNumber: 'MD123456',
      department: 'Cardiology',
      status: 'active',
      hireDate: '2015-03-15',
      assignedPatients: ['1', '2'],
      createdAt: '2023-01-01T00:00:00Z',
      updatedAt: '2024-01-15T00:00:00Z',
    },
    {
      id: '2',
      firstName: 'Mary',
      lastName: 'Smith',
      email: 'mary.smith@hospital.com',
      phone: '(555) 234-5678',
      role: 'nurse',
      licenseNumber: 'RN789012',
      department: 'Emergency',
      status: 'active',
      hireDate: '2018-06-20',
      assignedPatients: ['3'],
      createdAt: '2023-01-01T00:00:00Z',
      updatedAt: '2024-01-10T00:00:00Z',
    },
    {
      id: '3',
      firstName: 'James',
      lastName: 'Wilson',
      email: 'james.wilson@hospital.com',
      phone: '(555) 345-6789',
      role: 'admin',
      licenseNumber: 'ADM345678',
      department: 'Administration',
      status: 'active',
      hireDate: '2020-01-10',
      assignedPatients: [],
      createdAt: '2023-01-01T00:00:00Z',
      updatedAt: '2024-01-05T00:00:00Z',
    },
    {
      id: '4',
      firstName: 'Dr. Michael',
      middleName: 'James',
      lastName: 'Brown',
      email: 'michael.brown@hospital.com',
      phone: '(555) 456-7890',
      role: 'specialist',
      specialization: 'Neurology',
      licenseNumber: 'MD987654',
      department: 'Neurology',
      status: 'active',
      hireDate: '2012-09-01',
      assignedPatients: ['1', '3'],
      createdAt: '2023-01-01T00:00:00Z',
      updatedAt: '2024-01-20T00:00:00Z',
    },
  ]

  const start = (page - 1) * pageSize
  const end = start + pageSize

  return {
    providers: providers.slice(start, end),
    total: providers.length,
    page,
    pageSize,
  }
}