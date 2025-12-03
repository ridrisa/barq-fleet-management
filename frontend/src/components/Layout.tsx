import { useState } from 'react'
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/lib/cn'
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

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const toggleSection = (label: string) => {
    setExpandedSections((prev) =>
      prev.includes(label) ? prev.filter((s) => s !== label) : [...prev, label]
    )
  }

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
        { label: 'Fuel Tracking', path: '/fleet/fuel', icon: null },
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
        { label: 'Salary', path: '/hr/salary', icon: null },
        { label: 'Payroll', path: '/hr/payroll', icon: null },
        { label: 'Bonuses', path: '/hr/bonuses', icon: null },
        { label: 'Penalties', path: '/hr/penalties', icon: null },
        { label: 'GOSI', path: '/hr/gosi', icon: null },
        { label: 'EOS Calculator', path: '/hr/eos', icon: null },
        { label: 'Assets', path: '/hr/assets', icon: null },
        { label: 'Financial Dashboard', path: '/finance/dashboard', icon: null },
        { label: 'Financial Reports', path: '/finance/reports', icon: null },
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
        { label: 'Delivery History', path: '/ops/delivery-history', icon: null },
        { label: 'Routes', path: '/ops/routes', icon: null },
        { label: 'Route Optimization', path: '/ops/route-optimization', icon: null },
        { label: 'Zone Management', path: '/ops/zones', icon: null },
        { label: 'COD Management', path: '/ops/cod', icon: null },
        { label: 'COD Reconciliation', path: '/ops/cod-reconciliation', icon: null },
        { label: 'Performance', path: '/ops/performance', icon: null },
        { label: 'Performance Metrics', path: '/ops/performance-metrics', icon: null },
        { label: 'Service Levels (SLA)', path: '/ops/sla', icon: null },
        { label: 'Quality Control', path: '/ops/quality', icon: null },
        { label: 'Incident Reporting', path: '/ops/incident-reporting', icon: null },
        { label: 'Customer Feedback', path: '/ops/feedback', icon: null },
        { label: 'Priority Queue', path: '/ops/priority-queue', icon: null },
        { label: 'Documents', path: '/ops/documents', icon: null },
        { label: 'Settings', path: '/ops/settings', icon: null },
      ],
    },
    {
      label: 'Accommodation',
      icon: <Building className="h-5 w-5" />,
      children: [
        { label: 'Buildings', path: '/accommodation/buildings', icon: null },
        { label: 'Rooms', path: '/accommodation/rooms', icon: null },
        { label: 'Beds', path: '/accommodation/beds', icon: null },
        { label: 'Bed Assignment', path: '/accommodation/bed-assignment', icon: null },
        { label: 'Allocations', path: '/accommodation/allocations', icon: null },
        { label: 'Occupancy', path: '/accommodation/occupancy', icon: null },
        { label: 'Maintenance', path: '/accommodation/maintenance', icon: null },
        { label: 'Maintenance Requests', path: '/accommodation/maintenance-requests', icon: null },
        { label: 'Utilities', path: '/accommodation/utilities', icon: null },
        { label: 'Inventory', path: '/accommodation/inventory', icon: null },
        { label: 'Contracts', path: '/accommodation/contracts', icon: null },
        { label: 'Transfer History', path: '/accommodation/transfer-history', icon: null },
        { label: 'Reports', path: '/accommodation/reports', icon: null },
      ],
    },
    {
      label: 'Workflows',
      icon: <Workflow className="h-5 w-5" />,
      children: [
        { label: 'Dashboard', path: '/workflows/dashboard', icon: null },
        { label: 'Templates', path: '/workflows/templates', icon: null },
        { label: 'Workflow Builder', path: '/workflows/builder', icon: null },
        { label: 'Active Workflows', path: '/workflows/active', icon: null },
        { label: 'Instances', path: '/workflows/instances', icon: null },
        { label: 'Approvals', path: '/workflows/approvals', icon: null },
        { label: 'Pending Approvals', path: '/workflows/pending-approvals', icon: null },
        { label: 'SLA Tracking', path: '/workflows/sla', icon: null },
        { label: 'Automations', path: '/workflows/automations', icon: null },
        { label: 'Triggers', path: '/workflows/triggers', icon: null },
        { label: 'History', path: '/workflows/history', icon: null },
        { label: 'Analytics', path: '/workflows/analytics', icon: null },
        { label: 'Notifications', path: '/workflows/notifications', icon: null },
        { label: 'Settings', path: '/workflows/settings', icon: null },
      ],
    },
    {
      label: 'Support',
      icon: <HeadphonesIcon className="h-5 w-5" />,
      children: [
        { label: 'Tickets', path: '/support/tickets', icon: null },
        { label: 'Knowledge Base', path: '/support/kb', icon: null },
        { label: 'FAQ', path: '/support/faq', icon: null },
        { label: 'Live Chat', path: '/support/chat', icon: null },
        { label: 'Feedback', path: '/support/feedback', icon: null },
        { label: 'Contact Support', path: '/support/contact', icon: null },
        { label: 'Documentation', path: '/support/docs', icon: null },
        { label: 'Support Analytics', path: '/support/analytics', icon: null },
      ],
    },
    {
      label: 'Analytics',
      icon: <BarChart3 className="h-5 w-5" />,
      children: [
        { label: 'Overview', path: '/analytics/overview', icon: null },
        { label: 'KPI Dashboard', path: '/analytics/kpi', icon: null },
        { label: 'Fleet Analytics', path: '/analytics/fleet', icon: null },
        { label: 'HR Analytics', path: '/analytics/hr', icon: null },
        { label: 'Financial Analytics', path: '/analytics/financial', icon: null },
        { label: 'Operations Analytics', path: '/analytics/operations', icon: null },
        { label: 'Courier Performance', path: '/analytics/courier-performance', icon: null },
        { label: 'Delivery Analytics', path: '/analytics/deliveries', icon: null },
        { label: 'Custom Reports', path: '/analytics/custom', icon: null },
        { label: 'Performance Reports', path: '/analytics/performance-reports', icon: null },
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
        { label: 'Monitoring', path: '/admin/monitoring', icon: null },
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
        { label: 'User Settings', path: '/settings/user', icon: null },
        { label: 'Preferences', path: '/settings/preferences', icon: null },
        { label: 'Notifications', path: '/settings/notifications', icon: null },
        { label: 'General Settings', path: '/settings/general', icon: null },
        { label: 'System Settings', path: '/settings/system', icon: null },
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
            className={cn(
              'w-full flex items-center justify-between px-4 py-2 text-sm font-medium rounded-lg transition-colors',
              'text-gray-700 hover:bg-gray-100'
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
          'flex items-center gap-3 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
          isActive
            ? 'bg-blue-50 text-blue-600'
            : 'text-gray-700 hover:bg-gray-100',
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
      {/* Sidebar */}
      <aside
        className={cn(
          'bg-white border-r border-gray-200 fixed inset-y-0 left-0 z-50 transition-transform duration-300',
          isSidebarOpen ? 'w-64' : 'w-0 -translate-x-full'
        )}
      >
        <div className="h-full flex flex-col">
          {/* Logo */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
            <h1 className="text-xl font-bold text-blue-600">BARQ Fleet</h1>
            <button
              onClick={() => setIsSidebarOpen(false)}
              className="lg:hidden"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4 space-y-1">
            {navItems.map((item) => renderNavItem(item))}
          </nav>

          {/* User Section */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <Users className="h-4 w-4 text-blue-600" />
                </div>
                <div className="text-sm">
                  <p className="font-medium text-gray-900">{user?.email}</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className={cn('flex-1 transition-all duration-300', isSidebarOpen && 'lg:ml-64')}>
        {/* Header */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center px-4 gap-4">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2.5 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-blue-600 shadow-sm active:scale-95 transition-all"
            aria-label="Toggle menu"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex-1" />
          <button
            onClick={() => i18n.changeLanguage(i18n.language === 'en' ? 'ar' : 'en')}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            {i18n.language === 'en' ? 'العربية' : 'English'}
          </button>
        </header>

        {/* Page Content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
