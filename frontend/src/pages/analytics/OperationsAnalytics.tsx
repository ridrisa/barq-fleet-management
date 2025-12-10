import { useState } from 'react'
import {
  KPICard,
  LineChart,
  BarChart,
  PieChart,
  AreaChart,
  DateRangePicker,
  Button,
  Select,
  Card,
  CardContent,
  Table,
} from '@/components/ui'
import { Download, TrendingUp, Package, CheckCircle, Clock, DollarSign } from 'lucide-react'
import { exportToExcelMultiSheet } from '@/utils/export'

export default function OperationsAnalytics() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  })
  const [selectedZone, setSelectedZone] = useState('all')
  const [chartView, setChartView] = useState<'daily' | 'weekly' | 'monthly'>('daily')

  // Mock data for summary cards
  const summaryData = {
    totalDeliveries: { value: 1294, trend: 12.5 },
    successRate: { value: '96.8%', trend: 2.3 },
    avgTime: { value: '28 min', trend: -8.5 },
    codCollected: { value: '156,200 SAR', trend: 21.5 },
  }

  // Mock data for delivery trends (30 days)
  const deliveryTrendData = [
    { date: '2024-01-01', deliveries: 145, successful: 139, failed: 6 },
    { date: '2024-01-02', deliveries: 178, successful: 172, failed: 6 },
    { date: '2024-01-03', deliveries: 163, successful: 158, failed: 5 },
    { date: '2024-01-04', deliveries: 195, successful: 189, failed: 6 },
    { date: '2024-01-05', deliveries: 201, successful: 195, failed: 6 },
    { date: '2024-01-06', deliveries: 189, successful: 183, failed: 6 },
    { date: '2024-01-07', deliveries: 223, successful: 216, failed: 7 },
    { date: '2024-01-08', deliveries: 198, successful: 192, failed: 6 },
    { date: '2024-01-09', deliveries: 187, successful: 181, failed: 6 },
    { date: '2024-01-10', deliveries: 209, successful: 202, failed: 7 },
    { date: '2024-01-11', deliveries: 215, successful: 208, failed: 7 },
    { date: '2024-01-12', deliveries: 193, successful: 187, failed: 6 },
    { date: '2024-01-13', deliveries: 201, successful: 195, failed: 6 },
    { date: '2024-01-14', deliveries: 188, successful: 182, failed: 6 },
    { date: '2024-01-15', deliveries: 210, successful: 203, failed: 7 },
    { date: '2024-01-16', deliveries: 225, successful: 218, failed: 7 },
    { date: '2024-01-17', deliveries: 197, successful: 191, failed: 6 },
    { date: '2024-01-18', deliveries: 204, successful: 198, failed: 6 },
    { date: '2024-01-19', deliveries: 192, successful: 186, failed: 6 },
    { date: '2024-01-20', deliveries: 218, successful: 211, failed: 7 },
    { date: '2024-01-21', deliveries: 208, successful: 201, failed: 7 },
    { date: '2024-01-22', deliveries: 195, successful: 189, failed: 6 },
    { date: '2024-01-23', deliveries: 212, successful: 205, failed: 7 },
    { date: '2024-01-24', deliveries: 199, successful: 193, failed: 6 },
    { date: '2024-01-25', deliveries: 221, successful: 214, failed: 7 },
    { date: '2024-01-26', deliveries: 206, successful: 200, failed: 6 },
    { date: '2024-01-27', deliveries: 194, successful: 188, failed: 6 },
    { date: '2024-01-28', deliveries: 217, successful: 210, failed: 7 },
    { date: '2024-01-29', deliveries: 203, successful: 197, failed: 6 },
    { date: '2024-01-30', deliveries: 228, successful: 221, failed: 7 },
  ]

  // Mock data for deliveries by zone
  const deliveriesByZoneData = [
    { zone: 'North', deliveries: 342, revenue: 45600 },
    { zone: 'South', deliveries: 298, revenue: 39800 },
    { zone: 'East', deliveries: 267, revenue: 35700 },
    { zone: 'West', deliveries: 234, revenue: 31200 },
    { zone: 'Central', deliveries: 153, revenue: 20400 },
  ]

  // Mock data for delivery status distribution
  const deliveryStatusData = [
    { name: 'Delivered', value: 1253, color: '#10b981' },
    { name: 'Pending', value: 28, color: '#f59e0b' },
    { name: 'Failed', value: 13, color: '#ef4444' },
  ]

  // Mock data for COD collection trends
  const codTrendData = [
    { date: '2024-01-01', cod: 12500, target: 15000 },
    { date: '2024-01-02', cod: 15300, target: 15000 },
    { date: '2024-01-03', cod: 14100, target: 15000 },
    { date: '2024-01-04', cod: 16800, target: 15000 },
    { date: '2024-01-05', cod: 17200, target: 15000 },
    { date: '2024-01-06', cod: 16500, target: 15000 },
    { date: '2024-01-07', cod: 19100, target: 15000 },
    { date: '2024-01-08', cod: 16800, target: 15000 },
    { date: '2024-01-09', cod: 15900, target: 15000 },
    { date: '2024-01-10', cod: 17800, target: 15000 },
    { date: '2024-01-11', cod: 18200, target: 15000 },
    { date: '2024-01-12', cod: 16400, target: 15000 },
    { date: '2024-01-13', cod: 17100, target: 15000 },
    { date: '2024-01-14', cod: 15900, target: 15000 },
  ]

  // Export to Excel functionality
  const exportToExcel = () => {
    const summaryExport = [{
      'Total Deliveries': summaryData.totalDeliveries.value,
      'Success Rate': summaryData.successRate.value,
      'Avg Delivery Time': summaryData.avgTime.value,
      'COD Collected': summaryData.codCollected.value,
      'Period': `${dateRange.start} to ${dateRange.end}`,
    }]

    exportToExcelMultiSheet([
      { name: 'Summary', data: summaryExport },
      { name: 'Delivery Trends', data: deliveryTrendData },
      { name: 'Deliveries by Zone', data: deliveriesByZoneData },
      { name: 'Delivery Status', data: deliveryStatusData },
      { name: 'COD Trends', data: codTrendData },
    ], `operations-analytics-${dateRange.start}-${dateRange.end}`)
  }

  // Calculate additional metrics
  const totalDeliveries = deliveryTrendData.reduce((sum, day) => sum + day.deliveries, 0)
  const totalSuccessful = deliveryTrendData.reduce((sum, day) => sum + day.successful, 0)
  const actualSuccessRate = ((totalSuccessful / totalDeliveries) * 100).toFixed(1)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Operations Analytics</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Deep dive into operational metrics and delivery performance
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <DateRangePicker
            startDate={dateRange.start}
            endDate={dateRange.end}
            onRangeChange={(start, end) => setDateRange({ start, end })}
          />
          <Button
            variant="primary"
            onClick={exportToExcel}
            className="flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Export to Excel
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex items-center gap-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Zone:
            </label>
            <Select
              value={selectedZone}
              onChange={(e) => setSelectedZone(e.target.value)}
              className="w-40"
            >
              <option value="all">All Zones</option>
              <option value="north">North</option>
              <option value="south">South</option>
              <option value="east">East</option>
              <option value="west">West</option>
              <option value="central">Central</option>
            </Select>
          </div>

          <div className="flex items-center gap-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              View:
            </label>
            <div className="flex gap-2">
              <Button
                variant={chartView === 'daily' ? 'primary' : 'outline'}
                onClick={() => setChartView('daily')}
                size="sm"
              >
                Daily
              </Button>
              <Button
                variant={chartView === 'weekly' ? 'primary' : 'outline'}
                onClick={() => setChartView('weekly')}
                size="sm"
              >
                Weekly
              </Button>
              <Button
                variant={chartView === 'monthly' ? 'primary' : 'outline'}
                onClick={() => setChartView('monthly')}
                size="sm"
              >
                Monthly
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Total Deliveries"
          value={summaryData.totalDeliveries.value.toLocaleString()}
          change={summaryData.totalDeliveries.trend}
          trend="up"
          icon={<Package className="w-6 h-6" />}
          color="blue"
        />
        <KPICard
          title="Success Rate"
          value={summaryData.successRate.value}
          change={summaryData.successRate.trend}
          trend="up"
          icon={<CheckCircle className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="Avg Delivery Time"
          value={summaryData.avgTime.value}
          change={summaryData.avgTime.trend}
          trend="down"
          icon={<Clock className="w-6 h-6" />}
          color="purple"
        />
        <KPICard
          title="COD Collected"
          value={summaryData.codCollected.value}
          change={summaryData.codCollected.trend}
          trend="up"
          icon={<DollarSign className="w-6 h-6" />}
          color="yellow"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Delivery Trends Line Chart */}
        <LineChart
          data={deliveryTrendData}
          xKey="date"
          yKey="deliveries"
          title="Delivery Trends (30 Days)"
          height={300}
          formatXAxis={(value) =>
            new Date(value).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            })
          }
        />

        {/* Deliveries by Zone Bar Chart */}
        <BarChart
          data={deliveriesByZoneData}
          xKey="zone"
          yKey="deliveries"
          title="Deliveries by Zone"
          height={300}
          color="#3b82f6"
        />

        {/* Delivery Status Pie Chart */}
        <PieChart
          data={deliveryStatusData}
          dataKey="value"
          nameKey="name"
          title="Delivery Status Distribution"
          height={300}
          colors={deliveryStatusData.map((d) => d.color)}
        />

        {/* COD Collection Area Chart */}
        <AreaChart
          data={codTrendData}
          xKey="date"
          yKey={['cod', 'target']}
          title="COD Collection Trends"
          height={300}
          colors={['#10b981', '#6b7280']}
          formatXAxis={(value) =>
            new Date(value).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            })
          }
          formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
        />
      </div>

      {/* Insights Panel */}
      <div className="bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-green-900 dark:text-green-100 mb-2">
              Key Insights
            </h3>
            <ul className="space-y-1 text-sm text-green-700 dark:text-green-300">
              <li>
                • Success rate of {actualSuccessRate}% exceeds target of 95%
              </li>
              <li>
                • North zone leads with {deliveriesByZoneData[0].deliveries} deliveries
              </li>
              <li>
                • COD collection trending above target for the past 7 days
              </li>
              <li>
                • Average delivery time improved by 8.5% compared to last period
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Detailed Stats Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Zone-Wise Performance
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Zone
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Deliveries
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Revenue
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Avg per Delivery
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {deliveriesByZoneData.map((zone) => (
                <tr key={zone.zone} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                    {zone.zone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                    {zone.deliveries.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                    {zone.revenue.toLocaleString()} SAR
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                    {(zone.revenue / zone.deliveries).toFixed(2)} SAR
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Additional Tables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Top Performing Couriers</h3>
            <Table
              data={[
                { courier: 'Ahmed Ali', deliveries: 156, onTime: 153, avgTime: 28 },
                { courier: 'Mohammed Hassan', deliveries: 142, onTime: 138, avgTime: 32 },
                { courier: 'Khaled Ibrahim', deliveries: 138, onTime: 137, avgTime: 25 },
                { courier: 'Omar Youssef', deliveries: 129, onTime: 125, avgTime: 35 },
              ]}
              columns={[
                { key: 'courier', header: 'Courier', render: (row: any) => row.courier.split(' ')[0] },
                { key: 'deliveries', header: 'Deliveries' },
                { key: 'avgTime', header: 'Avg Time', render: (row: any) => `${row.avgTime}m` },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Failed Deliveries Analysis</h3>
            <Table
              data={[
                { reason: 'Address Not Found', count: 12, percentage: 35.3 },
                { reason: 'Customer Unavailable', count: 9, percentage: 26.5 },
                { reason: 'Weather Conditions', count: 6, percentage: 17.6 },
                { reason: 'Wrong Address', count: 5, percentage: 14.7 },
              ]}
              columns={[
                { key: 'reason', header: 'Reason' },
                { key: 'count', header: 'Count' },
                { key: 'percentage', header: '%', render: (row: any) => `${row.percentage}%` },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Route Efficiency Metrics</h3>
            <Table
              data={[
                { route: 'North Zone', avgDistance: 45, avgTime: 32, efficiency: 92.5 },
                { route: 'South Zone', avgDistance: 52, avgTime: 38, efficiency: 88.2 },
                { route: 'East Zone', avgDistance: 38, avgTime: 28, efficiency: 94.1 },
                { route: 'West Zone', avgDistance: 48, avgTime: 35, efficiency: 90.3 },
              ]}
              columns={[
                { key: 'route', header: 'Route' },
                { key: 'avgTime', header: 'Avg Time', render: (row: any) => `${row.avgTime}m` },
                { key: 'efficiency', header: 'Efficiency', render: (row: any) => `${row.efficiency}%` },
              ]}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
