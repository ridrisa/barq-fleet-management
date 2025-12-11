import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useOrganizationStore, useCurrentOrganizationId, useRequireRole } from '../organizationStore'
import { renderHook } from '@testing-library/react'

// Mock the API
vi.mock('@/lib/api', () => ({
  organizationAPI: {
    getAll: vi.fn(),
    switch: vi.fn(),
  },
}))

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

const mockOrganization = {
  id: 1,
  name: 'Test Organization',
  slug: 'test-org',
  is_active: true,
  subscription_plan: 'PROFESSIONAL' as const,
  subscription_status: 'ACTIVE' as const,
  max_users: 100,
  max_couriers: 500,
  max_vehicles: 200,
  created_at: '2024-01-01T00:00:00Z',
}

const mockMemberships = [
  {
    organization: mockOrganization,
    role: 'ADMIN' as const,
    is_active: true,
    permissions: { can_manage_users: true, can_view_reports: true } as Record<string, boolean>,
  },
  {
    organization: {
      ...mockOrganization,
      id: 2,
      name: 'Second Organization',
      slug: 'second-org',
    },
    role: 'VIEWER' as const,
    is_active: true,
    permissions: { can_manage_users: false, can_view_reports: true } as Record<string, boolean>,
  },
]

describe('organizationStore', () => {
  beforeEach(() => {
    // Reset the store state
    useOrganizationStore.setState({
      currentOrganization: null,
      currentRole: null,
      organizations: [],
      isLoading: false,
      isSwitching: false,
      error: null,
    })
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have null currentOrganization initially', () => {
      const state = useOrganizationStore.getState()
      expect(state.currentOrganization).toBeNull()
    })

    it('should have null currentRole initially', () => {
      const state = useOrganizationStore.getState()
      expect(state.currentRole).toBeNull()
    })

    it('should have empty organizations array initially', () => {
      const state = useOrganizationStore.getState()
      expect(state.organizations).toEqual([])
    })

    it('should not be loading initially', () => {
      const state = useOrganizationStore.getState()
      expect(state.isLoading).toBe(false)
    })

    it('should not be switching initially', () => {
      const state = useOrganizationStore.getState()
      expect(state.isSwitching).toBe(false)
    })
  })

  describe('setCurrentOrganization', () => {
    it('should set the current organization and role', () => {
      useOrganizationStore.getState().setCurrentOrganization(mockOrganization, 'ADMIN')

      const state = useOrganizationStore.getState()
      expect(state.currentOrganization).toEqual(mockOrganization)
      expect(state.currentRole).toBe('ADMIN')
    })

    it('should clear any existing error', () => {
      useOrganizationStore.setState({ error: 'Previous error' })

      useOrganizationStore.getState().setCurrentOrganization(mockOrganization, 'ADMIN')

      expect(useOrganizationStore.getState().error).toBeNull()
    })
  })

  describe('switchOrganization', () => {
    beforeEach(() => {
      useOrganizationStore.setState({
        organizations: mockMemberships,
        currentOrganization: mockOrganization,
        currentRole: 'ADMIN',
      })
    })

    it('should set switching state when switching starts', async () => {
      const { organizationAPI } = await import('@/lib/api')
      ;(organizationAPI.switch as ReturnType<typeof vi.fn>).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ access_token: 'new-token' }), 100))
      )

      const switchPromise = useOrganizationStore.getState().switchOrganization(2)

      expect(useOrganizationStore.getState().isSwitching).toBe(true)

      await switchPromise
    })

    it('should switch to a different organization successfully', async () => {
      const { organizationAPI } = await import('@/lib/api')
      ;(organizationAPI.switch as ReturnType<typeof vi.fn>).mockResolvedValue({ access_token: 'new-token' })

      await useOrganizationStore.getState().switchOrganization(2)

      const state = useOrganizationStore.getState()
      expect(state.currentOrganization?.id).toBe(2)
      expect(state.currentRole).toBe('VIEWER')
      expect(state.isSwitching).toBe(false)
    })

    it('should update localStorage with new token', async () => {
      const { organizationAPI } = await import('@/lib/api')
      ;(organizationAPI.switch as ReturnType<typeof vi.fn>).mockResolvedValue({ access_token: 'new-token' })

      await useOrganizationStore.getState().switchOrganization(2)

      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'new-token')
    })

    it('should set error if organization not found', async () => {
      await useOrganizationStore.getState().switchOrganization(999)

      expect(useOrganizationStore.getState().error).toBe('Organization not found in your memberships')
    })

    it('should set error if organization is inactive', async () => {
      useOrganizationStore.setState({
        organizations: [
          {
            organization: { ...mockOrganization, id: 3, is_active: false },
            role: 'ADMIN' as const,
            is_active: true,
          },
        ],
      })

      await useOrganizationStore.getState().switchOrganization(3)

      expect(useOrganizationStore.getState().error).toBe('Organization is inactive')
    })

    it('should handle switch API error', async () => {
      const { organizationAPI } = await import('@/lib/api')
      ;(organizationAPI.switch as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Network error'))

      try {
        await useOrganizationStore.getState().switchOrganization(2)
      } catch (e) {
        // Expected to throw
      }

      const state = useOrganizationStore.getState()
      expect(state.error).toBe('Network error')
      expect(state.isSwitching).toBe(false)
    })
  })

  describe('loadOrganizations', () => {
    it('should load organizations successfully', async () => {
      const { organizationAPI } = await import('@/lib/api')
      ;(organizationAPI.getAll as ReturnType<typeof vi.fn>).mockResolvedValue(mockMemberships)

      await useOrganizationStore.getState().loadOrganizations()

      const state = useOrganizationStore.getState()
      expect(state.organizations).toEqual(mockMemberships)
      expect(state.isLoading).toBe(false)
    })

    it('should set first active organization as current if none selected', async () => {
      const { organizationAPI } = await import('@/lib/api')
      ;(organizationAPI.getAll as ReturnType<typeof vi.fn>).mockResolvedValue(mockMemberships)

      await useOrganizationStore.getState().loadOrganizations()

      const state = useOrganizationStore.getState()
      expect(state.currentOrganization).toEqual(mockOrganization)
      expect(state.currentRole).toBe('ADMIN')
    })

    it('should handle load error', async () => {
      const { organizationAPI } = await import('@/lib/api')
      ;(organizationAPI.getAll as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Failed to load'))

      await useOrganizationStore.getState().loadOrganizations()

      const state = useOrganizationStore.getState()
      expect(state.error).toBe('Failed to load')
      expect(state.isLoading).toBe(false)
    })
  })

  describe('clearOrganization', () => {
    it('should clear all organization state', () => {
      useOrganizationStore.setState({
        currentOrganization: mockOrganization,
        currentRole: 'ADMIN',
        organizations: mockMemberships,
        error: 'Some error',
      })

      useOrganizationStore.getState().clearOrganization()

      const state = useOrganizationStore.getState()
      expect(state.currentOrganization).toBeNull()
      expect(state.currentRole).toBeNull()
      expect(state.organizations).toEqual([])
      expect(state.error).toBeNull()
    })
  })

  describe('hasPermission', () => {
    it('should return true for owners', () => {
      useOrganizationStore.setState({
        currentOrganization: mockOrganization,
        currentRole: 'OWNER',
        organizations: mockMemberships,
      })

      expect(useOrganizationStore.getState().hasPermission('any_permission')).toBe(true)
    })

    it('should return true for admins', () => {
      useOrganizationStore.setState({
        currentOrganization: mockOrganization,
        currentRole: 'ADMIN',
        organizations: mockMemberships,
      })

      expect(useOrganizationStore.getState().hasPermission('any_permission')).toBe(true)
    })

    it('should check specific permission for non-admin roles', () => {
      useOrganizationStore.setState({
        currentOrganization: { ...mockOrganization, id: 2 },
        currentRole: 'VIEWER',
        organizations: mockMemberships,
      })

      expect(useOrganizationStore.getState().hasPermission('can_view_reports')).toBe(true)
      expect(useOrganizationStore.getState().hasPermission('can_manage_users')).toBe(false)
    })

    it('should return false if no organization is selected', () => {
      expect(useOrganizationStore.getState().hasPermission('any_permission')).toBe(false)
    })
  })

  describe('isOwnerOrAdmin', () => {
    it('should return true for OWNER role', () => {
      useOrganizationStore.setState({ currentRole: 'OWNER' })
      expect(useOrganizationStore.getState().isOwnerOrAdmin()).toBe(true)
    })

    it('should return true for ADMIN role', () => {
      useOrganizationStore.setState({ currentRole: 'ADMIN' })
      expect(useOrganizationStore.getState().isOwnerOrAdmin()).toBe(true)
    })

    it('should return false for MANAGER role', () => {
      useOrganizationStore.setState({ currentRole: 'MANAGER' })
      expect(useOrganizationStore.getState().isOwnerOrAdmin()).toBe(false)
    })

    it('should return false for VIEWER role', () => {
      useOrganizationStore.setState({ currentRole: 'VIEWER' })
      expect(useOrganizationStore.getState().isOwnerOrAdmin()).toBe(false)
    })

    it('should return false when no role is set', () => {
      expect(useOrganizationStore.getState().isOwnerOrAdmin()).toBe(false)
    })
  })
})

describe('useCurrentOrganizationId', () => {
  beforeEach(() => {
    useOrganizationStore.setState({
      currentOrganization: null,
      currentRole: null,
      organizations: [],
    })
  })

  it('should return null when no organization is selected', () => {
    const { result } = renderHook(() => useCurrentOrganizationId())
    expect(result.current).toBeNull()
  })

  it('should return organization id when organization is selected', () => {
    useOrganizationStore.setState({
      currentOrganization: mockOrganization,
    })

    const { result } = renderHook(() => useCurrentOrganizationId())
    expect(result.current).toBe(1)
  })
})

describe('useRequireRole', () => {
  beforeEach(() => {
    useOrganizationStore.setState({
      currentOrganization: null,
      currentRole: null,
    })
  })

  it('should return false when no role is set', () => {
    const { result } = renderHook(() => useRequireRole(['ADMIN']))
    expect(result.current).toBe(false)
  })

  it('should return true when user has required role', () => {
    useOrganizationStore.setState({ currentRole: 'ADMIN' })

    const { result } = renderHook(() => useRequireRole(['ADMIN', 'OWNER']))
    expect(result.current).toBe(true)
  })

  it('should return false when user does not have required role', () => {
    useOrganizationStore.setState({ currentRole: 'VIEWER' })

    const { result } = renderHook(() => useRequireRole(['ADMIN', 'OWNER']))
    expect(result.current).toBe(false)
  })

  it('should work with single role requirement', () => {
    useOrganizationStore.setState({ currentRole: 'MANAGER' })

    const { result } = renderHook(() => useRequireRole(['MANAGER']))
    expect(result.current).toBe(true)
  })
})
