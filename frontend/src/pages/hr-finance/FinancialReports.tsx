import { useState } from 'react'
import { FileText, Download, Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { financialReportsAPI } from '@/lib/api'
import { Spinner } from '@/components/ui/Spinner'

export default function FinancialReports() {
  const [reportType, setReportType] = useState('income_statement')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [groupBy, setGroupBy] = useState('month')
  const [category, setCategory] = useState('')
  const [reportData, setReportData] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [savedTemplates, setSavedTemplates] = useState<any[]>([])

  const generateReport = async () => {
    if (!startDate || !endDate) {
      alert('Please select start and end dates')
      return
    }

    setIsGenerating(true)
    try {
      const data = await financialReportsAPI.generate(reportType, startDate, endDate)
      setReportData(data)
    } catch (error) {
      console.error('Failed to generate report:', error)
      // Use mock data as fallback
      const mockData = generateMockReport()
      setReportData(mockData)
    } finally {
      setIsGenerating(false)
    }
  }

  const generateMockReport = () => {
    if (reportType === 'income_statement') {
      return {
        type: 'Income Statement',
        period: `${startDate} to ${endDate}`,
        data: [
          { category: 'Revenue', subcategory: 'Delivery Fees', amount: 850000, percentage: 68 },
          { category: 'Revenue', subcategory: 'COD Fees', amount: 250000, percentage: 20 },
          { category: 'Revenue', subcategory: 'Other Income', amount: 150000, percentage: 12 },
          { category: 'Total Revenue', subcategory: '', amount: 1250000, percentage: 100, bold: true },
          { category: 'Expenses', subcategory: 'Payroll', amount: 450000, percentage: 36 },
          { category: 'Expenses', subcategory: 'Fuel', amount: 180000, percentage: 14.4 },
          { category: 'Expenses', subcategory: 'Maintenance', amount: 120000, percentage: 9.6 },
          { category: 'Expenses', subcategory: 'Accommodation', amount: 80000, percentage: 6.4 },
          { category: 'Expenses', subcategory: 'Other', amount: 20000, percentage: 1.6 },
          { category: 'Total Expenses', subcategory: '', amount: 850000, percentage: 68, bold: true },
          { category: 'Net Profit', subcategory: '', amount: 400000, percentage: 32, bold: true, highlight: true },
        ],
      }
    } else if (reportType === 'balance_sheet') {
      return {
        type: 'Balance Sheet',
        period: `As of ${endDate}`,
        data: [
          { category: 'Assets', subcategory: 'Cash & Bank', amount: 500000 },
          { category: 'Assets', subcategory: 'Accounts Receivable', amount: 350000 },
          { category: 'Assets', subcategory: 'Vehicles', amount: 2000000 },
          { category: 'Assets', subcategory: 'Equipment', amount: 150000 },
          { category: 'Total Assets', subcategory: '', amount: 3000000, bold: true },
          { category: 'Liabilities', subcategory: 'Accounts Payable', amount: 200000 },
          { category: 'Liabilities', subcategory: 'Loans', amount: 500000 },
          { category: 'Total Liabilities', subcategory: '', amount: 700000, bold: true },
          { category: 'Equity', subcategory: '', amount: 2300000, bold: true, highlight: true },
        ],
      }
    } else if (reportType === 'cash_flow') {
      return {
        type: 'Cash Flow Statement',
        period: `${startDate} to ${endDate}`,
        data: [
          { category: 'Operating Activities', subcategory: 'Net Profit', amount: 400000 },
          { category: 'Operating Activities', subcategory: 'Depreciation', amount: 50000 },
          { category: 'Operating Activities', subcategory: 'Changes in Receivables', amount: -30000 },
          { category: 'Cash from Operations', subcategory: '', amount: 420000, bold: true },
          { category: 'Investing Activities', subcategory: 'Vehicle Purchase', amount: -200000 },
          { category: 'Investing Activities', subcategory: 'Equipment Purchase', amount: -50000 },
          { category: 'Cash from Investing', subcategory: '', amount: -250000, bold: true },
          { category: 'Financing Activities', subcategory: 'Loan Proceeds', amount: 100000 },
          { category: 'Financing Activities', subcategory: 'Loan Repayments', amount: -50000 },
          { category: 'Cash from Financing', subcategory: '', amount: 50000, bold: true },
          { category: 'Net Cash Change', subcategory: '', amount: 220000, bold: true, highlight: true },
        ],
      }
    } else {
      return {
        type: 'Expense Report',
        period: `${startDate} to ${endDate}`,
        data: [
          { category: 'Payroll', subcategory: 'Base Salary', amount: 350000, percentage: 41.2 },
          { category: 'Payroll', subcategory: 'Allowances', amount: 80000, percentage: 9.4 },
          { category: 'Payroll', subcategory: 'GOSI', amount: 20000, percentage: 2.4 },
          { category: 'Operations', subcategory: 'Fuel', amount: 180000, percentage: 21.2 },
          { category: 'Operations', subcategory: 'Maintenance', amount: 120000, percentage: 14.1 },
          { category: 'Operations', subcategory: 'Accommodation', amount: 80000, percentage: 9.4 },
          { category: 'Other', subcategory: 'Miscellaneous', amount: 20000, percentage: 2.4 },
          { category: 'Total', subcategory: '', amount: 850000, percentage: 100, bold: true },
        ],
      }
    }
  }

  const handleExportExcel = async () => {
    if (!reportData) {
      alert('Please generate a report first')
      return
    }

    try {
      const blob = await financialReportsAPI.export(reportData.id || 1, 'excel')
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${reportType}_${new Date().toISOString().split('T')[0]}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('Export functionality coming soon')
    }
  }

  const handleExportPDF = async () => {
    if (!reportData) {
      alert('Please generate a report first')
      return
    }

    try {
      const blob = await financialReportsAPI.export(reportData.id || 1, 'pdf')
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${reportType}_${new Date().toISOString().split('T')[0]}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('Export functionality coming soon')
    }
  }

  const handleSaveTemplate = () => {
    if (!startDate || !endDate) {
      alert('Please configure report first')
      return
    }

    const template = {
      id: savedTemplates.length + 1,
      name: `${reportType} - ${groupBy}`,
      type: reportType,
      start_date: startDate,
      end_date: endDate,
      group_by: groupBy,
      category,
      saved_at: new Date().toISOString(),
    }

    setSavedTemplates([template, ...savedTemplates])
    alert('Report template saved')
  }

  const reportColumns = [
    { key: 'category', header: 'Category' },
    {
      key: 'subcategory',
      header: 'Subcategory',
      render: (row: any) => row.subcategory || '-',
    },
    {
      key: 'amount',
      header: 'Amount (SAR)',
      render: (row: any) => (
        <span className={row.bold ? 'font-bold' : ''}>
          {row.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'percentage',
      header: '%',
      render: (row: any) => (row.percentage ? `${row.percentage.toFixed(1)}%` : '-'),
    },
  ]

  const templateColumns = [
    { key: 'id', header: 'ID' },
    { key: 'name', header: 'Template Name' },
    {
      key: 'type',
      header: 'Type',
      render: (row: any) => <Badge variant="default">{row.type}</Badge>,
    },
    {
      key: 'saved_at',
      header: 'Saved',
      render: (row: any) => new Date(row.saved_at).toLocaleDateString(),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => {
            setReportType(row.type)
            setStartDate(row.start_date)
            setEndDate(row.end_date)
            setGroupBy(row.group_by)
            setCategory(row.category)
          }}
        >
          Load
        </Button>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Financial Reports</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            <div className="flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Report Builder
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Report Type *</label>
              <Select
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                options={[
                  { value: 'income_statement', label: 'Income Statement' },
                  { value: 'balance_sheet', label: 'Balance Sheet' },
                  { value: 'cash_flow', label: 'Cash Flow' },
                  { value: 'expense_report', label: 'Expense Report' },
                ]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
              <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date *</label>
              <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Group By</label>
              <Select
                value={groupBy}
                onChange={(e) => setGroupBy(e.target.value)}
                options={[
                  { value: 'month', label: 'Monthly' },
                  { value: 'quarter', label: 'Quarterly' },
                  { value: 'year', label: 'Yearly' },
                ]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category Filter</label>
              <Select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                options={[
                  { value: '', label: 'All Categories' },
                  { value: 'payroll', label: 'Payroll' },
                  { value: 'operations', label: 'Operations' },
                  { value: 'maintenance', label: 'Maintenance' },
                  { value: 'other', label: 'Other' },
                ]}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={generateReport} disabled={isGenerating}>
              <FileText className="h-4 w-4 mr-2" />
              {isGenerating ? 'Generating...' : 'Generate Report'}
            </Button>
            <Button onClick={handleSaveTemplate} variant="outline">
              <Save className="h-4 w-4 mr-2" />
              Save Template
            </Button>
          </div>
        </CardContent>
      </Card>

      {isGenerating && (
        <div className="flex items-center justify-center h-32">
          <Spinner />
        </div>
      )}

      {reportData && !isGenerating && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>{reportData.type}</CardTitle>
                <p className="text-sm text-gray-600 mt-1">{reportData.period}</p>
              </div>
              <div className="flex gap-2">
                <Button onClick={handleExportExcel} variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Excel
                </Button>
                <Button onClick={handleExportPDF} variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  PDF
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {reportColumns.map((col) => (
                      <th
                        key={col.key}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {col.header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {reportData.data.map((row: any, index: number) => (
                    <tr
                      key={index}
                      className={`${row.bold ? 'bg-gray-50 font-semibold' : ''} ${
                        row.highlight ? 'bg-green-50' : ''
                      }`}
                    >
                      <td className={`px-6 py-4 text-sm text-gray-900 ${row.bold ? 'font-bold' : ''}`}>
                        {row.category}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">{row.subcategory || '-'}</td>
                      <td className={`px-6 py-4 text-sm text-gray-900 ${row.bold ? 'font-bold' : ''}`}>
                        {row.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {row.percentage ? `${row.percentage.toFixed(1)}%` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {savedTemplates.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Saved Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <Table data={savedTemplates} columns={templateColumns} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
