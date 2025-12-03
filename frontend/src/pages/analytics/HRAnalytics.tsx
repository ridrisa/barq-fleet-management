import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Users, UserCheck, Calendar, TrendingDown, Download } from 'lucide-react'
import { KPICard, LineChart, BarChart, Button, DateRangePicker, Card, CardContent, Table, Spinner, Badge } from '@/components/ui'
import { couriersAPI, leavesAPI, attendanceAPI } from '@/lib/api'

export default function HRAnalytics() {
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  })

  // Fetch employee/courier data
  const { data: employees, isLoading: employeesLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  // Fetch leave data
  const { data: _leaves } = useQuery({
    queryKey: ['leaves'],
    queryFn: () => leavesAPI.getAll(),
  })

  // Fetch attendance data
  const { data: _attendance } = useQuery({
    queryKey: ['attendance'],
    queryFn: () => attendanceAPI.getAll(),
  })

  const handleExportExcel = () => {
    console.log('Exporting to Excel...')
    // TODO: Implement Excel export functionality
  }

  // Mock data for charts
  const headcountTrendData = [
    { month: 'Jul', count: 98 },
    { month: 'Aug', count: 101 },
    { month: 'Sep', count: 103 },
    { month: 'Oct', count: 105 },
    { month: 'Nov', count: 107 },
    { month: 'Dec', count: 105 },
  ]

  const leaveBalanceData = [
    { courier: 'Ahmed Ali', balance: 15 },
    { courier: 'Mohammed Hassan', balance: 12 },
    { courier: 'Khaled Ibrahim', balance: 18 },
    { courier: 'Omar Youssef', balance: 8 },
    { courier: 'Abdullah Mahmoud', balance: 22 },
    { courier: 'Hassan Ahmed', balance: 14 },
  ]

  const salaryDistributionData = [
    { department: 'Operations', avgSalary: 4500 },
    { department: 'Fleet', avgSalary: 4200 },
    { department: 'Support', avgSalary: 3800 },
    { department: 'Admin', avgSalary: 5200 },
  ]

  const attendanceTrendData = [
    { date: '2024-01-01', rate: 96.5 },
    { date: '2024-01-02', rate: 95.8 },
    { date: '2024-01-03', rate: 97.2 },
    { date: '2024-01-04', rate: 96.1 },
    { date: '2024-01-05', rate: 95.5 },
    { date: '2024-01-06', rate: 97.8 },
    { date: '2024-01-07', rate: 96.9 },
  ]

  const leaveRequestsThisMonth = [
    { employee: 'Ahmed Ali', type: 'Annual', startDate: '2024-01-15', days: 5, status: 'Approved' },
    { employee: 'Mohammed Hassan', type: 'Sick', startDate: '2024-01-18', days: 2, status: 'Pending' },
    { employee: 'Khaled Ibrahim', type: 'Emergency', startDate: '2024-01-20', days: 1, status: 'Approved' },
    { employee: 'Omar Youssef', type: 'Annual', startDate: '2024-01-25', days: 3, status: 'Pending' },
  ]

  const salarySummary = [
    { department: 'Operations', employees: 42, total: 189000, avg: 4500 },
    { department: 'Fleet', employees: 28, total: 117600, avg: 4200 },
    { department: 'Support', employees: 18, total: 68400, avg: 3800 },
    { department: 'Admin', employees: 12, total: 62400, avg: 5200 },
  ]

  const attendanceIssues = [
    { employee: 'Hassan Ahmed', issue: 'Late Arrival', occurrences: 3, lastDate: '2024-01-10' },
    { employee: 'Ali Mohammed', issue: 'Absent', occurrences: 2, lastDate: '2024-01-12' },
    { employee: 'Youssef Khaled', issue: 'Late Arrival', occurrences: 4, lastDate: '2024-01-14' },
  ]

  // Calculate KPI values
  const totalEmployees = employees?.length || 105
  const activeEmployees = employees?.filter((e: any) => e.status === 'active').length || 102
  const onLeave = _leaves?.filter((l: any) => l.status === 'approved' && new Date(l.start_date) <= new Date() && new Date(l.end_date) >= new Date()).length || 3
  const turnoverRate = 3.8

  if (employeesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">HR Analytics</h1>
        <div className="flex items-center gap-4">
          <Button onClick={handleExportExcel} variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export to Excel
          </Button>
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
          title="Total Employees"
          value={totalEmployees.toString()}
          change={8.3}
          trend="up"
          icon={<Users className="w-6 h-6" />}
          color="blue"
        />
        <KPICard
          title="Active"
          value={activeEmployees.toString()}
          change={2.1}
          trend="up"
          icon={<UserCheck className="w-6 h-6" />}
          color="green"
        />
        <KPICard
          title="On Leave"
          value={onLeave.toString()}
          change={-15.2}
          trend="down"
          icon={<Calendar className="w-6 h-6" />}
          color="yellow"
        />
        <KPICard
          title="Turnover Rate"
          value={`${turnoverRate}%`}
          change={-1.2}
          trend="down"
          icon={<TrendingDown className="w-6 h-6" />}
          color="red"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={headcountTrendData}
          xKey="month"
          yKey="count"
          title="Headcount Trend (Monthly)"
          height={300}
        />

        <BarChart
          data={leaveBalanceData}
          xKey="courier"
          yKey="balance"
          title="Leave Balance Overview per Courier"
          height={300}
          formatXAxis={(value) => String(value).split(' ')[0]}
        />

        <BarChart
          data={salaryDistributionData}
          xKey="department"
          yKey="avgSalary"
          title="Salary Distribution by Department"
          height={300}
          formatYAxis={(value) => `${value} SAR`}
        />

        <LineChart
          data={attendanceTrendData}
          xKey="date"
          yKey="rate"
          title="Attendance Trend (Daily %)"
          height={300}
          formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          formatYAxis={(value) => `${value}%`}
        />
      </div>

      {/* Tables Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Leave Requests This Month</h3>
            <Table
              data={leaveRequestsThisMonth}
              columns={[
                { key: 'employee', header: 'Employee' },
                { key: 'type', header: 'Type' },
                { key: 'days', header: 'Days' },
                {
                  key: 'status',
                  header: 'Status',
                  render: (row: any) => (
                    <Badge variant={row.status === 'Approved' ? 'success' : 'warning'}>
                      {row.status}
                    </Badge>
                  ),
                },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Salary Summary by Department</h3>
            <Table
              data={salarySummary}
              columns={[
                { key: 'department', header: 'Department' },
                { key: 'employees', header: 'Employees' },
                { key: 'avg', header: 'Avg Salary', render: (row: any) => `${row.avg} SAR` },
              ]}
            />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">Attendance Issues (Late/Absent)</h3>
            <Table
              data={attendanceIssues}
              columns={[
                { key: 'employee', header: 'Employee' },
                { key: 'issue', header: 'Issue' },
                { key: 'occurrences', header: 'Count' },
              ]}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
