import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RiskLevelBadge } from './risk-level-badge'

describe('RiskLevelBadge', () => {
  it('renders low risk correctly', () => {
    render(<RiskLevelBadge level="LOW" />)
    
    const badge = screen.getByText('Low Risk')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-green-500', 'font-mono')
  })

  it('renders medium risk correctly', () => {
    render(<RiskLevelBadge level="MEDIUM" />)
    
    const badge = screen.getByText('Medium Risk')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-yellow-500', 'font-mono')
  })

  it('renders high risk correctly', () => {
    render(<RiskLevelBadge level="HIGH" />)
    
    const badge = screen.getByText('High Risk')
    expect(badge).toBeInTheDocument()
    expect(badge).toHaveClass('text-red-500', 'font-mono')
  })

  it('applies custom className', () => {
    render(<RiskLevelBadge level="LOW" className="custom-class" />)
    
    const badge = screen.getByText('Low Risk')
    expect(badge).toHaveClass('custom-class')
  })
})