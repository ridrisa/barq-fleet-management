import { useState } from 'react'
import { Download, Calculator, Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { eosAPI, couriersAPI } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { Spinner } from '@/components/ui/Spinner'

interface EOSCalculationResult {
  years_of_service: number
  months_of_service: number
  first_two_years_benefit: number
  next_three_years_benefit: number
  remaining_years_benefit: number
  total_eos: number
  deductions: number
  net_eos: number
  breakdown: Array<{
    period: string
    years: number
    rate: string
    amount: number
  }>
}

export default function EOSCalculation() {
  const [courierId, setCourierId] = useState('')
  const [joiningDate, setJoiningDate] = useState('')
  const [terminationDate, setTerminationDate] = useState('')
  const [lastSalary, setLastSalary] = useState('')
  const [terminationReason, setTerminationReason] = useState<'resignation' | 'termination'>('termination')
  const [calculationResult, setCalculationResult] = useState<EOSCalculationResult | null>(null)
  const [isCalculating, setIsCalculating] = useState(false)
  const [history, setHistory] = useState<any[]>([])

  const { data: couriers = [], isLoading: couriersLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  const calculateEOS = () => {
    if (!joiningDate || !terminationDate || !lastSalary) {
      alert('Please fill all required fields')
      return
    }

    setIsCalculating(true)

    const joining = new Date(joiningDate)
    const termination = new Date(terminationDate)
    const diffTime = Math.abs(termination.getTime() - joining.getTime())
    const diffYears = diffTime / (1000 * 60 * 60 * 24 * 365.25)
    const years = Math.floor(diffYears)
    const months = Math.floor((diffYears - years) * 12)

    const salary = parseFloat(lastSalary)
    const monthSalary = salary / 12
    const breakdown: Array<{ period: string; years: number; rate: string; amount: number }> = []

    let firstTwoYears = 0
    let nextThreeYears = 0
    let remainingYears = 0

    // Calculate based on Saudi labor law
    if (years < 2) {
      // Less than 2 years: 0.5 month salary per year (if termination, 0 if resignation)
      const rate = terminationReason === 'resignation' ? 0 : 0.5
      firstTwoYears = diffYears * monthSalary * rate
      breakdown.push({
        period: 'First 2 years',
        years: diffYears,
        rate: terminationReason === 'resignation' ? '0 (Resignation)' : '0.5 month/year',
        amount: firstTwoYears,
      })
    } else if (years >= 2 && years < 5) {
      // 2-5 years: 0.5 month for first 2 years + 1 month per year after
      firstTwoYears = 2 * monthSalary * 0.5
      nextThreeYears = (diffYears - 2) * monthSalary
      breakdown.push(
        {
          period: 'First 2 years',
          years: 2,
          rate: '0.5 month/year',
          amount: firstTwoYears,
        },
        {
          period: 'Years 2-5',
          years: diffYears - 2,
          rate: '1 month/year',
          amount: nextThreeYears,
        }
      )
    } else {
      // 5+ years: 1 month salary per year (full benefit)
      firstTwoYears = 2 * monthSalary * 0.5
      nextThreeYears = 3 * monthSalary
      remainingYears = (diffYears - 5) * monthSalary
      breakdown.push(
        {
          period: 'First 2 years',
          years: 2,
          rate: '0.5 month/year',
          amount: firstTwoYears,
        },
        {
          period: 'Years 2-5',
          years: 3,
          rate: '1 month/year',
          amount: nextThreeYears,
        },
        {
          period: 'Years 5+',
          years: diffYears - 5,
          rate: '1 month/year',
          amount: remainingYears,
        }
      )
    }

    const totalEOS = firstTwoYears + nextThreeYears + remainingYears
    const deductions = terminationReason === 'resignation' && years < 5 ? totalEOS * 0.1 : 0
    const netEOS = totalEOS - deductions

    const result: EOSCalculationResult = {
      years_of_service: years,
      months_of_service: months,
      first_two_years_benefit: firstTwoYears,
      next_three_years_benefit: nextThreeYears,
      remaining_years_benefit: remainingYears,
      total_eos: totalEOS,
      deductions,
      net_eos: netEOS,
      breakdown,
    }

    setCalculationResult(result)
    setIsCalculating(false)
  }

  const handleExportPDF = async () => {
    if (!courierId || !calculationResult) {
      alert('Please calculate EOS first')
      return
    }

    try {
      const blob = await eosAPI.export(parseInt(courierId))
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `EOS_Calculation_${courierId}_${new Date().toISOString().split('T')[0]}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export functionality coming soon')
    }
  }

  const handleSaveCalculation = () => {
    if (!calculationResult) return

    const newRecord = {
      id: history.length + 1,
      courier_id: courierId,
      calculated_at: new Date().toISOString(),
      joining_date: joiningDate,
      termination_date: terminationDate,
      last_salary: parseFloat(lastSalary),
      termination_reason: terminationReason,
      total_eos: calculationResult.total_eos,
      net_eos: calculationResult.net_eos,
    }

    setHistory([newRecord, ...history])
    alert('Calculation saved to history')
  }

  const columns = [
    { key: 'id', header: 'ID' },
    { key: 'courier_id', header: 'Employee ID' },
    {
      key: 'calculated_at',
      header: 'Date',
      render: (row: any) => new Date(row.calculated_at).toLocaleDateString(),
    },
    { key: 'last_salary', header: 'Last Salary', render: (row: any) => `${row.last_salary.toFixed(2)} SAR` },
    {
      key: 'termination_reason',
      header: 'Reason',
      render: (row: any) => (
        <Badge variant={row.termination_reason === 'termination' ? 'danger' : 'warning'}>
          {row.termination_reason}
        </Badge>
      ),
    },
    { key: 'total_eos', header: 'Total EOS', render: (row: any) => `${row.total_eos.toFixed(2)} SAR` },
    { key: 'net_eos', header: 'Net EOS', render: (row: any) => `${row.net_eos.toFixed(2)} SAR` },
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
        <h1 className="text-2xl font-bold">End of Service (EOS) Calculation</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Calculate EOS Benefits</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Employee ID</label>
              <Select
                value={courierId}
                onChange={(e) => setCourierId(e.target.value)}
                options={[
                  { value: '', label: 'Select employee...' },
                  ...couriers.map((c: any) => ({ value: c.id.toString(), label: `${c.id} - ${c.name}` })),
                ]}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Joining Date *</label>
              <Input type="date" value={joiningDate} onChange={(e) => setJoiningDate(e.target.value)} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Termination Date *</label>
              <Input type="date" value={terminationDate} onChange={(e) => setTerminationDate(e.target.value)} />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Last Monthly Salary (SAR) *</label>
              <Input
                type="number"
                step="0.01"
                value={lastSalary}
                onChange={(e) => setLastSalary(e.target.value)}
                placeholder="5000.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Termination Reason</label>
              <Select
                value={terminationReason}
                onChange={(e) => setTerminationReason(e.target.value as 'resignation' | 'termination')}
                options={[
                  { value: 'termination', label: 'Termination by Employer' },
                  { value: 'resignation', label: 'Resignation by Employee' },
                ]}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={calculateEOS} disabled={isCalculating}>
              <Calculator className="h-4 w-4 mr-2" />
              Calculate EOS
            </Button>
          </div>
        </CardContent>
      </Card>

      {calculationResult && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>EOS Calculation Result</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <p className="text-sm text-gray-600">Years of Service</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {calculationResult.years_of_service} years {calculationResult.months_of_service} months
                        </p>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <p className="text-sm text-gray-600">Total EOS Benefit</p>
                        <p className="text-2xl font-bold text-blue-600">{calculationResult.total_eos.toFixed(2)} SAR</p>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-center">
                        <p className="text-sm text-gray-600">Net EOS (After Deductions)</p>
                        <p className="text-2xl font-bold text-green-600">{calculationResult.net_eos.toFixed(2)} SAR</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-3">Detailed Breakdown</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Period
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Years
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Rate
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Amount (SAR)
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {calculationResult.breakdown.map((item, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {item.period}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {item.years.toFixed(2)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.rate}</td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {item.amount.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                        <tr className="bg-gray-50 font-semibold">
                          <td colSpan={3} className="px-6 py-4 text-right text-sm text-gray-900">
                            Total EOS:
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {calculationResult.total_eos.toFixed(2)}
                          </td>
                        </tr>
                        {calculationResult.deductions > 0 && (
                          <tr className="bg-red-50">
                            <td colSpan={3} className="px-6 py-4 text-right text-sm text-red-600">
                              Deductions:
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                              -{calculationResult.deductions.toFixed(2)}
                            </td>
                          </tr>
                        )}
                        <tr className="bg-green-50 font-bold">
                          <td colSpan={3} className="px-6 py-4 text-right text-sm text-green-700">
                            Net EOS Payable:
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-700">
                            {calculationResult.net_eos.toFixed(2)}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleSaveCalculation}>
                    <Save className="h-4 w-4 mr-2" />
                    Save Calculation
                  </Button>
                  <Button onClick={handleExportPDF} variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Export to PDF
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Calculation History</CardTitle>
          </CardHeader>
          <CardContent>
            <Table data={history} columns={columns} />
          </CardContent>
        </Card>
      )}
    </div>
  )
}
