import { useState } from 'react'
import { Download, CheckCircle, XCircle, Clock, Play } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Pagination } from '@/components/ui/Pagination'
import { payrollAPI, couriersAPI } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { Spinner } from '@/components/ui/Spinner'

interface PayrollRecord {
  id: string | number
  employee_id: string | number
  employee_name: string
  base_salary: number
  allowances: number
  housing_allowance: number
  transport_allowance: number
  deductions: number
  gosi_deduction: number
  loan_deduction: number
  net_salary: number
  status: string
  month: string
}

export default function Payroll() {
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7))
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10

  const { data: couriers = [], isLoading: couriersLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  // Generate mock payroll data
  const generatePayrollData = () => {
    if (!couriers || couriers.length === 0) return []

    return couriers.map((courier: any, index: number) => {
      const baseSalary = courier.base_salary || 5000
      const housingAllowance = baseSalary * 0.25
      const transportAllowance = baseSalary * 0.1
      const totalAllowances = housingAllowance + transportAllowance

      const gosiDeduction = baseSalary * 0.09
      const loanDeduction = index % 3 === 0 ? 500 : 0
      const totalDeductions = gosiDeduction + loanDeduction

      const netSalary = baseSalary + totalAllowances - totalDeductions

      // Randomize status for demo
      let status = 'draft'
      if (index % 4 === 0) status = 'approved'
      if (index % 4 === 1) status = 'paid'
      if (index % 4 === 2) status = 'processing'

      return {
        id: courier.id,
        employee_id: courier.id,
        employee_name: courier.name || `Courier ${courier.id}`,
        base_salary: baseSalary,
        allowances: totalAllowances,
        housing_allowance: housingAllowance,
        transport_allowance: transportAllowance,
        deductions: totalDeductions,
        gosi_deduction: gosiDeduction,
        loan_deduction: loanDeduction,
        net_salary: netSalary,
        status,
        month: selectedMonth,
      }
    })
  }

  const payrollData = generatePayrollData()

  // Filter by status
  const filteredData = statusFilter === 'all'
    ? payrollData
    : payrollData.filter((item: PayrollRecord) => item.status === statusFilter)

  const totalPages = Math.ceil(filteredData.length / pageSize)
  const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  // Calculate summary
  const totalBaseSalary = filteredData.reduce((sum: number, item: PayrollRecord) => sum + item.base_salary, 0)
  const totalAllowances = filteredData.reduce((sum: number, item: PayrollRecord) => sum + item.allowances, 0)
  const totalDeductions = filteredData.reduce((sum: number, item: PayrollRecord) => sum + item.deductions, 0)
  const totalNetSalary = filteredData.reduce((sum: number, item: PayrollRecord) => sum + item.net_salary, 0)

  const statusCounts = {
    draft: payrollData.filter((p: PayrollRecord) => p.status === 'draft').length,
    approved: payrollData.filter((p: PayrollRecord) => p.status === 'approved').length,
    processing: payrollData.filter((p: PayrollRecord) => p.status === 'processing').length,
    paid: payrollData.filter((p: PayrollRecord) => p.status === 'paid').length,
  }

  const handleGeneratePayroll = () => {
    alert('Generating payroll for all employees...')
    // In real app, this would call the API
  }

  const handleApproveAll = () => {
    const draftCount = statusCounts.draft
    if (draftCount === 0) {
      alert('No draft payroll records to approve')
      return
    }
    alert(`Approving ${draftCount} payroll records...`)
    // In real app, this would call the API
  }

  const handleProcessPayroll = () => {
    const approvedCount = statusCounts.approved
    if (approvedCount === 0) {
      alert('No approved payroll records to process')
      return
    }
    alert(`Processing ${approvedCount} payroll records...`)
    // In real app, this would call the API
  }

  const handleExportExcel = async () => {
    try {
      const blob = await payrollAPI.export(selectedMonth)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Payroll_${selectedMonth}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      alert('Export functionality coming soon')
    }
  }

  const handleApproveOne = (id: number) => {
    alert(`Approving payroll for employee ${id}`)
  }

  const handleRejectOne = (id: number) => {
    alert(`Rejecting payroll for employee ${id}`)
  }

  const columns = [
    {
      key: 'employee_id',
      header: 'Employee',
      render: (row: any) => (
        <div>
          <div className="font-medium">{row.employee_name}</div>
          <div className="text-sm text-gray-500">ID: {row.employee_id}</div>
        </div>
      ),
    },
    {
      key: 'base_salary',
      header: 'Base Salary',
      render: (row: any) => (
        <span className="font-medium">{row.base_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR</span>
      ),
    },
    {
      key: 'allowances',
      header: 'Allowances',
      render: (row: any) => (
        <span className="text-green-600">
          +{row.allowances.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'deductions',
      header: 'Deductions',
      render: (row: any) => (
        <span className="text-red-600">
          -{row.deductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'net_salary',
      header: 'Net Salary',
      render: (row: any) => (
        <span className="font-bold text-gray-900">
          {row.net_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const variants: Record<string, 'default' | 'success' | 'warning' | 'danger'> = {
          draft: 'default',
          approved: 'success',
          processing: 'warning',
          paid: 'success',
        }
        return <Badge variant={variants[row.status] || 'default'}>{row.status}</Badge>
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-1">
          {row.status === 'draft' && (
            <>
              <Button size="sm" variant="ghost" onClick={() => handleApproveOne(row.id)} title="Approve">
                <CheckCircle className="h-4 w-4 text-green-600" />
              </Button>
              <Button size="sm" variant="ghost" onClick={() => handleRejectOne(row.id)} title="Reject">
                <XCircle className="h-4 w-4 text-red-600" />
              </Button>
            </>
          )}
          {row.status === 'paid' && <span className="text-sm text-gray-500">Completed</span>}
          {row.status === 'processing' && (
            <span className="text-sm text-orange-600 flex items-center">
              <Clock className="h-3 w-3 mr-1" />
              Processing
            </span>
          )}
        </div>
      ),
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
        <h1 className="text-2xl font-bold">Payroll Processing</h1>
        <div className="flex gap-2">
          <Button onClick={handleGeneratePayroll} variant="outline">
            <Play className="h-4 w-4 mr-2" />
            Generate Payroll
          </Button>
          <Button onClick={handleExportExcel}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Base Salary</p>
              <p className="text-2xl font-bold text-gray-900">
                {totalBaseSalary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Allowances</p>
              <p className="text-2xl font-bold text-green-600">
                +{totalAllowances.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Deductions</p>
              <p className="text-2xl font-bold text-red-600">
                -{totalDeductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Net Payroll</p>
              <p className="text-2xl font-bold text-purple-600">
                {totalNetSalary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-3xl font-bold text-green-600">{statusCounts.approved}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Processing</p>
              <p className="text-3xl font-bold text-orange-600">{statusCounts.processing}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Paid</p>
              <p className="text-3xl font-bold text-blue-600">{statusCounts.paid}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Batch Actions */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium text-blue-900">Batch Actions</h3>
              <p className="text-sm text-blue-700 mt-1">Process multiple payroll records at once</p>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleApproveAll} variant="outline" size="sm">
                <CheckCircle className="h-4 w-4 mr-2" />
                Approve All Draft ({statusCounts.draft})
              </Button>
              <Button onClick={handleProcessPayroll} size="sm">
                <Play className="h-4 w-4 mr-2" />
                Process Approved ({statusCounts.approved})
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Payroll Table</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <div className="w-48">
              <Input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
              />
            </div>
            <div className="w-48">
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Status' },
                  { value: 'draft', label: 'Draft' },
                  { value: 'approved', label: 'Approved' },
                  { value: 'processing', label: 'Processing' },
                  { value: 'paid', label: 'Paid' },
                ]}
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <Table data={paginatedData} columns={columns} />
          </div>

          <div className="mt-4">
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalItems={filteredData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
