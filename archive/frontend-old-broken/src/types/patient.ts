export type PatientStatus = 'INQUIRY' | 'ONBOARDING' | 'ACTIVE' | 'CHURNED'
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH'

export interface Patient {
  id: string
  first_name: string
  last_name: string
  email: string
  phone: string
  date_of_birth: string
  status: PatientStatus
  risk_level: RiskLevel
  created_at: string
  updated_at?: string
}

export interface PatientFilters {
  search?: string
  status?: PatientStatus | 'ALL'
  risk_level?: RiskLevel | 'ALL'
}

export interface PatientSortConfig {
  key: keyof Patient
  direction: 'asc' | 'desc'
}

export interface CreatePatientData {
  first_name: string
  last_name: string
  email: string
  phone: string
  date_of_birth: string
  status?: PatientStatus
  risk_level?: RiskLevel
}

export interface UpdatePatientData extends Partial<CreatePatientData> {
  id: string
}