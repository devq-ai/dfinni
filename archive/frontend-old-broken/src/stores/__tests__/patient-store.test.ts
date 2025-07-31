import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { usePatientStore } from '../patient-store'
import { api } from '@/lib/fetch-wrapper'
import { createMockPatient } from '@/test/test-utils'

// Mock API
vi.mock('@/lib/fetch-wrapper', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    stateChange: vi.fn(),
    error: vi.fn(),
    info: vi.fn()
  }
}))

describe('PatientStore', () => {
  beforeEach(() => {
    // Reset store state
    const { result } = renderHook(() => usePatientStore())
    act(() => {
      result.current.patients = []
      result.current.totalCount = 0
      result.current.isLoading = false
      result.current.error = null
      result.current.selectedPatient = null
      result.current.filters = {
        status: 'all',
        riskLevel: 'all',
        search: ''
      }
      result.current.pagination = {
        page: 1,
        pageSize: 10
      }
    })
    
    vi.clearAllMocks()
  })

  describe('fetchPatients', () => {
    it('should fetch patients successfully', async () => {
      const mockPatients = [
        createMockPatient({ id: '1', firstName: 'John' }),
        createMockPatient({ id: '2', firstName: 'Jane' })
      ]
      
      ;(api.get as any).mockResolvedValueOnce({
        data: {
          patients: mockPatients,
          total: 2,
          page: 1,
          pageSize: 10
        },
        status: 200
      })

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.fetchPatients()
      })

      expect(result.current.patients).toEqual(mockPatients)
      expect(result.current.totalCount).toBe(2)
      expect(result.current.isLoading).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it('should handle fetch error', async () => {
      const errorMessage = 'Failed to fetch patients'
      ;(api.get as any).mockRejectedValueOnce(new Error(errorMessage))

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.fetchPatients()
      })

      expect(result.current.patients).toEqual([])
      expect(result.current.error).toBe(errorMessage)
      expect(result.current.isLoading).toBe(false)
    })

    it('should apply filters when fetching', async () => {
      const { result } = renderHook(() => usePatientStore())

      act(() => {
        result.current.setFilters({
          status: 'active',
          riskLevel: 'high',
          search: 'john'
        })
      })

      ;(api.get as any).mockResolvedValueOnce({
        data: { patients: [], total: 0, page: 1, pageSize: 10 },
        status: 200
      })

      await act(async () => {
        await result.current.fetchPatients()
      })

      expect(api.get).toHaveBeenCalledWith('/patients', {
        params: expect.objectContaining({
          status: 'active',
          riskLevel: 'high',
          search: 'john',
          page: 1,
          pageSize: 10
        })
      })
    })
  })

  describe('createPatient', () => {
    it('should create patient successfully', async () => {
      const newPatient = createMockPatient({ id: '3', firstName: 'Alice' })
      const patientData = {
        firstName: 'Alice',
        lastName: 'Smith',
        dateOfBirth: '1985-05-15',
        email: 'alice@example.com',
        phone: '555-0123'
      }

      ;(api.post as any).mockResolvedValueOnce({
        data: newPatient,
        status: 201
      })

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.createPatient(patientData)
      })

      expect(api.post).toHaveBeenCalledWith('/patients', patientData)
      expect(result.current.patients).toContainEqual(newPatient)
      expect(result.current.totalCount).toBe(1)
    })

    it('should handle creation error', async () => {
      const errorMessage = 'Failed to create patient'
      ;(api.post as any).mockRejectedValueOnce(new Error(errorMessage))

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.createPatient({
          firstName: 'Test',
          lastName: 'User',
          dateOfBirth: '1990-01-01',
          email: 'test@example.com',
          phone: '555-0000'
        })
      })

      expect(result.current.error).toBe(errorMessage)
    })
  })

  describe('updatePatient', () => {
    it('should update patient successfully', async () => {
      const existingPatient = createMockPatient({ id: '1', firstName: 'John' })
      const updatedPatient = { ...existingPatient, firstName: 'Jonathan' }

      const { result } = renderHook(() => usePatientStore())
      
      // Set initial patient
      act(() => {
        result.current.patients = [existingPatient]
      })

      ;(api.put as any).mockResolvedValueOnce({
        data: updatedPatient,
        status: 200
      })

      await act(async () => {
        await result.current.updatePatient('1', { firstName: 'Jonathan' })
      })

      expect(api.put).toHaveBeenCalledWith('/patients/1', { firstName: 'Jonathan' })
      expect(result.current.patients[0].firstName).toBe('Jonathan')
    })
  })

  describe('deletePatient', () => {
    it('should delete patient successfully', async () => {
      const patient1 = createMockPatient({ id: '1' })
      const patient2 = createMockPatient({ id: '2' })

      const { result } = renderHook(() => usePatientStore())
      
      act(() => {
        result.current.patients = [patient1, patient2]
        result.current.totalCount = 2
      })

      ;(api.delete as any).mockResolvedValueOnce({
        data: {},
        status: 204
      })

      await act(async () => {
        await result.current.deletePatient('1')
      })

      expect(api.delete).toHaveBeenCalledWith('/patients/1')
      expect(result.current.patients).toHaveLength(1)
      expect(result.current.patients[0].id).toBe('2')
      expect(result.current.totalCount).toBe(1)
    })
  })

  describe('filters and pagination', () => {
    it('should update filters', () => {
      const { result } = renderHook(() => usePatientStore())

      act(() => {
        result.current.setFilters({
          status: 'active',
          riskLevel: 'high',
          search: 'test'
        })
      })

      expect(result.current.filters).toEqual({
        status: 'active',
        riskLevel: 'high',
        search: 'test'
      })
    })

    it('should update pagination', () => {
      const { result } = renderHook(() => usePatientStore())

      act(() => {
        result.current.setPagination({
          page: 2,
          pageSize: 20
        })
      })

      expect(result.current.pagination).toEqual({
        page: 2,
        pageSize: 20
      })
    })

    it('should reset to page 1 when filters change', () => {
      const { result } = renderHook(() => usePatientStore())

      act(() => {
        result.current.setPagination({ page: 3, pageSize: 10 })
        result.current.setFilters({ status: 'active' })
      })

      expect(result.current.pagination.page).toBe(1)
    })
  })

  describe('patient selection', () => {
    it('should select patient', () => {
      const patient = createMockPatient({ id: '1' })
      const { result } = renderHook(() => usePatientStore())

      act(() => {
        result.current.setSelectedPatient(patient)
      })

      expect(result.current.selectedPatient).toEqual(patient)
    })

    it('should clear selected patient', () => {
      const patient = createMockPatient({ id: '1' })
      const { result } = renderHook(() => usePatientStore())

      act(() => {
        result.current.setSelectedPatient(patient)
        result.current.clearSelectedPatient()
      })

      expect(result.current.selectedPatient).toBeNull()
    })
  })

  describe('getFilteredPatients', () => {
    it('should return all patients when filters are default', () => {
      const patients = [
        createMockPatient({ id: '1' }),
        createMockPatient({ id: '2' })
      ]

      const { result } = renderHook(() => usePatientStore())
      
      act(() => {
        result.current.patients = patients
      })

      expect(result.current.getFilteredPatients()).toEqual(patients)
    })

    it('should filter by status', () => {
      const patients = [
        createMockPatient({ id: '1', status: 'active' }),
        createMockPatient({ id: '2', status: 'inactive' })
      ]

      const { result } = renderHook(() => usePatientStore())
      
      act(() => {
        result.current.patients = patients
        result.current.setFilters({ status: 'active' })
      })

      const filtered = result.current.getFilteredPatients()
      expect(filtered).toHaveLength(1)
      expect(filtered[0].id).toBe('1')
    })

    it('should filter by search term', () => {
      const patients = [
        createMockPatient({ id: '1', firstName: 'John', lastName: 'Doe' }),
        createMockPatient({ id: '2', firstName: 'Jane', lastName: 'Smith' })
      ]

      const { result } = renderHook(() => usePatientStore())
      
      act(() => {
        result.current.patients = patients
        result.current.setFilters({ search: 'smith' })
      })

      const filtered = result.current.getFilteredPatients()
      expect(filtered).toHaveLength(1)
      expect(filtered[0].id).toBe('2')
    })
  })
})