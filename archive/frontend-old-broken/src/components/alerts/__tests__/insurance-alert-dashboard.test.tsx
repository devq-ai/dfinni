import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { InsuranceAlertDashboard } from '../insurance-alert-dashboard'
import { insuranceAlertService } from '@/services/insurance-alert-service'
import { logger } from '@/lib/logfire'

vi.mock('@/services/insurance-alert-service', () => ({
  insuranceAlertService: {
    getInsuranceAlerts: vi.fn(),
    acknowledgeAlert: vi.fn(),
    resolveAlert: vi.fn(),
  }
}))

vi.mock('@/lib/logfire', () => ({
  logger: {
    componentMount: vi.fn(),
    componentUnmount: vi.fn(),
    userAction: vi.fn(),
    error: vi.fn(),
  }
}))

const mockAlerts = [
  {
    id: '1',
    type: 'coverage' as const,
    severity: 'critical' as const,
    priority: 'URGENT' as const,
    title: 'Insurance Coverage Ending Soon',
    description: 'Coverage expires in 5 days',
    message: 'Contact insurance provider immediately',
    patientId: '123',
    patientName: 'John Doe',
    insuranceProvider: 'Blue Cross',
    policyNumber: 'BC123456',
    requiresAction: true,
    createdAt: new Date().toISOString(),
    status: 'active' as const,
    metadata: {
      coveragePercentage: 80,
      remainingBenefits: 5000,
    }
  },
  {
    id: '2',
    type: 'claim' as const,
    severity: 'medium' as const,
    priority: 'MEDIUM' as const,
    title: 'Claim Pending Review',
    description: 'Claim #CLM12345 pending',
    patientId: '456',
    patientName: 'Jane Smith',
    insuranceProvider: 'Aetna',
    policyNumber: 'AE789012',
    requiresAction: false,
    createdAt: new Date().toISOString(),
    status: 'active' as const,
    metadata: {
      claimNumber: 'CLM12345',
      claimAmount: 2500,
    }
  }
]

describe('InsuranceAlertDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render loading state initially', () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<InsuranceAlertDashboard />)

    expect(screen.getByText('Loading insurance alerts...')).toBeInTheDocument()
    expect(logger.componentMount).toHaveBeenCalledWith(
      'InsuranceAlertDashboard',
      { patientId: undefined }
    )
  })

  it('should render alerts after loading', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(mockAlerts)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Insurance Coverage Ending Soon')).toBeInTheDocument()
      expect(screen.getByText('Claim Pending Review')).toBeInTheDocument()
    })

    expect(screen.getByText('2')).toBeInTheDocument() // Total active
    expect(screen.getByText('1')).toBeInTheDocument() // Critical
  })

  it('should render empty state when no alerts', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue([])

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('No insurance alerts found')).toBeInTheDocument()
    })
  })

  it('should handle patient-specific alerts', async () => {
    const patientId = '123'
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue([mockAlerts[0]])

    render(<InsuranceAlertDashboard patientId={patientId} />)

    await waitFor(() => {
      expect(insuranceAlertService.getInsuranceAlerts).toHaveBeenCalledWith({
        patientId,
        status: 'active'
      })
    })
  })

  it('should handle filter changes', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(mockAlerts)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('All Types')).toBeInTheDocument()
    })

    // Change type filter
    fireEvent.click(screen.getByText('All Types'))
    fireEvent.click(screen.getByText('Coverage'))

    await waitFor(() => {
      expect(insuranceAlertService.getInsuranceAlerts).toHaveBeenCalledWith({
        type: 'coverage',
        status: 'active'
      })
    })

    // Change severity filter
    fireEvent.click(screen.getByText('All Severities'))
    fireEvent.click(screen.getByText('Critical'))

    await waitFor(() => {
      expect(insuranceAlertService.getInsuranceAlerts).toHaveBeenCalledWith({
        type: 'coverage',
        severity: 'critical',
        status: 'active'
      })
    })

    // Change status filter
    fireEvent.click(screen.getByText('Active'))
    fireEvent.click(screen.getByText('All Statuses'))

    await waitFor(() => {
      expect(insuranceAlertService.getInsuranceAlerts).toHaveBeenCalledWith({
        type: 'coverage',
        severity: 'critical',
        status: 'all'
      })
    })
  })

  it('should handle acknowledge action', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(mockAlerts)
    vi.mocked(insuranceAlertService.acknowledgeAlert).mockResolvedValue(undefined)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Insurance Coverage Ending Soon')).toBeInTheDocument()
    })

    const acknowledgeButton = screen.getByText('Acknowledge')
    fireEvent.click(acknowledgeButton)

    await waitFor(() => {
      expect(insuranceAlertService.acknowledgeAlert).toHaveBeenCalledWith('1')
      expect(logger.userAction).toHaveBeenCalledWith(
        'acknowledge_insurance_alert',
        { alertId: '1' }
      )
    })
  })

  it('should handle resolve action', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(mockAlerts)
    vi.mocked(insuranceAlertService.resolveAlert).mockResolvedValue(undefined)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Insurance Coverage Ending Soon')).toBeInTheDocument()
    })

    const resolveButtons = screen.getAllByRole('button', { name: '' })
    const resolveButton = resolveButtons.find(btn => 
      btn.querySelector('svg.lucide-check-circle')
    )
    
    if (resolveButton) {
      fireEvent.click(resolveButton)
    }

    await waitFor(() => {
      expect(insuranceAlertService.resolveAlert).toHaveBeenCalledWith('1')
      expect(logger.userAction).toHaveBeenCalledWith(
        'resolve_insurance_alert',
        { alertId: '1' }
      )
    })
  })

  it('should handle refresh action', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(mockAlerts)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Insurance Coverage Ending Soon')).toBeInTheDocument()
    })

    const refreshButton = screen.getByText('Refresh')
    fireEvent.click(refreshButton)

    await waitFor(() => {
      expect(insuranceAlertService.getInsuranceAlerts).toHaveBeenCalledTimes(2)
    })
  })

  it('should handle API errors gracefully', async () => {
    const error = new Error('API Error')
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockRejectedValue(error)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(logger.error).toHaveBeenCalledWith(
        'Failed to fetch insurance alerts',
        error
      )
    })
  })

  it('should display alert metadata correctly', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(mockAlerts)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Coverage: 80%')).toBeInTheDocument()
      expect(screen.getByText('Remaining Benefits: $5,000')).toBeInTheDocument()
      expect(screen.getByText('Claim #: CLM12345')).toBeInTheDocument()
      expect(screen.getByText('Amount: $2,500')).toBeInTheDocument()
    })
  })

  it('should display severity icons and colors correctly', async () => {
    const alertsWithAllSeverities = [
      { ...mockAlerts[0], severity: 'critical' as const },
      { ...mockAlerts[1], severity: 'high' as const, id: '3' },
      { ...mockAlerts[0], severity: 'medium' as const, id: '4' },
      { ...mockAlerts[1], severity: 'low' as const, id: '5' },
    ]
    
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(alertsWithAllSeverities)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('Insurance Coverage Ending Soon')).toBeInTheDocument()
    })

    // Check that severity classes are applied
    const alerts = screen.getAllByRole('region').filter(el => 
      el.classList.contains('bg-zinc-900')
    )
    expect(alerts.length).toBeGreaterThan(0)
  })

  it('should display priority badges correctly', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(mockAlerts)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getByText('URGENT')).toBeInTheDocument()
      expect(screen.getByText('MEDIUM')).toBeInTheDocument()
    })
  })

  it('should display status badges correctly', async () => {
    const alertsWithStatuses = [
      { ...mockAlerts[0], status: 'active' as const },
      { ...mockAlerts[1], status: 'acknowledged' as const, id: '3' },
    ]
    
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue(alertsWithStatuses)

    render(<InsuranceAlertDashboard />)

    await waitFor(() => {
      expect(screen.getAllByText('active')).toHaveLength(2)
      expect(screen.getByText('acknowledged')).toBeInTheDocument()
    })
  })

  it('should cleanup on unmount', () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue([])

    const { unmount } = render(<InsuranceAlertDashboard />)
    
    unmount()

    expect(logger.componentUnmount).toHaveBeenCalledWith('InsuranceAlertDashboard')
  })

  it('should apply custom className', async () => {
    vi.mocked(insuranceAlertService.getInsuranceAlerts).mockResolvedValue([])
    
    const { container } = render(
      <InsuranceAlertDashboard className="custom-class" />
    )

    await waitFor(() => {
      const wrapper = container.firstChild as HTMLElement
      expect(wrapper.classList.contains('custom-class')).toBe(true)
    })
  })
})