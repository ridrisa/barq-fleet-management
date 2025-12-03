/**
 * Organization Context Provider
 *
 * React context for multi-tenant organization management.
 * Provides organization context to all components in the app tree.
 *
 * Features:
 * - Automatic organization loading on mount
 * - Organization switching with token refresh
 * - Role-based access control helpers
 * - Subscription status checks
 */
import {
  createContext,
  useContext,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react'
import {
  useOrganizationStore,
  Organization,
  OrganizationMembership,
} from '@/stores/organizationStore'
import { useAuthStore } from '@/stores/authStore'

/**
 * Organization context value type
 */
interface OrganizationContextValue {
  // Current organization
  organization: Organization | null
  organizationId: number | null
  role: string | null

  // Organization list
  organizations: OrganizationMembership[]

  // Loading states
  isLoading: boolean
  isSwitching: boolean
  error: string | null

  // Actions
  switchOrganization: (organizationId: number) => Promise<void>
  refreshOrganizations: () => Promise<void>

  // Permission helpers
  hasPermission: (permission: string) => boolean
  isOwnerOrAdmin: boolean
  isOwner: boolean
  isAdmin: boolean
  isManager: boolean

  // Subscription helpers
  isPaidPlan: boolean
  isEnterprise: boolean
  isTrialExpired: boolean

  // Limit helpers
  canAddUser: (currentCount: number) => boolean
  canAddCourier: (currentCount: number) => boolean
  canAddVehicle: (currentCount: number) => boolean
}

/**
 * Create the organization context
 */
const OrganizationContext = createContext<OrganizationContextValue | undefined>(
  undefined
)

/**
 * Organization Provider Props
 */
interface OrganizationProviderProps {
  children: ReactNode
}

/**
 * Organization Context Provider Component
 *
 * Wrap your app with this provider to enable multi-tenant functionality.
 *
 * @example
 * ```tsx
 * function App() {
 *   return (
 *     <OrganizationProvider>
 *       <Router />
 *     </OrganizationProvider>
 *   )
 * }
 * ```
 */
export function OrganizationProvider({ children }: OrganizationProviderProps) {
  const { isAuthenticated } = useAuthStore()
  const {
    currentOrganization,
    currentRole,
    organizations,
    isLoading,
    isSwitching,
    error,
    loadOrganizations,
    switchOrganization,
    hasPermission,
    isOwnerOrAdmin,
    clearOrganization,
  } = useOrganizationStore()

  // Load organizations when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadOrganizations()
    } else {
      clearOrganization()
    }
  }, [isAuthenticated, loadOrganizations, clearOrganization])

  // Memoized permission checks
  const isOwner = currentRole === 'OWNER'
  const isAdmin = currentRole === 'ADMIN'
  const isManager = currentRole === 'MANAGER'

  // Subscription helpers
  const isPaidPlan = currentOrganization
    ? currentOrganization.subscription_plan !== 'FREE'
    : false

  const isEnterprise = currentOrganization
    ? currentOrganization.subscription_plan === 'ENTERPRISE'
    : false

  const isTrialExpired = useCallback(() => {
    if (!currentOrganization?.trial_ends_at) return false
    if (currentOrganization.subscription_status !== 'TRIAL') return false
    return new Date(currentOrganization.trial_ends_at) < new Date()
  }, [currentOrganization])

  // Limit helpers
  const canAddUser = useCallback(
    (currentCount: number) => {
      if (!currentOrganization) return false
      return currentCount < currentOrganization.max_users
    },
    [currentOrganization]
  )

  const canAddCourier = useCallback(
    (currentCount: number) => {
      if (!currentOrganization) return false
      return currentCount < currentOrganization.max_couriers
    },
    [currentOrganization]
  )

  const canAddVehicle = useCallback(
    (currentCount: number) => {
      if (!currentOrganization) return false
      return currentCount < currentOrganization.max_vehicles
    },
    [currentOrganization]
  )

  // Context value
  const value: OrganizationContextValue = {
    organization: currentOrganization,
    organizationId: currentOrganization?.id ?? null,
    role: currentRole,
    organizations,
    isLoading,
    isSwitching,
    error,
    switchOrganization,
    refreshOrganizations: loadOrganizations,
    hasPermission,
    isOwnerOrAdmin: isOwnerOrAdmin(),
    isOwner,
    isAdmin,
    isManager,
    isPaidPlan,
    isEnterprise,
    isTrialExpired: isTrialExpired(),
    canAddUser,
    canAddCourier,
    canAddVehicle,
  }

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  )
}

/**
 * Hook to access organization context
 *
 * @throws Error if used outside of OrganizationProvider
 *
 * @example
 * ```tsx
 * function Dashboard() {
 *   const { organization, isOwnerOrAdmin } = useOrganization()
 *
 *   if (!organization) {
 *     return <OrganizationSelector />
 *   }
 *
 *   return (
 *     <div>
 *       <h1>{organization.name} Dashboard</h1>
 *       {isOwnerOrAdmin && <AdminPanel />}
 *     </div>
 *   )
 * }
 * ```
 */
export function useOrganization(): OrganizationContextValue {
  const context = useContext(OrganizationContext)

  if (context === undefined) {
    throw new Error(
      'useOrganization must be used within an OrganizationProvider'
    )
  }

  return context
}

/**
 * Hook to require organization context
 *
 * Returns organization or throws if not available.
 * Use this in components that absolutely require an organization.
 *
 * @throws Error if no organization is selected
 */
export function useRequiredOrganization(): Organization {
  const { organization } = useOrganization()

  if (!organization) {
    throw new Error('Organization context is required but not available')
  }

  return organization
}

/**
 * Hook to check if user has required role in current organization
 *
 * @example
 * ```tsx
 * function AdminPage() {
 *   const canAccess = useHasRole(['OWNER', 'ADMIN'])
 *
 *   if (!canAccess) {
 *     return <AccessDenied />
 *   }
 *
 *   return <AdminContent />
 * }
 * ```
 */
export function useHasRole(
  roles: Array<'OWNER' | 'ADMIN' | 'MANAGER' | 'VIEWER'>
): boolean {
  const { role } = useOrganization()

  if (!role) return false

  return roles.includes(role as 'OWNER' | 'ADMIN' | 'MANAGER' | 'VIEWER')
}

/**
 * Higher-order component to require organization context
 *
 * @example
 * ```tsx
 * const ProtectedPage = withOrganization(MyPage)
 * ```
 */
export function withOrganization<P extends object>(
  WrappedComponent: React.ComponentType<P & { organization: Organization }>
) {
  return function WithOrganizationWrapper(props: P) {
    const { organization, isLoading } = useOrganization()

    if (isLoading) {
      return <div>Loading organization...</div>
    }

    if (!organization) {
      return <div>Please select an organization</div>
    }

    return <WrappedComponent {...props} organization={organization} />
  }
}

export default OrganizationProvider
