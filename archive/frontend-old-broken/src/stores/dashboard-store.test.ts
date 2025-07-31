import { describe, it, expect, vi, beforeEach } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useDashboardStore } from './dashboard-store'

// Mock logfire
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock fetch
global.fetch = vi.fn()

describe('useDashboardStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
    // Reset store state
    act(() => {
      useDashboardStore.setState({
        metrics: null,
        activities: [],
        isLoading: false,
        error: null,
        lastRefresh: null,
        refreshInterval: 30,
      })
    })
  })

  describe('fetchMetrics', () => {
    it('fetches dashboard metrics successfully', async () => {
      const mockMetrics = {
        totalPatients: 150,
        activePatients: 100,
        newPatientsThisMonth: 15,
        patientGrowthRate: 12.5,
        statusDistribution: {
          inquiry: 10,
          onboarding: 20,
          active: 100,
          churned: 20,
        },
        riskDistribution: {
          low: 90,
          medium: 45,
          high: 15,
        },
        healthOutcomes: {
          improved: 60,
          stable: 70,
          declined: 20,
        },
        recentActivities: [],
      }
      
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => mockMetrics,
      } as Response)

      const { result } = renderHook(() => useDashboardStore())

      await act(async () => {
        await result.current.fetchMetrics()
      })

      expect(result.current.metrics).toEqual(mockMetrics)
      expect(result.current.lastRefresh).toBeInstanceOf(Date)
      expect(result.current.isLoading).toBe(false)
    })

    it('handles fetch metrics error', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => useDashboardStore())

      await act(async () => {
        await result.current.fetchMetrics()
      })

      expect(result.current.error).toBe('Network error')
      expect(result.current.isLoading).toBe(false)
      expect(result.current.metrics).toBeDefined() // Should have default metrics
    })
  })

  describe('fetchActivities', () => {
    it('fetches activities successfully', async () => {
      const mockActivities = [
        {
          id: '1',
          type: 'patient_added' as const,
          title: 'New patient added',
          description: 'John Doe was added to the system',
          timestamp: new Date().toISOString(),
        },
        {
          id: '2',
          type: 'status_changed' as const,
          title: 'Status updated',
          description: 'Jane Smith status changed to Active',
          timestamp: new Date().toISOString(),
        },
      ]
      
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: mockActivities }),
      } as Response)

      const { result } = renderHook(() => useDashboardStore())

      await act(async () => {
        await result.current.fetchActivities()
      })

      expect(result.current.activities).toEqual(mockActivities)
      expect(result.current.isLoading).toBe(false)
    })

    it('fetches activities with pagination', async () => {
      vi.mocked(fetch).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [] }),
      } as Response)

      const { result } = renderHook(() => useDashboardStore())

      await act(async () => {
        await result.current.fetchActivities(2, 20)
      })

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('page=2&limit=20'),
        expect.any(Object)
      )
    })
  })

  describe('refreshDashboard', () => {
    it('refreshes both metrics and activities', async () => {
      vi.mocked(fetch)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            totalPatients: 100,
            activePatients: 70,
            newPatientsThisMonth: 10,
            patientGrowthRate: 10,
            statusDistribution: { inquiry: 10, onboarding: 10, active: 70, churned: 10 },
            riskDistribution: { low: 60, medium: 30, high: 10 },
            healthOutcomes: { improved: 40, stable: 40, declined: 20 },
            recentActivities: [],
          }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ items: [] }),
        } as Response)

      const { result } = renderHook(() => useDashboardStore())

      await act(async () => {
        await result.current.refreshDashboard()
      })

      expect(fetch).toHaveBeenCalledTimes(2)
      expect(result.current.metrics).toBeDefined()
      expect(result.current.activities).toBeDefined()
    })
  })

  describe('setRefreshInterval', () => {
    it('updates refresh interval', () => {
      const { result } = renderHook(() => useDashboardStore())

      act(() => {
        result.current.setRefreshInterval(60)
      })

      expect(result.current.refreshInterval).toBe(60)
    })
  })

  describe('clearError', () => {
    it('clears error state', () => {
      const { result } = renderHook(() => useDashboardStore())

      act(() => {
        useDashboardStore.setState({ error: 'Test error' })
      })

      expect(result.current.error).toBe('Test error')

      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })
  })
})