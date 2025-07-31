import { logger } from '@/lib/logfire'

export interface InsuranceAlert {
  id: string
  type: 'eligibility' | 'coverage' | 'claim' | 'authorization' | 'expiry'
  severity: 'low' | 'medium' | 'high' | 'critical'
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT'
  title: string
  description: string
  message?: string
  patientId?: string
  patientName?: string
  insuranceProvider?: string
  policyNumber?: string
  expiresAt?: string
  requiresAction: boolean
  metadata?: {
    claimNumber?: string
    authorizationNumber?: string
    coveragePercentage?: number
    remainingBenefits?: number
    x12TransactionId?: string
    [key: string]: any
  }
  createdAt: string
  status: 'active' | 'acknowledged' | 'resolved' | 'expired'
}

export interface InsuranceAlertPattern {
  id: string
  name: string
  description: string
  x12Segments: string[]
  triggerConditions: {
    field: string
    operator: 'equals' | 'contains' | 'greater' | 'less' | 'expired'
    value: any
  }[]
  alertTemplate: {
    type: InsuranceAlert['type']
    severity: InsuranceAlert['severity']
    priority: InsuranceAlert['priority']
    titleTemplate: string
    descriptionTemplate: string
  }
}

// Mock X12 patterns for demonstration
const INSURANCE_ALERT_PATTERNS: InsuranceAlertPattern[] = [
  {
    id: 'coverage-ending',
    name: 'Coverage Ending Soon',
    description: 'Alert when insurance coverage is ending within 30 days',
    x12Segments: ['DTP*348', 'DTP*349'], // Coverage period segments
    triggerConditions: [
      {
        field: 'coverageEndDate',
        operator: 'less',
        value: 30 // days
      }
    ],
    alertTemplate: {
      type: 'coverage',
      severity: 'high',
      priority: 'HIGH',
      titleTemplate: 'Insurance Coverage Ending Soon',
      descriptionTemplate: 'Coverage for {{patientName}} with {{insuranceProvider}} expires in {{daysRemaining}} days'
    }
  },
  {
    id: 'eligibility-check-failed',
    name: 'Eligibility Check Failed',
    description: 'Alert when patient eligibility verification fails',
    x12Segments: ['EB*N'], // Eligibility response with rejection
    triggerConditions: [
      {
        field: 'eligibilityStatus',
        operator: 'equals',
        value: 'N' // Not eligible
      }
    ],
    alertTemplate: {
      type: 'eligibility',
      severity: 'critical',
      priority: 'URGENT',
      titleTemplate: 'Eligibility Verification Failed',
      descriptionTemplate: 'Patient {{patientName}} is not eligible for coverage under policy {{policyNumber}}'
    }
  },
  {
    id: 'high-claim-rejection',
    name: 'High Value Claim Rejected',
    description: 'Alert when claims over $5000 are rejected',
    x12Segments: ['CLP*', 'CAS*'], // Claim payment and adjustment segments
    triggerConditions: [
      {
        field: 'claimAmount',
        operator: 'greater',
        value: 5000
      },
      {
        field: 'claimStatus',
        operator: 'equals',
        value: 'rejected'
      }
    ],
    alertTemplate: {
      type: 'claim',
      severity: 'high',
      priority: 'HIGH',
      titleTemplate: 'High Value Claim Rejected',
      descriptionTemplate: 'Claim #{{claimNumber}} for ${{claimAmount}} was rejected. Reason: {{rejectionReason}}'
    }
  },
  {
    id: 'prior-auth-expiring',
    name: 'Prior Authorization Expiring',
    description: 'Alert when prior authorization is expiring within 7 days',
    x12Segments: ['REF*G1', 'DTP*435'], // Authorization reference and expiry date
    triggerConditions: [
      {
        field: 'authExpiryDate',
        operator: 'less',
        value: 7 // days
      }
    ],
    alertTemplate: {
      type: 'authorization',
      severity: 'medium',
      priority: 'MEDIUM',
      titleTemplate: 'Prior Authorization Expiring',
      descriptionTemplate: 'Authorization #{{authorizationNumber}} for {{patientName}} expires in {{daysRemaining}} days'
    }
  }
]

class InsuranceAlertService {
  private apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

  async generateAlertsFromX12(x12Data: string): Promise<InsuranceAlert[]> {
    logger.userAction('generate_insurance_alerts_from_x12', { 
      dataLength: x12Data.length 
    })

    try {
      // In production, this would parse actual X12 data
      // For now, we'll simulate based on patterns
      const alerts: InsuranceAlert[] = []
      
      // Simulate pattern matching
      INSURANCE_ALERT_PATTERNS.forEach(pattern => {
        // Mock: randomly decide if pattern matches
        if (Math.random() > 0.7) {
          const alert = this.createAlertFromPattern(pattern)
          alerts.push(alert)
        }
      })

      logger.userAction('insurance_alerts_generated', { 
        count: alerts.length 
      })

      return alerts
    } catch (error) {
      logger.error('Failed to generate insurance alerts', error)
      throw error
    }
  }

  async getInsuranceAlerts(params?: {
    patientId?: string
    type?: InsuranceAlert['type']
    severity?: InsuranceAlert['severity']
    status?: InsuranceAlert['status']
  }): Promise<InsuranceAlert[]> {
    logger.userAction('fetch_insurance_alerts', params)

    try {
      const queryParams = new URLSearchParams()
      if (params?.patientId) queryParams.append('patient_id', params.patientId)
      if (params?.type) queryParams.append('type', params.type)
      if (params?.severity) queryParams.append('severity', params.severity)
      if (params?.status) queryParams.append('status', params.status)

      const response = await fetch(
        `${this.apiUrl}/api/v1/alerts?${queryParams.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to fetch insurance alerts')
      }

      const data = await response.json()
      
      // Filter for insurance-related alerts
      const insuranceAlerts = data.alerts.filter((alert: any) => 
        alert.type === 'insurance_expiry' || 
        alert.metadata?.insuranceRelated
      )

      return insuranceAlerts
    } catch (error) {
      logger.error('Failed to fetch insurance alerts', error)
      // Return mock data for demo
      return this.getMockInsuranceAlerts()
    }
  }

  async createInsuranceAlert(alert: Omit<InsuranceAlert, 'id' | 'createdAt' | 'status'>): Promise<InsuranceAlert> {
    logger.userAction('create_insurance_alert', { 
      type: alert.type,
      severity: alert.severity 
    })

    try {
      const response = await fetch(`${this.apiUrl}/api/v1/alerts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          ...alert,
          metadata: {
            ...alert.metadata,
            insuranceRelated: true
          }
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to create insurance alert')
      }

      const data = await response.json()
      return data
    } catch (error) {
      logger.error('Failed to create insurance alert', error)
      throw error
    }
  }

  async acknowledgeAlert(alertId: string): Promise<void> {
    logger.userAction('acknowledge_insurance_alert', { alertId })

    try {
      const response = await fetch(`${this.apiUrl}/api/v1/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to acknowledge alert')
      }
    } catch (error) {
      logger.error('Failed to acknowledge insurance alert', error)
      throw error
    }
  }

  async resolveAlert(alertId: string, resolutionNotes?: string): Promise<void> {
    logger.userAction('resolve_insurance_alert', { alertId })

    try {
      const response = await fetch(`${this.apiUrl}/api/v1/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({ resolution_notes: resolutionNotes }),
      })

      if (!response.ok) {
        throw new Error('Failed to resolve alert')
      }
    } catch (error) {
      logger.error('Failed to resolve insurance alert', error)
      throw error
    }
  }

  private createAlertFromPattern(pattern: InsuranceAlertPattern): InsuranceAlert {
    // Mock data generation
    const mockPatients = [
      { id: '1', name: 'John Doe', provider: 'Blue Cross', policy: 'BC123456' },
      { id: '2', name: 'Jane Smith', provider: 'Aetna', policy: 'AE789012' },
      { id: '3', name: 'Bob Johnson', provider: 'UnitedHealth', policy: 'UH345678' },
    ]

    const patient = mockPatients[Math.floor(Math.random() * mockPatients.length)]
    
    return {
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: pattern.alertTemplate.type,
      severity: pattern.alertTemplate.severity,
      priority: pattern.alertTemplate.priority,
      title: pattern.alertTemplate.titleTemplate
        .replace('{{patientName}}', patient.name)
        .replace('{{insuranceProvider}}', patient.provider),
      description: pattern.alertTemplate.descriptionTemplate
        .replace('{{patientName}}', patient.name)
        .replace('{{insuranceProvider}}', patient.provider)
        .replace('{{policyNumber}}', patient.policy)
        .replace('{{daysRemaining}}', String(Math.floor(Math.random() * 30)))
        .replace('{{claimNumber}}', `CLM${Math.floor(Math.random() * 100000)}`)
        .replace('{{claimAmount}}', String(Math.floor(Math.random() * 10000) + 5000))
        .replace('{{authorizationNumber}}', `AUTH${Math.floor(Math.random() * 100000)}`),
      patientId: patient.id,
      patientName: patient.name,
      insuranceProvider: patient.provider,
      policyNumber: patient.policy,
      requiresAction: pattern.alertTemplate.severity === 'high' || pattern.alertTemplate.severity === 'critical',
      createdAt: new Date().toISOString(),
      status: 'active',
      metadata: {
        x12TransactionId: `X12-${Date.now()}`,
        generatedFromPattern: pattern.id
      }
    }
  }

  private getMockInsuranceAlerts(): InsuranceAlert[] {
    return [
      {
        id: '1',
        type: 'coverage',
        severity: 'high',
        priority: 'HIGH',
        title: 'Insurance Coverage Ending Soon',
        description: 'Coverage for John Doe with Blue Cross expires in 15 days',
        patientId: '1',
        patientName: 'John Doe',
        insuranceProvider: 'Blue Cross',
        policyNumber: 'BC123456',
        requiresAction: true,
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        status: 'active',
        metadata: {
          coverageEndDate: new Date(Date.now() + 15 * 86400000).toISOString(),
          coveragePercentage: 80,
          remainingBenefits: 5000
        }
      },
      {
        id: '2',
        type: 'eligibility',
        severity: 'critical',
        priority: 'URGENT',
        title: 'Eligibility Verification Failed',
        description: 'Patient Jane Smith is not eligible for coverage under policy AE789012',
        patientId: '2',
        patientName: 'Jane Smith',
        insuranceProvider: 'Aetna',
        policyNumber: 'AE789012',
        requiresAction: true,
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        status: 'active',
        metadata: {
          verificationDate: new Date().toISOString(),
          rejectionCode: 'E001',
          rejectionReason: 'Policy terminated'
        }
      },
      {
        id: '3',
        type: 'claim',
        severity: 'medium',
        priority: 'MEDIUM',
        title: 'Claim Pending Review',
        description: 'Claim #CLM98765 for $2,500 is pending insurance review',
        patientId: '3',
        patientName: 'Bob Johnson',
        insuranceProvider: 'UnitedHealth',
        policyNumber: 'UH345678',
        requiresAction: false,
        createdAt: new Date(Date.now() - 7200000).toISOString(),
        status: 'active',
        metadata: {
          claimNumber: 'CLM98765',
          claimAmount: 2500,
          submittedDate: new Date(Date.now() - 172800000).toISOString()
        }
      }
    ]
  }
}

export const insuranceAlertService = new InsuranceAlertService()