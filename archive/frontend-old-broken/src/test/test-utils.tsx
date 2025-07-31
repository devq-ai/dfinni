import React from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { ErrorBoundary } from '@/components/error-boundary'

// Mock providers and wrappers
interface AllTheProvidersProps {
  children: React.ReactNode
}

function AllTheProviders({ children }: AllTheProvidersProps) {
  return (
    <ErrorBoundary>
      {children}
    </ErrorBoundary>
  )
}

// Custom render method
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }

// Test data factories
export const createMockPatient = (overrides = {}) => ({
  id: 'patient-1',
  firstName: 'John',
  lastName: 'Doe',
  dateOfBirth: '1990-01-01',
  email: 'john.doe@example.com',
  phone: '555-0123',
  status: 'active' as const,
  riskLevel: 'low' as const,
  lastVisit: new Date().toISOString(),
  nextAppointment: null,
  conditions: [],
  medications: [],
  insuranceStatus: 'active' as const,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  ...overrides
})

export const createMockUser = (overrides = {}) => ({
  id: 'user-1',
  email: 'test@example.com',
  name: 'Test User',
  role: 'provider' as const,
  isActive: true,
  ...overrides
})

export const createMockAlert = (overrides = {}) => ({
  id: 'alert-1',
  type: 'eligibility' as const,
  severity: 'medium' as const,
  priority: 'MEDIUM' as const,
  title: 'Test Alert',
  message: 'This is a test alert',
  isRead: false,
  timestamp: new Date().toISOString(),
  ...overrides
})

// Wait utilities
export const waitForLoadingToFinish = () => 
  screen.findByText((content, element) => {
    return !element?.className?.includes('animate-pulse')
  })

// Mock API responses
export const mockApiResponse = (data: any, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  statusText: status === 200 ? 'OK' : 'Error',
  headers: new Headers({ 'content-type': 'application/json' }),
  json: async () => data,
  text: async () => JSON.stringify(data),
  blob: async () => new Blob([JSON.stringify(data)]),
  clone: () => mockApiResponse(data, status)
})

// Performance testing utilities
export const measureRenderTime = async (
  component: React.ReactElement,
  options?: RenderOptions
) => {
  const startTime = performance.now()
  const result = customRender(component, options)
  await screen.findByTestId('render-complete', { timeout: 5000 }).catch(() => {})
  const endTime = performance.now()
  
  return {
    ...result,
    renderTime: endTime - startTime
  }
}

// Accessibility testing helpers
export const checkA11y = async (container: HTMLElement) => {
  const results = []
  
  // Check for alt text on images
  const images = container.querySelectorAll('img')
  images.forEach(img => {
    if (!img.alt) {
      results.push({
        type: 'error',
        message: `Image missing alt text: ${img.src}`
      })
    }
  })
  
  // Check for button labels
  const buttons = container.querySelectorAll('button')
  buttons.forEach(button => {
    if (!button.textContent && !button.getAttribute('aria-label')) {
      results.push({
        type: 'error',
        message: 'Button missing accessible label'
      })
    }
  })
  
  // Check for form labels
  const inputs = container.querySelectorAll('input, select, textarea')
  inputs.forEach(input => {
    const id = input.id
    if (id && !container.querySelector(`label[for="${id}"]`)) {
      results.push({
        type: 'warning',
        message: `Input missing associated label: ${id}`
      })
    }
  })
  
  return results
}

import { screen } from '@testing-library/react'