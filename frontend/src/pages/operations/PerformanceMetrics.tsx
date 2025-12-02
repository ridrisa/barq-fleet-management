import { useState, useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { TrendingUp, TrendingDown, Clock, Package, Target, AlertTriangle, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Spinner } from '@/components/ui/Spinner'
import { LineChart } from '@/components/charts/LineChart'
import { PieChart } from '@/components/charts/PieChart'
import { deliveriesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { exportToExcel } from '@/lib/export'

export default function PerformanceMetrics() {
  useTranslation()
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')

  const {
    isLoading,
    error,
    filteredData: deliveries,
  } = useDataTable({
    queryKey: 'performance-deliveries',
    queryFn: deliveriesAPI.getAll,
    pageSize: 1000,
  })

  // Filter by date range
  let displayData = deliveries
  if (startDate || endDate) {
    displayData = displayData.filter((d: any) => {
      const deliveryDate = new Date(d.delivery_date || d.created_at)
      const start = startDate ? new Date(startDate) : new Date(0)
      const end = endDate ? new Date(endDate) : new Date()
      return deliveryDate >= start && deliveryDate <= end
    })
  }

  // Calculate KPIs
  const totalDeliveries = displayData.length
  const successfulDeliveries = displayData.filter((d: any) => d.status === 'delivered').length
  const failedDeliveries = displayData.filter((d: any) =>
    d.status === 'failed' || d.status === 'returned' || d.status === 'cancelled'
  ).length
  const onTimeDeliveries = displayData.filter((d: any) => {
    // Assume on-time if delivered and no delay flag
    return d.status === 'delivered' && !d.is_delayed
  }).length

  const metrics = {
    onTimePercentage: totalDeliveries > 0
      ? ((onTimeDeliveries / totalDeliveries) * 100).toFixed(1)
      : 0,
    successRate: totalDeliveries > 0
      ? ((successfulDeliveries / totalDeliveries) * 100).toFixed(1)
      : 0,
    failureRate: totalDeliveries > 0
      ? ((failedDeliveries / totalDeliveries) * 100).toFixed(1)
      : 0,
    avgDeliveryTime: '2.5', // Mock data - calculate from actual delivery times
    totalRevenue: displayData.reduce((sum: number, d: any) =>
      sum + (parseFloat(d.cod_amount || d.amount || 0)), 0
    ).toFixed(2),
  }

  // Trend indicators (mock - would be calculated from historical comparison)
  const trends = {
    onTime: 'up',
    success: 'up',
    avgTime: 'down',
    revenue: 'up',
  }

  // Prepare chart data
  const trendData = useMemo(() => {
    // Group deliveries by date for trend chart
    const dateGroups: Record<string, { total: number; delivered: number; onTime: number }> = {}

    displayData.forEach((d: any) => {
      const date = new Date(d.delivery_date || d.created_at).toISOString().split('T')[0]
      if (!dateGroups[date]) {
        dateGroups[date] = { total: 0, delivered: 0, onTime: 0 }
      }
      dateGroups[date].total++
      if (d.status === 'delivered') dateGroups[date].delivered++
      if (d.status === 'delivered' && !d.is_delayed) dateGroups[date].onTime++
    })

    return Object.entries(dateGroups)
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-14) // Last 14 days
      .map(([date, data]) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        'Success Rate': data.total > 0 ? Math.round((data.delivered / data.total) * 100) : 0,
        'On-Time Rate': data.total > 0 ? Math.round((data.onTime / data.total) * 100) : 0,
      }))
  }, [displayData])

  const statusDistribution = useMemo(() => {
    const delivered = displayData.filter((d: any) => d.status === 'delivered').length
    const inTransit = displayData.filter((d: any) => d.status === 'in_transit').length
    const pending = displayData.filter((d: any) => d.status === 'pending').length
    const failed = displayData.filter((d: any) => d.status === 'failed' || d.status === 'returned').length

    return [
      { name: 'Delivered', value: delivered, color: '#22c55e' },
      { name: 'In Transit', value: inTransit, color: '#f59e0b' },
      { name: 'Pending', value: pending, color: '#6b7280' },
      { name: 'Failed', value: failed, color: '#ef4444' },
    ].filter(item => item.value > 0)
  }, [displayData])

  const handleExportReport = () => {
    const exportData = displayData.map((d: any) => ({
      'Tracking #': d.tracking_number || `TRK-${d.id}`,
      'Status': d.status,
      'Customer': d.customer_name || d.receiver_name,
      'Address': d.delivery_address,
      'COD Amount': d.cod_amount || d.amount || 0,
      'Date': d.delivery_date || d.created_at,
    }))
    exportToExcel(exportData, `performance-report-${new Date().toISOString().split('T')[0]}`)
  }

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
        <p className="text-red-800">Error loading performance metrics: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Operations Performance Metrics</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportReport}>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Date Range Filter */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
            <div className="flex items-end">
              <Button
                variant="outline"
                onClick={() => {
                  setStartDate('')
                  setEndDate('')
                }}
              >
                Clear
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Performance Indicators */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <p className="text-sm font-medium text-gray-600">On-Time Delivery %</p>
                  {trends.onTime === 'up' ? (
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-600" />
                  )}
                </div>
                <p className="text-3xl font-bold text-blue-600">{metrics.onTimePercentage}%</p>
                <p className="text-xs text-gray-500 mt-1">
                  {onTimeDeliveries} of {totalDeliveries} deliveries
                </p>
              </div>
              <Target className="h-10 w-10 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <p className="text-sm font-medium text-gray-600">Success Rate</p>
                  {trends.success === 'up' ? (
                    <TrendingUp className="h-4 w-4 text-green-600" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-600" />
                  )}
                </div>
                <p className="text-3xl font-bold text-green-600">{metrics.successRate}%</p>
                <p className="text-xs text-gray-500 mt-1">
                  {successfulDeliveries} successful
                </p>
              </div>
              <Package className="h-10 w-10 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <p className="text-sm font-medium text-gray-600">Avg Delivery Time</p>
                  {trends.avgTime === 'down' ? (
                    <TrendingDown className="h-4 w-4 text-green-600" />
                  ) : (
                    <TrendingUp className="h-4 w-4 text-red-600" />
                  )}
                </div>
                <p className="text-3xl font-bold text-orange-600">{metrics.avgDeliveryTime}h</p>
                <p className="text-xs text-gray-500 mt-1">
                  Average time to deliver
                </p>
              </div>
              <Clock className="h-10 w-10 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <p className="text-sm font-medium text-gray-600">Failed Deliveries</p>
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                </div>
                <p className="text-3xl font-bold text-red-600">{failedDeliveries}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {metrics.failureRate}% failure rate
                </p>
              </div>
              <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
                <span className="text-red-600 text-2xl">✗</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Deliveries</p>
                <p className="text-2xl font-bold text-gray-900">{totalDeliveries}</p>
              </div>
              <Package className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Revenue (COD)</p>
                <p className="text-2xl font-bold text-green-600">${metrics.totalRevenue}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-green-600 text-xl">$</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Couriers</p>
                <p className="text-2xl font-bold text-blue-600">-</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <span className="text-blue-600 text-xl">👤</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Delivery Performance Trend</CardTitle>
          </CardHeader>
          <CardContent>
            {trendData.length > 0 ? (
              <LineChart
                data={trendData}
                xKey="date"
                yKeys={['Success Rate', 'On-Time Rate']}
                colors={['#22c55e', '#3b82f6']}
                height={280}
              />
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                No trend data available for the selected period
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Delivery Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {statusDistribution.length > 0 ? (
              <PieChart
                data={statusDistribution}
                height={280}
              />
            ) : (
              <div className="h-64 flex items-center justify-center text-gray-500">
                No delivery data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Delivery Summary by Status */}
      <Card>
        <CardHeader>
          <CardTitle>Delivery Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {statusDistribution.map((item) => (
              <div key={item.name} className="p-4 bg-gray-50 rounded-lg text-center">
                <div
                  className="w-4 h-4 rounded-full mx-auto mb-2"
                  style={{ backgroundColor: item.color }}
                />
                <p className="text-2xl font-bold" style={{ color: item.color }}>
                  {item.value}
                </p>
                <p className="text-sm text-gray-600">{item.name}</p>
                <p className="text-xs text-gray-500">
                  {totalDeliveries > 0 ? ((item.value / totalDeliveries) * 100).toFixed(1) : 0}%
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
