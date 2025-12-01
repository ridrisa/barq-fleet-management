import { useState } from 'react'
import { KPICard } from '@/components/ui'
import { Button, Select } from '@/components/ui'
import {
  Truck,
  Users,
  Package,
  DollarSign,
  TrendingUp,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3,
  FileText,
  Wrench,
  UserCheck,
  Briefcase,
  Target,
} from 'lucide-react'

export default function KPIDashboard() {
  const [timePeriod, setTimePeriod] = useState('month')
  const [selectedKPIs, setSelectedKPIs] = useState<Set<string>>(new Set([
    'totalVehicles', 'activeVehicles', 'maintenance', 'totalEmployees',
    'attendanceRate', 'leaveBalance', 'deliveriesToday', 'successRate',
    'onTimePercentage', 'revenueMTD', 'expensesMTD', 'profitMargin',
    'codCollected', 'avgDeliveryTime', 'customerSatisfaction', 'fuelEfficiency'
  ]))
  const [layoutMode, setLayoutMode] = useState<'grid' | 'compact'>('grid')

  // Mock KPI data with calculations based on time period
  const kpiData = {
    // Fleet KPIs
    totalVehicles: { value: 80, change: 0, trend: 'up' as const },
    activeVehicles: { value: 42, change: 5.2, trend: 'up' as const },
    maintenance: { value: 8, change: -12.5, trend: 'down' as const },
    fuelEfficiency: { value: '12.5 km/L', change: 3.8, trend: 'up' as const },

    // HR KPIs
    totalEmployees: { value: 156, change: 2.6, trend: 'up' as const },
    attendanceRate: { value: '94.2%', change: 1.5, trend: 'up' as const },
    leaveBalance: { value: '12 days', change: -5.0, trend: 'down' as const },
    activeCouriers: { value: 42, change: 4.8, trend: 'up' as const },

    // Operations KPIs
    deliveriesToday: { value: 223, change: 15.6, trend: 'up' as const },
    successRate: { value: '96.8%', change: 2.3, trend: 'up' as const },
    onTimePercentage: { value: '91.5%', change: -1.2, trend: 'down' as const },
    avgDeliveryTime: { value: '28 min', change: -8.5, trend: 'up' as const },

    // Finance KPIs
    revenueMTD: { value: '498,500 SAR', change: 18.3, trend: 'up' as const },
    expensesMTD: { value: '312,800 SAR', change: 12.1, trend: 'up' as const },
    profitMargin: { value: '37.3%', change: 4.2, trend: 'up' as const },
    codCollected: { value: '156,200 SAR', change: 21.5, trend: 'up' as const },

    // Additional KPIs
    customerSatisfaction: { value: '4.7/5', change: 5.6, trend: 'up' as const },
    totalOrders: { value: 1294, change: 12.5, trend: 'up' as const },
  }

  const kpiDefinitions = [
    // Fleet
    { id: 'totalVehicles', title: 'Total Vehicles', category: 'Fleet', icon: Truck, color: 'blue' as const },
    { id: 'activeVehicles', title: 'Active Vehicles', category: 'Fleet', icon: CheckCircle, color: 'green' as const },
    { id: 'maintenance', title: 'In Maintenance', category: 'Fleet', icon: Wrench, color: 'yellow' as const },
    { id: 'fuelEfficiency', title: 'Fuel Efficiency', category: 'Fleet', icon: BarChart3, color: 'purple' as const },

    // HR
    { id: 'totalEmployees', title: 'Total Employees', category: 'HR', icon: Users, color: 'blue' as const },
    { id: 'attendanceRate', title: 'Attendance Rate', category: 'HR', icon: UserCheck, color: 'green' as const },
    { id: 'leaveBalance', title: 'Avg Leave Balance', category: 'HR', icon: Calendar, color: 'purple' as const },
    { id: 'activeCouriers', title: 'Active Couriers', category: 'HR', icon: Briefcase, color: 'indigo' as const },

    // Operations
    { id: 'deliveriesToday', title: 'Deliveries Today', category: 'Operations', icon: Package, color: 'blue' as const },
    { id: 'successRate', title: 'Success Rate', category: 'Operations', icon: CheckCircle, color: 'green' as const },
    { id: 'onTimePercentage', title: 'On-Time %', category: 'Operations', icon: Clock, color: 'yellow' as const },
    { id: 'avgDeliveryTime', title: 'Avg Delivery Time', category: 'Operations', icon: TrendingUp, color: 'purple' as const },

    // Finance
    { id: 'revenueMTD', title: 'Revenue MTD', category: 'Finance', icon: DollarSign, color: 'green' as const },
    { id: 'expensesMTD', title: 'Expenses MTD', category: 'Finance', icon: AlertTriangle, color: 'red' as const },
    { id: 'profitMargin', title: 'Profit Margin', category: 'Finance', icon: Target, color: 'blue' as const },
    { id: 'codCollected', title: 'COD Collected', category: 'Finance', icon: DollarSign, color: 'green' as const },

    // Additional
    { id: 'customerSatisfaction', title: 'Customer Satisfaction', category: 'Additional', icon: CheckCircle, color: 'green' as const },
    { id: 'totalOrders', title: 'Total Orders', category: 'Additional', icon: FileText, color: 'blue' as const },
  ]

  const toggleKPI = (kpiId: string) => {
    const newSelected = new Set(selectedKPIs)
    if (newSelected.has(kpiId)) {
      newSelected.delete(kpiId)
    } else {
      newSelected.add(kpiId)
    }
    setSelectedKPIs(newSelected)
  }

  const exportDashboard = () => {
    // Mock PDF export
    alert('Exporting dashboard as PDF...\n\nThis would generate a PDF report with all visible KPIs and their current values.')
  }

  const resetLayout = () => {
    setSelectedKPIs(new Set([
      'totalVehicles', 'activeVehicles', 'maintenance', 'totalEmployees',
      'attendanceRate', 'leaveBalance', 'deliveriesToday', 'successRate',
      'onTimePercentage', 'revenueMTD', 'expensesMTD', 'profitMargin',
      'codCollected', 'avgDeliveryTime', 'customerSatisfaction', 'fuelEfficiency'
    ]))
    setLayoutMode('grid')
  }

  const visibleKPIs = kpiDefinitions.filter(kpi => selectedKPIs.has(kpi.id))
  const categories = ['Fleet', 'HR', 'Operations', 'Finance', 'Additional']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">KPI Dashboard</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Monitor key performance indicators across all departments
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <Select
            value={timePeriod}
            onChange={(e) => setTimePeriod(e.target.value)}
            className="w-40"
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </Select>

          <Button
            variant="outline"
            onClick={exportDashboard}
            className="flex items-center gap-2"
          >
            <FileText className="w-4 h-4" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Layout Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Layout Mode:
            </span>
            <div className="flex gap-2">
              <Button
                variant={layoutMode === 'grid' ? 'primary' : 'outline'}
                onClick={() => setLayoutMode('grid')}
                size="sm"
              >
                Grid
              </Button>
              <Button
                variant={layoutMode === 'compact' ? 'primary' : 'outline'}
                onClick={() => setLayoutMode('compact')}
                size="sm"
              >
                Compact
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {selectedKPIs.size} of {kpiDefinitions.length} KPIs visible
            </span>
            <Button variant="ghost" onClick={resetLayout} size="sm">
              Reset
            </Button>
          </div>
        </div>

        {/* KPI Selector */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Customize KPIs:
          </p>
          <div className="space-y-3">
            {categories.map(category => {
              const categoryKPIs = kpiDefinitions.filter(kpi => kpi.category === category)
              return (
                <div key={category}>
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                    {category}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {categoryKPIs.map(kpi => (
                      <button
                        key={kpi.id}
                        onClick={() => toggleKPI(kpi.id)}
                        className={`px-3 py-1.5 text-xs rounded-md border transition-colors ${
                          selectedKPIs.has(kpi.id)
                            ? 'bg-blue-100 border-blue-300 text-blue-700 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-400'
                            : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-400'
                        }`}
                      >
                        {kpi.title}
                      </button>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* KPI Grid */}
      {visibleKPIs.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <p className="text-gray-500 dark:text-gray-400">
            No KPIs selected. Choose KPIs from the customization panel above.
          </p>
        </div>
      ) : (
        <div className={`grid gap-4 ${
          layoutMode === 'grid'
            ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
            : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6'
        }`}>
          {visibleKPIs.map(kpi => {
            const data = kpiData[kpi.id as keyof typeof kpiData]
            const Icon = kpi.icon

            return (
              <KPICard
                key={kpi.id}
                title={kpi.title}
                value={data.value}
                change={data.change}
                trend={data.trend}
                icon={<Icon className="w-6 h-6" />}
                color={kpi.color}
              />
            )
          })}
        </div>
      )}

      {/* Summary Footer */}
      <div className="bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
              Dashboard Insights for {timePeriod === 'month' ? 'This Month' : timePeriod}
            </h3>
            <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
              Overall performance is trending positively with 85% of KPIs showing improvement.
              Focus areas: On-time delivery percentage needs attention, while revenue and success rate are exceeding targets.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
