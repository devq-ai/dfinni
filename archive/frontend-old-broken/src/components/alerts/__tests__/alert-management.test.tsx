import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AlertManagement } from '../alert-management'
import { usePatientStore } from '@/stores/patient-store'
import { logger } from '@/lib/logfire'
import { addDays } from 'date-fns'

vi.mock('@/stores/patient-store')
vi.mock('@/lib/logfire', () => ({
  logger: {
    componentMount: vi.fn(),
    componentUnmount: vi.fn(),
    userAction: vi.fn(),
  }
}))

const mockPatients = [
  {
    id: '1',
    firstName: 'John',
    lastName: 'Doe',
    dateOfBirth: addDays(new Date(), 5).toISOString(), // Birthday in 5 days
    status: 'Active',
  },
  {
    id: '2',
    firstName: 'Jane',
    lastName: 'Smith',
    dateOfBirth: addDays(new Date(), -30).toISOString(), // Birthday 30 days ago
    status: 'Churned',
  },
  {
    id: '3',
    firstName: 'Bob',
    lastName: 'Johnson',
    dateOfBirth: addDays(new Date(), 15).toISOString(), // Birthday in 15 days
    status: 'Active',
  },
]

describe('AlertManagement', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usePatientStore).mockReturnValue({
      patients: mockPatients,
    } as ReturnType<typeof usePatientStore>)
  })

  it('should render and mount correctly', () => {
    render(<AlertManagement />)

    expect(screen.getByText('Alert Preferences')).toBeInTheDocument()
    expect(logger.componentMount).toHaveBeenCalledWith('AlertManagement')
  })

  it('should generate birthday alerts within threshold', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      // John Doe's birthday is in 5 days (within default 7-day threshold)
      expect(screen.getByText(/John Doe's birthday is in \d+ days/)).toBeInTheDocument()
    })

    expect(logger.userAction).toHaveBeenCalledWith(
      'alerts_generated',
      expect.objectContaining({ count: expect.any(Number) })
    )
  })

  it('should generate status change alerts', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      // Should show status change alerts
      const statusChangeAlerts = screen.getAllByText('Patient Status Changed')
      expect(statusChangeAlerts.length).toBeGreaterThan(0)
    })
  })

  it('should generate urgent care alerts when enough patients exist', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      // Should show urgent care alert for third patient
      expect(screen.getByText('Urgent Care Needed')).toBeInTheDocument()
      expect(screen.getByText(/Bob Johnson has critical lab results/)).toBeInTheDocument()
    })
  })

  it('should toggle edit preferences mode', async () => {
    render(<AlertManagement />)

    const editButton = screen.getByText('Edit')
    fireEvent.click(editButton)

    expect(screen.getByText('Save')).toBeInTheDocument()
    
    // Days before input should be visible
    expect(screen.getByDisplayValue('7')).toBeInTheDocument()
  })

  it('should update birthday alert preferences', async () => {
    render(<AlertManagement />)

    // Enter edit mode
    fireEvent.click(screen.getByText('Edit'))

    // Change days before
    const daysInput = screen.getByDisplayValue('7')
    fireEvent.change(daysInput, { target: { value: '14' } })

    // Save preferences
    fireEvent.click(screen.getByText('Save'))

    // Should regenerate alerts with new preferences
    await waitFor(() => {
      expect(logger.userAction).toHaveBeenCalledWith(
        'alerts_generated',
        expect.any(Object)
      )
    })
  })

  it('should toggle alert types on/off', async () => {
    render(<AlertManagement />)

    // Enter edit mode
    fireEvent.click(screen.getByText('Edit'))

    // Find and uncheck birthday alerts
    const birthdayCheckbox = screen.getByLabelText('Birthday Alerts')
    fireEvent.click(birthdayCheckbox)

    // Save
    fireEvent.click(screen.getByText('Save'))

    // Birthday alerts should not be generated
    await waitFor(() => {
      expect(screen.queryByText(/birthday is in/)).not.toBeInTheDocument()
    })
  })

  it('should acknowledge alerts', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      expect(screen.getByText('Urgent Care Needed')).toBeInTheDocument()
    })

    // Find acknowledge button for urgent care alert
    const acknowledgeButtons = screen.getAllByRole('button').filter(btn =>
      btn.querySelector('svg.lucide-check-circle')
    )
    
    if (acknowledgeButtons.length > 0) {
      fireEvent.click(acknowledgeButtons[0])

      expect(logger.userAction).toHaveBeenCalledWith(
        'acknowledge_system_alert',
        expect.objectContaining({ alertId: expect.any(String) })
      )
    }
  })

  it('should display empty state when no alerts', async () => {
    vi.mocked(usePatientStore).mockReturnValue({
      patients: [],
    } as ReturnType<typeof usePatientStore>)

    render(<AlertManagement />)

    await waitFor(() => {
      expect(screen.getByText('No active alerts')).toBeInTheDocument()
    })
  })

  it('should display alert icons based on type', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      const container = screen.getByText('Upcoming Birthday').closest('div')
      expect(container?.querySelector('svg.lucide-cake')).toBeInTheDocument()
    })
  })

  it('should display priority colors correctly', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      // High priority urgent care alert should have red border
      const urgentAlert = screen.getByText('Urgent Care Needed').closest('.bg-zinc-900')
      expect(urgentAlert?.classList.toString()).toMatch(/border-red/)
    })
  })

  it('should display status badges', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      expect(screen.getByText('pending')).toBeInTheDocument()
      expect(screen.getByText('sent')).toBeInTheDocument()
    })
  })

  it('should cleanup on unmount', () => {
    const { unmount } = render(<AlertManagement />)
    
    unmount()

    expect(logger.componentUnmount).toHaveBeenCalledWith('AlertManagement')
  })

  it('should handle patients without birth dates', async () => {
    vi.mocked(usePatientStore).mockReturnValue({
      patients: [
        { ...mockPatients[0], dateOfBirth: undefined },
        { ...mockPatients[1], dateOfBirth: null },
      ],
    } as ReturnType<typeof usePatientStore>)

    render(<AlertManagement />)

    await waitFor(() => {
      // Should not crash and should show other alerts
      expect(screen.queryByText(/birthday is in/)).not.toBeInTheDocument()
    })
  })

  it('should handle invalid preference values', async () => {
    render(<AlertManagement />)

    fireEvent.click(screen.getByText('Edit'))

    const daysInput = screen.getByDisplayValue('7')
    fireEvent.change(daysInput, { target: { value: 'invalid' } })

    fireEvent.click(screen.getByText('Save'))

    // Should default to 7 days
    await waitFor(() => {
      expect(screen.getByDisplayValue('7')).toBeInTheDocument()
    })
  })

  it('should not show acknowledged alerts as actionable', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      expect(screen.getByText('Urgent Care Needed')).toBeInTheDocument()
    })

    // Acknowledge first alert
    const acknowledgeButtons = screen.getAllByRole('button').filter(btn =>
      btn.querySelector('svg.lucide-check-circle')
    )
    
    if (acknowledgeButtons.length > 0) {
      fireEvent.click(acknowledgeButtons[0])

      await waitFor(() => {
        const acknowledgedAlert = screen.getByText('Urgent Care Needed').closest('.bg-zinc-900')
        expect(acknowledgedAlert?.classList.contains('opacity-60')).toBe(true)
        
        // Acknowledge button should be gone
        const updatedButtons = acknowledgedAlert?.querySelectorAll('button').length || 0
        expect(updatedButtons).toBe(0)
      })
    }
  })

  it('should calculate birthday correctly for past birthdays this year', async () => {
    const pastBirthdayThisYear = new Date()
    pastBirthdayThisYear.setMonth(pastBirthdayThisYear.getMonth() - 1)

    vi.mocked(usePatientStore).mockReturnValue({
      patients: [{
        id: '4',
        firstName: 'Past',
        lastName: 'Birthday',
        dateOfBirth: pastBirthdayThisYear.toISOString(),
        status: 'Active',
      }],
    } as ReturnType<typeof usePatientStore>)

    render(<AlertManagement />)

    await waitFor(() => {
      // Should calculate for next year's birthday
      expect(screen.queryByText(/Past Birthday's birthday is in/)).toBeInTheDocument()
    })
  })

  it('should respect status filter preferences', async () => {
    render(<AlertManagement />)

    fireEvent.click(screen.getByText('Edit'))

    // Uncheck status change alerts
    const statusCheckbox = screen.getByLabelText('Status Change Alerts')
    fireEvent.click(statusCheckbox)

    fireEvent.click(screen.getByText('Save'))

    await waitFor(() => {
      expect(screen.queryByText('Patient Status Changed')).not.toBeInTheDocument()
    })
  })

  it('should disable urgent care alerts when toggled off', async () => {
    render(<AlertManagement />)

    fireEvent.click(screen.getByText('Edit'))

    const urgentCheckbox = screen.getByLabelText('Urgent Care Alerts')
    fireEvent.click(urgentCheckbox)

    fireEvent.click(screen.getByText('Save'))

    await waitFor(() => {
      expect(screen.queryByText('Urgent Care Needed')).not.toBeInTheDocument()
    })
  })

  it('should format time correctly in alerts', async () => {
    render(<AlertManagement />)

    await waitFor(() => {
      // Check for "X ago" format
      const timeElements = screen.getAllByText(/ago/)
      expect(timeElements.length).toBeGreaterThan(0)
    })
  })
})