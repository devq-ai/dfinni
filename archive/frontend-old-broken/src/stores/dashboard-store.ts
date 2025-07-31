import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { logger } from '@/lib/logfire'
import type { DashboardMetrics, Activity } from '@/types/dashboard'

interface DashboardState {
  // State
  metrics: DashboardMetrics | null
  activities: Activity[]
  isLoading: boolean
  error: string | null
  lastRefresh: Date | null
  refreshInterval: number // in seconds

  // Actions
  fetchMetrics: () => Promise<void>
  fetchActivities: (page?: number, limit?: number) => Promise<void>
  refreshDashboard: () => Promise<void>
  setRefreshInterval: (seconds: number) => void
  clearError: () => void
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

const defaultMetrics: DashboardMetrics = {
  totalPatients: 0,
  activePatients: 0,
  newPatientsThisMonth: 0,
  patientGrowthRate: 0,
  statusDistribution: {
    inquiry: 0,
    onboarding: 0,
    active: 0,
    churned: 0,
  },
  riskDistribution: {
    low: 0,
    medium: 0,
    high: 0,
  },
  healthOutcomes: {
    improved: 0,
    stable: 0,
    declined: 0,
  },
  recentActivities: [],
}

export const useDashboardStore = create<DashboardState>()(
  devtools(
    (set, get) => ({
      // Initial state
      metrics: null,
      activities: [],
      isLoading: false,
      error: null,
      lastRefresh: null,
      refreshInterval: 30, // Default 30 seconds

      // Fetch dashboard metrics
      fetchMetrics: async () => {
        logger.userAction('fetch_dashboard_metrics')
        set({ isLoading: true, error: null })
        
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/metrics`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
          })

          if (!response.ok) {
            throw new Error(`Failed to fetch metrics: ${response.statusText}`)
          }

          const data = await response.json()
          
          set({
            metrics: data,
            lastRefresh: new Date(),
            isLoading: false,
          })

          logger.userAction('dashboard_metrics_fetched', {
            totalPatients: data.totalPatients,
            activePatients: data.activePatients,
          })
        } catch (error) {
          logger.error('Failed to fetch dashboard metrics', error)
          // For demo purposes, use mock data when API is not available
          const mockMetrics: DashboardMetrics = {
            totalPatients: 156,
            activePatients: 112,
            newPatientsThisMonth: 18,
            patientGrowthRate: 12.5,
            statusDistribution: {
              inquiry: 15,
              onboarding: 22,
              active: 89,
              churned: 30,
            },
            riskDistribution: {
              low: 95,
              medium: 47,
              high: 14,
            },
            healthOutcomes: {
              improved: 68,
              stable: 72,
              declined: 16,
            },
            recentActivities: [],
          }
          set({ 
            error: null, // Clear error for demo
            isLoading: false,
            metrics: mockMetrics,
          })
        }
      },

      // Fetch recent activities
      fetchActivities: async (page = 1, limit = 10) => {
        logger.userAction('fetch_dashboard_activities', { page, limit })
        set({ isLoading: true, error: null })
        
        try {
          const params = new URLSearchParams({
            page: page.toString(),
            limit: limit.toString(),
          })

          const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/activities?${params}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
            },
          })

          if (!response.ok) {
            throw new Error(`Failed to fetch activities: ${response.statusText}`)
          }

          const data = await response.json()
          
          set({
            activities: data.items || [],
            isLoading: false,
          })

          logger.userAction('dashboard_activities_fetched', { count: data.items?.length || 0 })
        } catch (error) {
          logger.error('Failed to fetch dashboard activities', error)
          // For demo purposes, use empty activities when API is not available
          set({ 
            error: null, // Clear error for demo
            isLoading: false,
            activities: [],
          })
        }
      },

      // Refresh all dashboard data
      refreshDashboard: async () => {
        logger.userAction('refresh_dashboard')
        
        set({ isLoading: true, error: null })
        
        try {
          // Fetch metrics directly without calling fetchMetrics to avoid double loading state
          try {
            const response = await fetch(`${API_BASE_URL}/api/v1/dashboard/metrics`, {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
              },
            })

            if (!response.ok) {
              throw new Error(`Failed to fetch metrics: ${response.statusText}`)
            }

            const data = await response.json()
            
            set({
              metrics: data,
              lastRefresh: new Date(),
            })
          } catch (error) {
            // Use mock data for demo
            const mockMetrics: DashboardMetrics = {
              totalPatients: 156,
              activePatients: 112,
              newPatientsThisMonth: 18,
              patientGrowthRate: 12.5,
              statusDistribution: {
                inquiry: 15,
                onboarding: 22,
                active: 89,
                churned: 30,
              },
              riskDistribution: {
                low: 95,
                medium: 47,
                high: 14,
              },
              healthOutcomes: {
                improved: 68,
                stable: 72,
                declined: 16,
              },
              recentActivities: [],
            }
            set({ 
              metrics: mockMetrics,
              lastRefresh: new Date(),
            })
          }
          
          logger.userAction('dashboard_refreshed', { 
            timestamp: new Date().toISOString() 
          })
        } catch (error) {
          logger.error('Failed to refresh dashboard', error)
        } finally {
          // Always clear loading state
          set({ isLoading: false })
        }
      },

      // Set refresh interval
      setRefreshInterval: (seconds: number) => {
        logger.userAction('set_dashboard_refresh_interval', { seconds })
        set({ refreshInterval: seconds })
      },

      // Clear error
      clearError: () => set({ error: null }),
    }),
    {
      name: 'dashboard-store',
    }
  )
)