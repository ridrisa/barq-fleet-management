import { Suspense } from 'react'
import { useRoutes, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './stores/authStore'
import { routes } from './router/routes'
import { ErrorBoundary } from './components/ErrorBoundary'
import { LoadingScreen } from './components/ui/Spinner'
import { OrganizationProvider } from './contexts/OrganizationContext'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function AppRoutes() {
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
  return (
    <ErrorBoundary>
      <OrganizationProvider>
        <Toaster />
        <AppRoutes />
      </OrganizationProvider>
    </ErrorBoundary>
  )
}

export default App
