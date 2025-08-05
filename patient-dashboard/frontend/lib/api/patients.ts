import { Patient, PatientListResponse, CreatePatientDto, UpdatePatientDto } from '@/types/patient'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL

if (!API_BASE_URL) {
  console.error('NEXT_PUBLIC_API_URL is not defined. Please set it in your environment variables.')
}

export const patientsApi = {
  async getPatients(getHeaders: () => Promise<HeadersInit>, page = 1, pageSize = 10, filter?: string): Promise<PatientListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: pageSize.toString(),
    })
    
    if (filter) {
      params.append('filter', filter)
    }
    
    const response = await fetch(`${API_BASE_URL}/api/v1/patients?${params}`, {
      headers: await getHeaders(),
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch patients')
    }
    
    return response.json()
  },

  async getPatient(getHeaders: () => Promise<HeadersInit>, id: string): Promise<Patient> {
    const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
      headers: await getHeaders(),
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch patient')
    }
    
    return response.json()
  },

  async createPatient(getHeaders: () => Promise<HeadersInit>, data: CreatePatientDto): Promise<Patient> {
    const response = await fetch(`${API_BASE_URL}/api/v1/patients`, {
      method: 'POST',
      headers: await getHeaders(),
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error('Failed to create patient')
    }
    
    return response.json()
  },

  async updatePatient(getHeaders: () => Promise<HeadersInit>, id: string, data: UpdatePatientDto): Promise<Patient> {
    const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
      method: 'PATCH',
      headers: await getHeaders(),
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error('Failed to update patient')
    }
    
    return response.json()
  },

  async deletePatient(getHeaders: () => Promise<HeadersInit>, id: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
      method: 'DELETE',
      headers: await getHeaders(),
    })
    
    if (!response.ok) {
      throw new Error('Failed to delete patient')
    }
  },

  async getDashboardStats(getHeaders: () => Promise<HeadersInit>): Promise<{
    current: {
      totalPatients: number;
      activePatients: number;
      highRiskPatients: number;
      appointmentsToday: number;
    };
    previous: {
      totalPatients: number;
      activePatients: number;
      highRiskPatients: number;
      appointmentsToday: number;
    };
    trends: {
      totalPatients: { value: string; isUp: boolean };
      activePatients: { value: string; isUp: boolean };
      highRiskPatients: { value: string; isUp: boolean };
      appointmentsToday: { value: string; isUp: boolean };
    };
  }> {
    try {
      // Temporarily use test endpoint until Clerk auth is fixed
      const response = await fetch(`${API_BASE_URL}/api/v1/test-dashboard-stats`, {
        headers: {
          'Content-Type': 'application/json'
        },
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Dashboard stats error:', {
          status: response.status,
          statusText: response.statusText,
          error: errorText,
          url: `${API_BASE_URL}/api/v1/test-dashboard-stats`
        })
        throw new Error(`Failed to fetch dashboard stats: ${response.status}`)
      }
      
      return response.json()
    } catch (error) {
      console.error('Dashboard stats request failed:', error)
      throw error
    }
  },
}