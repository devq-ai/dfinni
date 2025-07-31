import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary, useErrorHandler } from '../error-boundary'
import { renderHook, act } from '@testing-library/react'

// Mock error logging
vi.mock('@/lib/error-handler', () => ({
  logErrorToService: vi.fn()
}))

// Mock Next.js Link
vi.mock('next/link', () => ({
  default: ({ children, href }: any) => <a href={href}>{children}</a>
}))

// Component that throws an error
function ThrowError({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error('Test error')
  }
  return <div>No error</div>
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Suppress console.error for cleaner test output
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('should render children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    )

    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('should display error UI when error is thrown', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText(/We encountered an unexpected error/)).toBeInTheDocument()
  })

  it('should display custom fallback when provided', () => {
    const customFallback = <div>Custom error message</div>

    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Custom error message')).toBeInTheDocument()
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
  })

  it('should call onError callback when error occurs', () => {
    const onError = vi.fn()

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String)
      })
    )
  })

  it('should reset error state when Try again is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Something went wrong')).toBeInTheDocument()

    // Click Try again
    fireEvent.click(screen.getByText('Try again'))

    // Rerender with no error
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    )

    expect(screen.getByText('No error')).toBeInTheDocument()
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument()
  })

  it('should display error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'development'

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Error details')).toBeInTheDocument()
    
    // Click to expand details
    fireEvent.click(screen.getByText('Error details'))
    
    expect(screen.getByText(/Error: Test error/)).toBeInTheDocument()

    process.env.NODE_ENV = originalEnv
  })

  it('should not display error details in production mode', () => {
    const originalEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.queryByText('Error details')).not.toBeInTheDocument()

    process.env.NODE_ENV = originalEnv
  })

  it('should provide dashboard link', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    const dashboardLink = screen.getByRole('link', { name: /Go to Dashboard/i })
    expect(dashboardLink).toHaveAttribute('href', '/dashboard')
  })
})

describe('useErrorHandler', () => {
  it('should capture and throw errors', () => {
    const { result } = renderHook(() => useErrorHandler())

    expect(() => {
      act(() => {
        result.current.captureError(new Error('Hook error'))
      })
    }).toThrow('Hook error')
  })

  it('should reset error state', () => {
    const { result } = renderHook(() => useErrorHandler())

    // First capture an error
    try {
      act(() => {
        result.current.captureError(new Error('Hook error'))
      })
    } catch {
      // Expected to throw
    }

    // Reset should not throw
    expect(() => {
      act(() => {
        result.current.resetError()
      })
    }).not.toThrow()
  })
})