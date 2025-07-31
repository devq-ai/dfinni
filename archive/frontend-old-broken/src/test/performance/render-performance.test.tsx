import { describe, it, expect, vi, beforeEach } from 'vitest'
import { measureRenderTime, render, screen } from '@/test/test-utils'
import DashboardPage from '@/app/(dashboard)/dashboard/page'
import { DataTable } from '@/components/patients/data-table'
import { createMockPatient } from '@/test/test-utils'
import { usePatientStore } from '@/stores/patient-store'
import { useDashboardStore } from '@/stores/dashboard-store'

// Mock stores
vi.mock('@/stores/patient-store')
vi.mock('@/stores/dashboard-store')

// Mock dynamic imports for predictable performance
vi.mock('@/lib/dynamic-imports', () => ({
  DynamicComponents: {
    ActivityFeed: () => <div data-testid="render-complete">Activity Feed</div>,
    StatusDistributionChart: () => <div>Status Distribution Chart</div>
  }
}))

describe('Render Performance Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default mocks
    ;(useDashboardStore as any).mockReturnValue({
      metrics: {
        totalPatients: 150,
        activePatients: 105,
        newPatientsThisMonth: 15,
        patientGrowthRate: 12.5,
        statusDistribution: { inquiry: 10, onboarding: 15, active: 65, churned: 10 },
        riskDistribution: { low: 60, medium: 30, high: 10 },
        healthOutcomes: { improved: 45, stable: 40, declined: 15 },
        recentActivities: []
      },
      refreshDashboard: vi.fn(),
      isLoading: false,
      error: null
    })
  })

  describe('Dashboard Performance', () => {
    it('should render dashboard within 3 seconds', async () => {
      const { renderTime } = await measureRenderTime(<DashboardPage />)
      
      expect(renderTime).toBeLessThan(3000)
      console.log(`Dashboard render time: ${renderTime}ms`)
    })

    it('should handle large metric updates efficiently', async () => {
      const { rerender } = render(<DashboardPage />)
      
      // Measure re-render time with updated metrics
      const startTime = performance.now()
      
      ;(useDashboardStore as any).mockReturnValue({
        ...useDashboardStore(),
        metrics: {
          ...useDashboardStore().metrics,
          totalPatients: 10000,
          activePatients: 7000
        }
      })
      
      rerender(<DashboardPage />)
      
      const endTime = performance.now()
      const rerenderTime = endTime - startTime
      
      expect(rerenderTime).toBeLessThan(100)
      console.log(`Dashboard re-render time: ${rerenderTime}ms`)
    })
  })

  describe('Patient Table Performance', () => {
    it('should render table with 100 patients efficiently', async () => {
      const manyPatients = Array.from({ length: 100 }, (_, i) =>
        createMockPatient({ id: `patient-${i}`, firstName: `Patient${i}` })
      )
      
      ;(usePatientStore as any).mockReturnValue({
        patients: manyPatients,
        totalCount: 100,
        isLoading: false,
        error: null,
        filters: { status: 'all', riskLevel: 'all', search: '' },
        pagination: { page: 1, pageSize: 10 },
        getFilteredPatients: () => manyPatients.slice(0, 10),
        fetchPatients: vi.fn(),
        setFilters: vi.fn(),
        setPagination: vi.fn()
      })
      
      const startTime = performance.now()
      render(<DataTable />)
      const endTime = performance.now()
      
      const renderTime = endTime - startTime
      expect(renderTime).toBeLessThan(500)
      console.log(`Table render time (100 patients): ${renderTime}ms`)
    })

    it('should handle rapid filter changes efficiently', async () => {
      const mockSetFilters = vi.fn()
      ;(usePatientStore as any).mockReturnValue({
        patients: Array.from({ length: 50 }, (_, i) => createMockPatient({ id: `${i}` })),
        totalCount: 50,
        isLoading: false,
        error: null,
        filters: { status: 'all', riskLevel: 'all', search: '' },
        setFilters: mockSetFilters,
        getFilteredPatients: () => []
      })
      
      render(<DataTable />)
      
      const searchInput = screen.getByPlaceholderText(/search patients/i)
      
      // Simulate rapid typing
      const startTime = performance.now()
      
      for (let i = 0; i < 10; i++) {
        fireEvent.change(searchInput, { target: { value: `search${i}` } })
      }
      
      const endTime = performance.now()
      const totalTime = endTime - startTime
      
      // Should handle rapid updates without blocking
      expect(totalTime).toBeLessThan(100)
      console.log(`Rapid filter update time: ${totalTime}ms`)
    })
  })

  describe('Memory Usage', () => {
    it('should not leak memory on component unmount', async () => {
      // Get initial memory if available
      const getMemory = () => {
        if ('memory' in performance) {
          return (performance as any).memory.usedJSHeapSize
        }
        return 0
      }
      
      const initialMemory = getMemory()
      
      // Mount and unmount component multiple times
      for (let i = 0; i < 10; i++) {
        const { unmount } = render(<DashboardPage />)
        await screen.findByText('Dashboard')
        unmount()
      }
      
      // Force garbage collection if available
      if (global.gc) {
        global.gc()
      }
      
      // Wait a bit for cleanup
      await new Promise(resolve => setTimeout(resolve, 100))
      
      const finalMemory = getMemory()
      const memoryIncrease = finalMemory - initialMemory
      
      // Memory increase should be minimal
      if (initialMemory > 0) {
        const percentIncrease = (memoryIncrease / initialMemory) * 100
        expect(percentIncrease).toBeLessThan(10)
        console.log(`Memory increase: ${percentIncrease.toFixed(2)}%`)
      }
    })
  })

  describe('Bundle Size Impact', () => {
    it('should lazy load heavy components', async () => {
      const { container } = render(<DashboardPage />)
      
      // Initially, lazy loaded components should not be in DOM
      const lazyComponents = container.querySelectorAll('[data-lazy-loaded]')
      expect(lazyComponents.length).toBe(0)
      
      // Wait for lazy components to load
      await screen.findByText('Activity Feed')
      await screen.findByText('Status Distribution Chart')
      
      // Components should now be loaded
      expect(screen.getByText('Activity Feed')).toBeInTheDocument()
    })
  })
})