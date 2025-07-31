import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@/test/test-utils'
import { createMockPatient } from '@/test/test-utils'
import PatientDialog from '@/components/patients/patient-dialog'
import { DataTable } from '@/components/patients/data-table'
import { usePatientStore } from '@/stores/patient-store'
import { api } from '@/lib/fetch-wrapper'

// Mock API and stores
vi.mock('@/lib/fetch-wrapper', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('@/stores/patient-store')

describe('Patient Management Flow', () => {
  const mockPatients = [
    createMockPatient({ id: '1', firstName: 'John', lastName: 'Doe' }),
    createMockPatient({ id: '2', firstName: 'Jane', lastName: 'Smith' })
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default store mock
    ;(usePatientStore as any).mockReturnValue({
      patients: mockPatients,
      totalCount: 2,
      isLoading: false,
      error: null,
      selectedPatient: null,
      filters: { status: 'all', riskLevel: 'all', search: '' },
      pagination: { page: 1, pageSize: 10 },
      fetchPatients: vi.fn(),
      createPatient: vi.fn(),
      updatePatient: vi.fn(),
      deletePatient: vi.fn(),
      setSelectedPatient: vi.fn(),
      clearSelectedPatient: vi.fn(),
      setFilters: vi.fn(),
      setPagination: vi.fn(),
      getFilteredPatients: () => mockPatients
    })
  })

  describe('Patient List View', () => {
    it('should display patients in table', () => {
      render(<DataTable />)

      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
    })

    it('should show loading state', () => {
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        isLoading: true,
        patients: []
      })

      render(<DataTable />)

      expect(screen.getByText(/Loading patients/i)).toBeInTheDocument()
    })

    it('should show empty state', () => {
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        patients: [],
        totalCount: 0
      })

      render(<DataTable />)

      expect(screen.getByText(/No patients found/i)).toBeInTheDocument()
    })

    it('should handle pagination', () => {
      const mockSetPagination = vi.fn()
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        setPagination: mockSetPagination,
        totalCount: 50
      })

      render(<DataTable />)

      // Click next page
      const nextButton = screen.getByRole('button', { name: /next/i })
      fireEvent.click(nextButton)

      expect(mockSetPagination).toHaveBeenCalledWith({ page: 2, pageSize: 10 })
    })
  })

  describe('Create Patient Flow', () => {
    it('should create new patient', async () => {
      const mockCreatePatient = vi.fn().mockResolvedValue(undefined)
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        createPatient: mockCreatePatient
      })

      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)

      // Fill form
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: 'Alice' }
      })
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: 'Johnson' }
      })
      fireEvent.change(screen.getByLabelText(/date of birth/i), {
        target: { value: '1990-05-15' }
      })
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: 'alice@example.com' }
      })
      fireEvent.change(screen.getByLabelText(/phone/i), {
        target: { value: '555-0123' }
      })

      // Submit form
      fireEvent.click(screen.getByRole('button', { name: /create patient/i }))

      await waitFor(() => {
        expect(mockCreatePatient).toHaveBeenCalledWith({
          firstName: 'Alice',
          lastName: 'Johnson',
          dateOfBirth: '1990-05-15',
          email: 'alice@example.com',
          phone: '555-0123',
          status: 'inquiry',
          riskLevel: 'low'
        })
      })
    })

    it('should validate required fields', async () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)

      // Submit without filling required fields
      fireEvent.click(screen.getByRole('button', { name: /create patient/i }))

      await waitFor(() => {
        expect(screen.getByText(/first name is required/i)).toBeInTheDocument()
        expect(screen.getByText(/last name is required/i)).toBeInTheDocument()
        expect(screen.getByText(/date of birth is required/i)).toBeInTheDocument()
      })
    })
  })

  describe('Edit Patient Flow', () => {
    it('should edit existing patient', async () => {
      const patient = mockPatients[0]
      const mockUpdatePatient = vi.fn().mockResolvedValue(undefined)
      
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        selectedPatient: patient,
        updatePatient: mockUpdatePatient
      })

      render(<PatientDialog open={true} onOpenChange={() => {}} mode="edit" />)

      // Check pre-filled values
      expect(screen.getByDisplayValue('John')).toBeInTheDocument()
      expect(screen.getByDisplayValue('Doe')).toBeInTheDocument()

      // Update first name
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: 'Jonathan' }
      })

      // Submit form
      fireEvent.click(screen.getByRole('button', { name: /update patient/i }))

      await waitFor(() => {
        expect(mockUpdatePatient).toHaveBeenCalledWith(
          patient.id,
          expect.objectContaining({
            firstName: 'Jonathan'
          })
        )
      })
    })
  })

  describe('Delete Patient Flow', () => {
    it('should delete patient with confirmation', async () => {
      const mockDeletePatient = vi.fn().mockResolvedValue(undefined)
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        deletePatient: mockDeletePatient
      })

      render(<DataTable />)

      // Click delete button for first patient
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      fireEvent.click(deleteButtons[0])

      // Confirm deletion in dialog
      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument()
      })

      fireEvent.click(screen.getByRole('button', { name: /confirm/i }))

      await waitFor(() => {
        expect(mockDeletePatient).toHaveBeenCalledWith('1')
      })
    })
  })

  describe('Search and Filter', () => {
    it('should filter patients by search term', () => {
      const mockSetFilters = vi.fn()
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        setFilters: mockSetFilters
      })

      render(<DataTable />)

      const searchInput = screen.getByPlaceholderText(/search patients/i)
      fireEvent.change(searchInput, { target: { value: 'john' } })

      // Debounced search
      setTimeout(() => {
        expect(mockSetFilters).toHaveBeenCalledWith({ search: 'john' })
      }, 300)
    })

    it('should filter by status', () => {
      const mockSetFilters = vi.fn()
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        setFilters: mockSetFilters
      })

      render(<DataTable />)

      const statusSelect = screen.getByRole('combobox', { name: /status/i })
      fireEvent.change(statusSelect, { target: { value: 'active' } })

      expect(mockSetFilters).toHaveBeenCalledWith({ status: 'active' })
    })

    it('should filter by risk level', () => {
      const mockSetFilters = vi.fn()
      ;(usePatientStore as any).mockReturnValue({
        ...usePatientStore(),
        setFilters: mockSetFilters
      })

      render(<DataTable />)

      const riskSelect = screen.getByRole('combobox', { name: /risk level/i })
      fireEvent.change(riskSelect, { target: { value: 'high' } })

      expect(mockSetFilters).toHaveBeenCalledWith({ riskLevel: 'high' })
    })
  })
})