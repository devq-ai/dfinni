'use client'

import { Patient, PatientListResponse, CreatePatientDto, UpdatePatientDto } from '@/types/patient'
import { useAuth } from '@clerk/nextjs'
import { API_BASE_URL } from '@/lib/config'

export function usePatientsApi() {
  const { getToken } = useAuth()
  
  const getAuthHeaders = async (): Promise<HeadersInit> => {
    const token = await getToken()
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  }
  
  return {
    async getPatients(page = 1, pageSize = 10): Promise<PatientListResponse> {
      // Temporarily use raw endpoint and transform data
      const response = await fetch(`${API_BASE_URL}/api/v1/test-patients-raw`, {
        headers: {
          'Content-Type': 'application/json'
        },
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch patients')
      }
      
      const data = await response.json()
      
      // Transform raw data to match frontend expectations
      const patients = data.patients.map((p: any) => ({
        id: p.id,
        mrn: p.mrn || `MRN${p.id.slice(-6)}`,
        firstName: p.first_name,
        middleName: p.middle_name,
        lastName: p.last_name,
        dateOfBirth: p.date_of_birth,
        gender: p.gender?.toLowerCase() || 'other',
        email: p.email,
        phone: p.phone,
        address: p.address || { street: '', city: '', state: '', zip: '' },
        insurance: p.insurance ? {
          provider: p.insurance.provider || p.insurance.company,
          policyNumber: p.insurance.member_id,
          groupNumber: p.insurance.group_number
        } : undefined,
        status: p.status,
        riskScore: p.risk_score || (p.risk_level === 'High' ? 5 : p.risk_level === 'Medium' ? 3 : 1),
        riskLevel: p.risk_level,
        lastVisit: p.last_visit,
        nextAppointment: p.next_appointment,
        assignedProviderName: p.primary_care_provider,
        createdAt: p.created_at,
        updatedAt: p.updated_at || p.created_at
      }))
      
      return {
        patients,
        total: data.count,
        page: 1,
        pageSize: 10
      }
    },

    async getPatient(id: string): Promise<Patient> {
      const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
        headers: await getAuthHeaders(),
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch patient')
      }
      
      return response.json()
    },

    async createPatient(data: CreatePatientDto): Promise<Patient> {
      const response = await fetch(`${API_BASE_URL}/api/v1/patients`, {
        method: 'POST',
        headers: await getAuthHeaders(),
        body: JSON.stringify(data),
      })
      
      if (!response.ok) {
        throw new Error('Failed to create patient')
      }
      
      return response.json()
    },

    async updatePatient(id: string, data: UpdatePatientDto): Promise<Patient> {
      const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
        method: 'PATCH',
        headers: await getAuthHeaders(),
        body: JSON.stringify(data),
      })
      
      if (!response.ok) {
        throw new Error('Failed to update patient')
      }
      
      return response.json()
    },

    async deletePatient(id: string): Promise<void> {
      const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
        method: 'DELETE',
        headers: await getAuthHeaders(),
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete patient')
      }
    },

    async getDashboardStats(): Promise<{
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
      const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/stats`, {
        headers: await getAuthHeaders(),
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard stats')
      }
      
      return response.json()
    },
  }
}