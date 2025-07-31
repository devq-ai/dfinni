export interface DashboardMetrics {
  totalPatients: number
  activePatients: number
  newPatientsThisMonth: number
  patientGrowthRate: number
  statusDistribution: {
    inquiry: number
    onboarding: number
    active: number
    churned: number
  }
  riskDistribution: {
    low: number
    medium: number
    high: number
  }
  healthOutcomes: {
    improved: number
    stable: number
    declined: number
  }
  recentActivities: Activity[]
}

export interface Activity {
  id: string
  type: 'patient_added' | 'status_changed' | 'risk_updated' | 'alert_created'
  title: string
  description: string
  patientId?: string
  patientName?: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface MetricCard {
  title: string
  value: number | string
  change?: number
  changeType?: 'increase' | 'decrease' | 'neutral'
  icon?: string
  color?: string
}