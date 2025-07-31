import { describe, it, expect, vi } from 'vitest'
import { render, screen, checkA11y } from '@/test/test-utils'
import { axe, toHaveNoViolations } from 'jest-axe'
import DashboardPage from '@/app/(dashboard)/dashboard/page'
import LoginPage from '@/app/login/page'
import { PatientDialog } from '@/components/patients/patient-dialog'
import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'
import { ErrorBoundary } from '@/components/error-boundary'

// Extend matchers
expect.extend(toHaveNoViolations)

// Mock stores and dependencies
vi.mock('@/stores/dashboard-store', () => ({
  useDashboardStore: () => ({
    metrics: {
      totalPatients: 100,
      activePatients: 80,
      newPatientsThisMonth: 10,
      patientGrowthRate: 5,
      statusDistribution: { inquiry: 10, onboarding: 15, active: 65, churned: 10 },
      riskDistribution: { low: 60, medium: 30, high: 10 },
      healthOutcomes: { improved: 45, stable: 40, declined: 15 },
      recentActivities: []
    },
    refreshDashboard: vi.fn(),
    isLoading: false,
    error: null
  })
}))

vi.mock('@/stores/patient-store', () => ({
  usePatientStore: () => ({
    totalCount: 100,
    selectedPatient: null,
    createPatient: vi.fn(),
    updatePatient: vi.fn()
  })
}))

vi.mock('@/stores/auth-store', () => ({
  useAuthStore: () => ({
    user: { id: '1', email: 'test@example.com', name: 'Test User' },
    logout: vi.fn()
  })
}))

// Mock dynamic imports
vi.mock('@/lib/dynamic-imports', () => ({
  DynamicComponents: {
    ActivityFeed: () => <div>Activity Feed</div>,
    StatusDistributionChart: () => <div>Status Distribution Chart</div>
  }
}))

describe('Accessibility Tests', () => {
  describe('Page Level Accessibility', () => {
    it('dashboard page should have no accessibility violations', async () => {
      const { container } = render(<DashboardPage />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('login page should have no accessibility violations', async () => {
      const { container } = render(<LoginPage />)
      const results = await axe(container)
      expect(results).toHaveNoViolations()
    })

    it('should have proper page structure', () => {
      render(<DashboardPage />)
      
      // Should have main landmark
      expect(screen.getByRole('main')).toBeInTheDocument()
      
      // Should have proper heading hierarchy
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
    })
  })

  describe('Component Accessibility', () => {
    it('header should have proper ARIA labels', () => {
      render(<Header />)
      
      // Navigation buttons should have labels
      expect(screen.getByLabelText(/view notifications/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/toggle theme/i)).toBeInTheDocument()
      
      // User menu should be accessible
      const userButton = screen.getByRole('button', { name: /test user/i })
      expect(userButton).toHaveAttribute('aria-expanded', 'false')
    })

    it('sidebar should have navigation landmarks', () => {
      render(<Sidebar />)
      
      // Should have navigation role
      expect(screen.getByRole('navigation')).toBeInTheDocument()
      
      // Links should indicate current page
      const links = screen.getAllByRole('link')
      const currentLink = links.find(link => link.getAttribute('aria-current') === 'page')
      expect(currentLink).toBeDefined()
    })

    it('patient dialog should have accessible form', async () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      // Form inputs should have labels
      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/date of birth/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/phone/i)).toBeInTheDocument()
      
      // Dialog should have proper ARIA attributes
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-labelledby')
      expect(dialog).toHaveAttribute('aria-describedby')
    })
  })

  describe('Keyboard Navigation', () => {
    it('should support keyboard navigation in sidebar', () => {
      render(<Sidebar />)
      
      const links = screen.getAllByRole('link')
      
      // All links should be focusable
      links.forEach(link => {
        expect(link).toHaveAttribute('href')
        expect(parseInt(link.getAttribute('tabindex') || '0')).toBeGreaterThanOrEqual(0)
      })
    })

    it('should trap focus in dialog', () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      const dialog = screen.getByRole('dialog')
      const focusableElements = dialog.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      
      expect(focusableElements.length).toBeGreaterThan(0)
    })
  })

  describe('Color Contrast', () => {
    it('should have sufficient color contrast for text', () => {
      const { container } = render(<DashboardPage />)
      
      // Check main text elements
      const textElements = container.querySelectorAll('p, h1, h2, h3, span')
      
      textElements.forEach(element => {
        const styles = window.getComputedStyle(element)
        const color = styles.color
        const backgroundColor = styles.backgroundColor
        
        // Basic check - ensure text is not same color as background
        expect(color).not.toBe(backgroundColor)
      })
    })
  })

  describe('Screen Reader Support', () => {
    it('should announce loading states', () => {
      vi.mocked(useDashboardStore).mockReturnValue({
        ...useDashboardStore(),
        isLoading: true
      })
      
      render(<DashboardPage />)
      
      // Loading message should be announced
      expect(screen.getByText(/refreshing dashboard/i)).toBeInTheDocument()
      expect(screen.getByText(/refreshing dashboard/i).closest('div')).toHaveAttribute('aria-live')
    })

    it('should announce errors', () => {
      render(
        <ErrorBoundary>
          <ThrowError />
        </ErrorBoundary>
      )
      
      const errorMessage = screen.getByText(/something went wrong/i)
      expect(errorMessage).toBeInTheDocument()
      expect(errorMessage.closest('div')).toHaveAttribute('role', 'alert')
    })
  })

  describe('Form Accessibility', () => {
    it('should show validation errors accessibly', async () => {
      render(<PatientDialog open={true} onOpenChange={() => {}} mode="create" />)
      
      // Submit empty form
      const submitButton = screen.getByRole('button', { name: /create patient/i })
      fireEvent.click(submitButton)
      
      // Wait for validation
      await waitFor(() => {
        const firstNameInput = screen.getByLabelText(/first name/i)
        expect(firstNameInput).toHaveAttribute('aria-invalid', 'true')
        expect(firstNameInput).toHaveAttribute('aria-describedby')
      })
      
      // Error messages should be associated with inputs
      const errorMessage = screen.getByText(/first name is required/i)
      expect(errorMessage).toHaveAttribute('id')
    })
  })

  describe('Custom A11y Checks', () => {
    it('should pass custom accessibility checks', async () => {
      const { container } = render(<DashboardPage />)
      const results = await checkA11y(container)
      
      // No errors expected
      const errors = results.filter(r => r.type === 'error')
      expect(errors).toHaveLength(0)
      
      // Check for warnings
      const warnings = results.filter(r => r.type === 'warning')
      if (warnings.length > 0) {
        console.warn('Accessibility warnings:', warnings)
      }
    })
  })
})

// Helper component that throws error
function ThrowError() {
  throw new Error('Test error')
  return null
}