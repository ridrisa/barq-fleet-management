import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Zap, Clock, Package, AlertTriangle, Filter } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { priorityQueueAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'

export default function PriorityQueue() {
  useTranslation()
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  const {
    isLoading,
    error,
    refetch,
    filteredData: deliveries,
  } = useDataTable({
    queryKey: 'priority-queue',
    queryFn: priorityQueueAPI.getAll,
    pageSize: 1000,
  })

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      refetch()
    }, 30000)

    return () => clearInterval(interval)
  }, [refetch])

  // Apply filters
  let displayData = deliveries
  if (priorityFilter !== 'all') {
    displayData = displayData.filter((d: any) => d.priority === priorityFilter)
  }

  // Sort by priority then SLA deadline
  const priorityOrder: Record<string, number> = {
    express: 1,
    same_day: 2,
    standard: 3,
    deferred: 4,
  }

  displayData = [...displayData].sort((a: any, b: any) => {
    const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority]
    if (priorityDiff !== 0) return priorityDiff

    const aDeadline = new Date(a.sla_deadline || a.scheduled_time).getTime()
    const bDeadline = new Date(b.sla_deadline || b.scheduled_time).getTime()
    return aDeadline - bDeadline
  })

  // Calculate stats
  const stats = {
    express: displayData.filter((d: any) => d.priority === 'express').length,
    sameDay: displayData.filter((d: any) => d.priority === 'same_day').length,
    standard: displayData.filter((d: any) => d.priority === 'standard').length,
    overdue: displayData.filter((d: any) => {
      const deadline = new Date(d.sla_deadline || d.scheduled_time)
      return deadline < new Date() && d.status !== 'delivered'
    }).length,
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      express: 'text-red-600 bg-red-50',
      same_day: 'text-orange-600 bg-orange-50',
      standard: 'text-blue-600 bg-blue-50',
      deferred: 'text-gray-600 bg-gray-50',
    }
    return colors[priority] || 'text-gray-600 bg-gray-50'
  }

  const getPriorityBadgeVariant = (priority: string): 'danger' | 'warning' | 'default' | 'success' => {
    const variants: Record<string, 'danger' | 'warning' | 'default' | 'success'> = {
      express: 'danger',
      same_day: 'warning',
      standard: 'default',
      deferred: 'success',
    }
    return variants[priority] || 'default'
  }

  const calculateTimeRemaining = (deadline: string) => {
    const now = new Date()
    const slaDeadline = new Date(deadline)
    const diff = slaDeadline.getTime() - now.getTime()

    if (diff < 0) {
      const hours = Math.abs(Math.floor(diff / (1000 * 60 * 60)))
      const minutes = Math.abs(Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)))
      return { time: `${hours}h ${minutes}m`, overdue: true }
    }

    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    return { time: `${hours}h ${minutes}m`, overdue: false }
  }

  const DeliveryQueueItem = ({ delivery }: any) => {
    const deadline = delivery.sla_deadline || delivery.scheduled_time
    const timeRemaining = deadline ? calculateTimeRemaining(deadline) : null

    return (
      <div className={`p-4 border rounded-lg ${getPriorityColor(delivery.priority)}`}>
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <div className="font-mono text-sm font-semibold text-blue-600">
                {delivery.tracking_number || `TRK-${delivery.id?.toString().padStart(6, '0')}`}
              </div>
              <Badge variant={getPriorityBadgeVariant(delivery.priority)} size="sm">
                {delivery.priority?.toUpperCase()}
              </Badge>
              {timeRemaining?.overdue && (
                <Badge variant="danger" size="sm">
                  <AlertTriangle className="h-3 w-3 mr-1" />
                  OVERDUE
                </Badge>
              )}
            </div>
            <div className="text-sm font-medium text-gray-900">
              {delivery.customer_name || delivery.receiver_name || 'N/A'}
            </div>
            <div className="text-xs text-gray-600 mt-1 truncate">
              {delivery.delivery_address || 'N/A'}
            </div>
          </div>
          {timeRemaining && (
            <div className={`text-right ${timeRemaining.overdue ? 'text-red-600' : 'text-gray-700'}`}>
              <div className="text-xs font-medium mb-1">
                {timeRemaining.overdue ? 'Overdue by' : 'Time remaining'}
              </div>
              <div className="font-bold text-lg">{timeRemaining.time}</div>
            </div>
          )}
        </div>
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2 text-gray-600">
            <Package className="h-4 w-4" />
            <span>{delivery.courier_name || `Courier #${delivery.courier_id}`}</span>
          </div>
          <div className="text-xs text-gray-500">
            Scheduled: {new Date(delivery.scheduled_time || delivery.created_at).toLocaleString()}
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading priority queue: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Priority Queue</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Express</p>
                <p className="text-2xl font-bold text-red-600">{stats.express}</p>
              </div>
              <Zap className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Same Day</p>
                <p className="text-2xl font-bold text-orange-600">{stats.sameDay}</p>
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Standard</p>
                <p className="text-2xl font-bold text-blue-600">{stats.standard}</p>
              </div>
              <Package className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Overdue</p>
                <p className="text-2xl font-bold text-red-600">{stats.overdue}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="w-full sm:w-64">
            <Select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Priorities' },
                { value: 'express', label: 'Express Only' },
                { value: 'same_day', label: 'Same Day Only' },
                { value: 'standard', label: 'Standard Only' },
                { value: 'deferred', label: 'Deferred Only' },
              ]}
              leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
            />
          </div>
        </CardContent>
      </Card>

      {/* Priority Queue List */}
      <Card>
        <CardHeader>
          <CardTitle>Delivery Queue (Sorted by Priority & SLA)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {displayData.length > 0 ? (
              displayData.map((delivery: any) => (
                <DeliveryQueueItem key={delivery.id} delivery={delivery} />
              ))
            ) : (
              <div className="text-center text-gray-400 py-12">
                <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No deliveries in queue</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
