import { create } from 'zustand'
import { authAPI } from '@/lib/api'
import { setSentryUser, addSentryBreadcrumb } from '@/lib/sentry'

interface User {
  id: number
  email: string
  full_name?: string
  role: string
  is_active: boolean
  is_superuser: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: (credential: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null })
    try {
      const data = await authAPI.login(email, password)
      localStorage.setItem('token', data.access_token)

      // Load user data
      const user = await authAPI.getCurrentUser()

      // Set Sentry user context for error tracking
      setSentryUser({
        id: user.id.toString(),
        email: user.email,
        username: user.full_name,
      })
      addSentryBreadcrumb({
        category: 'auth',
        message: 'User logged in successfully',
        level: 'info',
        data: { userId: user.id, email: user.email },
      })

      set({
        token: data.access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      addSentryBreadcrumb({
        category: 'auth',
        message: 'Login failed',
        level: 'error',
        data: { error: error.response?.data?.detail || 'Unknown error' },
      })
      set({
        error: error.response?.data?.detail || 'Login failed',
        isLoading: false,
      })
      throw error
    }
  },

  loginWithGoogle: async (credential: string) => {
    set({ isLoading: true, error: null })
    try {
      const data = await authAPI.loginWithGoogle(credential)
      localStorage.setItem('token', data.access_token)

      // Load user data
      const user = await authAPI.getCurrentUser()

      // Set Sentry user context for error tracking
      setSentryUser({
        id: user.id.toString(),
        email: user.email,
        username: user.full_name,
      })
      addSentryBreadcrumb({
        category: 'auth',
        message: 'User logged in via Google',
        level: 'info',
        data: { userId: user.id, email: user.email },
      })

      set({
        token: data.access_token,
        user,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error: any) {
      addSentryBreadcrumb({
        category: 'auth',
        message: 'Google login failed',
        level: 'error',
        data: { error: error.response?.data?.detail || 'Unknown error' },
      })
      set({
        error: error.response?.data?.detail || 'Google login failed',
        isLoading: false,
      })
      throw error
    }
  },

  logout: () => {
    addSentryBreadcrumb({
      category: 'auth',
      message: 'User logged out',
      level: 'info',
    })
    // Clear Sentry user context
    setSentryUser(null)
    localStorage.removeItem('token')
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    })
  },

  loadUser: async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      set({ isAuthenticated: false })
      return
    }

    set({ isLoading: true })
    try {
      const user = await authAPI.getCurrentUser()
      // Set Sentry user context on session restore
      setSentryUser({
        id: user.id.toString(),
        email: user.email,
        username: user.full_name,
      })
      set({
        user,
        token,
        isAuthenticated: true,
        isLoading: false,
      })
    } catch (error) {
      // Clear Sentry user context on session expiry
      setSentryUser(null)
      localStorage.removeItem('token')
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      })
    }
  },

  clearError: () => set({ error: null }),
}))
