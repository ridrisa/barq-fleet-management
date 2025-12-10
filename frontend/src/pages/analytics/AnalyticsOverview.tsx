import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Spinner } from '@/components/ui/Spinner'
import { DateRangePicker } from '@/components/ui/DateRangePicker'
import { Button } from '@/components/ui/Button'
import { LineChart } from '@/components/ui/LineChart'
import { BarChart } from '@/components/ui/BarChart'
import { AreaChart } from '@/components/ui/AreaChart'
import { analyticsAPI } from '@/lib/api'
import { TrendingUp, TrendingDown, Truck, Users, Package, DollarSign, Download } from 'lucide-react'
import { exportToExcelMultiSheet } from '@/utils/export'

export default function AnalyticsOverview() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })

  // Fetch dashboard data from API
  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['analytics-dashboard', dateRange.start, dateRange.end],
    queryFn: () => analyticsAPI.getDashboard(dateRange.start, dateRange.end),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading analytics: {(error as Error).message}</p>
      </div>
    )
  }

  const {
    kpis = {},
    delivery_trend = [],
    revenue_trend = [],
    fleet_utilization = [],
    top_performers = []
  } = dashboardData || {}

  const handleExport = () => {
    const summaryData = [{
      'Total Deliveries': kpis.total_deliveries || 0,
      'Deliveries Change': `${kpis.deliveries_change || 0}%`,
      'Active Couriers': kpis.active_couriers || 0,
      'Fleet Size': kpis.fleet_size || 0,
      'Total Revenue': `${kpis.total_revenue || 0} SAR`,
      'Period': `${dateRange.start} to ${dateRange.end}`,
    }]

    const sheets = [{ name: 'Summary', data: summaryData }]

    if (delivery_trend.length > 0) {
      sheets.push({ name: 'Delivery Trend', data: delivery_trend })
    }
    if (revenue_trend.length > 0) {
      sheets.push({ name: 'Revenue Trend', data: revenue_trend })
    }
    if (fleet_utilization.length > 0) {
      sheets.push({ name: 'Fleet Utilization', data: fleet_utilization })
    }
    if (top_performers.length > 0) {
      sheets.push({ name: 'Top Performers', data: top_performers })
    }

    exportToExcelMultiSheet(sheets, `analytics-overview-${dateRange.start}-${dateRange.end}`)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Analytics Overview</h1>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <DateRangePicker
            startDate={dateRange.start}
            endDate={dateRange.end}
            onRangeChange={(start, end) => setDateRange({ start, end })}
          />
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Deliveries</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis.total_deliveries?.toLocaleString() || '0'}
                </p>
                {kpis.deliveries_change && (
                  <div className={`flex items-center gap-1 mt-1 text-sm ${
                    kpis.deliveries_change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {kpis.deliveries_change > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    <span>{Math.abs(kpis.deliveries_change)}% vs last period</span>
                  </div>
                )}
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Package className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Couriers</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis.active_couriers || '0'}
                </p>
                {kpis.couriers_change && (
                  <div className={`flex items-center gap-1 mt-1 text-sm ${
                    kpis.couriers_change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {kpis.couriers_change > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    <span>{Math.abs(kpis.couriers_change)}% vs last period</span>
                  </div>
                )}
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <Users className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Fleet Size</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis.fleet_size || '0'}
                </p>
                {kpis.fleet_change && (
                  <div className={`flex items-center gap-1 mt-1 text-sm ${
                    kpis.fleet_change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {kpis.fleet_change > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    <span>{Math.abs(kpis.fleet_change)}% vs last period</span>
                  </div>
                )}
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <Truck className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold text-gray-900">
                  {kpis.total_revenue?.toLocaleString() || '0'} SAR
                </p>
                {kpis.revenue_change && (
                  <div className={`flex items-center gap-1 mt-1 text-sm ${
                    kpis.revenue_change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {kpis.revenue_change > 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                    <span>{Math.abs(kpis.revenue_change)}% vs last period</span>
                  </div>
                )}
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <DollarSign className="w-6 h-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {delivery_trend.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Deliveries Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <LineChart
                data={delivery_trend}
                xKey="date"
                yKey="deliveries"
                height={300}
                formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
            </CardContent>
          </Card>
        )}

        {revenue_trend.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Revenue & Expenses Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <AreaChart
                data={revenue_trend}
                xKey="date"
                yKey={['revenue', 'expenses']}
                height={300}
                colors={['#10b981', '#ef4444']}
                formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
              />
            </CardContent>
          </Card>
        )}

        {fleet_utilization.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Fleet Utilization</CardTitle>
            </CardHeader>
            <CardContent>
              <BarChart
                data={fleet_utilization}
                xKey="status"
                yKey="count"
                height={300}
              />
            </CardContent>
          </Card>
        )}

        {top_performers.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Top 5 Performers</CardTitle>
            </CardHeader>
            <CardContent>
              <BarChart
                data={top_performers}
                xKey="name"
                yKey="deliveries"
                height={300}
                formatXAxis={(value) => String(value).split(' ')[0]}
              />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
