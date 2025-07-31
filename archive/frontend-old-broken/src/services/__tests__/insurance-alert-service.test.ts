import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { insuranceAlertService } from '../insurance-alert-service'
import { logger } from '@/lib/logfire'

vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  }
}))

describe('InsuranceAlertService', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    global.fetch = vi.fn()
    localStorage.setItem('auth_token', 'test-token')
  })

  afterEach(() => {
    vi.restoreAllMocks()
    localStorage.clear()
  })

  describe('generateAlertsFromX12', () => {
    it('should generate alerts from X12 data', async () => {
      const x12Data = 'ISA*00*...'
      const alerts = await insuranceAlertService.generateAlertsFromX12(x12Data)

      expect(logger.userAction).toHaveBeenCalledWith(
        'generate_insurance_alerts_from_x12',
        { dataLength: x12Data.length }
      )
      expect(Array.isArray(alerts)).toBe(true)
      alerts.forEach(alert => {
        expect(alert).toHaveProperty('id')
        expect(alert).toHaveProperty('type')
        expect(alert).toHaveProperty('severity')
        expect(alert).toHaveProperty('priority')
        expect(alert).toHaveProperty('title')
        expect(alert).toHaveProperty('description')
        expect(alert).toHaveProperty('status', 'active')
      })
    })

    it('should handle errors during alert generation', async () => {
      const mockError = new Error('Generation failed')
      vi.spyOn(Math, 'random').mockImplementation(() => {
        throw mockError
      })

      await expect(insuranceAlertService.generateAlertsFromX12('data'))
        .rejects.toThrow('Generation failed')
      
      expect(logger.error).toHaveBeenCalledWith(
        'Failed to generate insurance alerts',
        mockError
      )
    })
  })

  describe('getInsuranceAlerts', () => {
    it('should fetch insurance alerts successfully', async () => {
      const mockAlerts = [
        {
          id: '1',
          type: 'insurance_expiry',
          severity: 'high',
          priority: 'HIGH',
          title: 'Insurance Expiring',
          description: 'Insurance coverage is expiring soon',
          status: 'active',
        }
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ alerts: mockAlerts })
      })

      const alerts = await insuranceAlertService.getInsuranceAlerts()

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/v1/alerts?',
        {
          headers: {
            'Authorization': 'Bearer test-token',
          },
        }
      )
      expect(alerts).toEqual(mockAlerts)
      expect(logger.userAction).toHaveBeenCalledWith('fetch_insurance_alerts', undefined)
    })

    it('should fetch alerts with query parameters', async () => {
      const params = {
        patientId: '123',
        type: 'coverage' as const,
        severity: 'high' as const,
        status: 'active' as const,
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ alerts: [] })
      })

      await insuranceAlertService.getInsuranceAlerts(params)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/v1/alerts?patient_id=123&type=coverage&severity=high&status=active',
        expect.any(Object)
      )
    })

    it('should return mock data on fetch failure', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const alerts = await insuranceAlertService.getInsuranceAlerts()

      expect(alerts.length).toBeGreaterThan(0)
      expect(logger.error).toHaveBeenCalledWith(
        'Failed to fetch insurance alerts',
        expect.any(Error)
      )
    })

    it('should filter insurance-related alerts', async () => {
      const mockAlerts = [
        { id: '1', type: 'insurance_expiry', metadata: {} },
        { id: '2', type: 'other', metadata: { insuranceRelated: true } },
        { id: '3', type: 'other', metadata: {} },
      ]

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ alerts: mockAlerts })
      })

      const alerts = await insuranceAlertService.getInsuranceAlerts()

      expect(alerts).toHaveLength(2)
      expect(alerts.map(a => a.id)).toEqual(['1', '2'])
    })
  })

  describe('createInsuranceAlert', () => {
    it('should create an insurance alert successfully', async () => {
      const newAlert = {
        type: 'coverage' as const,
        severity: 'high' as const,
        priority: 'HIGH' as const,
        title: 'Coverage Alert',
        description: 'Coverage is ending soon',
        requiresAction: true,
      }

      const mockResponse = {
        id: '123',
        ...newAlert,
        createdAt: new Date().toISOString(),
        status: 'active' as const,
      }

      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      })

      const result = await insuranceAlertService.createInsuranceAlert(newAlert)

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/v1/alerts',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
          body: JSON.stringify({
            ...newAlert,
            metadata: {
              insuranceRelated: true
            }
          }),
        }
      )
      expect(result).toEqual(mockResponse)
      expect(logger.userAction).toHaveBeenCalledWith(
        'create_insurance_alert',
        { type: newAlert.type, severity: newAlert.severity }
      )
    })

    it('should handle creation errors', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
      })

      await expect(insuranceAlertService.createInsuranceAlert({
        type: 'coverage',
        severity: 'high',
        priority: 'HIGH',
        title: 'Test',
        description: 'Test',
        requiresAction: true,
      })).rejects.toThrow('Failed to create insurance alert')
    })
  })

  describe('acknowledgeAlert', () => {
    it('should acknowledge an alert successfully', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
      })

      await insuranceAlertService.acknowledgeAlert('alert-123')

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/v1/alerts/alert-123/acknowledge',
        {
          method: 'POST',
          headers: {
            'Authorization': 'Bearer test-token',
          },
        }
      )
      expect(logger.userAction).toHaveBeenCalledWith(
        'acknowledge_insurance_alert',
        { alertId: 'alert-123' }
      )
    })

    it('should handle acknowledgement errors', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
      })

      await expect(insuranceAlertService.acknowledgeAlert('alert-123'))
        .rejects.toThrow('Failed to acknowledge alert')

      expect(logger.error).toHaveBeenCalledWith(
        'Failed to acknowledge insurance alert',
        expect.any(Error)
      )
    })
  })

  describe('resolveAlert', () => {
    it('should resolve an alert successfully', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
      })

      await insuranceAlertService.resolveAlert('alert-123', 'Resolved by user')

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/v1/alerts/alert-123/resolve',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
          body: JSON.stringify({ resolution_notes: 'Resolved by user' }),
        }
      )
      expect(logger.userAction).toHaveBeenCalledWith(
        'resolve_insurance_alert',
        { alertId: 'alert-123' }
      )
    })

    it('should resolve without notes', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
      })

      await insuranceAlertService.resolveAlert('alert-123')

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          body: JSON.stringify({ resolution_notes: undefined }),
        })
      )
    })

    it('should handle resolution errors', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
      })

      await expect(insuranceAlertService.resolveAlert('alert-123'))
        .rejects.toThrow('Failed to resolve alert')

      expect(logger.error).toHaveBeenCalledWith(
        'Failed to resolve insurance alert',
        expect.any(Error)
      )
    })
  })

  describe('private methods', () => {
    it('should create alerts from patterns with correct template replacements', async () => {
      vi.spyOn(Math, 'random')
        .mockReturnValueOnce(0.8) // Make pattern match
        .mockReturnValueOnce(0.1) // Select first patient
        .mockReturnValueOnce(0.5) // For ID generation

      const alerts = await insuranceAlertService.generateAlertsFromX12('test')

      const alert = alerts[0]
      expect(alert).toBeDefined()
      expect(alert.title).toContain('Insurance Coverage Ending Soon')
      expect(alert.description).toMatch(/Coverage for .+ with .+ expires in \d+ days/)
      expect(alert.metadata).toHaveProperty('x12TransactionId')
      expect(alert.metadata).toHaveProperty('generatedFromPattern')
    })

    it('should generate mock alerts with proper structure', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      const alerts = await insuranceAlertService.getInsuranceAlerts()

      expect(alerts.length).toBe(3)
      alerts.forEach(alert => {
        expect(alert).toHaveProperty('id')
        expect(alert).toHaveProperty('type')
        expect(alert).toHaveProperty('severity')
        expect(alert).toHaveProperty('priority')
        expect(alert).toHaveProperty('title')
        expect(alert).toHaveProperty('description')
        expect(alert).toHaveProperty('patientId')
        expect(alert).toHaveProperty('patientName')
        expect(alert).toHaveProperty('insuranceProvider')
        expect(alert).toHaveProperty('policyNumber')
        expect(alert).toHaveProperty('requiresAction')
        expect(alert).toHaveProperty('createdAt')
        expect(alert).toHaveProperty('status')
        expect(alert).toHaveProperty('metadata')
      })
    })
  })
})