import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MetricCard } from './metric-card'
import { Users } from 'lucide-react'

vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

describe('MetricCard', () => {
  it('renders basic metric information', () => {
    render(
      <MetricCard 
        title="Total Patients"
        value={150}
      />
    )
    
    expect(screen.getByText('Total Patients')).toBeInTheDocument()
    expect(screen.getByText('150')).toBeInTheDocument()
  })

  it('renders with icon', () => {
    render(
      <MetricCard 
        title="Total Patients"
        value={150}
        icon={<Users data-testid="users-icon" />}
      />
    )
    
    expect(screen.getByTestId('users-icon')).toBeInTheDocument()
  })

  it('shows positive change with increase trend', () => {
    render(
      <MetricCard 
        title="Active Patients"
        value={100}
        change={5.2}
        changeType="increase"
      />
    )
    
    expect(screen.getByText('+5.2%')).toBeInTheDocument()
    expect(screen.getByText('+5.2%').parentElement).toHaveClass('text-green-500')
  })

  it('shows negative change with decrease trend', () => {
    render(
      <MetricCard 
        title="High Risk"
        value={10}
        change={-2.1}
        changeType="decrease"
      />
    )
    
    expect(screen.getByText('-2.1%')).toBeInTheDocument()
    expect(screen.getByText('-2.1%').parentElement).toHaveClass('text-red-500')
  })

  it('shows neutral change', () => {
    render(
      <MetricCard 
        title="Stable Patients"
        value={50}
        change={0}
        changeType="neutral"
      />
    )
    
    expect(screen.getByText('0%')).toBeInTheDocument()
    expect(screen.getByText('0%').parentElement).toHaveClass('text-zinc-400')
  })

  it('handles click events', () => {
    const mockClick = vi.fn()
    render(
      <MetricCard 
        title="Clickable Card"
        value={100}
        onClick={mockClick}
      />
    )
    
    const card = screen.getByRole('button')
    fireEvent.click(card)
    
    expect(mockClick).toHaveBeenCalled()
  })

  it('applies color styles', () => {
    const { container } = render(
      <MetricCard 
        title="Blue Card"
        value={100}
        color="blue"
      />
    )
    
    const card = container.firstChild
    expect(card).toHaveClass('border-blue-500/20', 'bg-blue-500/5')
  })

  it('applies custom className', () => {
    const { container } = render(
      <MetricCard 
        title="Custom Card"
        value={100}
        className="custom-class"
      />
    )
    
    const card = container.firstChild
    expect(card).toHaveClass('custom-class')
  })
})