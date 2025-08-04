import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { PatientForm } from './PatientForm'

// Mock fetch
global.fetch = vi.fn()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
)

describe('PatientForm', () => {
  const mockOnSuccess = vi.fn()
  const mockOnCancel = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    queryClient.clear()
  })

  it('renders form fields correctly', () => {
    render(<PatientForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, { wrapper })

    expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Date of Birth/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Phone/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Address/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Medical Record Number/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Risk Level/i)).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    const user = userEvent.setup()
    render(<PatientForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, { wrapper })

    // Click submit without filling fields
    const submitButton = screen.getByRole('button', { name: /Create Patient/i })
    await user.click(submitButton)

    // Check for validation errors
    await waitFor(() => {
      expect(screen.getByText('First name is required')).toBeInTheDocument()
      expect(screen.getByText('Last name is required')).toBeInTheDocument()
      expect(screen.getByText('Email is required')).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    render(<PatientForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, { wrapper })

    // Fill required fields first
    await user.type(screen.getByLabelText(/First Name/i), 'John')
    await user.type(screen.getByLabelText(/Last Name/i), 'Doe')
    
    const emailInput = screen.getByLabelText(/Email/i)
    await user.type(emailInput, 'invalid-email')
    
    const submitButton = screen.getByRole('button', { name: /Create Patient/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Invalid email format')).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    
    // Mock successful API response
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: '123', first_name: 'John', last_name: 'Doe' }),
    })

    render(<PatientForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, { wrapper })

    // Fill in form fields
    await user.type(screen.getByLabelText(/First Name/i), 'John')
    await user.type(screen.getByLabelText(/Last Name/i), 'Doe')
    await user.type(screen.getByLabelText(/Email/i), 'john.doe@example.com')
    await user.type(screen.getByLabelText(/Date of Birth/i), '1990-01-01')
    await user.type(screen.getByLabelText(/Phone/i), '(555) 123-4567')
    await user.type(screen.getByLabelText(/Address/i), '123 Main St')
    await user.type(screen.getByLabelText(/Medical Record Number/i), 'MRN12345')

    // Submit form
    const submitButton = screen.getByRole('button', { name: /Create Patient/i })
    await user.click(submitButton)

    // Verify API call
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/patients',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            first_name: 'John',
            last_name: 'Doe',
            email: 'john.doe@example.com',
            date_of_birth: '1990-01-01',
            phone: '(555) 123-4567',
            address: '123 Main St',
            medical_record_number: 'MRN12345',
            risk_level: 'Medium',
          }),
        })
      )
    })

    // Verify success callback
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledTimes(1)
    })
  })

  it('handles API errors gracefully', async () => {
    const user = userEvent.setup()
    
    // Mock API error
    ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

    render(<PatientForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, { wrapper })

    // Fill minimum required fields
    await user.type(screen.getByLabelText(/First Name/i), 'John')
    await user.type(screen.getByLabelText(/Last Name/i), 'Doe')
    await user.type(screen.getByLabelText(/Email/i), 'john.doe@example.com')

    // Submit form
    const submitButton = screen.getByRole('button', { name: /Create Patient/i })
    await user.click(submitButton)

    // Check for error handling (toast notification would appear)
    await waitFor(() => {
      expect(mockOnSuccess).not.toHaveBeenCalled()
    })
  })

  it('handles cancel action', async () => {
    const user = userEvent.setup()
    render(<PatientForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />, { wrapper })

    const cancelButton = screen.getByRole('button', { name: /Cancel/i })
    await user.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalled()
  })

  it('updates existing patient when patient prop is provided', async () => {
    const existingPatient = {
      id: '123',
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane.smith@example.com',
      date_of_birth: '1985-05-15',
      phone: '(555) 987-6543',
      address: '456 Oak Ave',
      medical_record_number: 'MRN54321',
      risk_level: 'High' as const,
    }

    const user = userEvent.setup()
    
    // Mock successful API response
    ;(global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ...existingPatient, first_name: 'Janet' }),
    })

    render(
      <PatientForm 
        patient={existingPatient} 
        onSuccess={mockOnSuccess} 
        onCancel={mockOnCancel} 
      />, 
      { wrapper }
    )

    // Check that form is pre-filled
    expect(screen.getByDisplayValue('Jane')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Smith')).toBeInTheDocument()
    expect(screen.getByDisplayValue('jane.smith@example.com')).toBeInTheDocument()

    // Update first name
    const firstNameInput = screen.getByLabelText(/First Name/i)
    await user.clear(firstNameInput)
    await user.type(firstNameInput, 'Janet')

    // Submit form
    const submitButton = screen.getByRole('button', { name: /Update Patient/i })
    await user.click(submitButton)

    // Verify API call for update
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        `http://localhost:8001/api/patients/123`,
        expect.objectContaining({
          method: 'PUT',
        })
      )
    })

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledTimes(1)
    })
  })
})