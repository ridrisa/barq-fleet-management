import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Table, LineChart, Select } from '@/components/ui'
import { CheckCircle2, AlertTriangle, XCircle, TrendingUp } from 'lucide-react'

export default function SLATracking() {
  const [timeRange, setTimeRange] = useState('30d')
  const [workflowFilter] = useState('')

  // Mock data - SLA Metrics by workflow type
  const slaMetrics = [
    {
      id: 1,
      workflow_type: 'Courier Onboarding',
      sla_target: '4 hours',
      current_avg: '2.5 hours',
      compliance_rate: 98.5,
      on_track: 336,
      at_risk: 4,
      breached: 2,
      status: 'on_track',
    },
    {
      id: 2,
      workflow_type: 'Leave Approval',
      sla_target: '2 hours',
      current_avg: '1.2 hours',
      compliance_rate: 99.2,
      on_track: 254,
      at_risk: 1,
      breached: 1,
      status: 'on_track',
    },
    {
      id: 3,
      workflow_type: 'Vehicle Maintenance',
      sla_target: '6 hours',
      current_avg: '3.1 hours',
      compliance_rate: 97.8,
      on_track: 185,
      at_risk: 3,
      breached: 1,
      status: 'on_track',
    },
    {
      id: 4,
      workflow_type: 'COD Reconciliation',
      sla_target: '1 hour',
      current_avg: '0.8 hours',
      compliance_rate: 99.8,
      on_track: 420,
      at_risk: 1,
      breached: 0,
      status: 'on_track',
    },
    {
      id: 5,
      workflow_type: 'Incident Management',
      sla_target: '4 hours',
      current_avg: '4.2 hours',
      compliance_rate: 85.0,
      on_track: 34,
      at_risk: 4,
      breached: 2,
      status: 'at_risk',
    },
    {
      id: 6,
      workflow_type: 'Document Verification',
      sla_target: '24 hours',
      current_avg: '28.5 hours',
      compliance_rate: 72.3,
      on_track: 103,
      at_risk: 25,
      breached: 14,
      status: 'breached',
    },
  ]

  // Mock data - SLA Breaches
  const slaBreaches = [
    {
      id: 1,
      workflow_name: 'Document Verification',
      instance_id: 'WF-2024-145',
      sla_target: '24 hours',
      actual_time: '36 hours',
      breach_time: '12 hours',
      started_at: '2024-01-05 08:00:00',
      breached_at: '2024-01-06 20:00:00',
      status: 'completed',
      severity: 'high',
    },
    {
      id: 2,
      workflow_name: 'Incident Management',
      instance_id: 'WF-2024-287',
      sla_target: '4 hours',
      actual_time: '6.5 hours',
      breach_time: '2.5 hours',
      started_at: '2024-01-06 14:00:00',
      breached_at: '2024-01-06 18:00:00',
      status: 'completed',
      severity: 'medium',
    },
    {
      id: 3,
      workflow_name: 'Document Verification',
      instance_id: 'WF-2024-198',
      sla_target: '24 hours',
      actual_time: '48 hours',
      breach_time: '24 hours',
      started_at: '2024-01-04 10:00:00',
      breached_at: '2024-01-05 10:00:00',
      status: 'completed',
      severity: 'critical',
    },
    {
      id: 4,
      workflow_name: 'Courier Onboarding',
      instance_id: 'WF-2024-056',
      sla_target: '4 hours',
      actual_time: '5 hours',
      breach_time: '1 hour',
      started_at: '2024-01-06 09:00:00',
      breached_at: '2024-01-06 13:00:00',
      status: 'completed',
      severity: 'low',
    },
  ]

  // Mock data - Compliance trend (last 30 days)
  const complianceTrend = [
    { date: '2024-01-01', compliance: 95.2, breaches: 8 },
    { date: '2024-01-05', compliance: 96.5, breaches: 5 },
    { date: '2024-01-10', compliance: 94.8, breaches: 9 },
    { date: '2024-01-15', compliance: 97.2, breaches: 4 },
    { date: '2024-01-20', compliance: 96.0, breaches: 6 },
    { date: '2024-01-25', compliance: 95.5, breaches: 7 },
    { date: '2024-01-30', compliance: 96.8, breaches: 5 },
  ]

  // Calculate summary stats
  const totalOnTrack = slaMetrics.reduce((sum, m) => sum + m.on_track, 0)
  const totalAtRisk = slaMetrics.reduce((sum, m) => sum + m.at_risk, 0)
  const totalBreached = slaMetrics.reduce((sum, m) => sum + m.breached, 0)
  const avgCompliance = (slaMetrics.reduce((sum, m) => sum + m.compliance_rate, 0) / slaMetrics.length).toFixed(1)

  const metricsColumns = [
    {
      key: 'workflow_type',
      header: 'Workflow Type',
      sortable: true,
      render: (row: any) => (
        <span className="font-medium">{row.workflow_type}</span>
      ),
    },
    {
      key: 'sla_target',
      header: 'SLA Target',
      render: (row: any) => (
        <span className="text-sm">{row.sla_target}</span>
      ),
    },
    {
      key: 'current_avg',
      header: 'Current Avg',
      render: (row: any) => (
        <span className="text-sm font-medium">{row.current_avg}</span>
      ),
    },
    {
      key: 'compliance_rate',
      header: 'Compliance Rate',
      sortable: true,
      render: (row: any) => (
        <div className="flex items-center gap-2">
          <div className="flex-1">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  row.compliance_rate >= 95
                    ? 'bg-green-600'
                    : row.compliance_rate >= 85
                    ? 'bg-yellow-600'
                    : 'bg-red-600'
                }`}
                style={{ width: `${row.compliance_rate}%` }}
              />
            </div>
          </div>
          <span className="text-sm font-semibold w-12 text-right">
            {row.compliance_rate}%
          </span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const statusConfig: Record<string, { variant: any; label: string }> = {
          on_track: { variant: 'success', label: 'On Track' },
          at_risk: { variant: 'warning', label: 'At Risk' },
          breached: { variant: 'danger', label: 'Breached' },
        }
        const config = statusConfig[row.status] || statusConfig.on_track
        return <Badge variant={config.variant}>{config.label}</Badge>
      },
    },
  ]

  const breachesColumns = [
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
      key: 'sla_target',
      header: 'SLA Target',
      render: (row: any) => (
        <span className="text-sm">{row.sla_target}</span>
      ),
    },
    {
      key: 'actual_time',
      header: 'Actual Time',
      render: (row: any) => (
        <span className="text-sm font-medium text-red-600">{row.actual_time}</span>
      ),
    },
    {
      key: 'breach_time',
      header: 'Breach By',
      sortable: true,
      render: (row: any) => (
        <span className="text-sm font-semibold text-red-600">+{row.breach_time}</span>
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (row: any) => {
        const variants: Record<string, any> = {
          critical: 'danger',
          high: 'danger',
          medium: 'warning',
          low: 'default',
        }
        return (
          <Badge variant={variants[row.severity]}>
            {row.severity.toUpperCase()}
          </Badge>
        )
      },
    },
    {
      key: 'breached_at',
      header: 'Breached At',
      sortable: true,
      render: (row: any) => (
        <span className="text-sm">{row.breached_at}</span>
      ),
    },
  ]

  const filteredMetrics = workflowFilter
    ? slaMetrics.filter(m => m.workflow_type.toLowerCase().includes(workflowFilter.toLowerCase()))
    : slaMetrics

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">SLA Tracking</h1>
        <Select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          options={[
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
                <p className="text-sm text-gray-600">On Track</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {totalOnTrack}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">At Risk</p>
                <p className="text-2xl font-bold text-yellow-600 mt-1">
                  {totalAtRisk}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-yellow-100 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Breached</p>
                <p className="text-2xl font-bold text-red-600 mt-1">
                  {totalBreached}
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Compliance</p>
                <p className="text-2xl font-bold text-blue-600 mt-1">
                  {avgCompliance}%
                </p>
              </div>
              <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* SLA Compliance Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>SLA Compliance Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <LineChart
            data={complianceTrend}
            xKey="date"
            yKey={['compliance']}
            height={300}
            colors={['#10b981']}
            formatXAxis={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
          />
        </CardContent>
      </Card>

      {/* SLA Metrics Table */}
      <Card>
        <CardHeader>
          <CardTitle>SLA Metrics by Workflow Type</CardTitle>
        </CardHeader>
        <CardContent>
          <Table data={filteredMetrics} columns={metricsColumns} />
        </CardContent>
      </Card>

      {/* SLA Breaches Table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent SLA Breaches</CardTitle>
        </CardHeader>
        <CardContent>
          <Table data={slaBreaches} columns={breachesColumns} />
        </CardContent>
      </Card>
    </div>
  )
}
