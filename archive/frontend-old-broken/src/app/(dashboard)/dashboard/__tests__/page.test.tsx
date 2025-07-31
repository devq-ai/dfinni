import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/test/test-utils'
import DashboardPage from '../page'
import { useDashboardStore } from '@/stores/dashboard-store'
import { usePatientStore } from '@/stores/patient-store'

// Mock stores
vi.mock('@/stores/dashboard-store')
vi.mock('@/stores/patient-store')

// Mock dynamic imports
vi.mock('@/lib/dynamic-imports', () => ({
  DynamicComponents: {
    ActivityFeed: () => <div>Activity Feed</div>,
    StatusDistributionChart: () => <div>Status Distribution Chart</div>
  }
}))

describe('DashboardPage', () => {
  const mockRefreshDashboard = vi.fn()
  
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default store mocks
    ;(useDashboardStore as any).mockReturnValue({
      metrics: {
        totalPatients: 150,
        activePatients: 105,
        newPatientsThisMonth: 15,
        patientGrowthRate: 12.5,
        statusDistribution: {
          inquiry: 10,
          onboarding: 15,
          active: 65,
          churned: 10,
        },
        riskDistribution: {
          low: 60,
          medium: 30,
          high: 10,
        },
        healthOutcomes: {
          improved: 45,
          stable: 40,
          declined: 15,
        },
        recentActivities: [],
      },
      refreshDashboard: mockRefreshDashboard,
      isLoading: false,
      error: null
    })
    
    ;(usePatientStore as any).mockReturnValue({
      totalCount: 150
    })
  })

  it('should render dashboard with metrics', async () => {
    render(<DashboardPage />)

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText(/Welcome back/)).toBeInTheDocument()
    
    // Check metric cards
    expect(screen.getByText('Total Patients')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument()
    
    expect(screen.getByText('Active Patients')).toBeInTheDocument()
    expect(screen.getByText('105')).toBeInTheDocument()
    
    expect(screen.getByText('New This Month')).toBeInTheDocument()
    expect(screen.getByText('15')).toBeInTheDocument()
    
    expect(screen.getByText('High Risk Patients')).toBeInTheDocument()
    expect(screen.getByText('10')).toBeInTheDocument()
  })

  it('should call refreshDashboard on mount', () => {
    render(<DashboardPage />)
    
    expect(mockRefreshDashboard).toHaveBeenCalledTimes(1)
  })

  it('should set up auto-refresh interval', async () => {
    vi.useFakeTimers()
    render(<DashboardPage />)
    
    // Fast-forward 30 seconds
    vi.advanceTimersByTime(30000)
    
    expect(mockRefreshDashboard).toHaveBeenCalledTimes(2)
    
    vi.useRealTimers()
  })

  it('should display loading overlay when isLoading is true', () => {
    ;(useDashboardStore as any).mockReturnValue({
      metrics: null,
      refreshDashboard: mockRefreshDashboard,
      isLoading: true,
      error: null
    })
    
    render(<DashboardPage />)
    
    expect(screen.getByText('Refreshing dashboard...')).toBeInTheDocument()
  })

  it('should display error message when error occurs', () => {
    const errorMessage = 'Failed to load dashboard data'
    ;(useDashboardStore as any).mockReturnValue({
      metrics: null,
      refreshDashboard: mockRefreshDashboard,
      isLoading: false,
      error: errorMessage
    })
    
    render(<DashboardPage />)
    
    expect(screen.getByText('Error Loading Dashboard')).toBeInTheDocument()
    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('should render dynamic components with suspense', async () => {
    render(<DashboardPage />)
    
    // Dynamic components should be rendered
    await waitFor(() => {
      expect(screen.getByText('Activity Feed')).toBeInTheDocument()
      expect(screen.getByText('Status Distribution Chart')).toBeInTheDocument()
    })
  })

  it('should display correct change indicators', () => {
    render(<DashboardPage />)
    
    // Active patients has positive change
    const activeCard = screen.getByText('Active Patients').closest('div')
    expect(activeCard).toHaveTextContent('5.2')
    
    // High risk patients has negative change (which is good)
    const riskCard = screen.getByText('High Risk Patients').closest('div')
    expect(riskCard).toHaveTextContent('-2.1')
  })

  it('should use mock metrics when store metrics are null', () => {
    ;(useDashboardStore as any).mockReturnValue({
      metrics: null,
      refreshDashboard: mockRefreshDashboard,
      isLoading: false,
      error: null
    })
    
    ;(usePatientStore as any).mockReturnValue({
      totalCount: 200
    })
    
    render(<DashboardPage />)
    
    // Should calculate mock metrics based on patient count
    expect(screen.getByText('200')).toBeInTheDocument() // Total patients
    expect(screen.getByText('140')).toBeInTheDocument() // Active patients (70%)
    expect(screen.getByText('20')).toBeInTheDocument() // New this month (10%)
  })

  it('should clean up interval on unmount', () => {
    const clearIntervalSpy = vi.spyOn(window, 'clearInterval')
    const { unmount } = render(<DashboardPage />)
    
    unmount()
    
    expect(clearIntervalSpy).toHaveBeenCalled()
  })
})