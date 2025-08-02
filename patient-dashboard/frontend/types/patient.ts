export type PatientStatus = 'inquiry' | 'onboarding' | 'active' | 'churned' | 'urgent';

export interface Patient {
  id: string
  mrn: string
  firstName: string
  middleName?: string
  lastName: string
  dateOfBirth: string
  gender: 'male' | 'female' | 'other'
  email?: string
  phone?: string
  address: {
    street: string
    city: string
    state: string
    zip: string
  }
  insurance?: {
    provider: string
    policyNumber: string
    groupNumber?: string
  }
  emergencyContact?: {
    name: string
    relationship: string
    phone: string
  }
  allergies?: string[]
  medications?: string[]
  conditions?: string[]
  riskScore?: number
  lastVisit?: string
  nextAppointment?: string
  status: PatientStatus
  assignedProviderId?: string
  assignedProviderName?: string
  createdAt: string
  updatedAt: string
}

export interface PatientListResponse {
  patients: Patient[]
  total: number
  page: number
  pageSize: number
}

export interface CreatePatientDto {
  mrn: string
  firstName: string
  middleName?: string
  lastName: string
  dateOfBirth: string
  gender: 'male' | 'female' | 'other'
  email?: string
  phone?: string
  address: {
    street: string
    city: string
    state: string
    zip: string
  }
  status: PatientStatus
  assignedProviderId?: string
  insurance?: {
    provider: string
    policyNumber: string
    groupNumber?: string
  }
  emergencyContact?: {
    name: string
    relationship: string
    phone: string
  }
}

export interface UpdatePatientDto extends Partial<CreatePatientDto> {
  allergies?: string[]
  medications?: string[]
  conditions?: string[]
}