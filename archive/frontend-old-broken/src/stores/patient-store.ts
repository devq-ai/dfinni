import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { logger } from '@/lib/logfire'
import type { Patient, CreatePatientData, UpdatePatientData, PatientFilters, PatientSortConfig } from '@/types/patient'

interface PatientState {
  // State
  patients: Patient[]
  selectedPatient: Patient | null
  isLoading: boolean
  error: string | null
  filters: PatientFilters
  sortConfig: PatientSortConfig
  totalCount: number
  currentPage: number
  pageSize: number

  // Actions
  fetchPatients: (page?: number) => Promise<void>
  fetchPatientById: (id: string) => Promise<void>
  createPatient: (data: CreatePatientData) => Promise<Patient>
  updatePatient: (data: UpdatePatientData) => Promise<Patient>
  deletePatient: (id: string) => Promise<void>
  selectPatient: (patient: Patient | null) => void
  setFilters: (filters: PatientFilters) => void
  setSortConfig: (config: PatientSortConfig) => void
  setPage: (page: number) => void
  setPageSize: (size: number) => void
  clearError: () => void
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export const usePatientStore = create<PatientState>()(
  devtools(
    (set, get) => ({
      // Initial state
      patients: [],
      selectedPatient: null,
      isLoading: false,
      error: null,
      filters: {},
      sortConfig: { key: 'created_at', direction: 'desc' },
      totalCount: 0,
      currentPage: 1,
      pageSize: 10,

      // Fetch patients with pagination and filters
      fetchPatients: async (page?: number) => {
        logger.userAction('fetch_patients', { page, filters: get().filters })
        set({ isLoading: true, error: null })
        
        try {
          const { filters, sortConfig, pageSize, currentPage } = get()
          const targetPage = page || currentPage
          
          const params = new URLSearchParams({
            page: targetPage.toString(),
            limit: pageSize.toString(),
            sort_by: sortConfig.key,
            sort_order: sortConfig.direction,
          })

          // Add filters
          if (filters.search) params.append('search', filters.search)
          if (filters.status && filters.status !== 'ALL') params.append('status', filters.status)
          if (filters.risk_level && filters.risk_level !== 'ALL') params.append('risk_level', filters.risk_level)

          const response = await fetch(`${API_BASE_URL}/api/v1/patients?${params}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
          })

          if (!response.ok) {
            throw new Error(`Failed to fetch patients: ${response.statusText}`)
          }

          const data = await response.json()
          
          set({
            patients: data.items || [],
            totalCount: data.total || 0,
            currentPage: targetPage,
            isLoading: false,
          })

          logger.userAction('patients_fetched', { count: data.items?.length || 0 })
        } catch (error) {
          logger.error('Failed to fetch patients', error)
          set({ error: error instanceof Error ? error.message : 'Failed to fetch patients', isLoading: false })
        }
      },

      // Fetch single patient
      fetchPatientById: async (id: string) => {
        logger.userAction('fetch_patient_by_id', { id })
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
          })

          if (!response.ok) {
            throw new Error(`Failed to fetch patient: ${response.statusText}`)
          }

          const patient = await response.json()
          
          set({
            selectedPatient: patient,
            isLoading: false,
          })

          logger.userAction('patient_fetched', { patientId: id })
        } catch (error) {
          logger.error('Failed to fetch patient', error, { patientId: id })
          set({ error: error instanceof Error ? error.message : 'Failed to fetch patient', isLoading: false })
        }
      },

      // Create patient
      createPatient: async (data: CreatePatientData) => {
        logger.userAction('create_patient', { email: data.email })
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/patients`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
            body: JSON.stringify(data),
          })

          if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || 'Failed to create patient')
          }

          const patient = await response.json()
          
          // Add to local state
          set(state => ({
            patients: [patient, ...state.patients],
            totalCount: state.totalCount + 1,
            isLoading: false,
          }))

          logger.userAction('patient_created', { patientId: patient.id })
          return patient
        } catch (error) {
          logger.error('Failed to create patient', error)
          set({ error: error instanceof Error ? error.message : 'Failed to create patient', isLoading: false })
          throw error
        }
      },

      // Update patient
      updatePatient: async (data: UpdatePatientData) => {
        logger.userAction('update_patient', { patientId: data.id })
        set({ isLoading: true, error: null })
        
        try {
          const { id, ...updateData } = data
          const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
            method: 'PATCH',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
            body: JSON.stringify(updateData),
          })

          if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.detail || 'Failed to update patient')
          }

          const patient = await response.json()
          
          // Update local state
          set(state => ({
            patients: state.patients.map(p => p.id === patient.id ? patient : p),
            selectedPatient: state.selectedPatient?.id === patient.id ? patient : state.selectedPatient,
            isLoading: false,
          }))

          logger.userAction('patient_updated', { patientId: patient.id })
          return patient
        } catch (error) {
          logger.error('Failed to update patient', error, { patientId: data.id })
          set({ error: error instanceof Error ? error.message : 'Failed to update patient', isLoading: false })
          throw error
        }
      },

      // Delete patient
      deletePatient: async (id: string) => {
        logger.userAction('delete_patient', { patientId: id })
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/patients/${id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
          })

          if (!response.ok) {
            throw new Error(`Failed to delete patient: ${response.statusText}`)
          }
          
          // Update local state
          set(state => ({
            patients: state.patients.filter(p => p.id !== id),
            selectedPatient: state.selectedPatient?.id === id ? null : state.selectedPatient,
            totalCount: state.totalCount - 1,
            isLoading: false,
          }))

          logger.userAction('patient_deleted', { patientId: id })
        } catch (error) {
          logger.error('Failed to delete patient', error, { patientId: id })
          set({ error: error instanceof Error ? error.message : 'Failed to delete patient', isLoading: false })
          throw error
        }
      },

      // Other actions
      selectPatient: (patient) => {
        logger.userAction('select_patient', { patientId: patient?.id })
        set({ selectedPatient: patient })
      },

      setFilters: (filters) => {
        logger.userAction('set_patient_filters', filters)
        set({ filters, currentPage: 1 }) // Reset to first page when filters change
        get().fetchPatients(1)
      },

      setSortConfig: (config) => {
        logger.userAction('set_patient_sort', config)
        set({ sortConfig: config })
        get().fetchPatients()
      },

      setPage: (page) => {
        logger.userAction('set_patient_page', { page })
        set({ currentPage: page })
        get().fetchPatients(page)
      },

      setPageSize: (size) => {
        logger.userAction('set_patient_page_size', { size })
        set({ pageSize: size, currentPage: 1 })
        get().fetchPatients(1)
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'patient-store',
    }
  )
)