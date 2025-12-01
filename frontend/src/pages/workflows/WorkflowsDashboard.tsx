import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Table, PieChart, LineChart, Select } from '@/components/ui'
import { TrendingUp, Clock, CheckCircle } from 'lucide-react'

export default function WorkflowsDashboard() {
  const [timeRange, setTimeRange] = useState('7d')

  // Mock data - Summary stats
  const stats = {
    total: 1248,
    active: 45,
    completedToday: 87,
    avgTime: '2.5h',
  }

  // Mock data - Recent workflows
  const recentWorkflows = [
    {
      id: 1,
      workflow_name: 'Courier Onboarding',
      instance_id: 'WF-2024-001',
      status: 'completed',
      started_at: '2024-01-07 14:30:00',
      completed_at: '2024-01-07 16:45:00',
      duration: '2h 15m',
      initiated_by: 'HR Manager',
    },
    {
      id: 2,
      workflow_name: 'Leave Approval',
      instance_id: 'WF-2024-002',
      status: 'in_progress',
      started_at: '2024-01-07 15:00:00',
      completed_at: null,
      duration: '2h 30m',
      initiated_by: 'John Doe',
    },
    {
      id: 3,
      workflow_name: 'Vehicle Maintenance',
      instance_id: 'WF-2024-003',
      status: 'completed',
      started_at: '2024-01-07 09:00:00',
      completed_at: '2024-01-07 11:30:00',
      duration: '2h 30m',
      initiated_by: 'Fleet Manager',
    },
    {
      id: 4,
      workflow_name: 'COD Reconciliation',
      instance_id: 'WF-2024-004',
      status: 'in_progress',
      started_at: '2024-01-07 16:00:00',
      completed_at: null,
      duration: '1h 30m',
      initiated_by: 'Finance Team',
    },
    {
      id: 5,
      workflow_name: 'Incident Management',
      instance_id: 'WF-2024-005',
      status: 'failed',
      started_at: '2024-01-07 13:00:00',
      completed_at: '2024-01-07 13:45:00',
      duration: '45m',
      initiated_by: 'Operations',
    },
  ]

  // Mock data - Status distribution
  const statusData = [
    { name: 'Completed', value: 892, color: '#10b981' },
    { name: 'In Progress', value: 45, color: '#3b82f6' },
    { name: 'Pending', value: 28, color: '#f59e0b' },
    { name: 'Failed', value: 12, color: '#ef4444' },
  ]

  // Mock data - Completion trends (last 7 days)
  const completionTrends = [
    { date: '2024-01-01', completed: 112, failed: 3 },
    { date: '2024-01-02', completed: 125, failed: 2 },
    { date: '2024-01-03', completed: 108, failed: 5 },
    { date: '2024-01-04', completed: 134, failed: 4 },
    { date: '2024-01-05', completed: 118, failed: 2 },
    { date: '2024-01-06', completed: 142, failed: 1 },
    { date: '2024-01-07', completed: 87, failed: 3 },
  ]

  // Mock data - Workflow types performance
  const workflowTypes = [
    { type: 'Courier Onboarding', total: 342, avg_time: '2.5h', success_rate: 98.5 },
    { type: 'Leave Approval', total: 256, avg_time: '1.2h', success_rate: 99.2 },
    { type: 'Vehicle Maintenance', total: 189, avg_time: '3.1h', success_rate: 97.8 },
    { type: 'COD Reconciliation', total: 421, avg_time: '0.8h', success_rate: 99.8 },
    { type: 'Incident Management', total: 40, avg_time: '4.2h', success_rate: 85.0 },
  ]

  const columns = [
    {
      key: 'workflow_name',
      header: 'Workflow',
      sortable: true,
      render: (row: any) => (
        <div>
          <span className="font-medium">{row.workflow_name}</span>
          <p className="text-xs text-gray-500">{row.instance_id}</p>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const variants: Record<string, any> = {
          completed: 'success',
          in_progress: 'warning',
          failed: 'danger',
          pending: 'default',
        }
        return (
          <Badge variant={variants[row.status]}>
            {row.status.replace('_', ' ')}
          </Badge>
        )
      },
    },
    {
      key: 'started_at',
      header: 'Started At',
      sortable: true,
      render: (row: any) => (
        <span className="text-sm">{row.started_at}</span>
      ),
    },
    {
      key: 'duration',
      header: 'Duration',
      render: (row: any) => (
        <span className="text-sm font-medium">{row.duration}</span>
      ),
    },
    {
      key: 'initiated_by',
      header: 'Initiated By',
      render: (row: any) => (
        <span className="text-sm">{row.initiated_by}</span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflows Dashboard</h1>
        <Select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          options={[
            { value: '24h', label: 'Last 24 Hours' },
            { value: '7d', label: 'Last 7 Days' },
            { value: '30d', label: 'Last 30 Days' },
            { value: '90d', label: 'Last 90 Days' },
          ]}
        />
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Workflows</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stats.total}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">
                  {stats.active}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                <Clock className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Completed Today</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {stats.completedToday}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Completion Time</p>
                <p className="text-2xl font-bold text-purple-600 mt-1">
                  {stats.avgTime}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Workflow Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <PieChart
              data={statusData}
              dataKey="value"
              nameKey="name"
              height={300}
              showLabels={true}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Completion Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart
              data={completionTrends}
              xKey="date"
              yKey={['completed', 'failed']}
              height={300}
              colors={['#10b981', '#ef4444']}
              formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
          </CardContent>
        </Card>
      </div>

      {/* Workflow Types Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Workflow Types Performance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {workflowTypes.map((workflow, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{workflow.type}</h3>
                  <div className="flex gap-4 mt-2">
                    <span className="text-sm text-gray-600">
                      Total: <span className="font-semibold">{workflow.total}</span>
                    </span>
                    <span className="text-sm text-gray-600">
                      Avg Time: <span className="font-semibold">{workflow.avg_time}</span>
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">
                    {workflow.success_rate}%
                  </div>
                  <div className="text-xs text-gray-500">Success Rate</div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Workflows Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Workflows</CardTitle>
        </CardHeader>
        <CardContent>
          <Table data={recentWorkflows} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
