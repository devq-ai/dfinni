import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PatientStatusBadge } from './patient-status-badge'

describe('PatientStatusBadge', () => {
  it('renders active status correctly', () => {
    render(<PatientStatusBadge status="ACTIVE" />)
    
    const badge = screen.getByText('Active')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-green-500/10', 'text-green-500', 'border-green-500/50')
  })

  it('renders inquiry status correctly', () => {
    render(<PatientStatusBadge status="INQUIRY" />)
    
    const badge = screen.getByText('Inquiry')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-yellow-500/10', 'text-yellow-500', 'border-yellow-500/50')
  })

  it('renders onboarding status correctly', () => {
    render(<PatientStatusBadge status="ONBOARDING" />)
    
    const badge = screen.getByText('Onboarding')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-blue-500/10', 'text-blue-500', 'border-blue-500/50')
  })

  it('renders churned status correctly', () => {
    render(<PatientStatusBadge status="CHURNED" />)
    
    const badge = screen.getByText('Churned')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('bg-red-500/10', 'text-red-500', 'border-red-500/50')
  })

  it('applies custom className', () => {
    render(<PatientStatusBadge status="ACTIVE" className="custom-class" />)
    
    const badge = screen.getByText('Active')
    expect(badge).toHaveClass('custom-class')
  })
})