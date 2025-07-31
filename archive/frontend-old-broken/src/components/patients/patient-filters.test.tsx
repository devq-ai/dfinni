import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { PatientFilters } from './patient-filters'
import type { PatientFilters as Filters } from '@/types/patient'

vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

describe('PatientFilters', () => {
  const mockOnFiltersChange = vi.fn()
  const mockOnClose = vi.fn()
  
  const defaultFilters: Filters = {
    status: 'ALL',
    risk_level: 'ALL',
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders filter options', () => {
    render(
      <PatientFilters 
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    )
    
    expect(screen.getByText('Filters')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
    expect(screen.getByText('Risk Level')).toBeInTheDocument()
    expect(screen.getByText('Clear Filters')).toBeInTheDocument()
  })

  it('displays current filter values', () => {
    const filters: Filters = {
      status: 'ACTIVE',
      risk_level: 'HIGH',
    }
    
    render(
      <PatientFilters 
        filters={filters}
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    )
    
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('High Risk')).toBeInTheDocument()
  })

  it('calls onClose when close button clicked', () => {
    render(
      <PatientFilters 
        filters={defaultFilters}
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    )
    
    const closeButton = screen.getByRole('button', { name: /close filters/i })
    fireEvent.click(closeButton)
    
    expect(mockOnClose).toHaveBeenCalled()
  })

  it('clears filters and closes when clear button clicked', () => {
    render(
      <PatientFilters 
        filters={{ status: 'ACTIVE', risk_level: 'HIGH' }}
        onFiltersChange={mockOnFiltersChange}
        onClose={mockOnClose}
      />
    )
    
    const clearButton = screen.getByText('Clear Filters')
    fireEvent.click(clearButton)
    
    expect(mockOnFiltersChange).toHaveBeenCalledWith({})
    expect(mockOnClose).toHaveBeenCalled()
  })
})