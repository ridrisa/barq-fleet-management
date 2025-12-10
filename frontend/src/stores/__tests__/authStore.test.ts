import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useAuthStore } from '../authStore'

// Mock the API
vi.mock('@/lib/api', () => ({
  authAPI: {
    login: vi.fn(),
    getCurrentUser: vi.fn(),
    loginWithGoogle: vi.fn(),
  },
}))

// Mock Sentry
vi.mock('@/lib/sentry', () => ({
  setSentryUser: vi.fn(),
  addSentryBreadcrumb: vi.fn(),
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

describe('authStore', () => {
  beforeEach(() => {
    // Reset the store state
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
    vi.clearAllMocks()
    localStorageMock.clear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have null user initially', () => {
      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
    })

    it('should not be authenticated initially', () => {
      const state = useAuthStore.getState()
      expect(state.isAuthenticated).toBe(false)
    })

    it('should not be loading initially', () => {
      const state = useAuthStore.getState()
      expect(state.isLoading).toBe(false)
    })

    it('should have no error initially', () => {
      const state = useAuthStore.getState()
      expect(state.error).toBeNull()
    })
  })

  describe('login', () => {
    it('should set loading state when login starts', async () => {
      const { authAPI } = await import('@/lib/api')
      ;(authAPI.login as ReturnType<typeof vi.fn>).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ access_token: 'test-token' }), 100))
      )
      ;(authAPI.getCurrentUser as ReturnType<typeof vi.fn>).mockResolvedValue({
        id: 1,
        email: 'test@example.com',
        role: 'admin',
        is_active: true,
        is_superuser: false,
      })

      const loginPromise = useAuthStore.getState().login('test@example.com', 'password')

      // Check loading state
      expect(useAuthStore.getState().isLoading).toBe(true)

      await loginPromise
    })

    it('should set user and token after successful login', async () => {
      const { authAPI } = await import('@/lib/api')
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin',
        is_active: true,
        is_superuser: false,
      }

      ;(authAPI.login as ReturnType<typeof vi.fn>).mockResolvedValue({ access_token: 'test-token' })
      ;(authAPI.getCurrentUser as ReturnType<typeof vi.fn>).mockResolvedValue(mockUser)

      await useAuthStore.getState().login('test@example.com', 'password')

      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockUser)
      expect(state.token).toBe('test-token')
      expect(state.isAuthenticated).toBe(true)
      expect(state.isLoading).toBe(false)
    })

    it('should store token in localStorage after successful login', async () => {
      const { authAPI } = await import('@/lib/api')
      ;(authAPI.login as ReturnType<typeof vi.fn>).mockResolvedValue({ access_token: 'test-token' })
      ;(authAPI.getCurrentUser as ReturnType<typeof vi.fn>).mockResolvedValue({
        id: 1,
        email: 'test@example.com',
        role: 'admin',
        is_active: true,
        is_superuser: false,
      })

      await useAuthStore.getState().login('test@example.com', 'password')

      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'test-token')
    })

    it('should set error state on login failure', async () => {
      const { authAPI } = await import('@/lib/api')
      ;(authAPI.login as ReturnType<typeof vi.fn>).mockRejectedValue({
        response: { data: { detail: 'Invalid credentials' } },
      })

      try {
        await useAuthStore.getState().login('test@example.com', 'wrong-password')
      } catch (e) {
        // Expected to throw
      }

      const state = useAuthStore.getState()
      expect(state.error).toBe('Invalid credentials')
      expect(state.isLoading).toBe(false)
      expect(state.isAuthenticated).toBe(false)
    })
  })

  describe('loginWithGoogle', () => {
    it('should authenticate user with Google credential', async () => {
      const { authAPI } = await import('@/lib/api')
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin',
        is_active: true,
        is_superuser: false,
      }

      ;(authAPI.loginWithGoogle as ReturnType<typeof vi.fn>).mockResolvedValue({ access_token: 'google-token' })
      ;(authAPI.getCurrentUser as ReturnType<typeof vi.fn>).mockResolvedValue(mockUser)

      await useAuthStore.getState().loginWithGoogle('google-credential')

      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockUser)
      expect(state.token).toBe('google-token')
      expect(state.isAuthenticated).toBe(true)
    })

    it('should set error on Google login failure', async () => {
      const { authAPI } = await import('@/lib/api')
      ;(authAPI.loginWithGoogle as ReturnType<typeof vi.fn>).mockRejectedValue({
        response: { data: { detail: 'Google login failed' } },
      })

      try {
        await useAuthStore.getState().loginWithGoogle('invalid-credential')
      } catch (e) {
        // Expected to throw
      }

      const state = useAuthStore.getState()
      expect(state.error).toBe('Google login failed')
      expect(state.isAuthenticated).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear user and token on logout', async () => {
      // First, set up an authenticated state
      useAuthStore.setState({
        user: { id: 1, email: 'test@example.com', role: 'admin', is_active: true, is_superuser: false },
        token: 'test-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })

      useAuthStore.getState().logout()

      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.token).toBeNull()
      expect(state.isAuthenticated).toBe(false)
    })

    it('should remove token from localStorage on logout', () => {
      useAuthStore.setState({
        user: { id: 1, email: 'test@example.com', role: 'admin', is_active: true, is_superuser: false },
        token: 'test-token',
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })

      useAuthStore.getState().logout()

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token')
    })

    it('should clear any existing error on logout', () => {
      useAuthStore.setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Some previous error',
      })

      useAuthStore.getState().logout()

      const state = useAuthStore.getState()
      expect(state.error).toBeNull()
    })
  })

  describe('loadUser', () => {
    it('should load user from token in localStorage', async () => {
      const { authAPI } = await import('@/lib/api')
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin',
        is_active: true,
        is_superuser: false,
      }

      localStorageMock.setItem('token', 'existing-token')
      ;(authAPI.getCurrentUser as ReturnType<typeof vi.fn>).mockResolvedValue(mockUser)

      // Reset state to simulate fresh load
      useAuthStore.setState({
        user: null,
        token: 'existing-token',
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })

      await useAuthStore.getState().loadUser()

      const state = useAuthStore.getState()
      expect(state.user).toEqual(mockUser)
      expect(state.isAuthenticated).toBe(true)
    })

    it('should clear state if token is invalid', async () => {
      const { authAPI } = await import('@/lib/api')
      localStorageMock.setItem('token', 'invalid-token')
      ;(authAPI.getCurrentUser as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('Invalid token'))

      useAuthStore.setState({
        user: null,
        token: 'invalid-token',
        isAuthenticated: false,
        isLoading: false,
        error: null,
      })

      await useAuthStore.getState().loadUser()

      const state = useAuthStore.getState()
      expect(state.user).toBeNull()
      expect(state.isAuthenticated).toBe(false)
    })

    it('should not attempt to load if no token exists', async () => {
      const { authAPI } = await import('@/lib/api')

      await useAuthStore.getState().loadUser()

      expect(authAPI.getCurrentUser).not.toHaveBeenCalled()
      expect(useAuthStore.getState().isAuthenticated).toBe(false)
    })
  })

  describe('clearError', () => {
    it('should clear the error state', () => {
      useAuthStore.setState({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Some error',
      })

      useAuthStore.getState().clearError()

      expect(useAuthStore.getState().error).toBeNull()
    })
  })
})
