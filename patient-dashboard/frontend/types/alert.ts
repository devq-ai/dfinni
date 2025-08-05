export interface Alert {
  id: string
  type: 'insurance' | 'clinical' | 'appointment' | 'medication' | 'lab'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  patientId?: string
  patientName?: string
  createdAt: string
  updatedAt: string
  status: 'new' | 'acknowledged' | 'resolved'
  metadata?: {
    claimId?: string
    appointmentId?: string
    medicationName?: string
    labTestName?: string
    dueDate?: string
    [key: string]: any
  }
}

export interface AlertListResponse {
  alerts: Alert[]
  total: number
  page: number
  pageSize: number
  data?: {
    alerts: Alert[]
    stats?: {
      total: number
      byType?: Record<string, number>
      bySeverity?: Record<string, number>
    }
  }
}

export interface CreateAlertDto {
  type: 'insurance' | 'clinical' | 'appointment' | 'medication' | 'lab'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  patientId?: string
  metadata?: Record<string, any>
}