export interface Patient {
  id: string
  mrn: string
  firstName: string
  lastName: string
  dateOfBirth: string
  gender: 'male' | 'female' | 'other'
  email?: string
  phone?: string
  address?: {
    street: string
    city: string
    state: string
    zipCode: string
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
  status: 'active' | 'inactive' | 'discharged'
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
  lastName: string
  dateOfBirth: string
  gender: 'male' | 'female' | 'other'
  email?: string
  phone?: string
  address?: {
    street: string
    city: string
    state: string
    zipCode: string
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
}

export interface UpdatePatientDto extends Partial<CreatePatientDto> {
  allergies?: string[]
  medications?: string[]
  conditions?: string[]
  status?: 'active' | 'inactive' | 'discharged'
}