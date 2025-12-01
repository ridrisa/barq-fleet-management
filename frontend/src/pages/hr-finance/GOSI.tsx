import { useState } from 'react'
import { Download, Search, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Pagination } from '@/components/ui/Pagination'
import { gosiAPI, couriersAPI } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { Spinner } from '@/components/ui/Spinner'

interface GOSIRecord {
  id: string | number
  employee_id: string | number
  employee_name: string
  salary: number
  employee_contribution: number
  employer_contribution: number
  total: number
  month: string
}

export default function GOSI() {
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7))
  const [searchTerm, setSearchTerm] = useState('')

  const { data: couriers = [], isLoading: couriersLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  // Generate mock GOSI data based on couriers
  const generateGOSIData = () => {
    if (!couriers || couriers.length === 0) return []

    return couriers.map((courier: any) => {
      const baseSalary = courier.base_salary || 5000
      const employeeContribution = baseSalary * 0.09
      const employerContribution = baseSalary * 0.09
      const totalContribution = employeeContribution + employerContribution

      return {
        id: courier.id,
        employee_id: courier.id,
        employee_name: courier.name || `Courier ${courier.id}`,
        salary: baseSalary,
        employee_contribution: employeeContribution,
        employer_contribution: employerContribution,
        total: totalContribution,
        month: selectedMonth,
      }
    })
  }

  const gosiData = generateGOSIData()

  // Filter data by search term
  const filteredData = gosiData.filter((item: GOSIRecord) =>
    item.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.employee_id.toString().includes(searchTerm)
  )

  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10
  const totalPages = Math.ceil(filteredData.length / pageSize)
  const paginatedData = filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  // Calculate summary
  const totalEmployees = filteredData.length
  const totalContributions = filteredData.reduce((sum: number, item: GOSIRecord) => sum + item.total, 0)
  const totalEmployeeContributions = filteredData.reduce((sum: number, item: GOSIRecord) => sum + item.employee_contribution, 0)
  const totalEmployerContributions = filteredData.reduce((sum: number, item: GOSIRecord) => sum + item.employer_contribution, 0)

  const handleExportExcel = async () => {
    try {
      const blob = await gosiAPI.export(selectedMonth)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `GOSI_${selectedMonth}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export functionality coming soon')
    }
  }

  const columns = [
    {
      key: 'employee_id',
      header: 'Employee ID',
      sortable: true,
    },
    {
      key: 'employee_name',
      header: 'Employee Name',
    },
    {
      key: 'salary',
      header: 'Salary (SAR)',
      render: (row: any) => row.salary.toLocaleString('en-US', { minimumFractionDigits: 2 }),
    },
    {
      key: 'employee_contribution',
      header: 'Employee (9%)',
      render: (row: any) => (
        <span className="text-blue-600 font-medium">
          {row.employee_contribution.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'employer_contribution',
      header: 'Employer (9%)',
      render: (row: any) => (
        <span className="text-green-600 font-medium">
          {row.employer_contribution.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'total',
      header: 'Total (18%)',
      render: (row: any) => (
        <span className="font-bold text-gray-900">
          {row.total.toLocaleString('en-US', { minimumFractionDigits: 2 })}
        </span>
      ),
    },
    {
      key: 'month',
      header: 'Month',
      render: (row: any) => {
        const date = new Date(row.month + '-01')
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
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
        <h1 className="text-2xl font-bold">GOSI Management</h1>
        <Button onClick={handleExportExcel}>
          <Download className="h-4 w-4 mr-2" />
          Export to Excel
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Employees</p>
              <p className="text-3xl font-bold text-gray-900">{totalEmployees}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Employee Contributions</p>
              <p className="text-2xl font-bold text-blue-600">
                {totalEmployeeContributions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
              <p className="text-xs text-gray-500 mt-1">9% of salary</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Employer Contributions</p>
              <p className="text-2xl font-bold text-green-600">
                {totalEmployerContributions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
              <p className="text-xs text-gray-500 mt-1">9% of salary</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Contributions</p>
              <p className="text-2xl font-bold text-purple-600">
                {totalContributions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
              <p className="text-xs text-gray-500 mt-1">18% of salary</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-blue-400"
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
              <h3 className="text-sm font-medium text-blue-800">GOSI Contribution Rates (Saudi Arabia)</h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Employee contribution: 9% of monthly salary</li>
                  <li>Employer contribution: 9% of monthly salary</li>
                  <li>Total contribution: 18% of monthly salary</li>
                  <li>Covers: Retirement, disability, death, and occupational hazards</li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>GOSI Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search by employee name or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <div className="w-48">
              <Input
                type="month"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                leftIcon={<Calendar className="h-4 w-4 text-gray-400" />}
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

      {/* Summary Footer */}
      <Card className="bg-gray-50">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-gray-600">Monthly Payroll Base</p>
              <p className="text-xl font-bold text-gray-900">
                {filteredData.reduce((sum: number, item: GOSIRecord) => sum + item.salary, 0).toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                })}{' '}
                SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Deductions (9%)</p>
              <p className="text-xl font-bold text-blue-600">
                {totalEmployeeContributions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Company Burden (9%)</p>
              <p className="text-xl font-bold text-green-600">
                {totalEmployerContributions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
