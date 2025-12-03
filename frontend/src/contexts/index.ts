/**
 * Contexts Module
 *
 * Export all React context providers and hooks.
 */
export {
  OrganizationProvider,
  useOrganization,
  useRequiredOrganization,
  useHasRole,
  withOrganization,
} from './OrganizationContext'

export type {
  Organization,
  OrganizationMembership,
} from '@/stores/organizationStore'
