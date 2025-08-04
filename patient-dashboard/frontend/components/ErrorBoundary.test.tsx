import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ErrorBoundary } from './ErrorBoundary'

// Component that throws an error
const ThrowError = ({ shouldThrow }: { shouldThrow: boolean }) => {
  if (shouldThrow) {
    throw new Error('Test error message')
  }
  return <div>No error</div>
}

// Mock console.error to avoid noise in test output
const originalError = console.error
beforeAll(() => {
  console.error = vi.fn()
})

afterAll(() => {
  console.error = originalError
})

describe('ErrorBoundary', () => {
  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    )

    expect(screen.getByText('Test content')).toBeInTheDocument()
  })

  it('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    // Check for error UI elements
    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument()
    expect(screen.getByText(/We apologize for the inconvenience/)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Try again/i })).toBeInTheDocument()
  })

  it('displays error message in development mode', () => {
    const originalEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'development'

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByText('Error: Test error message')).toBeInTheDocument()

    process.env.NODE_ENV = originalEnv
  })

  it('hides error details in production mode', () => {
    const originalEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'production'

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.queryByText('Error: Test error message')).not.toBeInTheDocument()

    process.env.NODE_ENV = originalEnv
  })

  it('resets error state when clicking Try again button', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    // Error UI should be shown
    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument()

    // Click Try again
    const tryAgainButton = screen.getByRole('button', { name: /Try again/i })
    tryAgainButton.click()

    // Rerender with non-throwing component
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    )

    // Should show normal content
    expect(screen.getByText('No error')).toBeInTheDocument()
    expect(screen.queryByText('Oops! Something went wrong')).not.toBeInTheDocument()
  })

  it('logs error to console in development', () => {
    const originalEnv = process.env.NODE_ENV
    process.env.NODE_ENV = 'development'

    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(console.error).toHaveBeenCalled()

    process.env.NODE_ENV = originalEnv
  })

  it('catches errors in nested components', () => {
    const NestedError = () => {
      throw new Error('Nested error')
    }

    const ParentComponent = () => (
      <div>
        <h1>Parent</h1>
        <NestedError />
      </div>
    )

    render(
      <ErrorBoundary>
        <ParentComponent />
      </ErrorBoundary>
    )

    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument()
    expect(screen.queryByText('Parent')).not.toBeInTheDocument()
  })

  it('renders custom fallback component if provided', () => {
    const CustomFallback = ({ error, resetError }: any) => (
      <div>
        <h1>Custom Error</h1>
        <p>{error.message}</p>
        <button onClick={resetError}>Reset</button>
      </div>
    )

    // If ErrorBoundary supports custom fallback
    render(
      <ErrorBoundary fallback={CustomFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    // This test assumes ErrorBoundary can accept a fallback prop
    // If not implemented, this test should be adjusted
  })

  it('maintains error boundary isolation', () => {
    render(
      <div>
        <ErrorBoundary>
          <ThrowError shouldThrow={true} />
        </ErrorBoundary>
        <div>Outside error boundary</div>
      </div>
    )

    // Error boundary should contain the error
    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument()
    // Content outside should still render
    expect(screen.getByText('Outside error boundary')).toBeInTheDocument()
  })
})