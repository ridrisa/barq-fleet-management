import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Calendar, Package } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { deliveriesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'

export default function ScheduledDeliveries() {
  useTranslation()
  const [dateFilter, setDateFilter] = useState<string>('')

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
  } = useDataTable({
    queryKey: 'scheduled-deliveries',
    queryFn: deliveriesAPI.getAll,
    pageSize: 15,
  })

  // Filter for scheduled/upcoming deliveries
  const scheduledData = filteredData.filter((d: any) => {
    const isScheduled = d.status === 'scheduled' || d.status === 'pending'
    const scheduledDate = d.scheduled_date || d.delivery_date
    if (!scheduledDate) return false

    const isFuture = new Date(scheduledDate) >= new Date()
    return isScheduled && isFuture
  })

  // Apply date filter
  let displayData = scheduledData
  if (dateFilter) {
    displayData = displayData.filter((d: any) => {
      const scheduled = new Date(d.scheduled_date || d.delivery_date).toISOString().split('T')[0]
      return scheduled === dateFilter
    })
  }

  // Summary stats
  const stats = {
    today: scheduledData.filter((d: any) => {
      const scheduled = new Date(d.scheduled_date || d.delivery_date).toDateString()
      return scheduled === new Date().toDateString()
    }).length,
    thisWeek: scheduledData.filter((d: any) => {
      const scheduled = new Date(d.scheduled_date || d.delivery_date)
      const weekFromNow = new Date()
      weekFromNow.setDate(weekFromNow.getDate() + 7)
      return scheduled <= weekFromNow
    }).length,
    total: scheduledData.length,
  }

  const columns = [
    {
      key: 'tracking_number',
      header: 'Tracking #',
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.tracking_number || `TRK-${row.id?.toString().padStart(6, '0')}`}
        </div>
      ),
    },
    {
      key: 'scheduled_date',
      header: 'Scheduled Date',
      render: (row: any) => {
        const date = row.scheduled_date || row.delivery_date
        return date ? (
          <div className="text-sm">
            <div>{new Date(date).toLocaleDateString()}</div>
            <div className="text-xs text-gray-500">{new Date(date).toLocaleTimeString()}</div>
          </div>
        ) : (
          'N/A'
        )
      },
    },
    {
      key: 'customer_name',
      header: 'Customer',
      render: (row: any) => row.customer_name || row.receiver_name || 'N/A',
    },
    {
      key: 'delivery_address',
      header: 'Address',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.delivery_address || 'N/A'}
        </div>
      ),
    },
    {
      key: 'courier_id',
      header: 'Assigned Courier',
      render: (row: any) => {
        if (row.courier_name || row.courier_id) {
          return row.courier_name || `Courier #${row.courier_id}`
        }
        return (
          <Badge variant="warning">Unassigned</Badge>
        )
      },
    },
    {
      key: 'priority',
      header: 'Priority',
      render: (row: any) => {
        const priority = row.priority || 'normal'
        const variant = priority === 'high' ? 'danger' : priority === 'urgent' ? 'danger' : 'default'
        return <Badge variant={variant}>{priority}</Badge>
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant="default">
          {row.status || 'scheduled'}
        </Badge>
      ),
    },
  ]

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
        <p className="text-red-800">Error loading scheduled deliveries: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Scheduled Deliveries</h1>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Schedule Delivery
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Today</p>
                <p className="text-2xl font-bold text-blue-600">{stats.today}</p>
              </div>
              <Calendar className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">This Week</p>
                <p className="text-2xl font-bold text-orange-600">{stats.thisWeek}</p>
              </div>
              <Package className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Scheduled</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                <span className="text-gray-600 text-xl">#</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Simple Calendar View */}
      <Card>
        <CardHeader>
          <CardTitle>Delivery Calendar - Next 7 Days</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-7 gap-2">
            {Array.from({ length: 7 }, (_, i) => {
              const date = new Date()
              date.setDate(date.getDate() + i)
              const dateStr = date.toISOString().split('T')[0]
              const dayDeliveries = scheduledData.filter((d: any) => {
                const scheduled = new Date(d.scheduled_date || d.delivery_date).toISOString().split('T')[0]
                return scheduled === dateStr
              })
              const isToday = i === 0

              return (
                <div
                  key={i}
                  className={`p-3 rounded-lg text-center ${
                    isToday ? 'bg-blue-100 border-2 border-blue-500' : 'bg-gray-50'
                  }`}
                >
                  <p className="text-xs text-gray-500">
                    {date.toLocaleDateString('en-US', { weekday: 'short' })}
                  </p>
                  <p className={`text-lg font-bold ${isToday ? 'text-blue-600' : 'text-gray-900'}`}>
                    {date.getDate()}
                  </p>
                  <p className="text-xs text-gray-500">
                    {date.toLocaleDateString('en-US', { month: 'short' })}
                  </p>
                  <div className="mt-2">
                    {dayDeliveries.length > 0 ? (
                      <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-600 text-white text-xs font-bold rounded-full">
                        {dayDeliveries.length}
                      </span>
                    ) : (
                      <span className="inline-flex items-center justify-center w-6 h-6 bg-gray-200 text-gray-400 text-xs rounded-full">
                        0
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Scheduled Deliveries Table */}
      <Card>
        <CardHeader>
          <CardTitle>Upcoming Deliveries</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search deliveries..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-48">
                <Input
                  type="date"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  placeholder="Filter by date"
                />
              </div>
            </div>

            <Table
              data={displayData.slice((currentPage - 1) * pageSize, currentPage * pageSize)}
              columns={columns}
            />

            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(displayData.length / pageSize)}
              onPageChange={setCurrentPage}
              totalItems={displayData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
