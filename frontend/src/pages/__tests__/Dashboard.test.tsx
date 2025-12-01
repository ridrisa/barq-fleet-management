import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@/tests/test-utils'
import Dashboard from '../Dashboard'

// Mock the API calls
vi.mock('@/services/api', () => ({
  dashboardAPI: {
    getSummary: vi.fn().mockResolvedValue({
      totalCouriers: 150,
      activeCouriers: 120,
      totalVehicles: 80,
      activeDeliveries: 45,
      todayDeliveries: 230,
      completedDeliveries: 180,
      pendingDeliveries: 50,
    }),
    getRecentActivity: vi.fn().mockResolvedValue([]),
  },
}))

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard title', async () => {
    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
    })
  })

  it('displays loading state initially', () => {
    render(<Dashboard />)

    // Check for loading indicators (skeletons or spinners)
    const loadingElements = document.querySelectorAll('.animate-pulse, .animate-spin')
    expect(loadingElements.length).toBeGreaterThan(0)
  })

  it('displays summary cards with data', async () => {
    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('150')).toBeInTheDocument() // Total couriers
      expect(screen.getByText('120')).toBeInTheDocument() // Active couriers
      expect(screen.getByText('80')).toBeInTheDocument() // Total vehicles
      expect(screen.getByText('45')).toBeInTheDocument() // Active deliveries
    })
  })

  it('renders summary card titles', async () => {
    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText(/total couriers/i)).toBeInTheDocument()
      expect(screen.getByText(/active couriers/i)).toBeInTheDocument()
      expect(screen.getByText(/total vehicles/i)).toBeInTheDocument()
    })
  })
})
