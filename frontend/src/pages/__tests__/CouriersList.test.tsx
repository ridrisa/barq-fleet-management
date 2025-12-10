import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/tests/test-utils'
import CouriersList from '../fleet/CouriersList'

// Mock the API calls
vi.mock('@/lib/api', () => ({
  couriersAPI: {
    getAll: vi.fn().mockResolvedValue([
      {
        id: 1,
        barq_id: 'BRQ-001',
        full_name: 'John Doe',
        mobile_number: '+966501234567',
        city: 'Riyadh',
        nationality: 'Saudi',
        status: 'ACTIVE',
      },
      {
        id: 2,
        barq_id: 'BRQ-002',
        full_name: 'Jane Smith',
        mobile_number: '+966507654321',
        city: 'Jeddah',
        nationality: 'Egyptian',
        status: 'ON_LEAVE',
      },
      {
        id: 3,
        barq_id: 'BRQ-003',
        full_name: 'Bob Wilson',
        mobile_number: '+966509876543',
        city: 'Dammam',
        nationality: 'Pakistani',
        status: 'TERMINATED',
      },
    ]),
    create: vi.fn().mockResolvedValue({ id: 4, full_name: 'New Courier' }),
    update: vi.fn().mockResolvedValue({ id: 1, full_name: 'Updated Courier' }),
    delete: vi.fn().mockResolvedValue(undefined),
  },
}))

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}))

// Mock react-router-dom
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  }
})

describe('CouriersList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      expect(screen.getByText('nav.couriers')).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    render(<CouriersList />)

    // Check for loading indicator
    const loadingElements = document.querySelectorAll('.animate-spin')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays summary cards with courier counts', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      // Total couriers
      expect(screen.getByText('Total Couriers')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()

      // Active couriers
      expect(screen.getByText('Active')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()

      // On Leave couriers
      expect(screen.getByText('On Leave')).toBeInTheDocument()

      // Terminated couriers
      expect(screen.getByText('Terminated')).toBeInTheDocument()
    })
  })

  it('renders the Add Courier button', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add courier/i })).toBeInTheDocument()
    })
  })

  it('displays couriers in the table', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('BRQ-001')).toBeInTheDocument()
      expect(screen.getByText('Riyadh')).toBeInTheDocument()
    })
  })

  it('filters couriers by search term', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/search couriers/i)
    fireEvent.change(searchInput, { target: { value: 'John' } })

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })
  })

  it('displays status badges with correct variants', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      // Check for Active badge
      const activeBadge = screen.getByText('Active', { selector: 'span' })
      expect(activeBadge).toBeInTheDocument()

      // Check for On Leave badge
      const onLeaveBadge = screen.getByText('On Leave', { selector: 'span' })
      expect(onLeaveBadge).toBeInTheDocument()
    })
  })

  it('shows Clear Filters button when filters are applied', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
    })

    // Initially, Clear Filters should not be visible
    expect(screen.queryByText('Clear Filters')).not.toBeInTheDocument()

    // Apply a status filter by clicking on Active card
    const activeCard = screen.getByText('Active').closest('.cursor-pointer')
    if (activeCard) {
      fireEvent.click(activeCard)
    }

    // Now Clear Filters button should appear
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /clear filters/i })).toBeInTheDocument()
    })
  })

  it('renders pagination component', async () => {
    render(<CouriersList />)

    await waitFor(() => {
      // Check for pagination - look for page info or pagination controls
      expect(screen.getByText(/showing/i)).toBeInTheDocument()
    })
  })
})
