import { useState, useEffect } from 'react'
import { Download, Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { couriersAPI } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { Spinner } from '@/components/ui/Spinner'

interface SalaryBreakdown {
  base_salary: number
  housing_allowance: number
  transport_allowance: number
  mobile_allowance: number
  other_allowances: number
  total_allowances: number
  gosi_deduction: number
  loan_deduction: number
  penalty_deduction: number
  other_deductions: number
  total_deductions: number
  gross_salary: number
  net_salary: number
}

export default function SalaryCalculation() {
  const [selectedCourierId, setSelectedCourierId] = useState('')
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7))

  // Allowances
  const [baseSalary, setBaseSalary] = useState(0)
  const [housingAllowance, setHousingAllowance] = useState(0)
  const [transportAllowance, setTransportAllowance] = useState(0)
  const [mobileAllowance, setMobileAllowance] = useState(0)
  const [otherAllowances, setOtherAllowances] = useState(0)

  // Deductions
  const [gosiDeduction, setGosiDeduction] = useState(0)
  const [loanDeduction, setLoanDeduction] = useState(0)
  const [penaltyDeduction, setPenaltyDeduction] = useState(0)
  const [otherDeductions, setOtherDeductions] = useState(0)

  const [salaryHistory, setSalaryHistory] = useState<any[]>([])
  const [breakdown, setBreakdown] = useState<SalaryBreakdown | null>(null)

  const { data: couriers = [], isLoading: couriersLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  // Auto-calculate when employee is selected
  useEffect(() => {
    if (selectedCourierId) {
      const courier = couriers.find((c: any) => c.id.toString() === selectedCourierId)
      if (courier) {
        const base = courier.base_salary || 5000
        setBaseSalary(base)
        setHousingAllowance(base * 0.25)
        setTransportAllowance(base * 0.1)
        setMobileAllowance(200)
        setOtherAllowances(0)

        // Calculate GOSI (9% of base salary)
        setGosiDeduction(base * 0.09)
        setLoanDeduction(0)
        setPenaltyDeduction(0)
        setOtherDeductions(0)
      }
    }
  }, [selectedCourierId, couriers])

  // Auto-calculate breakdown whenever values change
  useEffect(() => {
    calculateSalary()
  }, [
    baseSalary,
    housingAllowance,
    transportAllowance,
    mobileAllowance,
    otherAllowances,
    gosiDeduction,
    loanDeduction,
    penaltyDeduction,
    otherDeductions,
  ])

  const calculateSalary = () => {
    const totalAllowances = housingAllowance + transportAllowance + mobileAllowance + otherAllowances
    const totalDeductions = gosiDeduction + loanDeduction + penaltyDeduction + otherDeductions
    const grossSalary = baseSalary + totalAllowances
    const netSalary = grossSalary - totalDeductions

    const newBreakdown: SalaryBreakdown = {
      base_salary: baseSalary,
      housing_allowance: housingAllowance,
      transport_allowance: transportAllowance,
      mobile_allowance: mobileAllowance,
      other_allowances: otherAllowances,
      total_allowances: totalAllowances,
      gosi_deduction: gosiDeduction,
      loan_deduction: loanDeduction,
      penalty_deduction: penaltyDeduction,
      other_deductions: otherDeductions,
      total_deductions: totalDeductions,
      gross_salary: grossSalary,
      net_salary: netSalary,
    }

    setBreakdown(newBreakdown)
  }

  const handleSaveBreakdown = () => {
    if (!selectedCourierId || !breakdown) {
      alert('Please select an employee and calculate salary')
      return
    }

    const courier = couriers.find((c: any) => c.id.toString() === selectedCourierId)
    const newRecord = {
      id: salaryHistory.length + 1,
      employee_id: selectedCourierId,
      employee_name: courier?.name || 'Unknown',
      month: selectedMonth,
      ...breakdown,
      saved_at: new Date().toISOString(),
    }

    setSalaryHistory([newRecord, ...salaryHistory])
    alert('Salary breakdown saved')
  }

  const handleExportSlip = async () => {
    if (!selectedCourierId || !breakdown) {
      alert('Please calculate salary first')
      return
    }

    alert('Salary slip export functionality coming soon')
  }

  const historyColumns = [
    { key: 'id', header: 'ID' },
    { key: 'employee_name', header: 'Employee' },
    {
      key: 'month',
      header: 'Month',
      render: (row: any) => {
        const date = new Date(row.month + '-01')
        return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' })
      },
    },
    {
      key: 'base_salary',
      header: 'Base',
      render: (row: any) => `${row.base_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR`,
    },
    {
      key: 'total_allowances',
      header: 'Allowances',
      render: (row: any) => (
        <span className="text-green-600">
          +{row.total_allowances.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
        </span>
      ),
    },
    {
      key: 'total_deductions',
      header: 'Deductions',
      render: (row: any) => (
        <span className="text-red-600">
          -{row.total_deductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
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
      key: 'saved_at',
      header: 'Date',
      render: (row: any) => new Date(row.saved_at).toLocaleDateString(),
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
        <h1 className="text-2xl font-bold">Salary Calculation</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Input Section */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Employee Selection</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Employee *</label>
                  <Select
                    value={selectedCourierId}
                    onChange={(e) => setSelectedCourierId(e.target.value)}
                    options={[
                      { value: '', label: 'Select employee...' },
                      ...couriers.map((c: any) => ({ value: c.id.toString(), label: `${c.id} - ${c.name}` })),
                    ]}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Month</label>
                  <Input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)} />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Salary Components</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Base Salary</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Base Salary (SAR)</label>
                  <Input
                    type="number"
                    step="0.01"
                    value={baseSalary}
                    onChange={(e) => setBaseSalary(parseFloat(e.target.value) || 0)}
                    placeholder="5000.00"
                  />
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Allowances</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Housing Allowance</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={housingAllowance}
                      onChange={(e) => setHousingAllowance(parseFloat(e.target.value) || 0)}
                      placeholder="1250.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Transport Allowance</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={transportAllowance}
                      onChange={(e) => setTransportAllowance(parseFloat(e.target.value) || 0)}
                      placeholder="500.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Mobile Allowance</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={mobileAllowance}
                      onChange={(e) => setMobileAllowance(parseFloat(e.target.value) || 0)}
                      placeholder="200.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Other Allowances</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={otherAllowances}
                      onChange={(e) => setOtherAllowances(parseFloat(e.target.value) || 0)}
                      placeholder="0.00"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Deductions</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">GOSI (9%)</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={gosiDeduction}
                      onChange={(e) => setGosiDeduction(parseFloat(e.target.value) || 0)}
                      placeholder="450.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Loan Installment</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={loanDeduction}
                      onChange={(e) => setLoanDeduction(parseFloat(e.target.value) || 0)}
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Penalties</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={penaltyDeduction}
                      onChange={(e) => setPenaltyDeduction(parseFloat(e.target.value) || 0)}
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Other Deductions</label>
                    <Input
                      type="number"
                      step="0.01"
                      value={otherDeductions}
                      onChange={(e) => setOtherDeductions(parseFloat(e.target.value) || 0)}
                      placeholder="0.00"
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t">
                <Button onClick={handleSaveBreakdown}>
                  <Save className="h-4 w-4 mr-2" />
                  Save Breakdown
                </Button>
                <Button onClick={handleExportSlip} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export Salary Slip
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Breakdown Section */}
        <div className="space-y-6">
          {breakdown && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle>Salary Breakdown</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Base Salary:</span>
                      <span className="font-medium">
                        {breakdown.base_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                      </span>
                    </div>

                    <div className="pt-2 border-t">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span className="font-medium">Allowances:</span>
                      </div>
                      <div className="flex justify-between text-sm pl-4">
                        <span className="text-gray-600">Housing:</span>
                        <span className="text-green-600">
                          +{breakdown.housing_allowance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm pl-4">
                        <span className="text-gray-600">Transport:</span>
                        <span className="text-green-600">
                          +{breakdown.transport_allowance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm pl-4">
                        <span className="text-gray-600">Mobile:</span>
                        <span className="text-green-600">
                          +{breakdown.mobile_allowance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      {breakdown.other_allowances > 0 && (
                        <div className="flex justify-between text-sm pl-4">
                          <span className="text-gray-600">Other:</span>
                          <span className="text-green-600">
                            +{breakdown.other_allowances.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                      )}
                      <div className="flex justify-between text-sm font-medium mt-2 pl-4 pt-2 border-t">
                        <span>Total Allowances:</span>
                        <span className="text-green-600">
                          +{breakdown.total_allowances.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                        </span>
                      </div>
                    </div>

                    <div className="pt-2 border-t">
                      <div className="flex justify-between text-sm font-medium mb-2">
                        <span className="text-gray-900">Gross Salary:</span>
                        <span className="text-blue-600">
                          {breakdown.gross_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                        </span>
                      </div>
                    </div>

                    <div className="pt-2 border-t">
                      <div className="flex justify-between text-sm text-gray-600 mb-2">
                        <span className="font-medium">Deductions:</span>
                      </div>
                      <div className="flex justify-between text-sm pl-4">
                        <span className="text-gray-600">GOSI (9%):</span>
                        <span className="text-red-600">
                          -{breakdown.gosi_deduction.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </span>
                      </div>
                      {breakdown.loan_deduction > 0 && (
                        <div className="flex justify-between text-sm pl-4">
                          <span className="text-gray-600">Loan:</span>
                          <span className="text-red-600">
                            -{breakdown.loan_deduction.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                      )}
                      {breakdown.penalty_deduction > 0 && (
                        <div className="flex justify-between text-sm pl-4">
                          <span className="text-gray-600">Penalties:</span>
                          <span className="text-red-600">
                            -{breakdown.penalty_deduction.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                      )}
                      {breakdown.other_deductions > 0 && (
                        <div className="flex justify-between text-sm pl-4">
                          <span className="text-gray-600">Other:</span>
                          <span className="text-red-600">
                            -{breakdown.other_deductions.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                      )}
                      <div className="flex justify-between text-sm font-medium mt-2 pl-4 pt-2 border-t">
                        <span>Total Deductions:</span>
                        <span className="text-red-600">
                          -{breakdown.total_deductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                        </span>
                      </div>
                    </div>

                    <div className="pt-3 border-t-2">
                      <div className="flex justify-between">
                        <span className="text-lg font-bold text-gray-900">Net Salary:</span>
                        <span className="text-lg font-bold text-green-600">
                          {breakdown.net_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="pt-6">
                  <div className="text-center">
                    <p className="text-sm text-blue-800 font-medium">Monthly Take-Home</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">
                      {breakdown.net_salary.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </p>
                    <p className="text-sm text-blue-700 mt-1">SAR</p>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>

      {salaryHistory.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Salary History</CardTitle>
          </CardHeader>
          <CardContent>
            <Table data={salaryHistory} columns={historyColumns} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
