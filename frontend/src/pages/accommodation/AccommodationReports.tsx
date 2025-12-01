import { useState } from 'react'
import { FileDown, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'

export default function AccommodationReports() {
  const [reportType, setReportType] = useState('occupancy')
  const [dateRange, setDateRange] = useState({ start: '', end: '' })

  const handleGenerateReport = () => {
    console.log('Generating report:', reportType, dateRange)
  }

  const handleExport = (format: string) => {
    console.log('Exporting as:', format)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Accommodation Reports</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-blue-600">24</p><p className="text-sm text-gray-600">Reports Generated</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-green-600">3</p><p className="text-sm text-gray-600">Scheduled Reports</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-purple-600">Oct 2024</p><p className="text-sm text-gray-600">Current Period</p></div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-center"><p className="text-2xl font-bold text-orange-600">78%</p><p className="text-sm text-gray-600">Avg Occupancy</p></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Generate Report</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Report Type</label>
              <Select value={reportType} onChange={(e) => setReportType(e.target.value)} options={[
                {value: 'occupancy', label: 'Monthly Occupancy Report'},
                {value: 'maintenance', label: 'Maintenance Summary'},
                {value: 'utilities', label: 'Utility Costs Analysis'},
                {value: 'allocations', label: 'Allocation History'}
              ]} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Start Date</label>
                <Input type="date" value={dateRange.start} onChange={(e) => setDateRange({...dateRange, start: e.target.value})} leftIcon={<Calendar className="h-4 w-4" />} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">End Date</label>
                <Input type="date" value={dateRange.end} onChange={(e) => setDateRange({...dateRange, end: e.target.value})} leftIcon={<Calendar className="h-4 w-4" />} />
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <Button onClick={handleGenerateReport} className="flex-1">Generate Report</Button>
              <Button onClick={() => handleExport('excel')} variant="outline"><FileDown className="h-4 w-4 mr-2" />Export Excel</Button>
              <Button onClick={() => handleExport('pdf')} variant="outline"><FileDown className="h-4 w-4 mr-2" />Export PDF</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Report Preview</CardTitle></CardHeader>
        <CardContent>
          <div className="text-center text-gray-500 py-8">
            Select report parameters and click "Generate Report" to view
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
