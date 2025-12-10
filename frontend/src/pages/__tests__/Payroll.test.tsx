import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/tests/test-utils'
import Payroll from '../hr-finance/Payroll'

// Mock the API calls
vi.mock('@/lib/api', () => ({
  payrollAPI: {
    generate: vi.fn().mockResolvedValue({ success: true }),
    approveAll: vi.fn().mockResolvedValue({ success: true }),
    process: vi.fn().mockResolvedValue({ success: true }),
    export: vi.fn().mockResolvedValue(new Blob(['mock data'])),
  },
  couriersAPI: {
    getAll: vi.fn().mockResolvedValue([
      {
        id: 1,
        name: 'John Doe',
        base_salary: 5000,
      },
      {
        id: 2,
        name: 'Jane Smith',
        base_salary: 6000,
      },
      {
        id: 3,
        name: 'Bob Wilson',
        base_salary: 5500,
      },
      {
        id: 4,
        name: 'Alice Brown',
        base_salary: 5200,
      },
    ]),
  },
}))

// Mock window.alert
global.alert = vi.fn()

// Mock URL.createObjectURL and URL.revokeObjectURL
global.URL.createObjectURL = vi.fn(() => 'mock-url')
global.URL.revokeObjectURL = vi.fn()

describe('Payroll', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByText('Payroll Processing')).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    render(<Payroll />)

    const loadingElements = document.querySelectorAll('.animate-spin')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays financial summary cards', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByText('Total Base Salary')).toBeInTheDocument()
      expect(screen.getByText('Total Allowances')).toBeInTheDocument()
      expect(screen.getByText('Total Deductions')).toBeInTheDocument()
      expect(screen.getByText('Net Payroll')).toBeInTheDocument()
    })
  })

  it('displays status count cards', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByText('Draft')).toBeInTheDocument()
      expect(screen.getByText('Approved')).toBeInTheDocument()
      expect(screen.getByText('Processing')).toBeInTheDocument()
      expect(screen.getByText('Paid')).toBeInTheDocument()
    })
  })

  it('renders Generate Payroll button', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate payroll/i })).toBeInTheDocument()
    })
  })

  it('renders Export button', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument()
    })
  })

  it('displays payroll data in the table', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Jane Smith')).toBeInTheDocument()
    })
  })

  it('displays salary calculations correctly', async () => {
    render(<Payroll />)

    await waitFor(() => {
      // Check for base salary formatting
      expect(screen.getByText(/5,000.00 SAR/i)).toBeInTheDocument()
    })
  })

  it('displays allowances as positive values', async () => {
    render(<Payroll />)

    await waitFor(() => {
      // Allowances should be shown with + prefix
      const allowanceElements = screen.getAllByText(/^\+.*SAR$/i)
      expect(allowanceElements.length).toBeGreaterThan(0)
    })
  })

  it('displays deductions as negative values', async () => {
    render(<Payroll />)

    await waitFor(() => {
      // Deductions should be shown with - prefix
      const deductionElements = screen.getAllByText(/^-.*SAR$/i)
      expect(deductionElements.length).toBeGreaterThan(0)
    })
  })

  it('triggers generate payroll when button is clicked', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /generate payroll/i })).toBeInTheDocument()
    })

    const generateButton = screen.getByRole('button', { name: /generate payroll/i })
    fireEvent.click(generateButton)

    expect(global.alert).toHaveBeenCalledWith('Generating payroll for all employees...')
  })

  it('has month filter', async () => {
    render(<Payroll />)

    await waitFor(() => {
      const monthInput = screen.getByDisplayValue(new Date().toISOString().slice(0, 7))
      expect(monthInput).toBeInTheDocument()
    })
  })

  it('has status filter dropdown', async () => {
    render(<Payroll />)

    await waitFor(() => {
      const statusSelect = screen.getByDisplayValue('All Status')
      expect(statusSelect).toBeInTheDocument()
    })
  })

  it('displays batch actions section', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByText('Batch Actions')).toBeInTheDocument()
      expect(screen.getByText(/approve all draft/i)).toBeInTheDocument()
      expect(screen.getByText(/process approved/i)).toBeInTheDocument()
    })
  })

  it('shows approve/reject buttons for draft status', async () => {
    render(<Payroll />)

    await waitFor(() => {
      // Look for approve buttons (CheckCircle icons)
      const approveButtons = document.querySelectorAll('[title="Approve"]')
      expect(approveButtons.length).toBeGreaterThan(0)
    })
  })

  it('shows processing indicator for processing status', async () => {
    render(<Payroll />)

    await waitFor(() => {
      // Check for "Processing" text in table
      const processingElements = screen.getAllByText(/Processing/i)
      expect(processingElements.length).toBeGreaterThan(0)
    })
  })

  it('shows completed indicator for paid status', async () => {
    render(<Payroll />)

    await waitFor(() => {
      expect(screen.getByText('Completed')).toBeInTheDocument()
    })
  })
})
