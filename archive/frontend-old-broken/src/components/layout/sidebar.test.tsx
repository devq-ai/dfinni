import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Sidebar } from './sidebar'
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

// Mock Link component
vi.mock('next/link', () => ({
  default: ({ children, href, onClick, className, ...props }: any) => (
    <a href={href} onClick={onClick} className={className} {...props}>
      {children}
    </a>
  ),
}))

describe('Sidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(usePathname).mockReturnValue('/dashboard')
  })

  it('renders all navigation items', () => {
    render(<Sidebar />)

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Patients')).toBeInTheDocument()
    expect(screen.getByText('AI Insights')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
    expect(screen.getByText('Alerts')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('highlights active navigation item', () => {
    vi.mocked(usePathname).mockReturnValue('/patients')
    
    render(<Sidebar />)

    const patientsLink = screen.getByText('Patients').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')

    expect(patientsLink).toHaveClass('bg-zinc-800', 'text-white')
    expect(dashboardLink).not.toHaveClass('bg-zinc-800', 'text-white')
  })

  it('highlights parent route when on sub-route', () => {
    vi.mocked(usePathname).mockReturnValue('/patients/123')
    
    render(<Sidebar />)

    const patientsLink = screen.getByText('Patients').closest('a')
    expect(patientsLink).toHaveClass('bg-zinc-800', 'text-white')
  })

  it('renders logo', () => {
    render(<Sidebar />)
    
    expect(screen.getByText('PFINNI')).toBeInTheDocument()
  })

  it('renders footer', () => {
    render(<Sidebar />)
    
    expect(screen.getByText('© 2025 PFINNI Healthcare')).toBeInTheDocument()
  })

  describe('mobile menu', () => {
    it('toggles mobile menu on button click', () => {
      render(<Sidebar />)

      const toggleButton = screen.getByLabelText('Toggle sidebar')
      
      // Initially hidden on mobile (class includes -translate-x-full)
      const sidebar = screen.getByText('Dashboard').closest('div.fixed')
      expect(sidebar).toHaveClass('-translate-x-full')

      // Click to open
      fireEvent.click(toggleButton)
      expect(sidebar).toHaveClass('translate-x-0')

      // Click to close
      fireEvent.click(toggleButton)
      expect(sidebar).toHaveClass('-translate-x-full')
    })

    it('closes mobile menu when backdrop is clicked', () => {
      render(<Sidebar />)

      const toggleButton = screen.getByLabelText('Toggle sidebar')
      
      // Open menu
      fireEvent.click(toggleButton)
      
      // Click backdrop
      const backdrop = document.querySelector('.bg-black\\/50')
      expect(backdrop).toBeInTheDocument()
      fireEvent.click(backdrop!)

      // Menu should be closed
      const sidebar = screen.getByText('Dashboard').closest('div.fixed')
      expect(sidebar).toHaveClass('-translate-x-full')
    })

    it('closes mobile menu when navigation item is clicked', () => {
      render(<Sidebar />)

      const toggleButton = screen.getByLabelText('Toggle sidebar')
      
      // Open menu
      fireEvent.click(toggleButton)
      
      // Click navigation item
      const patientsLink = screen.getByText('Patients')
      fireEvent.click(patientsLink)

      // Menu should be closed
      const sidebar = screen.getByText('Dashboard').closest('div.fixed')
      expect(sidebar).toHaveClass('-translate-x-full')
    })
  })

  it('applies custom className', () => {
    const { container } = render(<Sidebar className="custom-class" />)
    
    const sidebar = container.querySelector('.custom-class')
    expect(sidebar).toBeInTheDocument()
  })

  it('sets aria-current on active link', () => {
    vi.mocked(usePathname).mockReturnValue('/analytics')
    
    render(<Sidebar />)

    const analyticsLink = screen.getByText('Analytics').closest('a')
    const dashboardLink = screen.getByText('Dashboard').closest('a')

    expect(analyticsLink).toHaveAttribute('aria-current', 'page')
    expect(dashboardLink).not.toHaveAttribute('aria-current')
  })
})