import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
  }
  return { default: mockAxios }
})

// Mock sentry
vi.mock('@/lib/sentry', () => ({
  addSentryBreadcrumb: vi.fn(),
  captureException: vi.fn(),
}))

// Import the mocked api after setting up mocks
import { api, safeApiCall, authAPI, couriersAPI, vehiclesAPI, deliveriesAPI, leavesAPI } from '../api'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

describe('API Module', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('axios instance', () => {
    it('should create axios instance with correct base config', () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL: expect.any(String),
        headers: {
          'Content-Type': 'application/json',
        },
      })
    })

    it('should set up request interceptor', () => {
      expect(api.interceptors.request.use).toHaveBeenCalled()
    })

    it('should set up response interceptor', () => {
      expect(api.interceptors.response.use).toHaveBeenCalled()
    })
  })

  describe('safeApiCall', () => {
    it('should return data on successful API call', async () => {
      const mockData = { id: 1, name: 'Test' }
      const apiCall = vi.fn().mockResolvedValue(mockData)

      const result = await safeApiCall(apiCall, { fallback: true })

      expect(result).toEqual(mockData)
      expect(apiCall).toHaveBeenCalled()
    })

    it('should return fallback on 404 error', async () => {
      const fallbackData = { fallback: true }
      const apiCall = vi.fn().mockRejectedValue({ response: { status: 404 } })

      const result = await safeApiCall(apiCall, fallbackData)

      expect(result).toEqual(fallbackData)
    })

    it('should throw error on non-404 errors', async () => {
      const apiCall = vi.fn().mockRejectedValue({ response: { status: 500 } })

      await expect(safeApiCall(apiCall, {})).rejects.toEqual({ response: { status: 500 } })
    })
  })

  describe('authAPI', () => {
    describe('login', () => {
      it('should send login request with form data', async () => {
        const mockResponse = { data: { access_token: 'test-token' } }
        ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse)

        const result = await authAPI.login('test@example.com', 'password')

        expect(api.post).toHaveBeenCalledWith(
          '/auth/login',
          expect.any(URLSearchParams),
          expect.objectContaining({
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          })
        )
        expect(result).toEqual({ access_token: 'test-token' })
      })
    })

    describe('getCurrentUser', () => {
      it('should fetch current user', async () => {
        const mockUser = { id: 1, email: 'test@example.com' }
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockUser })

        const result = await authAPI.getCurrentUser()

        expect(api.get).toHaveBeenCalledWith('/auth/me')
        expect(result).toEqual(mockUser)
      })
    })

    describe('loginWithGoogle', () => {
      it('should send Google login request', async () => {
        const mockResponse = { data: { access_token: 'google-token' } }
        ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue(mockResponse)

        const result = await authAPI.loginWithGoogle('google-credential')

        expect(api.post).toHaveBeenCalledWith('/auth/google', { credential: 'google-credential' })
        expect(result).toEqual({ access_token: 'google-token' })
      })
    })
  })

  describe('couriersAPI', () => {
    describe('getAll', () => {
      it('should fetch all couriers with default limit', async () => {
        const mockCouriers = [{ id: 1, name: 'Courier 1' }]
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockCouriers })

        const result = await couriersAPI.getAll()

        expect(api.get).toHaveBeenCalledWith('/fleet/couriers?limit=2000')
        expect(result).toEqual(mockCouriers)
      })

      it('should fetch couriers with pagination params', async () => {
        const mockCouriers = [{ id: 1, name: 'Courier 1' }]
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockCouriers })

        await couriersAPI.getAll(10, 50)

        expect(api.get).toHaveBeenCalledWith('/fleet/couriers?skip=10&limit=50')
      })
    })

    describe('getById', () => {
      it('should fetch courier by id', async () => {
        const mockCourier = { id: 1, name: 'Courier 1' }
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockCourier })

        const result = await couriersAPI.getById(1)

        expect(api.get).toHaveBeenCalledWith('/fleet/couriers/1')
        expect(result).toEqual(mockCourier)
      })
    })

    describe('create', () => {
      it('should create a new courier', async () => {
        const newCourier = { name: 'New Courier', mobile_number: '+966501234567' }
        const mockResponse = { id: 1, ...newCourier }
        ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse })

        const result = await couriersAPI.create(newCourier)

        expect(api.post).toHaveBeenCalledWith('/fleet/couriers', newCourier)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('update', () => {
      it('should update a courier', async () => {
        const updateData = { name: 'Updated Courier' }
        const mockResponse = { id: 1, name: 'Updated Courier' }
        ;(api.put as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse })

        const result = await couriersAPI.update(1, updateData)

        expect(api.put).toHaveBeenCalledWith('/fleet/couriers/1', updateData)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('delete', () => {
      it('should delete a courier', async () => {
        ;(api.delete as ReturnType<typeof vi.fn>).mockResolvedValue({ data: {} })

        await couriersAPI.delete(1)

        expect(api.delete).toHaveBeenCalledWith('/fleet/couriers/1')
      })
    })
  })

  describe('vehiclesAPI', () => {
    describe('getAll', () => {
      it('should fetch all vehicles', async () => {
        const mockVehicles = [{ id: 1, plate_number: 'ABC-1234' }]
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockVehicles })

        const result = await vehiclesAPI.getAll()

        expect(api.get).toHaveBeenCalledWith('/fleet/vehicles')
        expect(result).toEqual(mockVehicles)
      })
    })

    describe('getById', () => {
      it('should fetch vehicle by id', async () => {
        const mockVehicle = { id: 1, plate_number: 'ABC-1234' }
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockVehicle })

        const result = await vehiclesAPI.getById(1)

        expect(api.get).toHaveBeenCalledWith('/fleet/vehicles/1')
        expect(result).toEqual(mockVehicle)
      })
    })

    describe('create', () => {
      it('should create a new vehicle', async () => {
        const newVehicle = { plate_number: 'ABC-1234', make: 'Toyota' }
        const mockResponse = { id: 1, ...newVehicle }
        ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse })

        const result = await vehiclesAPI.create(newVehicle)

        expect(api.post).toHaveBeenCalledWith('/fleet/vehicles', newVehicle)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('update', () => {
      it('should update a vehicle', async () => {
        const updateData = { status: 'MAINTENANCE' }
        const mockResponse = { id: 1, status: 'MAINTENANCE' }
        ;(api.put as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse })

        const result = await vehiclesAPI.update(1, updateData)

        expect(api.put).toHaveBeenCalledWith('/fleet/vehicles/1', updateData)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('delete', () => {
      it('should delete a vehicle', async () => {
        ;(api.delete as ReturnType<typeof vi.fn>).mockResolvedValue({ data: {} })

        await vehiclesAPI.delete(1)

        expect(api.delete).toHaveBeenCalledWith('/fleet/vehicles/1')
      })
    })
  })

  describe('deliveriesAPI', () => {
    describe('getAll', () => {
      it('should fetch all deliveries', async () => {
        const mockDeliveries = [{ id: 1, tracking_number: 'TRK-001' }]
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockDeliveries })

        const result = await deliveriesAPI.getAll()

        expect(api.get).toHaveBeenCalledWith('/operations/deliveries')
        expect(result).toEqual(mockDeliveries)
      })
    })

    describe('create', () => {
      it('should create a new delivery', async () => {
        const newDelivery = { customer_name: 'John Doe', delivery_address: '123 Main St' }
        const mockResponse = { id: 1, ...newDelivery }
        ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse })

        const result = await deliveriesAPI.create(newDelivery)

        expect(api.post).toHaveBeenCalledWith('/operations/deliveries', newDelivery)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('track', () => {
      it('should track a delivery', async () => {
        const mockTracking = { status: 'in_transit', location: { lat: 24.7, lng: 46.7 } }
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockTracking })

        const result = await deliveriesAPI.track(1)

        expect(api.get).toHaveBeenCalledWith('/operations/deliveries/1/track')
        expect(result).toEqual(mockTracking)
      })
    })
  })

  describe('leavesAPI', () => {
    describe('getAll', () => {
      it('should fetch all leaves', async () => {
        const mockLeaves = [{ id: 1, leave_type: 'annual' }]
        ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockLeaves })

        const result = await leavesAPI.getAll()

        expect(api.get).toHaveBeenCalledWith('/hr/leave/')
        expect(result).toEqual(mockLeaves)
      })
    })

    describe('create', () => {
      it('should create a new leave request', async () => {
        const newLeave = { leave_type: 'annual', start_date: '2024-01-15', end_date: '2024-01-20' }
        const mockResponse = { id: 1, ...newLeave }
        ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse })

        const result = await leavesAPI.create(newLeave)

        expect(api.post).toHaveBeenCalledWith('/hr/leave/', newLeave)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('update', () => {
      it('should update a leave request', async () => {
        const updateData = { status: 'approved' }
        const mockResponse = { id: 1, status: 'approved' }
        ;(api.put as ReturnType<typeof vi.fn>).mockResolvedValue({ data: mockResponse })

        const result = await leavesAPI.update(1, updateData)

        expect(api.put).toHaveBeenCalledWith('/hr/leave/1', updateData)
        expect(result).toEqual(mockResponse)
      })
    })

    describe('delete', () => {
      it('should delete a leave request', async () => {
        ;(api.delete as ReturnType<typeof vi.fn>).mockResolvedValue({ data: {} })

        await leavesAPI.delete(1)

        expect(api.delete).toHaveBeenCalledWith('/hr/leave/1')
      })
    })
  })
})
