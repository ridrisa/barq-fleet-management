/**
 * Organization Store
 *
 * Zustand store for managing multi-tenant organization context.
 * Handles organization selection, switching, and persistence.
 *
 * The organization context is embedded in JWT tokens for backend
 * authentication and is also used for frontend routing/filtering.
 */
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { organizationAPI } from '@/lib/api'

/**
 * Organization interface matching backend model
 */
export interface Organization {
  id: number
  name: string
  slug: string
  is_active: boolean
  subscription_plan: 'FREE' | 'BASIC' | 'PROFESSIONAL' | 'ENTERPRISE'
  subscription_status: 'TRIAL' | 'ACTIVE' | 'SUSPENDED' | 'CANCELLED'
  max_users: number
  max_couriers: number
  max_vehicles: number
  trial_ends_at?: string
  settings?: Record<string, unknown>
  created_at: string
  updated_at?: string
}

/**
 * Organization membership with role
 */
export interface OrganizationMembership {
  organization: Organization
  role: 'OWNER' | 'ADMIN' | 'MANAGER' | 'VIEWER'
  is_active: boolean
  permissions?: Record<string, boolean>
}

/**
 * Organization store state and actions
 */
interface OrganizationState {
  // Current organization context
  currentOrganization: Organization | null
  currentRole: string | null

  // List of organizations user belongs to
  organizations: OrganizationMembership[]

  // Loading states
  isLoading: boolean
  isSwitching: boolean
  error: string | null

  // Actions
  setCurrentOrganization: (org: Organization, role: string) => void
  switchOrganization: (organizationId: number) => Promise<void>
  loadOrganizations: () => Promise<void>
  clearOrganization: () => void
  hasPermission: (permission: string) => boolean
  isOwnerOrAdmin: () => boolean
}

/**
 * Organization store with persistence
 *
 * The current organization is persisted to localStorage so users
 * don't need to re-select their organization on each visit.
 */
export const useOrganizationStore = create<OrganizationState>()(
  persist(
    (set, get) => ({
      currentOrganization: null,
      currentRole: null,
      organizations: [],
      isLoading: false,
      isSwitching: false,
      error: null,

      /**
       * Set the current organization context
       */
      setCurrentOrganization: (org: Organization, role: string) => {
        set({
          currentOrganization: org,
          currentRole: role,
          error: null,
        })
      },

      /**
       * Switch to a different organization
       *
       * This will:
       * 1. Request a new JWT token with the organization context
       * 2. Update the stored token
       * 3. Update the current organization state
       */
      switchOrganization: async (organizationId: number) => {
        const { organizations } = get()

        // Find the organization in user's memberships
        const membership = organizations.find(
          (m) => m.organization.id === organizationId
        )

        if (!membership) {
          set({ error: 'Organization not found in your memberships' })
          return
        }

        if (!membership.organization.is_active) {
          set({ error: 'Organization is inactive' })
          return
        }

        set({ isSwitching: true, error: null })

        try {
          // Request new token with organization context
          const response = await organizationAPI.switch(organizationId)

          // Update stored token
          localStorage.setItem('token', response.access_token)

          // Update organization state
          set({
            currentOrganization: membership.organization,
            currentRole: membership.role,
            isSwitching: false,
          })
        } catch (error: unknown) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to switch organization'
          set({
            error: errorMessage,
            isSwitching: false,
          })
          throw error
        }
      },

      /**
       * Load all organizations the user belongs to
       */
      loadOrganizations: async () => {
        set({ isLoading: true, error: null })

        try {
          const memberships = await organizationAPI.getAll()

          set({
            organizations: memberships,
            isLoading: false,
          })

          // If no current organization is set, use the first active one
          const { currentOrganization } = get()
          if (!currentOrganization && memberships.length > 0) {
            const activeMembership = memberships.find(
              (m: OrganizationMembership) => m.organization.is_active && m.is_active
            )
            if (activeMembership) {
              set({
                currentOrganization: activeMembership.organization,
                currentRole: activeMembership.role,
              })
            }
          }
        } catch (error: unknown) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to load organizations'
          set({
            error: errorMessage,
            isLoading: false,
          })
        }
      },

      /**
       * Clear organization context (on logout)
       */
      clearOrganization: () => {
        set({
          currentOrganization: null,
          currentRole: null,
          organizations: [],
          error: null,
        })
      },

      /**
       * Check if user has a specific permission in current organization
       */
      hasPermission: (permission: string) => {
        const { currentOrganization, currentRole, organizations } = get()

        if (!currentOrganization || !currentRole) return false

        // Owners and admins have all permissions
        if (currentRole === 'OWNER' || currentRole === 'ADMIN') return true

        // Check custom permissions
        const membership = organizations.find(
          (m) => m.organization.id === currentOrganization.id
        )

        return membership?.permissions?.[permission] === true
      },

      /**
       * Check if user is owner or admin of current organization
       */
      isOwnerOrAdmin: () => {
        const { currentRole } = get()
        return currentRole === 'OWNER' || currentRole === 'ADMIN'
      },
    }),
    {
      name: 'organization-storage',
      partialize: (state) => ({
        currentOrganization: state.currentOrganization,
        currentRole: state.currentRole,
      }),
    }
  )
)

/**
 * Hook to get current organization ID (convenience)
 */
export const useCurrentOrganizationId = (): number | null => {
  const currentOrganization = useOrganizationStore((state) => state.currentOrganization)
  return currentOrganization?.id ?? null
}

/**
 * Hook to check if user has required role
 */
export const useRequireRole = (
  requiredRoles: Array<'OWNER' | 'ADMIN' | 'MANAGER' | 'VIEWER'>
): boolean => {
  const currentRole = useOrganizationStore((state) => state.currentRole)
  if (!currentRole) return false
  return requiredRoles.includes(currentRole as 'OWNER' | 'ADMIN' | 'MANAGER' | 'VIEWER')
}
