import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/tests/test-utils'
import userEvent from '@testing-library/user-event'
import { CourierForm } from '../CourierForm'

describe('CourierForm', () => {
  const mockOnSubmit = vi.fn()
  const mockOnCancel = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all form fields', () => {
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    expect(screen.getByPlaceholderText('EMP-001')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('John Doe')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('+971 50 123 4567')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('john.doe@example.com')).toBeInTheDocument()
  })

  it('validates required fields', async () => {
    const user = userEvent.setup()
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    const submitButton = screen.getByRole('button', { name: /create courier/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Employee ID is required')).toBeInTheDocument()
      expect(screen.getByText('Name is required')).toBeInTheDocument()
      expect(screen.getByText('Phone is required')).toBeInTheDocument()
      expect(screen.getByText('Email is required')).toBeInTheDocument()
    })

    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('validates email format', async () => {
    const user = userEvent.setup()
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    const emailInput = screen.getByPlaceholderText('john.doe@example.com')
    await user.type(emailInput, 'invalid-email')

    const submitButton = screen.getByRole('button', { name: /create courier/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Invalid email format')).toBeInTheDocument()
    })
  })

  it('validates phone format', async () => {
    const user = userEvent.setup()
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    const phoneInput = screen.getByPlaceholderText('+971 50 123 4567')
    await user.type(phoneInput, 'abc')

    const submitButton = screen.getByRole('button', { name: /create courier/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Invalid phone number format')).toBeInTheDocument()
    })
  })

  it('validates name length', async () => {
    const user = userEvent.setup()
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    const nameInput = screen.getByPlaceholderText('John Doe')
    await user.type(nameInput, 'A')

    const submitButton = screen.getByRole('button', { name: /create courier/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Name must be at least 2 characters')).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const user = userEvent.setup()
    mockOnSubmit.mockResolvedValue(undefined)

    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    await user.type(screen.getByPlaceholderText('EMP-001'), 'EMP-123')
    await user.type(screen.getByPlaceholderText('John Doe'), 'John Smith')
    await user.type(screen.getByPlaceholderText('+971 50 123 4567'), '+971501234567')
    await user.type(screen.getByPlaceholderText('john.doe@example.com'), 'john@example.com')

    const submitButton = screen.getByRole('button', { name: /create courier/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          employee_id: 'EMP-123',
          name: 'John Smith',
          phone: '+971501234567',
          email: 'john@example.com',
        })
      )
    })
  })

  it('populates form with initial data in edit mode', () => {
    const initialData = {
      employee_id: 'EMP-001',
      name: 'John Doe',
      phone: '+971501234567',
      email: 'john@example.com',
      status: 'active' as const,
    }

    render(
      <CourierForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        initialData={initialData}
        mode="edit"
      />
    )

    expect(screen.getByDisplayValue('EMP-001')).toBeInTheDocument()
    expect(screen.getByDisplayValue('John Doe')).toBeInTheDocument()
    expect(screen.getByDisplayValue('+971501234567')).toBeInTheDocument()
    expect(screen.getByDisplayValue('john@example.com')).toBeInTheDocument()
  })

  it('disables employee ID field in edit mode', () => {
    render(
      <CourierForm
        onSubmit={mockOnSubmit}
        onCancel={mockOnCancel}
        initialData={{ employee_id: 'EMP-001' }}
        mode="edit"
      />
    )

    const employeeIdInput = screen.getByDisplayValue('EMP-001')
    expect(employeeIdInput).toBeDisabled()
  })

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup()
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(mockOnCancel).toHaveBeenCalledTimes(1)
  })

  it('shows correct button text based on mode', () => {
    const { rerender } = render(
      <CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} mode="create" />
    )

    expect(screen.getByRole('button', { name: /create courier/i })).toBeInTheDocument()

    rerender(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} mode="edit" />)

    expect(screen.getByRole('button', { name: /update courier/i })).toBeInTheDocument()
  })

  it('disables form when isLoading is true', () => {
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} isLoading />)

    const submitButton = screen.getByRole('button', { name: /saving/i })
    const cancelButton = screen.getByRole('button', { name: /cancel/i })

    expect(submitButton).toBeDisabled()
    expect(cancelButton).toBeDisabled()
  })

  it('clears error when user starts typing', async () => {
    const user = userEvent.setup()
    render(<CourierForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

    const submitButton = screen.getByRole('button', { name: /create courier/i })
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument()
    })

    const nameInput = screen.getByPlaceholderText('John Doe')
    await user.type(nameInput, 'J')

    expect(screen.queryByText('Name is required')).not.toBeInTheDocument()
  })
})
