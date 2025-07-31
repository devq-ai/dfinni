import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { DashboardLayout } from './dashboard-layout'

// Mock the child components
vi.mock('./sidebar', () => ({
  Sidebar: () => <div data-testid="sidebar">Sidebar</div>,
}))

vi.mock('./header', () => ({
  Header: () => <div data-testid="header">Header</div>,
}))

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    componentMount: vi.fn(),
    componentUnmount: vi.fn(),
  },
}))

describe('DashboardLayout', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders sidebar and header', () => {
    render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    )

    expect(screen.getByTestId('sidebar')).toBeInTheDocument()
    expect(screen.getByTestId('header')).toBeInTheDocument()
  })

  it('renders children content', () => {
    render(
      <DashboardLayout>
        <div>Test Content</div>
      </DashboardLayout>
    )

    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('applies container styling to main content', () => {
    const { container } = render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    )

    const mainContent = container.querySelector('main')
    expect(mainContent).toHaveClass('flex-1', 'overflow-y-auto', 'bg-zinc-950')
    
    const contentWrapper = mainContent?.querySelector('.container')
    expect(contentWrapper).toHaveClass('mx-auto', 'px-4', 'sm:px-6', 'lg:px-8', 'py-8')
  })

  it('applies custom className to main element', () => {
    const { container } = render(
      <DashboardLayout className="custom-main-class">
        <div>Content</div>
      </DashboardLayout>
    )

    const mainElement = container.querySelector('main')
    expect(mainElement).toHaveClass('custom-main-class')
  })

  it('has correct layout structure', () => {
    const { container } = render(
      <DashboardLayout>
        <div>Content</div>
      </DashboardLayout>
    )

    // Root div with flex layout
    const rootDiv = container.firstChild
    expect(rootDiv).toHaveClass('flex', 'h-screen', 'bg-zinc-950', 'text-zinc-100')

    // Main content area with flex column
    const contentArea = container.querySelector('.flex-1.flex-col')
    expect(contentArea).toBeInTheDocument()
  })
})