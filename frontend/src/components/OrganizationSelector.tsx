/**
 * Organization Selector Component
 *
 * Dropdown component for switching between organizations.
 * Shows current organization and allows switching to other organizations.
 */
import { useState } from 'react'
import { useOrganization } from '@/contexts'
import { cn } from '@/lib/cn'

interface OrganizationSelectorProps {
  className?: string
}

/**
 * Get subscription badge color
 */
function getSubscriptionBadgeColor(
  plan: string
): string {
  switch (plan) {
    case 'ENTERPRISE':
      return 'bg-purple-100 text-purple-800'
    case 'PROFESSIONAL':
      return 'bg-blue-100 text-blue-800'
    case 'BASIC':
      return 'bg-green-100 text-green-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get role badge color
 */
function getRoleBadgeColor(role: string): string {
  switch (role) {
    case 'OWNER':
      return 'bg-amber-100 text-amber-800'
    case 'ADMIN':
      return 'bg-red-100 text-red-800'
    case 'MANAGER':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Organization Selector Dropdown
 */
export function OrganizationSelector({ className }: OrganizationSelectorProps) {
  const {
    organization,
    role,
    organizations,
    isSwitching,
    switchOrganization,
  } = useOrganization()

  const [isOpen, setIsOpen] = useState(false)

  // Don't render if no organizations
  if (organizations.length === 0) {
    return null
  }

  // Single organization - just show the name
  if (organizations.length === 1) {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <span className="text-sm font-semibold text-primary">
              {organization?.name?.charAt(0).toUpperCase() ?? 'O'}
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium">{organization?.name}</span>
            {role && (
              <span
                className={cn(
                  'text-xs px-1.5 py-0.5 rounded-full w-fit',
                  getRoleBadgeColor(role)
                )}
              >
                {role}
              </span>
            )}
          </div>
        </div>
      </div>
    )
  }

  // Multiple organizations - show dropdown
  return (
    <div className={cn('relative', className)}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isSwitching}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg',
          'hover:bg-gray-100 transition-colors',
          'disabled:opacity-50 disabled:cursor-not-allowed'
        )}
      >
        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
          <span className="text-sm font-semibold text-primary">
            {organization?.name?.charAt(0).toUpperCase() ?? 'O'}
          </span>
        </div>
        <div className="flex flex-col items-start">
          <span className="text-sm font-medium">
            {isSwitching ? 'Switching...' : organization?.name}
          </span>
          {role && (
            <span
              className={cn(
                'text-xs px-1.5 py-0.5 rounded-full',
                getRoleBadgeColor(role)
              )}
            >
              {role}
            </span>
          )}
        </div>
        <svg
          className={cn(
            'w-4 h-4 ml-1 transition-transform',
            isOpen && 'rotate-180'
          )}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown menu */}
          <div className="absolute top-full left-0 mt-1 w-72 bg-white rounded-lg shadow-lg border z-20">
            <div className="p-2">
              <p className="text-xs text-gray-500 px-2 py-1 font-medium">
                Switch Organization
              </p>
              {organizations.map((membership) => {
                const isSelected =
                  membership.organization.id === organization?.id
                const isInactive =
                  !membership.organization.is_active || !membership.is_active

                return (
                  <button
                    key={membership.organization.id}
                    onClick={async () => {
                      if (!isSelected && !isInactive) {
                        await switchOrganization(membership.organization.id)
                        setIsOpen(false)
                      }
                    }}
                    disabled={isSelected || isInactive || isSwitching}
                    className={cn(
                      'w-full flex items-center gap-3 px-2 py-2 rounded-md',
                      'hover:bg-gray-50 transition-colors',
                      'disabled:opacity-50 disabled:cursor-not-allowed',
                      isSelected && 'bg-primary/5'
                    )}
                  >
                    <div
                      className={cn(
                        'w-8 h-8 rounded-lg flex items-center justify-center',
                        isSelected ? 'bg-primary/20' : 'bg-gray-100'
                      )}
                    >
                      <span
                        className={cn(
                          'text-sm font-semibold',
                          isSelected ? 'text-primary' : 'text-gray-600'
                        )}
                      >
                        {membership.organization.name.charAt(0).toUpperCase()}
                      </span>
                    </div>

                    <div className="flex-1 flex flex-col items-start">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">
                          {membership.organization.name}
                        </span>
                        {isSelected && (
                          <svg
                            className="w-4 h-4 text-primary"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        )}
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span
                          className={cn(
                            'text-xs px-1.5 py-0.5 rounded-full',
                            getRoleBadgeColor(membership.role)
                          )}
                        >
                          {membership.role}
                        </span>
                        <span
                          className={cn(
                            'text-xs px-1.5 py-0.5 rounded-full',
                            getSubscriptionBadgeColor(
                              membership.organization.subscription_plan
                            )
                          )}
                        >
                          {membership.organization.subscription_plan}
                        </span>
                        {isInactive && (
                          <span className="text-xs px-1.5 py-0.5 rounded-full bg-red-100 text-red-800">
                            Inactive
                          </span>
                        )}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default OrganizationSelector
