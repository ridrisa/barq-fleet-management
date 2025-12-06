import { Link, useLocation } from 'react-router-dom'
import { cn } from '@/lib/cn'
import {
  Home,
  Truck,
  Package,
  Users,
  MoreHorizontal,
} from 'lucide-react'

export interface BottomNavItem {
  label: string
  path: string
  icon: React.ReactNode
  badge?: number | string
}

export interface BottomNavProps {
  items?: BottomNavItem[]
  onMoreClick?: () => void
  className?: string
}

// Default navigation items
const defaultItems: BottomNavItem[] = [
  { label: 'Home', path: '/', icon: <Home className="h-6 w-6" /> },
  { label: 'Fleet', path: '/fleet/couriers', icon: <Truck className="h-6 w-6" /> },
  { label: 'Operations', path: '/ops/deliveries', icon: <Package className="h-6 w-6" /> },
  { label: 'HR', path: '/hr/leave', icon: <Users className="h-6 w-6" /> },
]

export const BottomNav = ({
  items = defaultItems,
  onMoreClick,
  className,
}: BottomNavProps) => {
  const location = useLocation()

  // Check if current path matches or is a child of the nav item path
  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  // Limit to 4 items plus "More"
  const displayItems = items.slice(0, 4)
  const hasMore = items.length > 4 || onMoreClick

  return (
    <nav
      className={cn(
        'fixed bottom-0 left-0 right-0 z-40',
        'bg-white border-t border-gray-200',
        'pb-[env(safe-area-inset-bottom)]',
        'md:hidden', // Only show on mobile
        className
      )}
      role="navigation"
      aria-label="Primary navigation"
    >
      <div className="flex items-stretch justify-around h-16">
        {displayItems.map((item) => {
          const active = isActive(item.path)
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex flex-col items-center justify-center flex-1',
                'min-w-[64px] min-h-[48px] py-1 px-2',
                'transition-colors relative',
                active
                  ? 'text-blue-600'
                  : 'text-gray-500 hover:text-gray-700 active:text-blue-600'
              )}
              aria-current={active ? 'page' : undefined}
            >
              {/* Active indicator */}
              {active && (
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-blue-600 rounded-b-full" />
              )}

              {/* Icon with optional badge */}
              <div className="relative">
                {item.icon}
                {item.badge !== undefined && (
                  <span
                    className={cn(
                      'absolute -top-1 -right-1 min-w-[18px] h-[18px]',
                      'flex items-center justify-center',
                      'text-[10px] font-bold text-white',
                      'bg-red-500 rounded-full px-1'
                    )}
                  >
                    {typeof item.badge === 'number' && item.badge > 99
                      ? '99+'
                      : item.badge}
                  </span>
                )}
              </div>

              {/* Label */}
              <span
                className={cn(
                  'text-[10px] mt-1 font-medium',
                  active && 'font-semibold'
                )}
              >
                {item.label}
              </span>
            </Link>
          )
        })}

        {/* More button */}
        {hasMore && (
          <button
            onClick={onMoreClick}
            className={cn(
              'flex flex-col items-center justify-center flex-1',
              'min-w-[64px] min-h-[48px] py-1 px-2',
              'text-gray-500 hover:text-gray-700 active:text-blue-600',
              'transition-colors'
            )}
            aria-label="More options"
          >
            <MoreHorizontal className="h-6 w-6" />
            <span className="text-[10px] mt-1 font-medium">More</span>
          </button>
        )}
      </div>
    </nav>
  )
}

// Spacer component to prevent content from being hidden behind bottom nav
export const BottomNavSpacer = () => {
  return (
    <div
      className={cn(
        'h-16 md:hidden', // Match bottom nav height, only on mobile
        'pb-[env(safe-area-inset-bottom)]'
      )}
      aria-hidden="true"
    />
  )
}
