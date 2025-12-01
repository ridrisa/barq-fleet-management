import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Package, Clock, CheckCircle, TruckIcon, Filter, RefreshCw } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { KPICard } from '@/components/ui/KPICard'
import { dispatchAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

export default function OperationsDashboard() {
  const { t: _t } = useTranslation()
  const [zoneFilter, setZoneFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [courierFilter, setCourierFilter] = useState<string>('all')
  const [autoRefresh, setAutoRefresh] = useState(true)

  const {
    isLoading,
    error,
    refetch,
    filteredData: deliveries,
  } = useDataTable({
    queryKey: 'dispatch-board',
    queryFn: dispatchAPI.getAll,
    pageSize: 1000,
  })

  const { handleUpdate } = useCRUD({
    queryKey: 'dispatch-board',
    entityName: 'Delivery',
    update: dispatchAPI.updateStatus,
  })

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      refetch()
    }, 30000)

    return () => clearInterval(interval)
  }, [autoRefresh, refetch])

  // Apply filters
  let displayData = deliveries
  if (zoneFilter !== 'all') {
    displayData = displayData.filter((d: any) => d.zone === zoneFilter)
  }
  if (priorityFilter !== 'all') {
    displayData = displayData.filter((d: any) => d.priority === priorityFilter)
  }
  if (courierFilter !== 'all') {
    displayData = displayData.filter((d: any) => d.courier_id?.toString() === courierFilter)
  }

  // Group deliveries by status
  const pendingDeliveries = displayData.filter((d: any) => d.status === 'pending')
  const assignedDeliveries = displayData.filter((d: any) => d.status === 'assigned')
  const inTransitDeliveries = displayData.filter((d: any) => d.status === 'in_transit')
  const deliveredDeliveries = displayData.filter((d: any) => d.status === 'delivered')

  // Summary stats
  const stats = {
    totalToday: displayData.length,
    pending: pendingDeliveries.length,
    inTransit: inTransitDeliveries.length,
    completed: deliveredDeliveries.length,
  }

  const handleStatusUpdate = async (delivery: any, newStatus: string) => {
    await handleUpdate(delivery.id, newStatus)
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-gray-100 border-gray-300',
      assigned: 'bg-blue-100 border-blue-300',
      in_transit: 'bg-yellow-100 border-yellow-300',
      delivered: 'bg-green-100 border-green-300',
    }
    return colors[status] || 'bg-gray-100 border-gray-300'
  }

  const getPriorityColor = (priority: string): 'danger' | 'warning' | 'default' | 'success' => {
    const colors: Record<string, 'danger' | 'warning' | 'default' | 'success'> = {
      express: 'danger',
      same_day: 'warning',
      standard: 'default',
      deferred: 'success',
    }
    return colors[priority] || 'default'
  }

  const DeliveryCard = ({ delivery, onStatusChange }: any) => {
    const nextStatus: Record<string, string> = {
      pending: 'assigned',
      assigned: 'in_transit',
      in_transit: 'delivered',
    }

    return (
      <div
        className="p-3 mb-2 bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => {
          const next = nextStatus[delivery.status]
          if (next) {
            onStatusChange(delivery, next)
          }
        }}
      >
        <div className="flex items-start justify-between mb-2">
          <div className="font-mono text-xs font-semibold text-blue-600">
            {delivery.tracking_number || `TRK-${delivery.id?.toString().padStart(6, '0')}`}
          </div>
          {delivery.priority && (
            <Badge variant={getPriorityColor(delivery.priority)} size="sm">
              {delivery.priority}
            </Badge>
          )}
        </div>
        <div className="space-y-1 text-sm">
          <div className="flex items-center gap-1 text-gray-700">
            <TruckIcon className="h-3 w-3" />
            <span className="font-medium">{delivery.courier_name || `Courier #${delivery.courier_id}`}</span>
          </div>
          <div className="text-gray-600 truncate">
            {delivery.customer_name || delivery.receiver_name || 'N/A'}
          </div>
          <div className="text-xs text-gray-500 truncate">
            {delivery.delivery_address || 'N/A'}
          </div>
        </div>
      </div>
    )
  }

  const KanbanColumn = ({ title, status, deliveries, icon: Icon }: any) => (
    <div className="flex-1 min-w-[250px]">
      <div className={`rounded-lg border-2 ${getStatusColor(status)} p-4 h-full`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Icon className="h-5 w-5" />
            <h3 className="font-semibold text-gray-900">{title}</h3>
          </div>
          <Badge variant="default">{deliveries.length}</Badge>
        </div>
        <div className="space-y-2 max-h-[600px] overflow-y-auto">
          {deliveries.map((delivery: any) => (
            <DeliveryCard
              key={delivery.id}
              delivery={delivery}
              onStatusChange={handleStatusUpdate}
            />
          ))}
          {deliveries.length === 0 && (
            <div className="text-center text-gray-400 py-8">No deliveries</div>
          )}
        </div>
      </div>
    </div>
  )

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
        <p className="text-red-800">Error loading dispatch board: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dispatch Board</h1>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? 'Auto-Refresh ON' : 'Auto-Refresh OFF'}
          </Button>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Now
          </Button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Today"
          value={stats.totalToday}
          icon={<Package className="h-6 w-6" />}
          color="blue"
          loading={isLoading}
        />
        <KPICard
          title="Pending"
          value={stats.pending}
          icon={<Clock className="h-6 w-6" />}
          color="yellow"
          loading={isLoading}
        />
        <KPICard
          title="In Transit"
          value={stats.inTransit}
          icon={<TruckIcon className="h-6 w-6" />}
          color="indigo"
          loading={isLoading}
        />
        <KPICard
          title="Completed"
          value={stats.completed}
          icon={<CheckCircle className="h-6 w-6" />}
          color="green"
          loading={isLoading}
        />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Select
                value={zoneFilter}
                onChange={(e) => setZoneFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Zones' },
                  { value: 'north', label: 'North Zone' },
                  { value: 'south', label: 'South Zone' },
                  { value: 'east', label: 'East Zone' },
                  { value: 'west', label: 'West Zone' },
                ]}
                leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <div className="flex-1">
              <Select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Priorities' },
                  { value: 'express', label: 'Express' },
                  { value: 'same_day', label: 'Same Day' },
                  { value: 'standard', label: 'Standard' },
                  { value: 'deferred', label: 'Deferred' },
                ]}
                leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <div className="flex-1">
              <Select
                value={courierFilter}
                onChange={(e) => setCourierFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Couriers' },
                  { value: '1', label: 'Courier #1' },
                  { value: '2', label: 'Courier #2' },
                  { value: '3', label: 'Courier #3' },
                ]}
                leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        <KanbanColumn
          title="Pending"
          status="pending"
          deliveries={pendingDeliveries}
          icon={Clock}
        />
        <KanbanColumn
          title="Assigned"
          status="assigned"
          deliveries={assignedDeliveries}
          icon={Package}
        />
        <KanbanColumn
          title="In Transit"
          status="in_transit"
          deliveries={inTransitDeliveries}
          icon={TruckIcon}
        />
        <KanbanColumn
          title="Delivered"
          status="delivered"
          deliveries={deliveredDeliveries}
          icon={CheckCircle}
        />
      </div>
    </div>
  )
}
