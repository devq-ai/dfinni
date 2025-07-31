'use client'

import { useEffect, Suspense } from 'react'
import { useDashboardStore } from '@/stores/dashboard-store'
import { usePatientStore } from '@/stores/patient-store'
import { logger } from '@/lib/logfire'
import { MetricCard } from '@/components/dashboard/metric-card'
import { QuickActions } from '@/components/dashboard/quick-actions'
import { DynamicComponents } from '@/lib/dynamic-imports'
import { 
  Users, 
  AlertCircle,
  UserCheck,
  Calendar
} from 'lucide-react'

// Use dynamic imports for heavy components
const { ActivityFeed, StatusDistributionChart } = DynamicComponents

export default function DashboardPage() {
  const { metrics, refreshDashboard, isLoading, error } = useDashboardStore()
  const { totalCount: patientCount } = usePatientStore()

  useEffect(() => {
    logger.pageView('/dashboard')
    refreshDashboard()
  }, [])

  // Temporarily disable auto-refresh to prevent browser crash
  // useEffect(() => {
  //   // Set up auto-refresh every 30 seconds
  //   const interval = setInterval(() => {
  //     logger.userAction('dashboard_auto_refresh')
  //     refreshDashboard()
  //   }, 30000)

  //   return () => clearInterval(interval)
  // }, [refreshDashboard])

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-6 text-red-500">
          <h2 className="text-lg font-semibold mb-2">Error Loading Dashboard</h2>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  const mockMetrics = metrics || {
    totalPatients: patientCount || 0,
    activePatients: Math.floor((patientCount || 0) * 0.7),
    newPatientsThisMonth: Math.floor((patientCount || 0) * 0.1),
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
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-zinc-100">Dashboard</h1>
        <p className="text-zinc-400 mt-1">
          Welcome back! Here&apos;s an overview of your patient management system.
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Patients"
          value={mockMetrics.totalPatients}
          icon={<Users />}
          color="blue"
        />
        <MetricCard
          title="Active Patients"
          value={mockMetrics.activePatients}
          icon={<UserCheck />}
          color="green"
          change={5.2}
          changeType="increase"
        />
        <MetricCard
          title="New This Month"
          value={mockMetrics.newPatientsThisMonth}
          icon={<Calendar />}
          color="purple"
          change={mockMetrics.patientGrowthRate}
          changeType={mockMetrics.patientGrowthRate > 0 ? 'increase' : 'decrease'}
        />
        <MetricCard
          title="High Risk Patients"
          value={mockMetrics.riskDistribution.high}
          icon={<AlertCircle />}
          color="red"
          change={-2.1}
          changeType="decrease"
        />
      </div>

      {/* Charts and Activity Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Status Distribution Chart */}
        <div className="lg:col-span-2">
          <Suspense fallback={
            <div className="h-64 bg-zinc-900 border border-zinc-800 rounded-lg p-6 flex items-center justify-center">
              <div className="animate-pulse text-zinc-500">Loading chart...</div>
            </div>
          }>
            <StatusDistributionChart />
          </Suspense>
        </div>

        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <QuickActions />
        </div>
      </div>

      {/* Activity Feed */}
      <div>
        <Suspense fallback={
          <div className="h-64 bg-zinc-900 border border-zinc-800 rounded-lg p-6 flex items-center justify-center">
            <div className="animate-pulse text-zinc-500">Loading activities...</div>
          </div>
        }>
          <ActivityFeed />
        </Suspense>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
              <p className="text-zinc-100">Refreshing dashboard...</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}