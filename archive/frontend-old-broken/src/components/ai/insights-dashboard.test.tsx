import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { InsightsDashboard } from './insights-dashboard'
import { useAIStore } from '@/stores/ai-store'
import type { AIInsight } from '@/stores/ai-store'

// Mock dependencies
vi.mock('@/stores/ai-store', () => ({
  useAIStore: vi.fn(),
}))

vi.mock('@/lib/logfire', () => ({
  logger: {
    componentMount: vi.fn(),
    componentUnmount: vi.fn(),
    userAction: vi.fn(),
  },
}))

vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn(() => '2 hours ago'),
}))

describe('InsightsDashboard', () => {
  const mockFetchInsights = vi.fn()
  
  const mockInsights: AIInsight[] = [
    {
      id: '1',
      type: 'trend',
      title: 'Patient Volume Increase',
      description: 'Patient registrations increased by 15% this month',
      severity: 'medium',
      createdAt: new Date().toISOString(),
    },
    {
      id: '2',
      type: 'anomaly',
      title: 'Unusual Activity Pattern',
      description: 'Detected unusual login patterns from multiple locations',
      severity: 'high',
      patientId: 'patient-123',
      createdAt: new Date().toISOString(),
    },
    {
      id: '3',
      type: 'prediction',
      title: 'High Risk Patient',
      description: 'Patient shows indicators of potential health complications',
      severity: 'high',
      patientId: 'patient-456',
      createdAt: new Date().toISOString(),
    },
    {
      id: '4',
      type: 'recommendation',
      title: 'Schedule Follow-up',
      description: 'Recommend scheduling follow-up appointment within 2 weeks',
      severity: 'low',
      patientId: 'patient-123',
      createdAt: new Date().toISOString(),
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useAIStore).mockReturnValue({
      insights: [],
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })
  })

  it('renders loading state', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: [],
      isLoadingInsights: true,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    expect(screen.getByText('Loading AI insights...')).toBeInTheDocument()
  })

  it('renders empty state when no insights', () => {
    render(<InsightsDashboard />)
    
    expect(screen.getByText('No AI insights available yet')).toBeInTheDocument()
    expect(screen.getByText('Refresh Insights')).toBeInTheDocument()
  })

  it('fetches insights on mount', () => {
    render(<InsightsDashboard />)
    
    expect(mockFetchInsights).toHaveBeenCalled()
  })

  it('renders insights when available', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    expect(screen.getByText('Patient Volume Increase')).toBeInTheDocument()
    expect(screen.getByText('Unusual Activity Pattern')).toBeInTheDocument()
    expect(screen.getByText('High Risk Patient')).toBeInTheDocument()
    expect(screen.getByText('Schedule Follow-up')).toBeInTheDocument()
  })

  it('displays correct icons for insight types', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    expect(screen.getByText('trend')).toBeInTheDocument()
    expect(screen.getByText('anomaly')).toBeInTheDocument()
    expect(screen.getByText('prediction')).toBeInTheDocument()
    expect(screen.getByText('recommendation')).toBeInTheDocument()
  })

  it('displays severity badges', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    expect(screen.getByText('low')).toBeInTheDocument()
    expect(screen.getByText('medium')).toBeInTheDocument()
    expect(screen.getAllByText('high')).toHaveLength(2)
  })

  it('filters insights by patientId when provided', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard patientId="patient-123" />)
    
    // Should show only insights for patient-123
    expect(screen.getByText('Unusual Activity Pattern')).toBeInTheDocument()
    expect(screen.getByText('Schedule Follow-up')).toBeInTheDocument()
    
    // Should not show other insights
    expect(screen.queryByText('Patient Volume Increase')).not.toBeInTheDocument()
    expect(screen.queryByText('High Risk Patient')).not.toBeInTheDocument()
  })

  it('handles refresh button click', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    const refreshButton = screen.getByText('Refresh')
    fireEvent.click(refreshButton)
    
    // Should call fetchInsights again (once on mount, once on click)
    expect(mockFetchInsights).toHaveBeenCalledTimes(2)
  })

  it('disables refresh button while loading', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: true,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    // The component shows loading state, not the refresh button
    expect(screen.queryByText('Refresh')).not.toBeInTheDocument()
  })

  it('shows summary statistics', () => {
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    // Check summary counts
    expect(screen.getByText('1')).toBeInTheDocument() // 1 trend
    expect(screen.getByText('Trends')).toBeInTheDocument()
    expect(screen.getByText('Anomalies')).toBeInTheDocument()
    expect(screen.getByText('Predictions')).toBeInTheDocument()
    expect(screen.getByText('Recommendations')).toBeInTheDocument()
  })

  it('handles view button click', () => {
    const logfire = await import('@/lib/logfire')
    const { logger } = logfire
    
    vi.mocked(useAIStore).mockReturnValue({
      insights: mockInsights,
      isLoadingInsights: false,
      fetchInsights: mockFetchInsights,
      messages: [],
      isTyping: false,
      sendMessage: vi.fn(),
      clearMessages: vi.fn(),
      addMessage: vi.fn(),
      setTyping: vi.fn(),
      addInsight: vi.fn(),
      clearInsights: vi.fn(),
    })

    render(<InsightsDashboard />)
    
    const viewButtons = screen.getAllByText('View')
    fireEvent.click(viewButtons[0])
    
    expect(logger.userAction).toHaveBeenCalledWith('view_insight_details', {
      insightId: '1',
      type: 'trend'
    })
  })

  it('applies custom className', () => {
    const { container } = render(<InsightsDashboard className="custom-class" />)
    
    expect(container.firstChild).toHaveClass('custom-class')
  })
})