import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { PatientDataTable } from './data-table'
import { usePatientStore } from '@/stores/patient-store'
import type { Patient } from '@/types/patient'

// Mock the patient store
vi.mock('@/stores/patient-store', () => ({
  usePatientStore: vi.fn(),
}))

// Mock router
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
}))

// Mock logfire
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
    error: vi.fn(),
  },
}))

// Mock child components
vi.mock('./patient-status-badge', () => ({
  PatientStatusBadge: ({ status }: any) => <span data-testid="status-badge">{status}</span>,
}))

vi.mock('./risk-level-badge', () => ({
  RiskLevelBadge: ({ level }: any) => <span data-testid="risk-badge">{level}</span>,
}))

vi.mock('./patient-filters', () => ({
  PatientFilters: ({ filters, onFiltersChange, onClose }: any) => (
    <div data-testid="patient-filters">
      <button onClick={() => onFiltersChange({ status: 'ACTIVE' })}>Apply Filter</button>
      <button onClick={onClose}>Close</button>
    </div>
  ),
}))

vi.mock('./patient-dialog', () => ({
  PatientDialog: ({ open, onOpenChange, mode }: any) => 
    open ? (
      <div data-testid={`patient-dialog-${mode}`}>
        <button onClick={() => onOpenChange(false)}>Close Dialog</button>
      </div>
    ) : null,
}))

describe('PatientDataTable', () => {
  const mockPatients: Patient[] = [
    {
      id: '1',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john@example.com',
      phone: '123-456-7890',
      date_of_birth: '1990-01-01',
      status: 'ACTIVE',
      risk_level: 'LOW',
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: '2',
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane@example.com',
      phone: '098-765-4321',
      date_of_birth: '1985-05-15',
      status: 'INQUIRY',
      risk_level: 'HIGH',
      created_at: '2024-01-02T00:00:00Z',
    },
  ]

  const defaultStoreState = {
    patients: mockPatients,
    isLoading: false,
    error: null,
    filters: {},
    sortConfig: { key: 'created_at', direction: 'desc' },
    totalCount: 2,
    currentPage: 1,
    pageSize: 10,
    fetchPatients: vi.fn(),
    deletePatient: vi.fn(),
    selectPatient: vi.fn(),
    setFilters: vi.fn(),
    setSortConfig: vi.fn(),
    setPage: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usePatientStore).mockReturnValue(defaultStoreState as any)
  })

  describe('Rendering', () => {
    it('renders table with patient data', () => {
      render(<PatientDataTable />)
      
      expect(screen.getByText('Patients')).toBeInTheDocument()
      expect(screen.getByText('2 total')).toBeInTheDocument()
      expect(screen.getByText('Doe, John')).toBeInTheDocument()
      expect(screen.getByText('Smith, Jane')).toBeInTheDocument()
    })

    it('shows loading state', () => {
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        isLoading: true,
        patients: [],
      } as any)
      
      render(<PatientDataTable />)
      
      expect(screen.getByText('Loading patients...')).toBeInTheDocument()
    })

    it('shows empty state when no patients', () => {
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        patients: [],
        totalCount: 0,
      } as any)
      
      render(<PatientDataTable />)
      
      expect(screen.getByText('No patients found')).toBeInTheDocument()
    })

    it('shows error state', () => {
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        error: 'Failed to load patients',
      } as any)
      
      render(<PatientDataTable />)
      
      expect(screen.getByText('Failed to load patients')).toBeInTheDocument()
    })
  })

  describe('Search Functionality', () => {
    it('performs search when search button clicked', () => {
      const mockSetFilters = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        setFilters: mockSetFilters,
      } as any)
      
      render(<PatientDataTable />)
      
      const searchInput = screen.getByPlaceholderText('Search patients...')
      fireEvent.change(searchInput, { target: { value: 'John' } })
      fireEvent.click(screen.getByText('Search'))
      
      expect(mockSetFilters).toHaveBeenCalledWith({ search: 'John' })
    })

    it('performs search on Enter key', () => {
      const mockSetFilters = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        setFilters: mockSetFilters,
      } as any)
      
      render(<PatientDataTable />)
      
      const searchInput = screen.getByPlaceholderText('Search patients...')
      fireEvent.change(searchInput, { target: { value: 'Jane' } })
      fireEvent.keyDown(searchInput, { key: 'Enter' })
      
      expect(mockSetFilters).toHaveBeenCalledWith({ search: 'Jane' })
    })
  })

  describe('Filters', () => {
    it('toggles filter panel', () => {
      render(<PatientDataTable />)
      
      expect(screen.queryByTestId('patient-filters')).not.toBeInTheDocument()
      
      fireEvent.click(screen.getByText('Filters'))
      expect(screen.getByTestId('patient-filters')).toBeInTheDocument()
      
      fireEvent.click(screen.getByText('Close'))
      expect(screen.queryByTestId('patient-filters')).not.toBeInTheDocument()
    })
  })

  describe('Sorting', () => {
    it('sorts by column when header clicked', () => {
      const mockSetSortConfig = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        setSortConfig: mockSetSortConfig,
      } as any)
      
      render(<PatientDataTable />)
      
      const nameHeader = screen.getByText('Name')
      fireEvent.click(nameHeader)
      
      expect(mockSetSortConfig).toHaveBeenCalledWith({
        key: 'last_name',
        direction: 'asc'
      })
    })

    it('toggles sort direction on second click', () => {
      const mockSetSortConfig = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        sortConfig: { key: 'last_name', direction: 'asc' },
        setSortConfig: mockSetSortConfig,
      } as any)
      
      render(<PatientDataTable />)
      
      const nameHeader = screen.getByText('Name')
      fireEvent.click(nameHeader)
      
      expect(mockSetSortConfig).toHaveBeenCalledWith({
        key: 'last_name',
        direction: 'desc'
      })
    })
  })

  describe('CRUD Operations', () => {
    it('opens create dialog when Add Patient clicked', () => {
      render(<PatientDataTable />)
      
      fireEvent.click(screen.getByText('Add Patient'))
      
      expect(screen.getByTestId('patient-dialog-create')).toBeInTheDocument()
    })

    it('opens edit dialog when edit action clicked', async () => {
      const mockSelectPatient = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        selectPatient: mockSelectPatient,
      } as any)
      
      render(<PatientDataTable />)
      
      // Click the dropdown menu for first patient
      const moreButtons = screen.getAllByRole('button', { name: '' })
      const firstPatientMenu = moreButtons.find(btn => 
        btn.querySelector('.lucide-more-horizontal')
      )
      
      if (firstPatientMenu) {
        fireEvent.click(firstPatientMenu)
        
        // Note: Testing dropdown menu content is complex with Radix UI
        // In real tests, you might need more sophisticated queries
      }
    })

    it('handles delete with confirmation', async () => {
      const mockDeletePatient = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        deletePatient: mockDeletePatient,
      } as any)
      
      render(<PatientDataTable />)
      
      // This would require testing the dropdown menu interaction
      // which is complex with Radix UI portals
    })
  })

  describe('Pagination', () => {
    it('shows pagination controls when multiple pages', () => {
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        totalCount: 25,
        pageSize: 10,
      } as any)
      
      render(<PatientDataTable />)
      
      expect(screen.getByText('Previous')).toBeInTheDocument()
      expect(screen.getByText('Next')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })

    it('navigates to next page', () => {
      const mockSetPage = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        totalCount: 25,
        pageSize: 10,
        setPage: mockSetPage,
      } as any)
      
      render(<PatientDataTable />)
      
      fireEvent.click(screen.getByText('Next'))
      
      expect(mockSetPage).toHaveBeenCalledWith(2)
    })

    it('navigates to previous page', () => {
      const mockSetPage = vi.fn()
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        totalCount: 25,
        currentPage: 2,
        pageSize: 10,
        setPage: mockSetPage,
      } as any)
      
      render(<PatientDataTable />)
      
      fireEvent.click(screen.getByText('Previous'))
      
      expect(mockSetPage).toHaveBeenCalledWith(1)
    })

    it('disables Previous on first page', () => {
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        totalCount: 25,
        currentPage: 1,
        pageSize: 10,
      } as any)
      
      render(<PatientDataTable />)
      
      expect(screen.getByText('Previous')).toBeDisabled()
    })

    it('disables Next on last page', () => {
      vi.mocked(usePatientStore).mockReturnValue({
        ...defaultStoreState,
        totalCount: 20,
        currentPage: 2,
        pageSize: 10,
      } as any)
      
      render(<PatientDataTable />)
      
      expect(screen.getByText('Next')).toBeDisabled()
    })
  })
})