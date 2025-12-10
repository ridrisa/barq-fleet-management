import { useState } from 'react'
import { Card, CardContent, Button, Select, Input, Badge } from '@/components/ui'
import { Download } from 'lucide-react'
import { exportToExcelMultiSheet } from '@/utils/export'

interface ReportTemplate {
  id: string
  name: string
  dimensions: string[]
  metrics: string[]
  filters: any[]
  schedule?: string
}

export default function CustomReports() {
  const [reportName, setReportName] = useState('')
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>([])
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([])
  const [selectedFilters, setSelectedFilters] = useState<string[]>([])
  const [scheduleFrequency, setScheduleFrequency] = useState('none')
  const [savedTemplates, setSavedTemplates] = useState<ReportTemplate[]>([
    {
      id: '1',
      name: 'Daily Performance Summary',
      dimensions: ['date', 'courier'],
      metrics: ['deliveries', 'revenue'],
      filters: [],
      schedule: 'daily'
    },
    {
      id: '2',
      name: 'Weekly Fleet Analysis',
      dimensions: ['week', 'vehicle_type'],
      metrics: ['utilization', 'fuel_cost'],
      filters: ['active'],
      schedule: 'weekly'
    }
  ])

  const dimensions = [
    { value: 'date', label: 'Date' },
    { value: 'courier', label: 'Courier' },
    { value: 'vehicle', label: 'Vehicle' },
    { value: 'zone', label: 'Delivery Zone' },
    { value: 'customer', label: 'Customer' },
    { value: 'department', label: 'Department' },
  ]

  const metrics = [
    { value: 'deliveries', label: 'Total Deliveries' },
    { value: 'revenue', label: 'Revenue' },
    { value: 'expenses', label: 'Expenses' },
    { value: 'profit', label: 'Profit' },
    { value: 'successRate', label: 'Success Rate' },
    { value: 'avgTime', label: 'Avg Delivery Time' },
    { value: 'codCollected', label: 'COD Collected' },
  ]

  const filters = [
    { value: 'active', label: 'Active Only' },
    { value: 'completed', label: 'Completed' },
    { value: 'pending', label: 'Pending' },
    { value: 'failed', label: 'Failed' },
  ]

  const handleSaveTemplate = () => {
    if (!reportName) return

    const newTemplate: ReportTemplate = {
      id: Date.now().toString(),
      name: reportName,
      dimensions: selectedDimensions,
      metrics: selectedMetrics,
      filters: selectedFilters,
      schedule: scheduleFrequency !== 'none' ? scheduleFrequency : undefined
    }

    setSavedTemplates([...savedTemplates, newTemplate])
    // Reset form
    setReportName('')
    setSelectedDimensions([])
    setSelectedMetrics([])
    setSelectedFilters([])
    setScheduleFrequency('none')
  }

  const handleDeleteTemplate = (id: string) => {
    setSavedTemplates(savedTemplates.filter(t => t.id !== id))
  }

  const handleExportTemplate = (template: ReportTemplate) => {
    // Mock data generation based on template configuration
    const mockReportData = Array.from({ length: 10 }, (_, i) => {
      const row: Record<string, any> = { id: i + 1 }
      template.dimensions.forEach(dim => {
        row[dim] = `${dim}_value_${i + 1}`
      })
      template.metrics.forEach(metric => {
        row[metric] = Math.floor(Math.random() * 1000)
      })
      return row
    })

    exportToExcelMultiSheet([
      { name: 'Report Config', data: [{
        name: template.name,
        dimensions: template.dimensions.join(', '),
        metrics: template.metrics.join(', '),
        schedule: template.schedule || 'None'
      }]},
      { name: 'Report Data', data: mockReportData },
    ], `custom-report-${template.name.toLowerCase().replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}`)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Custom Reports Builder</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Builder Form */}
        <div className="lg:col-span-2">
          <Card>
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold">Build Your Report</h3>
            </div>
            <CardContent className="pt-6 space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Report Name</label>
                <Input
                  type="text"
                  placeholder="Enter report name..."
                  value={reportName}
                  onChange={(e) => setReportName(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Select Dimensions</label>
                <div className="grid grid-cols-2 gap-2">
                  {dimensions.map(dim => (
                    <label key={dim.value} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedDimensions.includes(dim.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedDimensions([...selectedDimensions, dim.value])
                          } else {
                            setSelectedDimensions(selectedDimensions.filter(d => d !== dim.value))
                          }
                        }}
                        className="rounded"
                      />
                      <span className="text-sm">{dim.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Select Metrics</label>
                <div className="grid grid-cols-2 gap-2">
                  {metrics.map(metric => (
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

              <div>
                <label className="block text-sm font-medium mb-2">Apply Filters</label>
                <div className="grid grid-cols-2 gap-2">
                  {filters.map(filter => (
                    <label key={filter.value} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={selectedFilters.includes(filter.value)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedFilters([...selectedFilters, filter.value])
                          } else {
                            setSelectedFilters(selectedFilters.filter(f => f !== filter.value))
                          }
                        }}
                        className="rounded"
                      />
                      <span className="text-sm">{filter.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Schedule Report</label>
                <Select value={scheduleFrequency} onChange={(e) => setScheduleFrequency(e.target.value)}>
                  <option value="none">No Schedule</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </Select>
              </div>

              <div className="flex gap-2">
                <Button onClick={handleSaveTemplate}>Save Template</Button>
                <Button variant="outline">Preview Report</Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Saved Templates */}
        <div>
          <Card>
            <div className="p-4 border-b">
              <h3 className="text-lg font-semibold">Saved Templates</h3>
            </div>
            <CardContent className="pt-6">
              <div className="space-y-3">
                {savedTemplates.map(template => (
                  <div key={template.id} className="p-3 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-sm">{template.name}</h4>
                      <button
                        onClick={() => handleDeleteTemplate(template.id)}
                        className="text-red-600 hover:text-red-700 text-xs"
                      >
                        Delete
                      </button>
                    </div>
                    <div className="space-y-1 text-xs text-gray-600">
                      <div>
                        <span className="font-medium">Dimensions:</span> {template.dimensions.join(', ')}
                      </div>
                      <div>
                        <span className="font-medium">Metrics:</span> {template.metrics.join(', ')}
                      </div>
                      {template.schedule && (
                        <div>
                          <Badge variant="outline">{template.schedule}</Badge>
                        </div>
                      )}
                    </div>
                    <div className="mt-2 flex gap-2">
                      <Button size="sm" variant="outline">Run Report</Button>
                      <Button size="sm" variant="outline" onClick={() => handleExportTemplate(template)}>
                        <Download className="w-3 h-3 mr-1" />
                        Export
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
