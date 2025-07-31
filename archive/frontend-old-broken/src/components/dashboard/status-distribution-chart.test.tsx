import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusDistributionChart } from './status-distribution-chart'
import { useDashboardStore } from '@/stores/dashboard-store'

// Mock the dashboard store
vi.mock('@/stores/dashboard-store', () => ({
  useDashboardStore: vi.fn(),
}))

// Mock logfire
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

import { logger } from '@/lib/logfire'

// Mock Recharts components
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: ({ data, children, onClick }: any) => (
    <div data-testid="pie" onClick={() => onClick && onClick(data[0])}>
      {children}
      {data?.map((item: any, index: number) => (
        <div key={index} data-testid={`pie-segment-${item.name.toLowerCase()}`}>
          {item.name}: {item.value}
        </div>
      ))}
    </div>
  ),
  Cell: ({ fill }: any) => <div data-testid="cell" style={{ backgroundColor: fill }} />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
}))

describe('StatusDistributionChart', () => {
  const mockMetrics = {
    totalPatients: 150,
    activePatients: 100,
    newPatientsThisMonth: 15,
    patientGrowthRate: 10,
    statusDistribution: {
      inquiry: 15,
      onboarding: 20,
      active: 100,
      churned: 15,
    },
    riskDistribution: {
      low: 90,
      medium: 45,
      high: 15,
    },
    healthOutcomes: {
      improved: 60,
      stable: 70,
      declined: 20,
    },
    recentActivities: [],
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders chart with metrics data', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      expect(screen.getByText('Patient Status Distribution')).toBeInTheDocument()
      expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
      expect(screen.getByTestId('pie')).toBeInTheDocument()
    })

    it('shows loading skeleton when metrics are null', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: null,
      } as any)
      
      const { container } = render(<StatusDistributionChart />)
      
      expect(screen.getByText('Patient Status Distribution')).toBeInTheDocument()
      const skeleton = container.querySelector('.animate-pulse')
      expect(skeleton).toBeInTheDocument()
    })

    it('displays all status segments', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      expect(screen.getByTestId('pie-segment-inquiry')).toBeInTheDocument()
      expect(screen.getByTestId('pie-segment-onboarding')).toBeInTheDocument()
      expect(screen.getByTestId('pie-segment-active')).toBeInTheDocument()
      expect(screen.getByTestId('pie-segment-churned')).toBeInTheDocument()
    })

    it('filters out segments with zero values', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: {
          ...mockMetrics,
          statusDistribution: {
            inquiry: 0,
            onboarding: 20,
            active: 100,
            churned: 0,
          },
        },
      } as any)
      
      render(<StatusDistributionChart />)
      
      expect(screen.queryByTestId('pie-segment-inquiry')).not.toBeInTheDocument()
      expect(screen.getByTestId('pie-segment-onboarding')).toBeInTheDocument()
      expect(screen.getByTestId('pie-segment-active')).toBeInTheDocument()
      expect(screen.queryByTestId('pie-segment-churned')).not.toBeInTheDocument()
    })
  })

  describe('Legend and Summary', () => {
    it('displays summary grid with counts', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      // Get all elements with the text and check for the one in the summary grid
      const inquiryElements = screen.getAllByText('Inquiry: 15')
      expect(inquiryElements.length).toBeGreaterThan(0)
      
      const onboardingElements = screen.getAllByText('Onboarding: 20')
      expect(onboardingElements.length).toBeGreaterThan(0)
      
      const activeElements = screen.getAllByText('Active: 100')
      expect(activeElements.length).toBeGreaterThan(0)
      
      const churnedElements = screen.getAllByText('Churned: 15')
      expect(churnedElements.length).toBeGreaterThan(0)
    })

    it('renders legend component', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      expect(screen.getByTestId('legend')).toBeInTheDocument()
    })
  })

  describe('Interactions', () => {
    it('handles pie segment click', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      const pieElement = screen.getByTestId('pie')
      pieElement.click()
      
      expect(logger.userAction).toHaveBeenCalledWith('status_chart_segment_click', {
        status: 'inquiry',
        value: 15,
      })
    })
  })

  describe('Chart Components', () => {
    it('renders tooltip component', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      expect(screen.getByTestId('tooltip')).toBeInTheDocument()
    })

    it('renders correct number of cells', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      const cells = screen.getAllByTestId('cell')
      expect(cells).toHaveLength(4) // One for each status
    })

    it('uses responsive container', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        metrics: mockMetrics,
      } as any)
      
      render(<StatusDistributionChart />)
      
      expect(screen.getByTestId('responsive-container')).toBeInTheDocument()
    })
  })
})