import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Select } from '@/components/ui/Select'
import { TrendingUp, TrendingDown, Clock, CheckCircle } from 'lucide-react'
import { useState } from 'react'

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('30')

  const metrics = {
    totalWorkflows: 156,
    avgApprovalTime: '2.4 days',
    approvalRate: 87,
    activeWorkflows: 23
  }

  const workflowsByType = [
    { name: 'Leave Requests', count: 45, percentage: 35 },
    { name: 'Vehicle Assignment', count: 38, percentage: 30 },
    { name: 'Loan Requests', count: 32, percentage: 25 },
    { name: 'Other', count: 13, percentage: 10 }
  ]

  const approvalTrends = [
    { month: 'Jan', approved: 45, rejected: 8 },
    { month: 'Feb', approved: 52, rejected: 6 },
    { month: 'Mar', approved: 48, rejected: 9 }
  ]

  const bottlenecks = [
    { step: 'Manager Approval', avgTime: '3.2 days', count: 12 },
    { step: 'HR Review', avgTime: '2.8 days', count: 8 },
    { step: 'Supervisor Review', avgTime: '1.5 days', count: 15 }
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflow Analytics</h1>
        <div className="w-48">
          <Select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Workflows</p>
                <p className="text-3xl font-bold mt-1">{metrics.totalWorkflows}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-blue-600" />
              </div>
            </div>
            <p className="text-xs text-green-600 mt-2">+12% from last period</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Approval Time</p>
                <p className="text-3xl font-bold mt-1">{metrics.avgApprovalTime}</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-lg">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
            </div>
            <p className="text-xs text-green-600 mt-2">-8% faster</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Approval Rate</p>
                <p className="text-3xl font-bold mt-1">{metrics.approvalRate}%</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
            <p className="text-xs text-green-600 mt-2">+3% improvement</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Now</p>
                <p className="text-3xl font-bold mt-1">{metrics.activeWorkflows}</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <TrendingDown className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
            <p className="text-xs text-gray-600 mt-2">Awaiting approval</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Workflows by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {workflowsByType.map((type) => (
                <div key={type.name}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{type.name}</span>
                    <span className="text-sm text-gray-600">{type.count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${type.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Approval Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {approvalTrends.map((trend) => (
                <div key={trend.month} className="flex items-center gap-4">
                  <div className="w-16 text-sm font-medium">{trend.month}</div>
                  <div className="flex-1">
                    <div className="flex gap-2">
                      <div
                        className="bg-green-500 h-8 rounded flex items-center justify-center text-white text-xs font-medium"
                        style={{ width: `${(trend.approved / 60) * 100}%`, minWidth: '40px' }}
                      >
                        {trend.approved}
                      </div>
                      <div
                        className="bg-red-500 h-8 rounded flex items-center justify-center text-white text-xs font-medium"
                        style={{ width: `${(trend.rejected / 60) * 100}%`, minWidth: '30px' }}
                      >
                        {trend.rejected}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              <div className="flex gap-4 pt-4 border-t">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span className="text-xs">Approved</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-red-500 rounded"></div>
                  <span className="text-xs">Rejected</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workflow Bottlenecks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {bottlenecks.map((bottleneck) => (
              <div key={bottleneck.step} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium">{bottleneck.step}</p>
                  <p className="text-sm text-gray-600">{bottleneck.count} pending workflows</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-red-600">{bottleneck.avgTime}</p>
                  <p className="text-xs text-gray-600">avg time</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Time-to-Complete Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium w-24">0-1 days</span>
              <div className="flex-1 bg-gray-200 rounded-full h-6">
                <div className="bg-green-500 h-6 rounded-full flex items-center justify-end pr-3 text-white text-xs font-medium" style={{ width: '45%' }}>
                  45%
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium w-24">1-3 days</span>
              <div className="flex-1 bg-gray-200 rounded-full h-6">
                <div className="bg-blue-500 h-6 rounded-full flex items-center justify-end pr-3 text-white text-xs font-medium" style={{ width: '35%' }}>
                  35%
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium w-24">3-7 days</span>
              <div className="flex-1 bg-gray-200 rounded-full h-6">
                <div className="bg-yellow-500 h-6 rounded-full flex items-center justify-end pr-3 text-white text-xs font-medium" style={{ width: '15%' }}>
                  15%
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium w-24">7+ days</span>
              <div className="flex-1 bg-gray-200 rounded-full h-6">
                <div className="bg-red-500 h-6 rounded-full flex items-center justify-end pr-3 text-white text-xs font-medium" style={{ width: '5%' }}>
                  5%
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
