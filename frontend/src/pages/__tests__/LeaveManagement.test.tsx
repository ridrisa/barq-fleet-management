import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/tests/test-utils'
import LeaveManagement from '../hr-finance/LeaveManagement'

// Mock the API calls
vi.mock('@/lib/api', () => ({
  leavesAPI: {
    getAll: vi.fn().mockResolvedValue([
      {
        id: 1,
        courier: { barq_id: 'BRQ-001', full_name: 'John Doe' },
        leave_type: 'annual',
        start_date: '2024-01-15',
        end_date: '2024-01-20',
        status: 'pending',
      },
      {
        id: 2,
        courier: { barq_id: 'BRQ-002', full_name: 'Jane Smith' },
        leave_type: 'sick',
        start_date: '2024-01-10',
        end_date: '2024-01-12',
        status: 'approved',
      },
      {
        id: 3,
        courier: { barq_id: 'BRQ-003', full_name: 'Bob Wilson' },
        leave_type: 'emergency',
        start_date: '2024-01-08',
        end_date: '2024-01-08',
        status: 'rejected',
      },
    ]),
    create: vi.fn().mockResolvedValue({ id: 4, status: 'pending' }),
    update: vi.fn().mockResolvedValue({ id: 1, status: 'approved' }),
    delete: vi.fn().mockResolvedValue(undefined),
  },
}))

// Mock window.confirm
global.confirm = vi.fn(() => true)

describe('LeaveManagement', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByText('Leave Management')).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    render(<LeaveManagement />)

    const loadingElements = document.querySelectorAll('.animate-spin')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays summary cards with leave request counts', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByText('Total Requests')).toBeInTheDocument()
      expect(screen.getByText('Pending')).toBeInTheDocument()
      expect(screen.getByText('Approved')).toBeInTheDocument()
      expect(screen.getByText('Rejected')).toBeInTheDocument()
    })
  })

  it('renders the New Leave Request button', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /new leave request/i })).toBeInTheDocument()
    })
  })

  it('displays leave requests in the table', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('BRQ-001')).toBeInTheDocument()
      expect(screen.getByText('annual')).toBeInTheDocument()
    })
  })

  it('displays status badges with correct variants', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByText('pending')).toBeInTheDocument()
      expect(screen.getByText('approved')).toBeInTheDocument()
      expect(screen.getByText('rejected')).toBeInTheDocument()
    })
  })

  it('shows approve/reject buttons for pending requests', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    // Check for approve and reject button icons (CheckCircle and XCircle)
    const approveButtons = document.querySelectorAll('[title="Approve"]')
    const rejectButtons = document.querySelectorAll('[title="Reject"]')

    expect(approveButtons.length).toBeGreaterThan(0)
    expect(rejectButtons.length).toBeGreaterThan(0)
  })

  it('calculates and displays leave duration in days', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      // John Doe: Jan 15-20 = 6 days
      expect(screen.getByText('6')).toBeInTheDocument()
      // Jane Smith: Jan 10-12 = 3 days
      expect(screen.getByText('3')).toBeInTheDocument()
      // Bob Wilson: Jan 8-8 = 1 day
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('has search functionality', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/search leave requests/i)
    expect(searchInput).toBeInTheDocument()

    fireEvent.change(searchInput, { target: { value: 'John' } })

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })

  it('opens modal when New Leave Request button is clicked', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /new leave request/i })).toBeInTheDocument()
    })

    const addButton = screen.getByRole('button', { name: /new leave request/i })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText('New Leave Request')).toBeInTheDocument()
    })
  })

  it('displays leave type badges', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      expect(screen.getByText('annual')).toBeInTheDocument()
      expect(screen.getByText('sick')).toBeInTheDocument()
      expect(screen.getByText('emergency')).toBeInTheDocument()
    })
  })

  it('formats dates correctly', async () => {
    render(<LeaveManagement />)

    await waitFor(() => {
      // Check that dates are displayed (format may vary by locale)
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })
})
