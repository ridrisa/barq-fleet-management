import { useState } from 'react'
import { SummaryCard, LineChart, BarChart, PieChart, AreaChart, DateRangePicker } from '@/components/ui'

export default function Overview() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })

  // Mock data
  const deliveryTrendData = [
    { date: '2024-01-01', deliveries: 145 },
    { date: '2024-01-02', deliveries: 178 },
    { date: '2024-01-03', deliveries: 163 },
    { date: '2024-01-04', deliveries: 195 },
    { date: '2024-01-05', deliveries: 201 },
    { date: '2024-01-06', deliveries: 189 },
    { date: '2024-01-07', deliveries: 223 },
  ]

  const revenueTrendData = [
    { date: '2024-01-01', revenue: 12500, expenses: 8200 },
    { date: '2024-01-02', revenue: 15300, expenses: 9100 },
    { date: '2024-01-03', revenue: 14100, expenses: 8800 },
    { date: '2024-01-04', revenue: 16800, expenses: 9500 },
    { date: '2024-01-05', revenue: 17200, expenses: 9800 },
    { date: '2024-01-06', revenue: 16500, expenses: 9300 },
    { date: '2024-01-07', revenue: 19100, expenses: 10200 },
  ]

  const fleetUtilizationData = [
    { name: 'Active', value: 42, color: '#10b981' },
    { name: 'Idle', value: 18, color: '#f59e0b' },
    { name: 'Maintenance', value: 8, color: '#ef4444' },
    { name: 'Available', value: 12, color: '#3b82f6' },
  ]

  const topPerformersData = [
    { name: 'Ahmed Ali', deliveries: 156 },
    { name: 'Mohammed Hassan', deliveries: 142 },
    { name: 'Khaled Ibrahim', deliveries: 138 },
    { name: 'Omar Youssef', deliveries: 129 },
    { name: 'Abdullah Mahmoud', deliveries: 121 },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analytics Overview</h1>
        <DateRangePicker
          startDate={dateRange.start}
          endDate={dateRange.end}
          onRangeChange={(start, end) => setDateRange({ start, end })}
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard
          title="Total Deliveries"
          value="1,294"
          color="blue"
          trend={{ value: 12.5, label: 'vs last month' }}
        />
        <SummaryCard
          title="Active Couriers"
          value="42"
          color="green"
          trend={{ value: 5.2, label: 'vs last month' }}
        />
        <SummaryCard
          title="Fleet Size"
          value="80"
          color="purple"
          trend={{ value: 0, label: 'vs last month' }}
        />
        <SummaryCard
          title="Total Revenue"
          value="98,500 SAR"
          color="yellow"
          trend={{ value: 18.3, label: 'vs last month' }}
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={deliveryTrendData}
          xKey="date"
          yKey="deliveries"
          title="Deliveries Trend"
          height={300}
          formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        />

        <AreaChart
          data={revenueTrendData}
          xKey="date"
          yKey={['revenue', 'expenses']}
          title="Revenue & Expenses Trend"
          height={300}
          colors={['#10b981', '#ef4444']}
          formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          formatYAxis={(value) => `${(value / 1000).toFixed(0)}K`}
        />

        <PieChart
          data={fleetUtilizationData}
          dataKey="value"
          nameKey="name"
          title="Fleet Utilization"
          height={300}
          colors={fleetUtilizationData.map(d => d.color)}
        />

        <BarChart
          data={topPerformersData}
          xKey="name"
          yKey="deliveries"
          title="Top 5 Performers"
          height={300}
          formatXAxis={(value) => value.split(' ')[0]}
        />
      </div>
    </div>
  )
}
