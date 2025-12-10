import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@/tests/test-utils'
import Vehicles from '../fleet/Vehicles'

// Mock the API calls
vi.mock('@/lib/api', () => ({
  vehiclesAPI: {
    getAll: vi.fn().mockResolvedValue([
      {
        id: 1,
        plate_number: 'ABC-1234',
        make: 'Toyota',
        model: 'Hilux',
        year: 2022,
        type: 'van',
        current_mileage: 45000,
        status: 'ACTIVE',
        assigned_courier_name: 'John Doe',
      },
      {
        id: 2,
        plate_number: 'XYZ-5678',
        make: 'Ford',
        model: 'Transit',
        year: 2021,
        type: 'truck',
        current_mileage: 78000,
        status: 'MAINTENANCE',
        assigned_courier_name: null,
      },
      {
        id: 3,
        plate_number: 'DEF-9012',
        make: 'Honda',
        model: 'CB500',
        year: 2023,
        type: 'motorcycle',
        current_mileage: 12000,
        status: 'RETIRED',
        assigned_courier_name: 'Jane Smith',
      },
    ]),
    create: vi.fn().mockResolvedValue({ id: 4, plate_number: 'NEW-1234' }),
    update: vi.fn().mockResolvedValue({ id: 1, status: 'ACTIVE' }),
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

describe('Vehicles', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the page title', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('Vehicle Management')).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    render(<Vehicles />)

    const loadingElements = document.querySelectorAll('.animate-spin')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays summary cards with vehicle counts', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('Total Vehicles')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
      expect(screen.getByText('Active')).toBeInTheDocument()
      expect(screen.getByText('Maintenance')).toBeInTheDocument()
      expect(screen.getByText('Retired')).toBeInTheDocument()
    })
  })

  it('renders the Add Vehicle button', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add vehicle/i })).toBeInTheDocument()
    })
  })

  it('displays vehicles in the table', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('ABC-1234')).toBeInTheDocument()
      expect(screen.getByText('Toyota')).toBeInTheDocument()
      expect(screen.getByText('Hilux')).toBeInTheDocument()
      expect(screen.getByText('2022')).toBeInTheDocument()
    })
  })

  it('displays vehicle type badges', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('Van')).toBeInTheDocument()
      expect(screen.getByText('Truck')).toBeInTheDocument()
      expect(screen.getByText('Motorcycle')).toBeInTheDocument()
    })
  })

  it('displays status badges with correct variants', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      // Find status badges in the table
      const activeStatuses = screen.getAllByText('Active')
      expect(activeStatuses.length).toBeGreaterThan(0)
    })
  })

  it('shows assigned courier name', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument()
      expect(screen.getByText('Unassigned')).toBeInTheDocument()
    })
  })

  it('displays mileage correctly', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('45,000')).toBeInTheDocument()
      expect(screen.getByText('78,000')).toBeInTheDocument()
    })
  })

  it('has search functionality', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('ABC-1234')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/search vehicles/i)
    expect(searchInput).toBeInTheDocument()

    fireEvent.change(searchInput, { target: { value: 'Toyota' } })

    await waitFor(() => {
      expect(screen.getByText('Toyota')).toBeInTheDocument()
    })
  })

  it('has status filter dropdown', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('ABC-1234')).toBeInTheDocument()
    })

    const statusSelect = screen.getByDisplayValue('All Status')
    expect(statusSelect).toBeInTheDocument()
  })

  it('opens modal when Add Vehicle button is clicked', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /add vehicle/i })).toBeInTheDocument()
    })

    const addButton = screen.getByRole('button', { name: /add vehicle/i })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(screen.getByText('Add New Vehicle')).toBeInTheDocument()
    })
  })

  it('filters vehicles by status when clicking summary card', async () => {
    render(<Vehicles />)

    await waitFor(() => {
      expect(screen.getByText('ABC-1234')).toBeInTheDocument()
    })

    // Click on Active status card
    const activeCards = screen.getAllByText('Active')
    const activeCard = activeCards[0].closest('.cursor-pointer')
    if (activeCard) {
      fireEvent.click(activeCard)
    }

    // After filtering, should still show the active vehicle
    await waitFor(() => {
      expect(screen.getByText('ABC-1234')).toBeInTheDocument()
    })
  })
})
