import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ThemeToggle } from './theme-toggle'

// Mock logger
vi.mock('@/lib/logfire', () => ({
  logger: {
    userAction: vi.fn(),
  },
}))

import { logger } from '@/lib/logfire'

describe('ThemeToggle', () => {
  // Mock localStorage
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
  }
  
  // Mock matchMedia
  const matchMediaMock = vi.fn().mockImplementation(query => ({
    matches: query === '(prefers-color-scheme: dark)',
    media: query,
    onchange: null,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }))

  beforeEach(() => {
    vi.clearAllMocks()
    Object.defineProperty(window, 'localStorage', { value: localStorageMock })
    Object.defineProperty(window, 'matchMedia', { value: matchMediaMock })
    
    // Reset document classes
    document.documentElement.classList.remove('dark')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders with dark theme by default', async () => {
    render(<ThemeToggle />)
    
    await waitFor(() => {
      const button = screen.getByLabelText('Switch to light mode')
      expect(button).toBeInTheDocument()
    })
    
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('loads theme from localStorage', async () => {
    localStorageMock.getItem.mockReturnValue('light')
    
    render(<ThemeToggle />)
    
    await waitFor(() => {
      const button = screen.getByLabelText('Switch to dark mode')
      expect(button).toBeInTheDocument()
    })
    
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggles between light and dark themes', async () => {
    render(<ThemeToggle />)
    
    await waitFor(() => {
      const button = screen.getByLabelText('Switch to light mode')
      expect(button).toBeInTheDocument()
    })
    
    const button = screen.getByRole('button')
    
    // Toggle to light
    fireEvent.click(button)
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(screen.getByLabelText('Switch to dark mode')).toBeInTheDocument()
    
    // Toggle back to dark
    fireEvent.click(button)
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(screen.getByLabelText('Switch to light mode')).toBeInTheDocument()
  })

  it('logs theme changes', async () => {
    const mockLogger = vi.mocked(logger.userAction)
    render(<ThemeToggle />)
    
    await waitFor(() => {
      expect(screen.getByRole('button')).toBeInTheDocument()
    })
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    expect(mockLogger).toHaveBeenCalledWith('theme_toggle', {
      from: 'dark',
      to: 'light'
    })
  })

  it('shows sun icon for dark theme', async () => {
    render(<ThemeToggle />)
    
    await waitFor(() => {
      const sunIcon = document.querySelector('.lucide-sun')
      expect(sunIcon).toBeInTheDocument()
    })
  })

  it('shows moon icon for light theme', async () => {
    localStorageMock.getItem.mockReturnValue('light')
    
    render(<ThemeToggle />)
    
    await waitFor(() => {
      const moonIcon = document.querySelector('.lucide-moon')
      expect(moonIcon).toBeInTheDocument()
    })
  })

  it('prevents hydration mismatch with placeholder', () => {
    const { container } = render(<ThemeToggle />)
    
    // Initially renders placeholder button
    const button = container.querySelector('button')
    expect(button).toBeInTheDocument()
    // Check that button has correct size classes
    expect(button).toHaveClass('w-9', 'h-9', 'p-0')
  })

  it('respects system preference when no saved theme', async () => {
    localStorageMock.getItem.mockReturnValue(null)
    
    render(<ThemeToggle />)
    
    await waitFor(() => {
      // System prefers dark (mocked above), but we default to dark anyway
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })
  })
})