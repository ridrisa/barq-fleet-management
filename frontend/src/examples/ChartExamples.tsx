/**
 * Usage examples for Chart components
 *
 * This file demonstrates how to use the chart components
 * with various configurations and data formats
 */

import { LineChart, BarChart, PieChart } from '@/components/ui/Charts'
import { KPICard } from '@/components/ui/KPICard'
import { Package, TrendingUp, Users, DollarSign } from 'lucide-react'

// Example 1: Line Chart - Revenue Over Time
export function LineChartExample() {
  const revenueData = [
    { month: 'Jan', revenue: 45000, expenses: 30000, profit: 15000 },
    { month: 'Feb', revenue: 52000, expenses: 32000, profit: 20000 },
    { month: 'Mar', revenue: 48000, expenses: 31000, profit: 17000 },
    { month: 'Apr', revenue: 61000, expenses: 35000, profit: 26000 },
    { month: 'May', revenue: 55000, expenses: 33000, profit: 22000 },
    { month: 'Jun', revenue: 67000, expenses: 38000, profit: 29000 },
  ]

  return (
    <LineChart
      data={revenueData}
      xKey="month"
      yKey={['revenue', 'expenses', 'profit']}
      title="Monthly Financial Overview"
      height={400}
      colors={['#3b82f6', '#ef4444', '#10b981']}
      showGrid={true}
      showLegend={true}
      formatYAxis={(value) => `$${(Number(value) / 1000).toFixed(0)}K`}
    />
  )
}

// Example 2: Bar Chart - Delivery Performance
export function BarChartExample() {
  const deliveryData = [
    { day: 'Mon', completed: 45, pending: 12, failed: 3 },
    { day: 'Tue', completed: 52, pending: 8, failed: 2 },
    { day: 'Wed', completed: 48, pending: 15, failed: 5 },
    { day: 'Thu', completed: 61, pending: 10, failed: 1 },
    { day: 'Fri', completed: 55, pending: 18, failed: 4 },
    { day: 'Sat', completed: 38, pending: 22, failed: 3 },
    { day: 'Sun', completed: 42, pending: 20, failed: 2 },
  ]

  return (
    <BarChart
      data={deliveryData}
      xKey="day"
      yKey={['completed', 'pending', 'failed']}
      title="Weekly Delivery Status"
      height={350}
      colors={['#10b981', '#f59e0b', '#ef4444']}
      horizontal={false}
      showLegend={true}
    />
  )
}

// Example 3: Horizontal Bar Chart
export function HorizontalBarChartExample() {
  const courierData = [
    { courier: 'Ahmed Ali', deliveries: 89 },
    { courier: 'Sarah Hassan', deliveries: 76 },
    { courier: 'Mohammed Khalid', deliveries: 72 },
    { courier: 'Fatima Ahmed', deliveries: 68 },
    { courier: 'Omar Ibrahim', deliveries: 65 },
  ]

  return (
    <BarChart
      data={courierData}
      xKey="courier"
      yKey="deliveries"
      title="Top Couriers This Month"
      height={300}
      colors={['#3b82f6']}
      horizontal={true}
      showLegend={false}
    />
  )
}

// Example 4: Pie Chart - Order Distribution
export function PieChartExample() {
  const orderTypeData = [
    { type: 'Food Delivery', count: 450 },
    { type: 'Package Delivery', count: 320 },
    { type: 'Document Delivery', count: 180 },
    { type: 'Grocery Delivery', count: 250 },
    { type: 'Pharmacy', count: 150 },
  ]

  return (
    <PieChart
      data={orderTypeData}
      dataKey="count"
      nameKey="type"
      title="Orders by Type"
      height={350}
      showLegend={true}
      showLabels={true}
    />
  )
}

// Example 5: Donut Chart (Pie with inner radius)
export function DonutChartExample() {
  const statusData = [
    { status: 'Completed', count: 1250 },
    { status: 'In Progress', count: 180 },
    { status: 'Pending', count: 95 },
    { status: 'Cancelled', count: 45 },
  ]

  return (
    <PieChart
      data={statusData}
      dataKey="count"
      nameKey="status"
      title="Order Status Distribution"
      height={300}
      innerRadius={60}
      colors={['#10b981', '#3b82f6', '#f59e0b', '#ef4444']}
      showLabels={true}
    />
  )
}

// Example 6: KPI Cards Dashboard
export function KPICardsExample() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard
        title="Total Orders"
        value="1,247"
        change={12.5}
        trend="up"
        icon={<Package className="w-6 h-6" />}
        color="blue"
      />

      <KPICard
        title="Revenue"
        value="$45,678"
        change={8.2}
        trend="up"
        icon={<DollarSign className="w-6 h-6" />}
        color="green"
      />

      <KPICard
        title="Active Couriers"
        value="89"
        change={-2.4}
        trend="down"
        icon={<Users className="w-6 h-6" />}
        color="purple"
      />

      <KPICard
        title="Completion Rate"
        value="94.8%"
        change={1.3}
        trend="up"
        icon={<TrendingUp className="w-6 h-6" />}
        color="indigo"
      />
    </div>
  )
}

// Example 7: Loading States
export function LoadingStateExample() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <KPICard
        title="Loading..."
        value="0"
        loading={true}
      />
      <KPICard
        title="Loading..."
        value="0"
        loading={true}
      />
      <KPICard
        title="Loading..."
        value="0"
        loading={true}
      />
    </div>
  )
}

// Example 8: Complete Analytics Dashboard
export function AnalyticsDashboardExample() {
  const revenueData = [
    { month: 'Jan', value: 45000 },
    { month: 'Feb', value: 52000 },
    { month: 'Mar', value: 48000 },
    { month: 'Apr', value: 61000 },
    { month: 'May', value: 55000 },
    { month: 'Jun', value: 67000 },
  ]

  const orderTypeData = [
    { type: 'Food', count: 450 },
    { type: 'Package', count: 320 },
    { type: 'Document', count: 180 },
    { type: 'Grocery', count: 250 },
  ]

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Revenue"
          value="$328K"
          change={15.3}
          trend="up"
          icon={<DollarSign className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="Total Orders"
          value="1,200"
          change={8.1}
          trend="up"
          icon={<Package className="w-6 h-6" />}
          color="blue"
        />
        <KPICard
          title="Active Couriers"
          value="89"
          change={-2.4}
          trend="down"
          icon={<Users className="w-6 h-6" />}
          color="purple"
        />
        <KPICard
          title="Success Rate"
          value="94.8%"
          change={1.3}
          trend="up"
          icon={<TrendingUp className="w-6 h-6" />}
          color="indigo"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={revenueData}
          xKey="month"
          yKey="value"
          title="Revenue Trend"
          height={300}
          formatYAxis={(value) => `$${(Number(value) / 1000).toFixed(0)}K`}
        />

        <PieChart
          data={orderTypeData}
          dataKey="count"
          nameKey="type"
          title="Order Distribution"
          height={300}
          innerRadius={50}
        />
      </div>
    </div>
  )
}
