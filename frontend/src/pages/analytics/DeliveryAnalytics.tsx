import { useState } from 'react'
import { KPICard, BarChart, PieChart, AreaChart, DateRangePicker, Button } from '@/components/ui'
import { Download } from 'lucide-react'
import { exportToExcelMultiSheet } from '@/utils/export'

export default function DeliveryAnalytics() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })

  // Mock data
  const deliveriesByHourData = [
    { hour: '6AM', count: 12 }, { hour: '7AM', count: 28 }, { hour: '8AM', count: 45 },
    { hour: '9AM', count: 68 }, { hour: '10AM', count: 92 }, { hour: '11AM', count: 105 },
    { hour: '12PM', count: 98 }, { hour: '1PM', count: 87 }, { hour: '2PM', count: 112 },
    { hour: '3PM', count: 98 }, { hour: '4PM', count: 85 }, { hour: '5PM', count: 72 },
    { hour: '6PM', count: 58 }, { hour: '7PM', count: 35 }, { hour: '8PM', count: 18 },
  ]

  const successRateTrendData = [
    { date: '2024-01-01', successRate: 94.2, failed: 5.8 },
    { date: '2024-01-02', successRate: 95.1, failed: 4.9 },
    { date: '2024-01-03', successRate: 93.8, failed: 6.2 },
    { date: '2024-01-04', successRate: 96.3, failed: 3.7 },
    { date: '2024-01-05', successRate: 95.7, failed: 4.3 },
    { date: '2024-01-06', successRate: 94.5, failed: 5.5 },
    { date: '2024-01-07', successRate: 97.1, failed: 2.9 },
  ]

  const failureReasonsData = [
    { reason: 'Customer Not Available', value: 42 },
    { reason: 'Wrong Address', value: 28 },
    { reason: 'Refused Delivery', value: 15 },
    { reason: 'Business Closed', value: 8 },
    { reason: 'Other', value: 7 },
  ]

  const deliveryZonesData = [
    { zone: 'North', deliveries: 345, avgTime: 28 },
    { zone: 'South', deliveries: 298, avgTime: 32 },
    { zone: 'East', deliveries: 412, avgTime: 25 },
    { zone: 'West', deliveries: 268, avgTime: 30 },
    { zone: 'Central', deliveries: 521, avgTime: 22 },
  ]

  const handleExport = () => {
    const summaryData = [{
      'Success Rate': '95.4%',
      'Failed Deliveries': 128,
      'Avg Delivery Time': '26 min',
      'Total Deliveries': 2856,
      'Period': `${dateRange.start} to ${dateRange.end}`,
    }]

    exportToExcelMultiSheet([
      { name: 'Summary', data: summaryData },
      { name: 'Deliveries by Hour', data: deliveriesByHourData },
      { name: 'Success Rate Trend', data: successRateTrendData },
      { name: 'Failure Reasons', data: failureReasonsData },
      { name: 'Delivery Zones', data: deliveryZonesData },
    ], `delivery-analytics-${dateRange.start}-${dateRange.end}`)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Delivery Analytics</h1>
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Success Rate" value="95.4%" color="green" change={2.3} />
        <KPICard title="Failed Deliveries" value="128" color="red" change={-8.5} />
        <KPICard title="Avg Delivery Time" value="26 min" color="blue" change={-5.2} />
        <KPICard title="Total Deliveries" value="2,856" color="purple" change={12.8} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BarChart
          data={deliveriesByHourData}
          xKey="hour"
          yKey="count"
          title="Deliveries by Hour"
          height={300}
        />

        <AreaChart
          data={successRateTrendData}
          xKey="date"
          yKey={["successRate", "failed"]}
          title="Success Rate Trend"
          height={300}
          colors={["#10b981", "#ef4444"]}
          formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          formatYAxis={(value) => value + "%"}
        />

        <PieChart
          data={failureReasonsData}
          dataKey="value"
          nameKey="reason"
          title="Failure Reasons"
          height={300}
          showLabels={false}
        />

        <BarChart
          data={deliveryZonesData}
          xKey="zone"
          yKey={["deliveries", "avgTime"]}
          title="Delivery Zones Heat Map"
          height={300}
          colors={["#3b82f6", "#f59e0b"]}
        />
      </div>
    </div>
  )
}
