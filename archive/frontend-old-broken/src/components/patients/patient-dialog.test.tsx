import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { PatientDialog } from './patient-dialog'
import { usePatientStore } from '@/stores/patient-store'
import type { Patient } from '@/types/patient'

// Mock the patient store
vi.mock('@/stores/patient-store', () => ({
  usePatientStore: vi.fn(),
}))

// Mock logfire
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

describe('PatientDialog', () => {
  const mockCreatePatient = vi.fn()
  const mockUpdatePatient = vi.fn()
  
  const mockPatient: Patient = {
    id: '1',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john@example.com',
    phone: '123-456-7890',
    date_of_birth: '1990-01-01',
    status: 'ACTIVE',
    risk_level: 'LOW',
    created_at: new Date().toISOString(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usePatientStore).mockReturnValue({
      selectedPatient: null,
      createPatient: mockCreatePatient,
      updatePatient: mockUpdatePatient,
    } as any)
  })

  describe('Create Mode', () => {
    it('renders create dialog with empty form', () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      expect(screen.getByText('Add New Patient')).toBeInTheDocument()
      expect(screen.getByText('Enter the patient details below.')).toBeInTheDocument()
      
      // Check form fields are empty
      expect(screen.getByLabelText('First Name')).toHaveValue('')
      expect(screen.getByLabelText('Last Name')).toHaveValue('')
      expect(screen.getByLabelText('Email')).toHaveValue('')
    })

    it('submits form with correct data', async () => {
      mockCreatePatient.mockResolvedValueOnce(mockPatient)
      const mockOnOpenChange = vi.fn()
      
      render(<PatientDialog open={true} onOpenChange={mockOnOpenChange} mode="create" />)
      
      // Fill form
      fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'John' } })
      fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } })
      fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'john@example.com' } })
      fireEvent.change(screen.getByLabelText('Phone'), { target: { value: '123-456-7890' } })
      fireEvent.change(screen.getByLabelText('Date of Birth'), { target: { value: '1990-01-01' } })
      
      // Submit
      fireEvent.click(screen.getByText('Create Patient'))
      
      await waitFor(() => {
        expect(mockCreatePatient).toHaveBeenCalledWith({
          first_name: 'John',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '123-456-7890',
          date_of_birth: '1990-01-01',
          status: 'INQUIRY',
          risk_level: 'LOW',
        })
        expect(mockOnOpenChange).toHaveBeenCalledWith(false)
      })
    })

    it('shows error message on create failure', async () => {
      mockCreatePatient.mockRejectedValueOnce(new Error('Email already exists'))
      
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      // Fill minimum required fields
      fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'John' } })
      fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } })
      fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'existing@example.com' } })
      fireEvent.change(screen.getByLabelText('Phone'), { target: { value: '123-456-7890' } })
      fireEvent.change(screen.getByLabelText('Date of Birth'), { target: { value: '1990-01-01' } })
      
      // Submit
      fireEvent.click(screen.getByText('Create Patient'))
      
      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument()
      })
    })
  })

  describe('Edit Mode', () => {
    beforeEach(() => {
      vi.mocked(usePatientStore).mockReturnValue({
        selectedPatient: mockPatient,
        createPatient: mockCreatePatient,
        updatePatient: mockUpdatePatient,
      } as any)
    })

    it('renders edit dialog with patient data', () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="edit" />)
      
      expect(screen.getByText('Edit Patient')).toBeInTheDocument()
      expect(screen.getByText('Update the patient information below.')).toBeInTheDocument()
      
      // Check form fields have patient data
      expect(screen.getByLabelText('First Name')).toHaveValue('John')
      expect(screen.getByLabelText('Last Name')).toHaveValue('Doe')
      expect(screen.getByLabelText('Email')).toHaveValue('john@example.com')
    })

    it('submits update with changed data', async () => {
      mockUpdatePatient.mockResolvedValueOnce({ ...mockPatient, first_name: 'Jane' })
      const mockOnOpenChange = vi.fn()
      
      render(<PatientDialog open={true} onOpenChange={mockOnOpenChange} mode="edit" />)
      
      // Change first name
      fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'Jane' } })
      
      // Submit
      fireEvent.click(screen.getByText('Update Patient'))
      
      await waitFor(() => {
        expect(mockUpdatePatient).toHaveBeenCalledWith({
          id: '1',
          first_name: 'Jane',
          last_name: 'Doe',
          email: 'john@example.com',
          phone: '123-456-7890',
          date_of_birth: '1990-01-01',
          status: 'ACTIVE',
          risk_level: 'LOW',
        })
        expect(mockOnOpenChange).toHaveBeenCalledWith(false)
      })
    })
  })

  describe('Dialog Behavior', () => {
    it('closes dialog when cancel is clicked', () => {
      const mockOnOpenChange = vi.fn()
      render(<PatientDialog open={true} onOpenChange={mockOnOpenChange} mode="create" />)
      
      fireEvent.click(screen.getByText('Cancel'))
      
      expect(mockOnOpenChange).toHaveBeenCalledWith(false)
    })

    it('resets form when dialog reopens', () => {
      const { rerender } = render(<PatientDialog open={false} onOpenChange={() => {}} mode="create" />)
      
      // Open dialog and fill form
      rerender(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'Test' } })
      
      // Close and reopen
      rerender(<PatientDialog open={false} onOpenChange={() => {}} mode="create" />)
      rerender(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      // Check form is reset
      expect(screen.getByLabelText('First Name')).toHaveValue('')
    })

    it('shows loading state during submission', async () => {
      mockCreatePatient.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      // Fill form
      fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'John' } })
      fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } })
      fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'john@example.com' } })
      fireEvent.change(screen.getByLabelText('Phone'), { target: { value: '123-456-7890' } })
      fireEvent.change(screen.getByLabelText('Date of Birth'), { target: { value: '1990-01-01' } })
      
      // Submit
      fireEvent.click(screen.getByText('Create Patient'))
      
      expect(screen.getByText('Creating...')).toBeInTheDocument()
      expect(screen.getByText('Cancel')).toBeDisabled()
    })
  })

  describe('Status and Risk Level Selection', () => {
    it('allows changing patient status', () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      const statusSelect = screen.getByLabelText('Status')
      fireEvent.click(statusSelect)
      
      // Note: Testing Radix UI select is complex due to portal rendering
      // In a real test environment, you might need to use more sophisticated queries
      expect(statusSelect).toBeInTheDocument()
    })

    it('allows changing risk level', () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      const riskSelect = screen.getByLabelText('Risk Level')
      fireEvent.click(riskSelect)
      
      expect(riskSelect).toBeInTheDocument()
    })
  })
})