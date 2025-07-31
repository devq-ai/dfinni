import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Breadcrumb } from './breadcrumb'
import { usePathname } from 'next/navigation'

// Mock next/navigation
vi.mock('next/navigation', () => ({
  usePathname: vi.fn(),
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

import { logger } from '@/lib/logfire'

// Mock Link component
vi.mock('next/link', () => ({
  default: ({ children, href, onClick, className }: any) => (
    <a href={href} onClick={onClick} className={className}>
      {children}
    </a>
  ),
}))

describe('Breadcrumb', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('does not render on home page', () => {
    vi.mocked(usePathname).mockReturnValue('/')
    
    const { container } = render(<Breadcrumb />)
    
    expect(container.firstChild).toBeNull()
  })

  it('renders breadcrumbs for nested paths', () => {
    vi.mocked(usePathname).mockReturnValue('/patients/123/edit')
    
    render(<Breadcrumb />)
    
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Patients')).toBeInTheDocument()
    expect(screen.getByText('123')).toBeInTheDocument()
    expect(screen.getByText('Edit')).toBeInTheDocument()
  })

  it('formats path segments with proper case', () => {
    vi.mocked(usePathname).mockReturnValue('/ai-insights/new-report')
    
    render(<Breadcrumb />)
    
    expect(screen.getByText('Ai Insights')).toBeInTheDocument()
    expect(screen.getByText('New Report')).toBeInTheDocument()
  })

  it('renders home icon for first breadcrumb', () => {
    vi.mocked(usePathname).mockReturnValue('/dashboard')
    
    render(<Breadcrumb />)
    
    const homeLink = screen.getByText('Home')
    const icon = homeLink.querySelector('svg')
    expect(icon).toBeInTheDocument()
  })

  it('renders chevron separators between items', () => {
    vi.mocked(usePathname).mockReturnValue('/patients/list')
    
    const { container } = render(<Breadcrumb />)
    
    const chevrons = container.querySelectorAll('.lucide-chevron-right')
    expect(chevrons).toHaveLength(2) // Between Home->Patients and Patients->List
  })

  it('makes last item non-clickable', () => {
    vi.mocked(usePathname).mockReturnValue('/settings/profile')
    
    render(<Breadcrumb />)
    
    const profileText = screen.getByText('Profile')
    expect(profileText.tagName).toBe('SPAN')
    expect(profileText.closest('a')).toBeNull()
  })

  it('makes non-last items clickable links', () => {
    vi.mocked(usePathname).mockReturnValue('/settings/profile')
    
    render(<Breadcrumb />)
    
    const homeLink = screen.getByText('Home').closest('a')
    const settingsLink = screen.getByText('Settings').closest('a')
    
    expect(homeLink).toHaveAttribute('href', '/')
    expect(settingsLink).toHaveAttribute('href', '/settings')
  })

  it('logs navigation when breadcrumb is clicked', () => {
    vi.mocked(usePathname).mockReturnValue('/patients/123')
    const mockLogger = vi.mocked(logger.userAction)
    
    render(<Breadcrumb />)
    
    const patientsLink = screen.getByText('Patients')
    fireEvent.click(patientsLink)
    
    expect(mockLogger).toHaveBeenCalledWith('breadcrumb_navigation', {
      from: '/patients/123',
      to: '/patients',
      label: 'Patients'
    })
  })

  it('applies custom className', () => {
    vi.mocked(usePathname).mockReturnValue('/dashboard')
    
    const { container } = render(<Breadcrumb className="custom-breadcrumb" />)
    
    const nav = container.querySelector('nav')
    expect(nav).toHaveClass('custom-breadcrumb')
  })

  it('has correct accessibility attributes', () => {
    vi.mocked(usePathname).mockReturnValue('/dashboard')
    
    const { container } = render(<Breadcrumb />)
    
    const nav = container.querySelector('nav')
    expect(nav).toHaveAttribute('aria-label', 'Breadcrumb')
  })
})