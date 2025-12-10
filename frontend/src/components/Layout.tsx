import { useState, useEffect } from 'react'
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/lib/cn'
import { OrganizationSelector } from '@/components/OrganizationSelector'
import { BottomNav } from '@/components/layouts/BottomNav'
import { useMobile, useLockBodyScroll, useSwipe } from '@/hooks/useMobile'
import {
  Home,
  Truck,
  Users,
  DollarSign,
  Package,
  Building,
  Workflow,
  HeadphonesIcon,
  BarChart3,
  Settings,
  LogOut,
  ChevronDown,
  Menu,
  X,
} from 'lucide-react'

interface NavItem {
  label: string
  path?: string
  icon: React.ReactNode
  children?: NavItem[]
}

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()
  const { i18n } = useTranslation()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [expandedSections, setExpandedSections] = useState<string[]>([])
  const isMobile = useMobile('lg') // < 1024px

  // Lock body scroll when mobile sidebar is open
  useLockBodyScroll(isMobile && isSidebarOpen)

  // Swipe to close sidebar on mobile
  const { onTouchStart, onTouchEnd } = useSwipe(
    () => {
      if (isMobile && isSidebarOpen) {
        setIsSidebarOpen(false)
      }
    },
    undefined,
    undefined,
    undefined,
    50
  )

  // Close sidebar on route change (mobile only)
  useEffect(() => {
    if (isMobile) {
      setIsSidebarOpen(false)
    }
  }, [location.pathname, isMobile])

  // Handle responsive sidebar state
  useEffect(() => {
    if (!isMobile) {
      setIsSidebarOpen(true)
    }
  }, [isMobile])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleSection = (label: string) => {
    setExpandedSections((prev) =>
      prev.includes(label) ? prev.filter((s) => s !== label) : [...prev, label]
    )
  }

  // Streamlined navigation - removed redundant/placeholder pages
  // Original: 120+ pages - Optimized: ~70 pages
  const navItems: NavItem[] = [
    { label: 'Dashboard', path: '/', icon: <Home className="h-5 w-5" /> },
    {
      label: 'Fleet',
      icon: <Truck className="h-5 w-5" />,
      children: [
        { label: 'Couriers', path: '/fleet/couriers', icon: null },
        { label: 'Vehicles', path: '/fleet/vehicles', icon: null },
        { label: 'Live Tracking', path: '/fleet/live-tracking', icon: null },
        { label: 'Assignments', path: '/fleet/assignments', icon: null },
        { label: 'Maintenance', path: '/fleet/maintenance', icon: null },
        { label: 'Performance', path: '/fleet/performance', icon: null },
        { label: 'Documents', path: '/fleet/documents', icon: null },
        { label: 'Vehicle History', path: '/fleet/vehicle-history', icon: null },
      ],
    },
    {
      label: 'HR & Finance',
      icon: <DollarSign className="h-5 w-5" />,
      children: [
        { label: 'Leave Management', path: '/hr/leave', icon: null },
        { label: 'Loans', path: '/hr/loans', icon: null },
        { label: 'Attendance', path: '/hr/attendance', icon: null },
        { label: 'Salary & GOSI', path: '/hr/salary', icon: null },
        { label: 'Payroll', path: '/hr/payroll', icon: null },
        { label: 'Bonuses', path: '/hr/bonuses', icon: null },
        { label: 'Penalties', path: '/hr/penalties', icon: null },
        { label: 'EOS Calculator', path: '/hr/eos', icon: null },
        { label: 'Assets', path: '/hr/assets', icon: null },
        { label: 'Financial Dashboard', path: '/finance/dashboard', icon: null },
        { label: 'Expense Tracking', path: '/finance/expenses', icon: null },
        { label: 'Budget Management', path: '/finance/budget', icon: null },
        { label: 'Tax Reporting', path: '/finance/tax', icon: null },
      ],
    },
    {
      label: 'Operations',
      icon: <Package className="h-5 w-5" />,
      children: [
        { label: 'Dashboard', path: '/ops/dashboard', icon: null },
        { label: 'Deliveries', path: '/ops/deliveries', icon: null },
        { label: 'Delivery Tracking', path: '/ops/delivery-tracking', icon: null },
        { label: 'Scheduled Deliveries', path: '/ops/scheduled-deliveries', icon: null },
        { label: 'Routes', path: '/ops/routes', icon: null },
        { label: 'Zone Management', path: '/ops/zones', icon: null },
        { label: 'COD Management', path: '/ops/cod', icon: null },
        { label: 'Performance Metrics', path: '/ops/performance-metrics', icon: null },
        { label: 'Service Levels (SLA)', path: '/ops/sla', icon: null },
        { label: 'Quality Control', path: '/ops/quality', icon: null },
        { label: 'Incident Reporting', path: '/ops/incident-reporting', icon: null },
        { label: 'Customer Feedback', path: '/ops/feedback', icon: null },
        { label: 'Priority Queue', path: '/ops/priority-queue', icon: null },
        { label: 'Settings', path: '/ops/settings', icon: null },
      ],
    },
    {
      label: 'Accommodation',
      icon: <Building className="h-5 w-5" />,
      children: [
        { label: 'Buildings', path: '/accommodation/buildings', icon: null },
        { label: 'Rooms', path: '/accommodation/rooms', icon: null },
        { label: 'Beds & Assignments', path: '/accommodation/beds', icon: null },
        { label: 'Maintenance', path: '/accommodation/maintenance', icon: null },
        { label: 'Transfer History', path: '/accommodation/transfer-history', icon: null },
      ],
    },
    {
      label: 'Workflows',
      icon: <Workflow className="h-5 w-5" />,
      children: [
        { label: 'Dashboard', path: '/workflows/dashboard', icon: null },
        { label: 'Templates', path: '/workflows/templates', icon: null },
        { label: 'Workflow Builder', path: '/workflows/builder', icon: null },
        { label: 'All Instances', path: '/workflows/instances', icon: null },
        { label: 'Approvals', path: '/workflows/approvals', icon: null },
        { label: 'SLA Tracking', path: '/workflows/sla', icon: null },
        { label: 'Analytics', path: '/workflows/analytics', icon: null },
        { label: 'Settings', path: '/workflows/settings', icon: null },
      ],
    },
    {
      label: 'Support',
      icon: <HeadphonesIcon className="h-5 w-5" />,
      children: [
        { label: 'Tickets', path: '/support/tickets', icon: null },
        { label: 'Knowledge Base', path: '/support/kb', icon: null },
        { label: 'Feedback', path: '/support/feedback', icon: null },
        { label: 'Documentation', path: '/support/docs', icon: null },
        { label: 'Analytics', path: '/support/analytics', icon: null },
      ],
    },
    {
      label: 'Analytics',
      icon: <BarChart3 className="h-5 w-5" />,
      children: [
        { label: 'Dashboard', path: '/analytics/overview', icon: null },
        { label: 'Fleet Analytics', path: '/analytics/fleet', icon: null },
        { label: 'HR Analytics', path: '/analytics/hr', icon: null },
        { label: 'Financial Analytics', path: '/analytics/financial', icon: null },
        { label: 'Operations Analytics', path: '/analytics/operations', icon: null },
        { label: 'Custom Reports', path: '/analytics/custom', icon: null },
        { label: 'Forecasting', path: '/analytics/forecasting', icon: null },
      ],
    },
    {
      label: 'Admin',
      icon: <Users className="h-5 w-5" />,
      children: [
        { label: 'Users', path: '/admin/users', icon: null },
        { label: 'Roles', path: '/admin/roles', icon: null },
        { label: 'Permissions', path: '/admin/permissions', icon: null },
        { label: 'Audit Logs', path: '/admin/audit', icon: null },
        { label: 'Backups', path: '/admin/backups', icon: null },
        { label: 'Integrations', path: '/admin/integrations', icon: null },
        { label: 'API Keys', path: '/admin/api-keys', icon: null },
      ],
    },
    {
      label: 'Settings',
      icon: <Settings className="h-5 w-5" />,
      children: [
        { label: 'Profile', path: '/settings/profile', icon: null },
        { label: 'Organization', path: '/settings/organization', icon: null },
        { label: 'Preferences', path: '/settings/preferences', icon: null },
      ],
    },
  ]

  const renderNavItem = (item: NavItem, level = 0) => {
    const hasChildren = item.children && item.children.length > 0
    const isExpanded = expandedSections.includes(item.label)
    const isActive = item.path === location.pathname

    if (hasChildren) {
      return (
        <div key={item.label}>
          <button
            onClick={() => toggleSection(item.label)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                toggleSection(item.label)
              }
            }}
            aria-expanded={isExpanded}
            aria-label={`${item.label} menu`}
            className={cn(
              'w-full flex items-center justify-between px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
              'text-gray-700 hover:bg-gray-100 active:bg-gray-200',
              // Touch-friendly sizing
              'min-h-[44px]'
            )}
          >
            <div className="flex items-center gap-3">
              {item.icon}
              {item.label}
            </div>
            <ChevronDown
              className={cn(
                'h-4 w-4 transition-transform',
                isExpanded && 'transform rotate-180'
              )}
              aria-hidden="true"
            />
          </button>
          {isExpanded && (
            <div className="ml-4 mt-1 space-y-1">
              {item.children?.map((child) => renderNavItem(child, level + 1))}
            </div>
          )}
        </div>
      )
    }

    return (
      <Link
        key={item.path}
        to={item.path!}
        className={cn(
          'flex items-center gap-3 px-4 py-2.5 text-sm font-medium rounded-lg transition-colors',
          // Touch-friendly sizing
          'min-h-[44px]',
          isActive
            ? 'bg-blue-50 text-blue-600'
            : 'text-gray-700 hover:bg-gray-100 active:bg-gray-200',
          level > 0 && 'pl-8'
        )}
      >
        {item.icon}
        {item.label}
      </Link>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-amber-500 focus:text-gray-900 focus:rounded-lg focus:font-semibold focus:shadow-lg"
      >
        Skip to main content
      </a>

      {/* Mobile Overlay */}
      {isMobile && isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden animate-in fade-in duration-200"
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'bg-white border-r border-gray-200 fixed inset-y-0 left-0 z-50',
          'transition-transform duration-300 ease-in-out',
          // Desktop width
          'w-64',
          // Mobile: slide in/out
          isMobile && !isSidebarOpen && '-translate-x-full',
          // Desktop: always visible when open
          !isMobile && !isSidebarOpen && 'w-0 -translate-x-full'
        )}
        onTouchStart={(e) => onTouchStart(e.nativeEvent)}
        onTouchEnd={(e) => onTouchEnd(e.nativeEvent)}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
            <div className="flex items-center gap-2">
              <img
                src="/images/logo.png"
                alt="SYNC Fleet"
                className="h-10 w-auto"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.nextElementSibling?.classList.remove('hidden');
                }}
              />
              <h1 className="hidden text-xl font-bold text-blue-600">SYNC Fleet</h1>
            </div>
            {/* Mobile close button */}
            <button
              onClick={() => setIsSidebarOpen(false)}
              className={cn(
                'lg:hidden min-w-[44px] min-h-[44px] flex items-center justify-center',
                'text-gray-500 hover:text-gray-700 -mr-2'
              )}
              aria-label="Close menu"
            >
              <X className="h-6 w-6" aria-hidden="true" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-1">
            {navItems.map((item) => renderNavItem(item))}
          </nav>

          {/* User Section */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <Users className="h-5 w-5 text-blue-600" />
                </div>
                <div className="text-sm min-w-0">
                  <p className="font-medium text-gray-900 truncate">{user?.email}</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className={cn(
                  'p-2.5 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors',
                  'min-w-[44px] min-h-[44px] flex items-center justify-center'
                )}
                aria-label="Log out"
              >
                <LogOut className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div
        className={cn(
          'flex-1 transition-all duration-300 min-w-0',
          // Desktop: margin when sidebar is open
          !isMobile && isSidebarOpen && 'lg:ml-64'
        )}
      >
        {/* Header */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center px-4 gap-3 sticky top-0 z-30">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className={cn(
              'p-2.5 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg',
              'text-blue-600 shadow-sm active:scale-95 transition-all',
              'min-w-[44px] min-h-[44px] flex items-center justify-center'
            )}
            aria-label={isSidebarOpen ? 'Close menu' : 'Open menu'}
          >
            <Menu className="h-6 w-6" />
          </button>

          <div className="flex-1" />

          {/* Organization Selector - hide on very small screens */}
          <div className="hidden sm:block">
            <OrganizationSelector />
          </div>

          <button
            onClick={() => i18n.changeLanguage(i18n.language === 'en' ? 'ar' : 'en')}
            className={cn(
              'px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg',
              'min-h-[44px] flex items-center justify-center'
            )}
          >
            {i18n.language === 'en' ? 'AR' : 'EN'}
          </button>
        </header>

        {/* Page Content */}
        <main
          id="main-content"
          className={cn(
            'p-4 sm:p-6',
            // Add bottom padding for mobile bottom nav
            isMobile && 'pb-24'
          )}
        >
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <BottomNav
          onMoreClick={() => setIsSidebarOpen(true)}
        />
      )}
    </div>
  )
}
