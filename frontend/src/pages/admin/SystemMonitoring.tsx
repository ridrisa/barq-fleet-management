import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { LineChart, Table } from '@/components/ui'
import { RefreshCw, Database, Server, Zap, Activity } from 'lucide-react'

export default function SystemMonitoring() {
  const [lastRefresh, setLastRefresh] = useState(new Date())
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 1000))
    setLastRefresh(new Date())
    setIsRefreshing(false)
  }

  // Mock data - System status
  const systemStatus = {
    database: { status: 'healthy', responseTime: 12, connections: 45 },
    api: { status: 'healthy', responseTime: 23, requests: 1250 },
    cache: { status: 'healthy', hitRate: 94.5, size: '2.3 GB' },
    queue: { status: 'warning', pending: 125, processing: 15 },
  }

  // Mock data - Server metrics
  const serverMetrics = {
    cpu: 45,
    memory: 68,
    disk: 72,
  }

  // Mock data - Active users
  const activeUsers = 24

  // Mock data - Recent errors
  const recentErrors = [
    { id: 1, timestamp: '2024-01-07 14:32:15', level: 'error', message: 'Database connection timeout', service: 'API' },
    { id: 2, timestamp: '2024-01-07 14:25:08', level: 'warning', message: 'High memory usage detected', service: 'Worker' },
    { id: 3, timestamp: '2024-01-07 14:18:42', level: 'error', message: 'Failed to process queue item', service: 'Queue' },
    { id: 4, timestamp: '2024-01-07 14:10:33', level: 'warning', message: 'Slow query detected (2.5s)', service: 'Database' },
  ]

  // Mock data - Performance metrics
  const performanceData = [
    { time: '00:00', cpu: 35, memory: 52, responseTime: 120 },
    { time: '04:00', cpu: 28, memory: 48, responseTime: 95 },
    { time: '08:00', cpu: 52, memory: 65, responseTime: 180 },
    { time: '12:00', cpu: 68, memory: 72, responseTime: 220 },
    { time: '16:00', cpu: 45, memory: 68, responseTime: 150 },
    { time: '20:00', cpu: 38, memory: 55, responseTime: 110 },
  ]

  const errorColumns = [
    {
      key: 'timestamp',
      header: 'Timestamp',
      sortable: true,
    },
    {
      key: 'level',
      header: 'Level',
      render: (row: any) => (
        <Badge variant={row.level === 'error' ? 'danger' : 'warning'}>
          {row.level.toUpperCase()}
        </Badge>
      ),
    },
    {
      key: 'service',
      header: 'Service',
    },
    {
      key: 'message',
      header: 'Message',
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success'
      case 'warning':
        return 'warning'
      case 'error':
        return 'danger'
      default:
        return 'default'
    }
  }

  const getMetricColor = (value: number) => {
    if (value < 60) return 'text-green-600'
    if (value < 80) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">System Monitoring</h1>
          <p className="text-sm text-gray-500 mt-1">
            Last updated: {lastRefresh.toLocaleString()}
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={isRefreshing}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Database className="h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold">Database</h3>
                </div>
                <Badge variant={getStatusColor(systemStatus.database.status)}>
                  {systemStatus.database.status}
                </Badge>
                <div className="mt-3 space-y-1">
                  <p className="text-sm text-gray-600">
                    Response: {systemStatus.database.responseTime}ms
                  </p>
                  <p className="text-sm text-gray-600">
                    Connections: {systemStatus.database.connections}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Server className="h-5 w-5 text-green-600" />
                  <h3 className="font-semibold">API</h3>
                </div>
                <Badge variant={getStatusColor(systemStatus.api.status)}>
                  {systemStatus.api.status}
                </Badge>
                <div className="mt-3 space-y-1">
                  <p className="text-sm text-gray-600">
                    Response: {systemStatus.api.responseTime}ms
                  </p>
                  <p className="text-sm text-gray-600">
                    Requests: {systemStatus.api.requests}/min
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Zap className="h-5 w-5 text-purple-600" />
                  <h3 className="font-semibold">Cache</h3>
                </div>
                <Badge variant={getStatusColor(systemStatus.cache.status)}>
                  {systemStatus.cache.status}
                </Badge>
                <div className="mt-3 space-y-1">
                  <p className="text-sm text-gray-600">
                    Hit Rate: {systemStatus.cache.hitRate}%
                  </p>
                  <p className="text-sm text-gray-600">
                    Size: {systemStatus.cache.size}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Activity className="h-5 w-5 text-orange-600" />
                  <h3 className="font-semibold">Queue</h3>
                </div>
                <Badge variant={getStatusColor(systemStatus.queue.status)}>
                  {systemStatus.queue.status}
                </Badge>
                <div className="mt-3 space-y-1">
                  <p className="text-sm text-gray-600">
                    Pending: {systemStatus.queue.pending}
                  </p>
                  <p className="text-sm text-gray-600">
                    Processing: {systemStatus.queue.processing}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Server Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Server Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">CPU Usage</p>
              <div className="relative w-32 h-32 mx-auto">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke={serverMetrics.cpu < 60 ? '#10b981' : serverMetrics.cpu < 80 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${serverMetrics.cpu * 3.51} 351`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-3xl font-bold ${getMetricColor(serverMetrics.cpu)}`}>
                    {serverMetrics.cpu}%
                  </span>
                </div>
              </div>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Memory Usage</p>
              <div className="relative w-32 h-32 mx-auto">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke={serverMetrics.memory < 60 ? '#10b981' : serverMetrics.memory < 80 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${serverMetrics.memory * 3.51} 351`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-3xl font-bold ${getMetricColor(serverMetrics.memory)}`}>
                    {serverMetrics.memory}%
                  </span>
                </div>
              </div>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-600 mb-2">Disk Usage</p>
              <div className="relative w-32 h-32 mx-auto">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="#e5e7eb"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke={serverMetrics.disk < 60 ? '#10b981' : serverMetrics.disk < 80 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${serverMetrics.disk * 3.51} 351`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-3xl font-bold ${getMetricColor(serverMetrics.disk)}`}>
                    {serverMetrics.disk}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Users */}
        <Card>
          <CardHeader>
            <CardTitle>Active Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-5xl font-bold text-blue-600">{activeUsers}</p>
              <p className="text-gray-600 mt-2">Currently Online</p>
            </div>
          </CardContent>
        </Card>

        {/* Performance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics (24h)</CardTitle>
          </CardHeader>
          <CardContent>
            <LineChart
              data={performanceData}
              xKey="time"
              yKey={['cpu', 'memory']}
              height={200}
              colors={['#3b82f6', '#10b981']}
            />
          </CardContent>
        </Card>
      </div>

      {/* Recent Errors */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Errors & Warnings</CardTitle>
        </CardHeader>
        <CardContent>
          <Table data={recentErrors} columns={errorColumns} />
        </CardContent>
      </Card>
    </div>
  )
}
