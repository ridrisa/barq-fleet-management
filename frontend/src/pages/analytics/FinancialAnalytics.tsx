import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { DollarSign, TrendingUp, TrendingDown, PieChart as PieIcon, Download } from 'lucide-react'
import { KPICard, LineChart, PieChart, AreaChart, BarChart, Select, DateRangePicker, Button, Card, CardContent, Table, Spinner } from '@/components/ui'
import { dashboardAPI, expensesAPI } from '@/lib/api'

export default function FinancialAnalytics() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })
  const [comparisonPeriod, setComparisonPeriod] = useState('month')

  // Fetch financial data
  const { data: _financialSummary, isLoading: summaryLoading } = useQuery({
    queryKey: ['financial-summary'],
    queryFn: () => dashboardAPI.getFinancialSummary(),
  })

  const { data: _expenses } = useQuery({
    queryKey: ['expenses'],
    queryFn: () => expensesAPI.getAll(),
  })

  const handleExport = () => {
    // TODO: Implement export functionality
  }

  // Mock data
  const revenueExpensesData = [
    { month: 'Jan', revenue: 285000, expenses: 198000, profit: 87000 },
    { month: 'Feb', revenue: 312000, expenses: 215000, profit: 97000 },
    { month: 'Mar', revenue: 298000, expenses: 205000, profit: 93000 },
    { month: 'Apr', revenue: 335000, expenses: 228000, profit: 107000 },
    { month: 'May', revenue: 352000, expenses: 238000, profit: 114000 },
    { month: 'Jun', revenue: 368000, expenses: 245000, profit: 123000 },
  ]

  const costCategoriesData = [
    { name: 'Fleet Operations', value: 98000 },
    { name: 'Personnel', value: 85000 },
    { name: 'Fuel', value: 45000 },
    { name: 'Maintenance', value: 28000 },
    { name: 'Insurance', value: 22000 },
    { name: 'Other', value: 12000 },
  ]

  const profitMarginData = [
    { month: 'Jan', margin: 30.5, revenue: 285000 },
    { month: 'Feb', margin: 31.1, revenue: 312000 },
    { month: 'Mar', margin: 31.2, revenue: 298000 },
    { month: 'Apr', margin: 31.9, revenue: 335000 },
    { month: 'May', margin: 32.4, revenue: 352000 },
    { month: 'Jun', margin: 33.4, revenue: 368000 },
  ]

  const cashFlowData = [
    { month: 'Jan', inflow: 285000, outflow: 198000, net: 87000 },
    { month: 'Feb', inflow: 312000, outflow: 215000, net: 97000 },
    { month: 'Mar', inflow: 298000, outflow: 205000, net: 93000 },
    { month: 'Apr', inflow: 335000, outflow: 228000, net: 107000 },
    { month: 'May', inflow: 352000, outflow: 238000, net: 114000 },
    { month: 'Jun', inflow: 368000, outflow: 245000, net: 123000 },
  ]

  // Calculate month-over-month changes
  const currentMonth = revenueExpensesData[revenueExpensesData.length - 1]
  const previousMonth = revenueExpensesData[revenueExpensesData.length - 2]
  const revenueChange = ((currentMonth.revenue - previousMonth.revenue) / previousMonth.revenue * 100).toFixed(1)
  const expensesChange = ((currentMonth.expenses - previousMonth.expenses) / previousMonth.expenses * 100).toFixed(1)
  const profitChange = ((currentMonth.profit - previousMonth.profit) / previousMonth.profit * 100).toFixed(1)
  const roiChange = ((currentMonth.profit / currentMonth.expenses * 100) - (previousMonth.profit / previousMonth.expenses * 100)).toFixed(1)

  const topExpenseCategories = [
    { category: 'Fleet Operations', amount: 98000, percentage: 33.8 },
    { category: 'Personnel', amount: 85000, percentage: 29.3 },
    { category: 'Fuel', amount: 45000, percentage: 15.5 },
    { category: 'Maintenance', amount: 28000, percentage: 9.7 },
    { category: 'Insurance', amount: 22000, percentage: 7.6 },
  ]

  const profitabilityByService = [
    { service: 'Standard Delivery', revenue: 185000, cost: 128000, profit: 57000, margin: 30.8 },
    { service: 'Express Delivery', revenue: 95000, cost: 58000, profit: 37000, margin: 38.9 },
    { service: 'COD Service', revenue: 62000, cost: 42000, profit: 20000, margin: 32.3 },
    { service: 'Special Handling', revenue: 26000, cost: 17000, profit: 9000, margin: 34.6 },
  ]

  const budgetStatus = [
    { department: 'Operations', budget: 120000, actual: 98000, variance: 22000, status: 'Under' },
    { department: 'Fleet', budget: 90000, actual: 85000, variance: 5000, status: 'Under' },
    { department: 'HR', budget: 50000, actual: 52000, variance: -2000, status: 'Over' },
    { department: 'Marketing', budget: 30000, actual: 28000, variance: 2000, status: 'Under' },
  ]

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Financial Analytics</h1>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Select
            value={comparisonPeriod}
            onChange={(e) => setComparisonPeriod(e.target.value)}
          >
            <option value="month">Month-over-Month</option>
            <option value="quarter">Quarter-over-Quarter</option>
            <option value="year">Year-over-Year</option>
          </Select>
          <DateRangePicker
            startDate={dateRange.start}
            endDate={dateRange.end}
            onRangeChange={(start, end) => setDateRange({ start, end })}
          />
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Revenue"
          value={`${currentMonth.revenue.toLocaleString()} SAR`}
          change={parseFloat(revenueChange)}
          trend={parseFloat(revenueChange) >= 0 ? 'up' : 'down'}
          icon={<DollarSign className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="Expenses"
          value={`${currentMonth.expenses.toLocaleString()} SAR`}
          change={parseFloat(expensesChange)}
          trend={parseFloat(expensesChange) >= 0 ? 'up' : 'down'}
          icon={<TrendingDown className="w-6 h-6" />}
          color="red"
        />
        <KPICard
          title="Profit"
          value={`${currentMonth.profit.toLocaleString()} SAR`}
          change={parseFloat(profitChange)}
          trend={parseFloat(profitChange) >= 0 ? 'up' : 'down'}
          icon={<TrendingUp className="w-6 h-6" />}
          color="blue"
        />
        <KPICard
          title="ROI"
          value={`${(currentMonth.profit / currentMonth.expenses * 100).toFixed(1)}%`}
          change={parseFloat(roiChange)}
          trend={parseFloat(roiChange) >= 0 ? 'up' : 'down'}
          icon={<PieIcon className="w-6 h-6" />}
          color="purple"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={revenueExpensesData}
          xKey="month"
          yKey={['revenue', 'expenses']}
          title="Revenue vs Expenses"
          height={300}
          colors={['#10b981', '#ef4444']}
          formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
        />

        <PieChart
          data={costCategoriesData}
          dataKey="value"
          nameKey="name"
          title="Cost Categories"
          height={300}
          showLabels={false}
        />

        <AreaChart
          data={profitMarginData}
          xKey="month"
          yKey={['margin']}
          title="Profit Margin Trend"
          height={300}
          colors={['#3b82f6']}
          formatYAxis={(value) => `${Number(value)}%`}
        />

        <AreaChart
          data={cashFlowData}
          xKey="month"
          yKey={['inflow', 'outflow', 'net']}
          title="Cash Flow Analysis"
          height={300}
          colors={['#10b981', '#ef4444', '#3b82f6']}
          formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
        />

        <BarChart
          data={revenueExpensesData}
          xKey="month"
          yKey={['revenue', 'expenses']}
          title="Budget vs Actual (Per Department)"
          height={300}
          colors={['#10b981', '#ef4444']}
          formatYAxis={(value) => `${(Number(value) / 1000).toFixed(0)}K`}
        />
      </div>

      {/* Tables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Top Expense Categories</h3>
            <Table
              data={topExpenseCategories}
              columns={[
                { key: 'category', header: 'Category' },
                { key: 'amount', header: 'Amount', render: (row: any) => `${row.amount.toLocaleString()} SAR` },
                { key: 'percentage', header: '%', render: (row: any) => `${row.percentage}%` },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Profitability by Service Type</h3>
            <Table
              data={profitabilityByService}
              columns={[
                { key: 'service', header: 'Service' },
                { key: 'profit', header: 'Profit', render: (row: any) => `${row.profit.toLocaleString()} SAR` },
                { key: 'margin', header: 'Margin', render: (row: any) => `${row.margin}%` },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Budget Status Overview</h3>
            <Table
              data={budgetStatus}
              columns={[
                { key: 'department', header: 'Department' },
                { key: 'variance', header: 'Variance', render: (row: any) => `${row.variance.toLocaleString()} SAR` },
                { key: 'status', header: 'Status' },
              ]}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
