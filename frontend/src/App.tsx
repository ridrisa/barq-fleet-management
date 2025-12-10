import { Suspense, useEffect, useState } from 'react'
import { useRoutes, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './stores/authStore'
import { routes } from './router/routes'
import { ErrorBoundary } from './components/ErrorBoundary'
import { LoadingScreen } from './components/ui/Spinner'
import { OrganizationProvider } from './contexts/OrganizationContext'
import { useNavigationTracking } from './hooks/useNavigationTracking'
import { OnboardingProvider } from './contexts/OnboardingContext'
import { OnboardingSlides, OnboardingTooltip, OnboardingTrigger } from './components/onboarding'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/landing" />
}

/**
 * Hook to initialize auth state on app startup.
 * Validates the token and loads user data if a token exists in localStorage.
 */
function useAuthInitializer() {
  const [isInitialized, setIsInitialized] = useState(false)
  const loadUser = useAuthStore((state) => state.loadUser)
  const token = useAuthStore((state) => state.token)

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        // Validate token and load user data
        await loadUser()
      }
      setIsInitialized(true)
    }
    initAuth()
  }, []) // Only run once on mount

  return isInitialized
}

function AppRoutes() {
  // Track navigation changes in Sentry for debugging
  useNavigationTracking()

  const routing = useRoutes(
    routes.map((route) => {
      // Public routes that don't require authentication
      if (route.path === '/login' || route.path === '/landing') return route
      return {
        ...route,
        element: <PrivateRoute>{route.element}</PrivateRoute>,
      }
    })
  )

  return <Suspense fallback={<LoadingScreen />}>{routing}</Suspense>
}

function App() {
  // Initialize auth state (validate token, load user) before rendering routes
  const isAuthInitialized = useAuthInitializer()

  // Show loading screen until auth is initialized
  if (!isAuthInitialized) {
    return <LoadingScreen />
  }

  return (
    <ErrorBoundary>
      <OrganizationProvider>
        <OnboardingProvider>
          <Toaster />
          <AppRoutes />
          {/* Onboarding Components */}
          <OnboardingSlides />
          <OnboardingTooltip />
          <OnboardingTrigger />
        </OnboardingProvider>
      </OrganizationProvider>
    </ErrorBoundary>
  )
}

export default App
