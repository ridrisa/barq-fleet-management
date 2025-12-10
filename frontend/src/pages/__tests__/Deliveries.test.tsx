import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/tests/test-utils'
import Deliveries from '../operations/Deliveries'

// Mock the API calls
vi.mock('@/lib/api', () => ({
  deliveriesAPI: {
    getAll: vi.fn().mockResolvedValue([
      {
        id: 1,
        tracking_number: 'TRK-000001',
        status: 'delivered',
        courier_id: 1,
        courier_name: 'John Doe',
        customer_name: 'Alice Smith',
        pickup_address: '123 Main St',
        delivery_address: '456 Oak Ave',
        delivery_date: '2024-01-15',
        cod_amount: 150.00,
      },
      {
        id: 2,
        tracking_number: 'TRK-000002',
        status: 'in_transit',
        courier_id: 2,
        courier_name: 'Jane Doe',
        customer_name: 'Bob Johnson',
        pickup_address: '789 Pine St',
        delivery_address: '321 Elm Ave',
        delivery_date: '2024-01-16',
        cod_amount: 75.50,
      },
      {
        id: 3,
        tracking_number: 'TRK-000003',
        status: 'failed',
        courier_id: 1,
        courier_name: 'John Doe',
        customer_name: 'Carol White',
        pickup_address: '555 Cedar Blvd',
        delivery_address: '888 Maple Dr',
        delivery_date: '2024-01-14',
        cod_amount: 200.00,
      },
    ]),
    create: vi.fn().mockResolvedValue({ id: 4, tracking_number: 'TRK-000004' }),
    update: vi.fn().mockResolvedValue({ id: 1, status: 'delivered' }),
    delete: vi.fn().mockResolvedValue(undefined),
  },
}))

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}))

// Mock window.alert
global.alert = vi.fn()

describe('Deliveries', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByText('Delivery Records')).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    render(<Deliveries />)

    // Check for loading spinner
    const loadingElements = document.querySelectorAll('.animate-spin')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays KPI cards with delivery statistics', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByText('Total Deliveries')).toBeInTheDocument()
      expect(screen.getByText('Success Rate')).toBeInTheDocument()
      expect(screen.getByText('Completed')).toBeInTheDocument()
      expect(screen.getByText('In Progress')).toBeInTheDocument()
      expect(screen.getByText('Failed')).toBeInTheDocument()
    })
  })

  it('renders Add Delivery button', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add delivery/i })).toBeInTheDocument()
    })
  })

  it('renders Export button', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument()
    })
  })

  it('displays deliveries in the table', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByText('TRK-000001')).toBeInTheDocument()
      expect(screen.getByText('Alice Smith')).toBeInTheDocument()
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })

  it('displays status badges with correct variants', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByText('delivered')).toBeInTheDocument()
      expect(screen.getByText('in_transit')).toBeInTheDocument()
      expect(screen.getByText('failed')).toBeInTheDocument()
    })
  })

  it('has search functionality', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByText('TRK-000001')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/search deliveries/i)
    expect(searchInput).toBeInTheDocument()

    fireEvent.change(searchInput, { target: { value: 'Alice' } })

    await waitFor(() => {
      expect(screen.getByText('Alice Smith')).toBeInTheDocument()
    })
  })

  it('has status filter dropdown', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByText('TRK-000001')).toBeInTheDocument()
    })

    // Check for status filter
    const statusSelect = screen.getByDisplayValue('All Status')
    expect(statusSelect).toBeInTheDocument()
  })

  it('triggers export when Export button is clicked', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument()
    })

    const exportButton = screen.getByRole('button', { name: /export/i })
    fireEvent.click(exportButton)

    expect(global.alert).toHaveBeenCalledWith('Exporting deliveries to Excel...')
  })

  it('opens modal when Add Delivery button is clicked', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add delivery/i })).toBeInTheDocument()
    })

    const addButton = screen.getByRole('button', { name: /add delivery/i })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText('Add New Delivery')).toBeInTheDocument()
    })
  })

  it('displays COD amounts correctly', async () => {
    render(<Deliveries />)

    await waitFor(() => {
      expect(screen.getByText('$150.00')).toBeInTheDocument()
      expect(screen.getByText('$75.50')).toBeInTheDocument()
    })
  })
})
