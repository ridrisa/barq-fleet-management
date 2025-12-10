import { useState } from 'react'
import { Card, CardContent, Button, Select, DateRangePicker, LineChart, BarChart } from '@/components/ui'
import { exportToExcelMultiSheet } from '@/utils/export'

export default function PerformanceReports() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })
  const [selectedMetrics, setSelectedMetrics] = useState(['deliveries', 'revenue'])
  const [groupBy, setGroupBy] = useState('day')
  const [reportData, setReportData] = useState<any[]>([])
  const [showPreview, setShowPreview] = useState(false)

  const availableMetrics = [
    { value: 'deliveries', label: 'Total Deliveries' },
    { value: 'revenue', label: 'Revenue' },
    { value: 'expenses', label: 'Expenses' },
    { value: 'couriers', label: 'Active Couriers' },
    { value: 'vehicles', label: 'Active Vehicles' },
    { value: 'successRate', label: 'Success Rate' },
    { value: 'avgDeliveryTime', label: 'Avg Delivery Time' },
  ]

  const handleGenerateReport = () => {
    // Mock report generation
    const mockData = [
      { period: '2024-01-01', deliveries: 145, revenue: 12500, expenses: 8200 },
      { period: '2024-01-02', deliveries: 178, revenue: 15300, expenses: 9100 },
      { period: '2024-01-03', deliveries: 163, revenue: 14100, expenses: 8800 },
      { period: '2024-01-04', deliveries: 195, revenue: 16800, expenses: 9500 },
      { period: '2024-01-05', deliveries: 201, revenue: 17200, expenses: 9800 },
    ]
    setReportData(mockData)
    setShowPreview(true)
  }

  const handleExportExcel = () => {
    if (reportData.length === 0) {
      alert('Please generate a report first')
      return
    }

    const summaryData = [{
      'Metrics': selectedMetrics.join(', '),
      'Group By': groupBy,
      'Period': `${dateRange.start} to ${dateRange.end}`,
      'Records': reportData.length,
    }]

    exportToExcelMultiSheet([
      { name: 'Summary', data: summaryData },
      { name: 'Report Data', data: reportData },
    ], `performance-report-${dateRange.start}-${dateRange.end}`)
  }

  const handleExportPDF = () => {
    // PDF export would require a separate library like jsPDF
    alert('PDF export coming soon. Use Excel export for now.')
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Performance Reports</h1>
      </div>

      <Card>
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold">Report Builder</h3>
        </div>
        <CardContent className="pt-6 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Select Metrics</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {availableMetrics.map(metric => (
                <label key={metric.value} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedMetrics.includes(metric.value)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedMetrics([...selectedMetrics, metric.value])
                      } else {
                        setSelectedMetrics(selectedMetrics.filter(m => m !== metric.value))
                      }
                    }}
                    className="rounded"
                  />
                  <span className="text-sm">{metric.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Group By</label>
              <Select value={groupBy} onChange={(e) => setGroupBy(e.target.value)}>
                <option value="day">Daily</option>
                <option value="week">Weekly</option>
                <option value="month">Monthly</option>
                <option value="quarter">Quarterly</option>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Date Range</label>
              <DateRangePicker
                startDate={dateRange.start}
                endDate={dateRange.end}
                onRangeChange={(start, end) => setDateRange({ start, end })}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={handleGenerateReport}>Generate Report</Button>
            <Button onClick={handleExportExcel} variant="outline">Export to Excel</Button>
            <Button onClick={handleExportPDF} variant="outline">Export to PDF</Button>
          </div>
        </CardContent>
      </Card>

      {showPreview && reportData.length > 0 && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <LineChart
              data={reportData}
              xKey="period"
              yKey={selectedMetrics.filter(m => ['deliveries', 'revenue', 'expenses'].includes(m))}
              title="Metrics Trend"
              height={300}
              formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <BarChart
              data={reportData}
              xKey="period"
              yKey={selectedMetrics.filter(m => ['deliveries', 'revenue', 'expenses'].includes(m))}
              title="Metrics Comparison"
              height={300}
              formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
          </div>

          <Card>
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold">Report Data</h3>
            </div>
            <CardContent className="pt-6">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Period</th>
                    {selectedMetrics.map(metric => (
                      <th key={metric} className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                        {availableMetrics.find(m => m.value === metric)?.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {reportData.map((row, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-4 py-2">{new Date(row.period).toLocaleDateString()}</td>
                      {selectedMetrics.map(metric => (
                        <td key={metric} className="px-4 py-2 text-right">
                          {row[metric] || '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
