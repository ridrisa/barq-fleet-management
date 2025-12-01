import { useState } from 'react'
import { FileText, Download, Calendar, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { taxAPI, couriersAPI } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { Spinner } from '@/components/ui/Spinner'

interface TaxRecord {
  id: number
  employee_id: string
  employee_name: string
  month: string
  gross_income: number
  deductions: number
  taxable_income: number
  tax_amount: number
  status: 'draft' | 'calculated' | 'filed'
}

export default function TaxReporting() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear().toString())
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7))
  const [taxReport, setTaxReport] = useState<any>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const { data: couriers = [], isLoading: couriersLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  // Generate mock tax data
  const generateTaxData = (): TaxRecord[] => {
    if (!couriers || couriers.length === 0) return []

    return couriers.map((courier: any, index: number) => {
      const baseSalary = courier.base_salary || 5000
      const allowances = baseSalary * 0.35
      const grossIncome = baseSalary + allowances
      const deductions = baseSalary * 0.09 // GOSI
      const taxableIncome = grossIncome - deductions

      // Simple tax calculation (mock - UAE has no income tax, but this is for demo)
      let taxAmount = 0
      if (taxableIncome > 100000) {
        taxAmount = (taxableIncome - 100000) * 0.05
      }

      return {
        id: index + 1,
        employee_id: courier.id.toString(),
        employee_name: courier.name || `Courier ${courier.id}`,
        month: selectedMonth,
        gross_income: grossIncome,
        deductions,
        taxable_income: taxableIncome,
        tax_amount: taxAmount,
        status: index % 3 === 0 ? 'filed' : index % 3 === 1 ? 'calculated' : 'draft',
      }
    })
  }

  const taxData = generateTaxData()

  // Calculate summary
  const totalGrossIncome = taxData.reduce((sum, record) => sum + record.gross_income, 0)
  const totalDeductions = taxData.reduce((sum, record) => sum + record.deductions, 0)
  const totalTaxableIncome = taxData.reduce((sum, record) => sum + record.taxable_income, 0)
  const totalTaxAmount = taxData.reduce((sum, record) => sum + record.tax_amount, 0)

  const statusCounts = {
    draft: taxData.filter(t => t.status === 'draft').length,
    calculated: taxData.filter(t => t.status === 'calculated').length,
    filed: taxData.filter(t => t.status === 'filed').length,
  }

  const handleGenerateReport = async () => {
    setIsGenerating(true)
    try {
      const report = await taxAPI.generate(selectedYear)
      setTaxReport(report)
    } catch (error) {
      // Mock report
      setTaxReport({
        year: selectedYear,
        total_gross_income: totalGrossIncome,
        total_deductions: totalDeductions,
        total_taxable_income: totalTaxableIncome,
        total_tax: totalTaxAmount,
        months: [
          { month: 'Jan', income: 85000, tax: 500 },
          { month: 'Feb', income: 88000, tax: 550 },
          { month: 'Mar', income: 92000, tax: 600 },
          { month: 'Apr', income: 90000, tax: 575 },
          { month: 'May', income: 95000, tax: 625 },
          { month: 'Jun', income: 98000, tax: 650 },
          { month: 'Jul', income: 100000, tax: 700 },
          { month: 'Aug', income: 97000, tax: 675 },
          { month: 'Sep', income: 94000, tax: 625 },
          { month: 'Oct', income: 96000, tax: 650 },
          { month: 'Nov', income: 99000, tax: 690 },
          { month: 'Dec', income: 102000, tax: 720 },
        ],
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleExportExcel = async () => {
    try {
      const blob = await taxAPI.export(selectedYear, 'excel')
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Tax_Report_${selectedYear}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('Export functionality coming soon')
    }
  }

  const handleDownloadCertificate = async () => {
    try {
      const blob = await taxAPI.downloadCertificate(selectedYear)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Tax_Certificate_${selectedYear}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('Tax certificate download coming soon')
    }
  }

  const columns = [
    {
      key: 'employee_id',
      header: 'Employee',
      render: (row: TaxRecord) => (
        <div>
          <div className="font-medium">{row.employee_name}</div>
          <div className="text-sm text-gray-500">ID: {row.employee_id}</div>
        </div>
      ),
    },
    {
      key: 'month',
      header: 'Month',
      render: (row: TaxRecord) => {
        const date = new Date(row.month + '-01')
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
      },
    },
    {
      key: 'gross_income',
      header: 'Gross Income',
      render: (row: TaxRecord) => (
        <span className="font-medium">
          {row.gross_income.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'deductions',
      header: 'Deductions',
      render: (row: TaxRecord) => (
        <span className="text-red-600">
          -{row.deductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'taxable_income',
      header: 'Taxable Income',
      render: (row: TaxRecord) => (
        <span className="font-medium text-blue-600">
          {row.taxable_income.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'tax_amount',
      header: 'Tax Amount',
      render: (row: TaxRecord) => (
        <span className="font-bold text-gray-900">
          {row.tax_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: TaxRecord) => {
        const variants: Record<string, 'default' | 'success' | 'warning'> = {
          draft: 'default',
          calculated: 'warning',
          filed: 'success',
        }
        return <Badge variant={variants[row.status] || 'default'}>{row.status}</Badge>
      },
    },
  ]

  if (couriersLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tax Reporting</h1>
        <div className="flex gap-2">
          <Button onClick={handleDownloadCertificate} variant="outline">
            <FileText className="h-4 w-4 mr-2" />
            Download Certificate
          </Button>
          <Button onClick={handleExportExcel}>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Info Card */}
      <Card className="bg-yellow-50 border-yellow-200">
        <CardContent className="pt-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">Tax Information (UAE/Saudi Arabia)</h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  Note: This is a demonstration module. UAE and Saudi Arabia have different tax systems. UAE has no
                  personal income tax for individuals. Saudi Arabia has Zakat and income tax for certain businesses.
                  This module demonstrates VAT reporting and tax calculation capabilities.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* VAT Report Summary */}
      <Card>
        <CardHeader>
          <CardTitle>VAT Report Summary (Monthly/Quarterly)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-green-700 font-medium">Standard Rate VAT (5%)</p>
                <TrendingUp className="h-4 w-4 text-green-600" />
              </div>
              <p className="text-2xl font-bold text-green-900">
                {(totalGrossIncome * 0.05).toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
              <p className="text-xs text-green-600 mt-1">VAT Collected</p>
            </div>
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-blue-700 font-medium">Input VAT (Recoverable)</p>
                <TrendingDown className="h-4 w-4 text-blue-600" />
              </div>
              <p className="text-2xl font-bold text-blue-900">
                {(totalDeductions * 0.05).toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
              <p className="text-xs text-blue-600 mt-1">VAT Paid on Expenses</p>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-purple-700 font-medium">Net VAT Payable</p>
                <FileText className="h-4 w-4 text-purple-600" />
              </div>
              <p className="text-2xl font-bold text-purple-900">
                {((totalGrossIncome - totalDeductions) * 0.05).toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
              <p className="text-xs text-purple-600 mt-1">Due to Tax Authority</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm text-gray-700 font-medium">Pending Submissions</p>
                <Calendar className="h-4 w-4 text-gray-600" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{statusCounts.draft}</p>
              <p className="text-xs text-gray-600 mt-1">Awaiting Filing</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Gross Income</p>
              <p className="text-2xl font-bold text-gray-900">
                {totalGrossIncome.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Deductions</p>
              <p className="text-2xl font-bold text-red-600">
                {totalDeductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Taxable Income</p>
              <p className="text-2xl font-bold text-blue-600">
                {totalTaxableIncome.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Tax</p>
              <p className="text-2xl font-bold text-purple-600">
                {totalTaxAmount.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Draft</p>
              <p className="text-3xl font-bold text-gray-900">{statusCounts.draft}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Calculated</p>
              <p className="text-3xl font-bold text-yellow-600">{statusCounts.calculated}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Filed</p>
              <p className="text-3xl font-bold text-green-600">{statusCounts.filed}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Tax Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <div className="w-48">
              <Input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <div className="w-32">
              <Select
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                options={[
                  { value: '2025', label: '2025' },
                  { value: '2024', label: '2024' },
                  { value: '2023', label: '2023' },
                  { value: '2022', label: '2022' },
                ]}
              />
            </div>
            <Button onClick={handleGenerateReport} disabled={isGenerating}>
              <FileText className="h-4 w-4 mr-2" />
              {isGenerating ? 'Generating...' : 'Generate Annual Report'}
            </Button>
          </div>

          <div className="overflow-x-auto">
            <Table data={taxData} columns={columns} />
          </div>
        </CardContent>
      </Card>

      {taxReport && (
        <Card>
          <CardHeader>
            <CardTitle>Annual Tax Report - {taxReport.year}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">Gross Income</p>
                  <p className="text-xl font-bold text-gray-900">
                    {taxReport.total_gross_income.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                  </p>
                </div>
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-gray-600">Deductions</p>
                  <p className="text-xl font-bold text-red-600">
                    {taxReport.total_deductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                  </p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-gray-600">Taxable Income</p>
                  <p className="text-xl font-bold text-blue-600">
                    {taxReport.total_taxable_income.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                  </p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-gray-600">Total Tax</p>
                  <p className="text-xl font-bold text-purple-600">
                    {taxReport.total_tax.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Monthly Breakdown</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Income</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tax</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {taxReport.months.map((item: any, index: number) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {item.month}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.income.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.tax.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
