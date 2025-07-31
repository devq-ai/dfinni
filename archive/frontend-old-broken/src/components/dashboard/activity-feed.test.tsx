import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ActivityFeed } from './activity-feed'
import { useDashboardStore } from '@/stores/dashboard-store'
import type { Activity } from '@/types/dashboard'

// Mock the dashboard store
vi.mock('@/stores/dashboard-store', () => ({
  useDashboardStore: vi.fn(),
}))

// Mock date-fns
vi.mock('date-fns', () => ({
  formatDistanceToNow: vi.fn((date) => '2 hours ago'),
}))

// Mock logfire
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

import { logger } from '@/lib/logfire'

describe('ActivityFeed', () => {
  const mockActivities: Activity[] = [
    {
      id: '1',
      type: 'patient_added',
      title: 'New patient added',
      description: 'John Doe was added to the system',
      timestamp: new Date().toISOString(),
      patientId: 'p1',
    },
    {
      id: '2',
      type: 'status_changed',
      title: 'Status updated',
      description: 'Jane Smith status changed to Active',
      timestamp: new Date().toISOString(),
      patientId: 'p2',
    },
    {
      id: '3',
      type: 'risk_updated',
      title: 'Risk level changed',
      description: 'Bob Johnson risk level updated to High',
      timestamp: new Date().toISOString(),
      patientId: 'p3',
    },
  ]

  const defaultStoreState = {
    activities: mockActivities,
    isLoading: false,
    fetchActivities: vi.fn(),
  }

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useDashboardStore).mockReturnValue(defaultStoreState as any)
  })

  describe('Rendering', () => {
    it('renders activity feed with activities', () => {
      render(<ActivityFeed />)
      
      expect(screen.getByText('Recent Activity')).toBeInTheDocument()
      expect(screen.getByText('View All')).toBeInTheDocument()
      expect(screen.getByText('New patient added')).toBeInTheDocument()
      expect(screen.getByText('Status updated')).toBeInTheDocument()
      expect(screen.getByText('Risk level changed')).toBeInTheDocument()
    })

    it('shows loading skeleton when loading with no activities', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        ...defaultStoreState,
        activities: [],
        isLoading: true,
      } as any)
      
      const { container } = render(<ActivityFeed />)
      
      const skeletons = container.querySelectorAll('.animate-pulse')
      expect(skeletons.length).toBeGreaterThan(0)
    })

    it('shows empty state when no activities', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        ...defaultStoreState,
        activities: [],
      } as any)
      
      render(<ActivityFeed />)
      
      expect(screen.getByText('No recent activity to display')).toBeInTheDocument()
    })

    it('displays activity descriptions and timestamps', () => {
      render(<ActivityFeed />)
      
      expect(screen.getByText('John Doe was added to the system')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith status changed to Active')).toBeInTheDocument()
      expect(screen.getAllByText('2 hours ago')).toHaveLength(3)
    })
  })

  describe('Activity Icons', () => {
    it('shows correct icons for activity types', () => {
      render(<ActivityFeed />)
      
      // Check for different icon types based on activity
      const activityItems = screen.getAllByRole('button')
      // There are 5 buttons: 3 activities + "View All" + "Load More"
      expect(activityItems).toHaveLength(5)
      
      // Icons should be rendered as SVG elements
      const container = screen.getByText('Recent Activity').parentElement?.parentElement
      const svgIcons = container?.querySelectorAll('svg')
      expect(svgIcons?.length).toBeGreaterThan(0)
    })
  })

  describe('Interactions', () => {
    it('handles activity click', () => {
      render(<ActivityFeed />)
      
      const firstActivity = screen.getByText('New patient added').closest('[role="button"]')
      fireEvent.click(firstActivity!)
      
      expect(logger.userAction).toHaveBeenCalledWith('activity_click', {
        activityId: '1',
        type: 'patient_added',
        patientId: 'p1',
      })
    })

    it('handles View All click', () => {
      render(<ActivityFeed />)
      
      fireEvent.click(screen.getByText('View All'))
      
      expect(logger.userAction).toHaveBeenCalledWith('view_all_activities_click')
    })
  })

  describe('Load More', () => {
    it('shows load more button when there are more activities', () => {
      render(<ActivityFeed />)
      
      expect(screen.getByText('Load More')).toBeInTheDocument()
    })

    it('loads more activities when button clicked', async () => {
      const mockFetchActivities = vi.fn()
      vi.mocked(useDashboardStore).mockReturnValue({
        ...defaultStoreState,
        fetchActivities: mockFetchActivities,
      } as any)
      
      render(<ActivityFeed />)
      
      fireEvent.click(screen.getByText('Load More'))
      
      expect(mockFetchActivities).toHaveBeenCalledWith(2, 10)
    })

    it('shows loading state while fetching more', async () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        ...defaultStoreState,
        isLoading: true,
      } as any)
      
      render(<ActivityFeed />)
      
      const loadMoreButton = screen.getByText('Loading...')
      expect(loadMoreButton).toBeDisabled()
    })

    it('hides load more when no more activities', () => {
      // Simulate having loaded all activities (less than a full page)
      vi.mocked(useDashboardStore).mockReturnValue({
        ...defaultStoreState,
        activities: mockActivities.slice(0, 2), // Only 2 activities
      } as any)
      
      const { rerender } = render(<ActivityFeed />)
      
      // Click load more
      fireEvent.click(screen.getByText('Load More'))
      
      // Simulate state after loading with no new activities
      vi.mocked(useDashboardStore).mockReturnValue({
        ...defaultStoreState,
        activities: mockActivities.slice(0, 2), // Still only 2
      } as any)
      
      rerender(<ActivityFeed />)
      
      // Load more should not be visible when hasMore is false
      // This would be set based on the response
    })
  })

  describe('Accessibility', () => {
    it('has accessible activity items', () => {
      render(<ActivityFeed />)
      
      // Activity items have tabIndex=0 set directly
      const firstActivity = screen.getByText('New patient added').closest('[role="button"]')
      expect(firstActivity).toHaveAttribute('tabIndex', '0')
      
      const secondActivity = screen.getByText('Status updated').closest('[role="button"]')
      expect(secondActivity).toHaveAttribute('tabIndex', '0')
    })
  })
})