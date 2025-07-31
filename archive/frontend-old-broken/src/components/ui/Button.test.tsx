import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'
import { logger } from '@/lib/logfire'

// Mock the logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

describe('Button Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders with default props', () => {
      render(<Button>Click me</Button>)
      
      const button = screen.getByRole('button', { name: 'Click me' })
      expect(button).toBeInTheDocument()
      expect(button).toHaveClass('bg-blue-600')
      expect(button).toHaveClass('px-4 py-2')
    })

    it.each([
      { variant: 'primary' as const, expectedClass: 'bg-blue-600' },
      { variant: 'secondary' as const, expectedClass: 'bg-gray-200' },
      { variant: 'danger' as const, expectedClass: 'bg-red-600' },
    ])('renders with $variant variant', ({ variant, expectedClass }) => {
      render(<Button variant={variant}>Button</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass(expectedClass)
    })

    it.each([
      { size: 'sm' as const, expectedClass: 'px-3 py-1.5' },
      { size: 'md' as const, expectedClass: 'px-4 py-2' },
      { size: 'lg' as const, expectedClass: 'px-6 py-3' },
    ])('renders with $size size', ({ size, expectedClass }) => {
      render(<Button size={size}>Button</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass(expectedClass)
    })

    it('renders loading state', () => {
      render(<Button isLoading>Submit</Button>)
      
      expect(screen.getByText('Loading...')).toBeInTheDocument()
      expect(screen.queryByText('Submit')).not.toBeInTheDocument()
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(button).toHaveClass('opacity-50')
    })

    it('renders disabled state', () => {
      render(<Button disabled>Click me</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toBeDisabled()
      expect(button).toHaveClass('opacity-50')
    })
  })

  describe('Interactions', () => {
    it('calls onClick handler when clicked', () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick}>Click me</Button>)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('does not call onClick when disabled', () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick} disabled>Click me</Button>)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      expect(handleClick).not.toHaveBeenCalled()
    })

    it('does not call onClick when loading', () => {
      const handleClick = vi.fn()
      render(<Button onClick={handleClick} isLoading>Click me</Button>)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      expect(handleClick).not.toHaveBeenCalled()
    })
  })

  describe('Logging', () => {
    it('logs user action on click', () => {
      render(<Button variant="primary" size="md">Submit Form</Button>)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      expect(logger.userAction).toHaveBeenCalledWith('button_click', {
        variant: 'primary',
        size: 'md',
        text: 'Submit Form',
      })
    })

    it('logs user action even when onClick is not provided', () => {
      render(<Button>Test Button</Button>)
      
      const button = screen.getByRole('button')
      fireEvent.click(button)
      
      expect(logger.userAction).toHaveBeenCalledWith('button_click', {
        variant: 'primary',
        size: 'md',
        text: 'Test Button',
      })
    })
  })

  describe('Accessibility', () => {
    it('forwards additional props to button element', () => {
      render(
        <Button aria-label="Save document" data-testid="save-button">
          Save
        </Button>
      )
      
      const button = screen.getByRole('button')
      expect(button).toHaveAttribute('aria-label', 'Save document')
      expect(button).toHaveAttribute('data-testid', 'save-button')
    })

    it('maintains focus styles', () => {
      render(<Button>Focus me</Button>)
      
      const button = screen.getByRole('button')
      expect(button).toHaveClass('focus:outline-none')
      expect(button).toHaveClass('focus:ring-2')
    })
  })
})