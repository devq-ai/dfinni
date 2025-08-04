import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DashboardCards } from './DashboardCards'

// Mock the icons
vi.mock('lucide-react', () => ({
  Users: () => <div data-testid="users-icon">Users Icon</div>,
  AlertCircle: () => <div data-testid="alert-icon">Alert Icon</div>,
  UserCheck: () => <div data-testid="user-check-icon">UserCheck Icon</div>,
  Activity: () => <div data-testid="activity-icon">Activity Icon</div>,
  TrendingUp: () => <div data-testid="trending-up-icon">TrendingUp Icon</div>,
  TrendingDown: () => <div data-testid="trending-down-icon">TrendingDown Icon</div>,
}))

describe('DashboardCards', () => {
  const mockStats = {
    total_patients: 150,
    active_alerts: 8,
    recent_appointments: 24,
    pending_reviews: 12,
    patient_growth: 5.2,
    alert_change: -15.3,
    appointment_change: 10.5,
    review_change: 0,
  }

  it('renders all dashboard cards', () => {
    render(<DashboardCards stats={mockStats} />)

    // Check that all cards are rendered
    expect(screen.getByText('Total Patients')).toBeInTheDocument()
    expect(screen.getByText('Active Alerts')).toBeInTheDocument()
    expect(screen.getByText('Recent Appointments')).toBeInTheDocument()
    expect(screen.getByText('Pending Reviews')).toBeInTheDocument()
  })

  it('displays correct statistics', () => {
    render(<DashboardCards stats={mockStats} />)

    // Check values
    expect(screen.getByText('150')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument()
    expect(screen.getByText('24')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
  })

  it('shows positive growth indicators', () => {
    render(<DashboardCards stats={mockStats} />)

    // Patient growth is positive
    expect(screen.getByText('+5.2%')).toBeInTheDocument()
    const trendingUpIcons = screen.getAllByTestId('trending-up-icon')
    expect(trendingUpIcons.length).toBeGreaterThan(0)
    
    // Appointment change is positive
    expect(screen.getByText('+10.5%')).toBeInTheDocument()
  })

  it('shows negative growth indicators', () => {
    render(<DashboardCards stats={mockStats} />)

    // Alert change is negative
    expect(screen.getByText('-15.3%')).toBeInTheDocument()
    expect(screen.getByTestId('trending-down-icon')).toBeInTheDocument()
  })

  it('handles zero change correctly', () => {
    render(<DashboardCards stats={mockStats} />)

    // Review change is 0
    expect(screen.getByText('0%')).toBeInTheDocument()
  })

  it('renders correct icons for each card', () => {
    render(<DashboardCards stats={mockStats} />)

    expect(screen.getAllByTestId('users-icon').length).toBe(1)
    expect(screen.getAllByTestId('alert-icon').length).toBe(1)
    expect(screen.getAllByTestId('user-check-icon').length).toBe(1)
    expect(screen.getAllByTestId('activity-icon').length).toBe(1)
  })

  it('applies correct styling for positive changes', () => {
    render(<DashboardCards stats={mockStats} />)

    const positiveChanges = screen.getAllByText(/\+/);
    positiveChanges.forEach(element => {
      expect(element.className).toContain('text-green-600')
    })
  })

  it('applies correct styling for negative changes', () => {
    render(<DashboardCards stats={mockStats} />)

    const negativeChange = screen.getByText('-15.3%')
    expect(negativeChange.className).toContain('text-red-600')
  })

  it('handles missing or undefined stats gracefully', () => {
    const incompleteStats = {
      total_patients: undefined,
      active_alerts: null,
      recent_appointments: 0,
      pending_reviews: 5,
      patient_growth: undefined,
      alert_change: null,
      appointment_change: 0,
      review_change: NaN,
    }

    render(<DashboardCards stats={incompleteStats as any} />)

    // Should render without crashing and show default values
    expect(screen.getByText('Total Patients')).toBeInTheDocument()
    expect(screen.getByText('Active Alerts')).toBeInTheDocument()
  })

  it('renders responsive grid layout', () => {
    const { container } = render(<DashboardCards stats={mockStats} />)
    
    const grid = container.querySelector('.grid')
    expect(grid).toHaveClass('grid', 'gap-4', 'md:grid-cols-2', 'lg:grid-cols-4')
  })
})