import { useState } from 'react'
import { TrendingUp, DollarSign, CreditCard } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { LineChart } from '@/components/ui/LineChart'
import { BarChart } from '@/components/ui/BarChart'
import { PieChart } from '@/components/ui/PieChart'
import { AreaChart } from '@/components/ui/AreaChart'
import { dashboardAPI } from '@/lib/api'
import { useQuery } from '@tanstack/react-query'
import { Spinner } from '@/components/ui/Spinner'

export default function FinancialDashboard() {
  const [period, setPeriod] = useState('6months')

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['financial-summary'],
    queryFn: () => dashboardAPI.getFinancialSummary(),
  })

  const { data: revenueExpenseData, isLoading: revenueLoading } = useQuery({
    queryKey: ['revenue-expense-chart', period],
    queryFn: () => dashboardAPI.getChartData('revenue_expense', period),
  })

  const { data: expenseBreakdownData, isLoading: expenseLoading } = useQuery({
    queryKey: ['expense-breakdown-chart', period],
    queryFn: () => dashboardAPI.getChartData('expense_breakdown', period),
  })

  const { data: profitComparisonData, isLoading: profitLoading } = useQuery({
    queryKey: ['profit-comparison-chart', period],
    queryFn: () => dashboardAPI.getChartData('profit_comparison', period),
  })

  const { data: cashFlowData, isLoading: cashFlowLoading } = useQuery({
    queryKey: ['cash-flow-chart', period],
    queryFn: () => dashboardAPI.getChartData('cash_flow', period),
  })

  // Mock data fallback
  const mockSummary = summary || {
    total_revenue: 1250000,
    total_expenses: 850000,
    net_profit: 400000,
    profit_margin: 32,
    payroll_this_month: 120000,
    cod_collected: 85000,
    pending_payments: 35000,
  }

  // Convert to Recharts format
  const mockRevenueExpense = revenueExpenseData || [
    { month: 'Jan', revenue: 180000, expenses: 120000 },
    { month: 'Feb', revenue: 210000, expenses: 135000 },
    { month: 'Mar', revenue: 195000, expenses: 130000 },
    { month: 'Apr', revenue: 225000, expenses: 145000 },
    { month: 'May', revenue: 240000, expenses: 150000 },
    { month: 'Jun', revenue: 250000, expenses: 155000 },
  ]

  const mockExpenseBreakdown = expenseBreakdownData || [
    { name: 'Payroll', value: 45 },
    { name: 'Fuel', value: 20 },
    { name: 'Maintenance', value: 15 },
    { name: 'Accommodation', value: 10 },
    { name: 'Operations', value: 7 },
    { name: 'Other', value: 3 },
  ]

  const mockProfitComparison = profitComparisonData || [
    { month: 'Jan', profit: 60000 },
    { month: 'Feb', profit: 75000 },
    { month: 'Mar', profit: 65000 },
    { month: 'Apr', profit: 80000 },
    { month: 'May', profit: 90000 },
    { month: 'Jun', profit: 95000 },
  ]

  const mockCashFlow = cashFlowData || [
    { month: 'Jan', cashFlow: 50000 },
    { month: 'Feb', cashFlow: 65000 },
    { month: 'Mar', cashFlow: 72000 },
    { month: 'Apr', cashFlow: 85000 },
    { month: 'May', cashFlow: 92000 },
    { month: 'Jun', cashFlow: 105000 },
  ]

  const isLoading = summaryLoading || revenueLoading || expenseLoading || profitLoading || cashFlowLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Financial Dashboard</h1>
        <div className="w-48">
          <Select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            options={[
              { value: '1month', label: 'Last Month' },
              { value: '3months', label: 'Last 3 Months' },
              { value: '6months', label: 'Last 6 Months' },
              { value: '1year', label: 'Last Year' },
            ]}
          />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Revenue</p>
                <p className="text-2xl font-bold text-gray-900">
                  {mockSummary.total_revenue.toLocaleString()} SAR
                </p>
                <div className="flex items-center mt-2 text-green-600">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  <span className="text-sm">+12.5%</span>
                </div>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Expenses</p>
                <p className="text-2xl font-bold text-gray-900">
                  {mockSummary.total_expenses.toLocaleString()} SAR
                </p>
                <div className="flex items-center mt-2 text-red-600">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  <span className="text-sm">+8.3%</span>
                </div>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <CreditCard className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Net Profit</p>
                <p className="text-2xl font-bold text-green-600">
                  {mockSummary.net_profit.toLocaleString()} SAR
                </p>
                <div className="flex items-center mt-2 text-green-600">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  <span className="text-sm">+18.2%</span>
                </div>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Profit Margin</p>
                <p className="text-2xl font-bold text-gray-900">{mockSummary.profit_margin}%</p>
                <div className="flex items-center mt-2 text-green-600">
                  <TrendingUp className="h-4 w-4 mr-1" />
                  <span className="text-sm">+3.2%</span>
                </div>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Payroll This Month</p>
              <p className="text-xl font-bold text-gray-900">{mockSummary.payroll_this_month.toLocaleString()} SAR</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">COD Collected</p>
              <p className="text-xl font-bold text-green-600">{mockSummary.cod_collected.toLocaleString()} SAR</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-sm text-gray-600">Pending Payments</p>
              <p className="text-xl font-bold text-orange-600">{mockSummary.pending_payments.toLocaleString()} SAR</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Revenue vs Expenses Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart
              data={mockRevenueExpense}
              xKey="month"
              yKey={['revenue', 'expenses']}
              height={300}
              colors={['#3b82f6', '#ef4444']}
              formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Expense Breakdown by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <PieChart
              data={mockExpenseBreakdown}
              dataKey="value"
              nameKey="name"
              height={300}
              colors={['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#9ca3af']}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monthly Profit Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <BarChart
              data={mockProfitComparison}
              xKey="month"
              yKey="profit"
              height={300}
              formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cash Flow</CardTitle>
          </CardHeader>
          <CardContent>
            <AreaChart
              data={mockCashFlow}
              xKey="month"
              yKey="cashFlow"
              height={300}
              formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
