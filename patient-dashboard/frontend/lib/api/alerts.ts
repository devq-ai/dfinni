// Last Updated: 2025-08-09T20:12:00-06:00
import { Alert, AlertListResponse, CreateAlertDto } from '@/types/alert'

const API_BASE_URL = 'https://db.devq.ai'

export const alertsApi = {
  async getAlerts(getHeaders: () => Promise<HeadersInit>, page = 1, pageSize = 10, status?: string): Promise<AlertListResponse> {
    try {
      // Temporarily use test endpoint to get actual database data
      const response = await fetch(`${API_BASE_URL}/api/v1/test-alerts-stats`, {
        headers: {
          'Content-Type': 'application/json'
        },
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch alerts')
      }
      
      const data = await response.json()
      return {
        alerts: data.data?.alerts || [],
        total: data.data?.stats?.total || 0,
        page: 1,
        pageSize: 10,
        data: data.data  // Include the full data object for compatibility
      }
    } catch (error) {
      console.warn('API not available, returning mock data')
      return getMockAlerts(page, pageSize, status)
    }
  },

  async acknowledgeAlert(getHeaders: () => Promise<HeadersInit>, id: string): Promise<Alert> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/alerts/${id}/acknowledge`, {
        method: 'POST',
        headers: await getHeaders(),
      })
      
      if (!response.ok) {
        throw new Error('Failed to acknowledge alert')
      }
      
      return response.json()
    } catch (error) {
      const alerts = getMockAlerts(1, 100).alerts
      const alert = alerts.find(a => a.id === id)
      if (!alert) throw new Error('Alert not found')
      return { ...alert, status: 'acknowledged', updatedAt: new Date().toISOString() }
    }
  },

  async resolveAlert(getHeaders: () => Promise<HeadersInit>, id: string): Promise<Alert> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/alerts/${id}/resolve`, {
        method: 'POST',
        headers: await getHeaders(),
      })
      
      if (!response.ok) {
        throw new Error('Failed to resolve alert')
      }
      
      return response.json()
    } catch (error) {
      const alerts = getMockAlerts(1, 100).alerts
      const alert = alerts.find(a => a.id === id)
      if (!alert) throw new Error('Alert not found')
      return { ...alert, status: 'resolved', updatedAt: new Date().toISOString() }
    }
  },
}

// Mock data function
function getMockAlerts(page: number, pageSize: number, status?: string): AlertListResponse {
  const alerts: Alert[] = [
    {
      id: '1',
      type: 'insurance',
      severity: 'high',
      title: 'Prior Authorization Required',
      description: 'Prior authorization needed for MRI scan - Patient John Doe',
      patientId: '1',
      patientName: 'John Doe',
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      status: 'new',
      metadata: {
        claimId: 'CLM-2024-001',
        procedureCode: '70553',
        procedureName: 'MRI Brain with Contrast',
      },
    },
    {
      id: '2',
      type: 'clinical',
      severity: 'critical',
      title: 'Critical Lab Result',
      description: 'HbA1c level 11.2% - Immediate intervention needed',
      patientId: '3',
      patientName: 'Robert Johnson',
      createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      status: 'new',
      metadata: {
        labTestName: 'HbA1c',
        result: '11.2%',
        normalRange: '4.0-5.6%',
      },
    },
    {
      id: '3',
      type: 'medication',
      severity: 'medium',
      title: 'Medication Refill Due',
      description: 'Metformin prescription expires in 7 days',
      patientId: '1',
      patientName: 'John Doe',
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      status: 'acknowledged',
      metadata: {
        medicationName: 'Metformin 500mg',
        expiryDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      },
    },
    {
      id: '4',
      type: 'appointment',
      severity: 'low',
      title: 'Upcoming Appointment Reminder',
      description: 'Annual checkup scheduled for next week',
      patientId: '2',
      patientName: 'Jane Smith',
      createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      status: 'acknowledged',
      metadata: {
        appointmentDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        appointmentType: 'Annual Physical',
      },
    },
    {
      id: '5',
      type: 'insurance',
      severity: 'medium',
      title: 'Coverage Verification Needed',
      description: 'Insurance eligibility check required for upcoming procedure',
      patientId: '2',
      patientName: 'Jane Smith',
      createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      status: 'new',
      metadata: {
        procedureName: 'Colonoscopy',
        scheduledDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
      },
    },
    {
      id: '6',
      type: 'lab',
      severity: 'high',
      title: 'Lab Results Pending Review',
      description: 'Lipid panel results require physician review',
      patientId: '3',
      patientName: 'Robert Johnson',
      createdAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      status: 'new',
      metadata: {
        labTestName: 'Lipid Panel',
        totalCholesterol: '285 mg/dL',
        ldl: '190 mg/dL',
        hdl: '35 mg/dL',
      },
    },
  ]

  let filteredAlerts = alerts
  if (status) {
    filteredAlerts = alerts.filter(alert => alert.status === status)
  }

  const start = (page - 1) * pageSize
  const end = start + pageSize

  return {
    alerts: filteredAlerts.slice(start, end),
    total: filteredAlerts.length,
    page,
    pageSize,
  }
}