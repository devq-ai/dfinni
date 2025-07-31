import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { usePatientStore } from './patient-store'

// Mock logfire
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock fetch
global.fetch = vi.fn()

describe('usePatientStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    // Reset store state
    act(() => {
      usePatientStore.setState({
        patients: [],
        selectedPatient: null,
        isLoading: false,
        error: null,
        filters: {},
        sortConfig: { key: 'created_at', direction: 'desc' },
        totalCount: 0,
        currentPage: 1,
        pageSize: 10,
      })
    })
  })

  describe('fetchPatients', () => {
    it('fetches patients successfully', async () => {
      const mockPatients = [
        { id: '1', first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
        { id: '2', first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' },
      ]
      
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: mockPatients, total: 2 }),
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.fetchPatients()
      })

      expect(result.current.patients).toEqual(mockPatients)
      expect(result.current.totalCount).toBe(2)
      expect(result.current.isLoading).toBe(false)
    })

    it('handles fetch error', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.fetchPatients()
      })

      expect(result.current.error).toBe('Network error')
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('createPatient', () => {
    it('creates patient successfully', async () => {
      const newPatient = {
        id: '3',
        first_name: 'New',
        last_name: 'Patient',
        email: 'new@example.com',
        phone: '123-456-7890',
        date_of_birth: '1990-01-01',
        status: 'INQUIRY' as const,
        risk_level: 'LOW' as const,
        created_at: new Date().toISOString(),
      }
      
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => newPatient,
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      let createdPatient
      await act(async () => {
        createdPatient = await result.current.createPatient({
          first_name: 'New',
          last_name: 'Patient',
          email: 'new@example.com',
          phone: '123-456-7890',
          date_of_birth: '1990-01-01',
        })
      })

      expect(createdPatient).toEqual(newPatient)
      expect(result.current.patients).toContainEqual(newPatient)
      expect(result.current.totalCount).toBe(1)
    })

    it('handles create error', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already exists' }),
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        try {
          await result.current.createPatient({
            first_name: 'New',
            last_name: 'Patient',
            email: 'existing@example.com',
            phone: '123-456-7890',
            date_of_birth: '1990-01-01',
          })
        } catch (error) {
          expect(error).toEqual(new Error('Email already exists'))
        }
      })

      expect(result.current.error).toBe('Email already exists')
    })
  })

  describe('updatePatient', () => {
    it('updates patient successfully', async () => {
      const existingPatient = {
        id: '1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '123-456-7890',
        date_of_birth: '1990-01-01',
        status: 'INQUIRY' as const,
        risk_level: 'LOW' as const,
        created_at: new Date().toISOString(),
      }
      
      const updatedPatient = { ...existingPatient, status: 'ACTIVE' as const }
      
      // Set initial state
      act(() => {
        usePatientStore.setState({ patients: [existingPatient] })
      })
      
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedPatient,
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.updatePatient({ id: '1', status: 'ACTIVE' })
      })

      expect(result.current.patients[0].status).toBe('ACTIVE')
    })
  })

  describe('deletePatient', () => {
    it('deletes patient successfully', async () => {
      const patient = {
        id: '1',
        first_name: 'John',
        last_name: 'Doe',
        email: 'john@example.com',
        phone: '123-456-7890',
        date_of_birth: '1990-01-01',
        status: 'INQUIRY' as const,
        risk_level: 'LOW' as const,
        created_at: new Date().toISOString(),
      }
      
      // Set initial state
      act(() => {
        usePatientStore.setState({ patients: [patient], totalCount: 1 })
      })
      
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        await result.current.deletePatient('1')
      })

      expect(result.current.patients).toEqual([])
      expect(result.current.totalCount).toBe(0)
    })
  })

  describe('filters and sorting', () => {
    it('sets filters and triggers fetch', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        result.current.setFilters({ status: 'ACTIVE', risk_level: 'HIGH' })
      })

      expect(result.current.filters).toEqual({ status: 'ACTIVE', risk_level: 'HIGH' })
      expect(result.current.currentPage).toBe(1)
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('status=ACTIVE&risk_level=HIGH'),
        expect.any(Object)
      )
    })

    it('sets sort config and triggers fetch', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        result.current.setSortConfig({ key: 'last_name', direction: 'asc' })
      })

      expect(result.current.sortConfig).toEqual({ key: 'last_name', direction: 'asc' })
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=last_name&sort_order=asc'),
        expect.any(Object)
      )
    })
  })

  describe('pagination', () => {
    it('sets page and fetches', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        result.current.setPage(3)
      })

      expect(result.current.currentPage).toBe(3)
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('page=3'),
        expect.any(Object)
      )
    })

    it('sets page size and resets to page 1', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0 }),
      } as Response)

      const { result } = renderHook(() => usePatientStore())

      await act(async () => {
        result.current.setPageSize(20)
      })

      expect(result.current.pageSize).toBe(20)
      expect(result.current.currentPage).toBe(1)
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('limit=20&'),
        expect.any(Object)
      )
    })
  })
})