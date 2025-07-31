import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { QuickActions } from './quick-actions'
import { useRouter } from 'next/navigation'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}))

// Mock logfire
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

import { logger } from '@/lib/logfire'

describe('QuickActions', () => {
  const mockPush = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any)
  })

  it('renders all quick action buttons', () => {
    render(<QuickActions />)
    
    expect(screen.getByText('Add New Patient')).toBeInTheDocument()
    expect(screen.getByText('Generate Report')).toBeInTheDocument()
    expect(screen.getByText('Export Data')).toBeInTheDocument()
    expect(screen.getByText('View Alerts')).toBeInTheDocument()
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument()
    expect(screen.getByText('AI Assistant')).toBeInTheDocument()
  })

  it('navigates to correct route when action with href is clicked', () => {
    render(<QuickActions />)
    
    const addPatientButton = screen.getByText('Add New Patient').closest('button')
    fireEvent.click(addPatientButton!)
    
    expect(mockPush).toHaveBeenCalledWith('/patients?action=new')
    expect(logger.userAction).toHaveBeenCalledWith('quick_action_click', {
      actionId: 'add-patient',
      title: 'Add New Patient'
    })
  })

  it('calls onClick handler for export action', () => {
    render(<QuickActions />)
    
    const exportButton = screen.getByText('Export Data').closest('button')
    fireEvent.click(exportButton!)
    
    expect(logger.userAction).toHaveBeenCalledWith('quick_action_click', {
      actionId: 'export-data',
      title: 'Export Data'
    })
    expect(logger.userAction).toHaveBeenCalledWith('export_data_initiated')
  })

  it('displays correct descriptions for each action', () => {
    render(<QuickActions />)
    
    expect(screen.getByText('Register a new patient in the system')).toBeInTheDocument()
    expect(screen.getByText('Create analytics and insights report')).toBeInTheDocument()
    expect(screen.getByText('Download patient data as CSV')).toBeInTheDocument()
    expect(screen.getByText('Check system and patient alerts')).toBeInTheDocument()
    expect(screen.getByText('View detailed analytics')).toBeInTheDocument()
    expect(screen.getByText('Chat with AI for insights')).toBeInTheDocument()
  })

  it('applies correct color styles to buttons', () => {
    render(<QuickActions />)
    
    const addPatientButton = screen.getByText('Add New Patient').closest('button')
    expect(addPatientButton).toHaveClass('text-blue-500')
    
    const exportButton = screen.getByText('Export Data').closest('button')
    expect(exportButton).toHaveClass('text-purple-500')
  })

  it('renders icons for each action', () => {
    const { container } = render(<QuickActions />)
    
    // Check that SVG icons are rendered
    const icons = container.querySelectorAll('svg')
    expect(icons.length).toBe(6) // 6 quick actions
  })
})