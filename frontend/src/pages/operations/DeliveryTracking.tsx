import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, MapPin, Clock, Package, Filter } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { deliveriesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'

export default function DeliveryTracking() {
  useTranslation()
  const [statusFilter, setStatusFilter] = useState<string>('all')

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
    queryKey: 'deliveries-tracking',
    queryFn: deliveriesAPI.getAll,
    pageSize: 15,
  })

  // Filter by status
  const statusFilteredData = statusFilter === 'all'
    ? filteredData
    : filteredData.filter((d: any) => d.status === statusFilter)

  // Summary stats
  const stats = {
    total: filteredData.length,
    inTransit: filteredData.filter((d: any) => d.status === 'in_transit').length,
    delivered: filteredData.filter((d: any) => d.status === 'delivered').length,
    pending: filteredData.filter((d: any) => d.status === 'pending').length,
  }

  const getStatusVariant = (status: string) => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      delivered: 'success',
      in_transit: 'warning',
      pending: 'default',
      failed: 'danger',
      returned: 'danger',
    }
    return variants[status] || 'default'
  }

  const columns = [
    {
      key: 'tracking_number',
      header: 'Tracking #',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.tracking_number || `TRK-${row.id?.toString().padStart(6, '0')}`}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={getStatusVariant(row.status || 'pending')}>
          {row.status || 'pending'}
        </Badge>
      ),
    },
    {
      key: 'courier_id',
      header: 'Courier',
      render: (row: any) => row.courier_name || `Courier #${row.courier_id || 'N/A'}`,
    },
    {
      key: 'customer_name',
      header: 'Customer',
      render: (row: any) => row.customer_name || row.receiver_name || 'N/A',
    },
    {
      key: 'pickup_address',
      header: 'From',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.pickup_address || 'N/A'}
        </div>
      ),
    },
    {
      key: 'delivery_address',
      header: 'To',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.delivery_address || 'N/A'}
        </div>
      ),
    },
    {
      key: 'estimated_delivery',
      header: 'ETA',
      render: (row: any) => {
        if (row.estimated_delivery) {
          return (
            <div className="flex items-center gap-1 text-sm">
              <Clock className="h-3 w-3 text-gray-400" />
              {new Date(row.estimated_delivery).toLocaleTimeString()}
            </div>
          )
        }
        return <span className="text-gray-400">N/A</span>
      },
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
        <p className="text-red-800">Error loading deliveries: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Real-Time Delivery Tracking</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Deliveries</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <Package className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">In Transit</p>
                <p className="text-2xl font-bold text-orange-600">{stats.inTransit}</p>
              </div>
              <MapPin className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Delivered</p>
                <p className="text-2xl font-bold text-green-600">{stats.delivered}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-green-600 text-xl">✓</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-gray-600">{stats.pending}</p>
              </div>
              <Clock className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tracking Table */}
      <Card>
        <CardHeader>
          <CardTitle>Active Deliveries</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by tracking number, courier, customer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-48">
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Statuses' },
                    { value: 'pending', label: 'Pending' },
                    { value: 'in_transit', label: 'In Transit' },
                    { value: 'delivered', label: 'Delivered' },
                    { value: 'failed', label: 'Failed' },
                    { value: 'returned', label: 'Returned' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
            </div>

            <Table data={statusFilteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)} columns={columns} />

            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(statusFilteredData.length / pageSize)}
              onPageChange={setCurrentPage}
              totalItems={statusFilteredData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>

      {/* Delivery Summary by Status */}
      <Card>
        <CardHeader>
          <CardTitle>Delivery Status Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg text-center">
              <Package className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-blue-600">{stats.total}</p>
              <p className="text-sm text-gray-600">Total Deliveries</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg text-center">
              <MapPin className="h-8 w-8 text-orange-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-orange-600">{stats.inTransit}</p>
              <p className="text-sm text-gray-600">In Transit</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg text-center">
              <div className="h-8 w-8 rounded-full bg-green-600 mx-auto mb-2 flex items-center justify-center">
                <span className="text-white text-lg">✓</span>
              </div>
              <p className="text-2xl font-bold text-green-600">{stats.delivered}</p>
              <p className="text-sm text-gray-600">Delivered</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg text-center">
              <Clock className="h-8 w-8 text-gray-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-gray-600">{stats.pending}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
