import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Search, TrendingUp, BarChart3, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { deliveriesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'

export default function DeliveryHistory() {
  useTranslation()
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')

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
    queryKey: 'delivery-history',
    queryFn: deliveriesAPI.getAll,
    pageSize: 20,
  })

  // Filter by date range
  let displayData = filteredData
  if (startDate || endDate) {
    displayData = displayData.filter((d: any) => {
      const deliveryDate = new Date(d.delivery_date || d.created_at)
      const start = startDate ? new Date(startDate) : new Date(0)
      const end = endDate ? new Date(endDate) : new Date()
      return deliveryDate >= start && deliveryDate <= end
    })
  }

  // Calculate analytics
  const stats = {
    total: displayData.length,
    delivered: displayData.filter((d: any) => d.status === 'delivered').length,
    failed: displayData.filter((d: any) => d.status === 'failed' || d.status === 'returned').length,
    successRate: displayData.length > 0
      ? ((displayData.filter((d: any) => d.status === 'delivered').length / displayData.length) * 100).toFixed(1)
      : 0,
  }

  const handleExport = () => {
    alert('Exporting delivery history to Excel...')
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
      key: 'delivery_date',
      header: 'Date',
      render: (row: any) => {
        const date = row.delivery_date || row.created_at
        return date ? new Date(date).toLocaleDateString() : 'N/A'
      },
    },
    {
      key: 'customer_name',
      header: 'Customer',
      render: (row: any) => row.customer_name || row.receiver_name || 'N/A',
    },
    {
      key: 'courier_id',
      header: 'Courier',
      render: (row: any) => row.courier_name || `Courier #${row.courier_id || 'N/A'}`,
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
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const status = row.status || 'unknown'
        const variant = status === 'delivered' ? 'success' : status === 'failed' ? 'danger' : 'default'
        return <Badge variant={variant}>{status}</Badge>
      },
    },
    {
      key: 'cod_amount',
      header: 'COD',
      render: (row: any) => {
        const amount = row.cod_amount || row.amount
        return amount ? (
          <span className="font-semibold text-green-600">${parseFloat(amount).toFixed(2)}</span>
        ) : (
          <span className="text-gray-400">-</span>
        )
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
        <p className="text-red-800">Error loading delivery history: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Delivery History & Analytics</h1>
        <Button variant="outline" onClick={handleExport}>
          <Download className="h-4 w-4 mr-2" />
          Export
        </Button>
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
              <BarChart3 className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Successful</p>
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
                <p className="text-sm font-medium text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                <span className="text-red-600 text-xl">✗</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-blue-600">{stats.successRate}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Deliveries Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-100 rounded-lg p-12 text-center">
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Line chart showing delivery trends</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Success Rate Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-100 rounded-lg p-12 text-center">
              <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Success rate over time</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Delivery History Table */}
      <Card>
        <CardHeader>
          <CardTitle>Historical Records</CardTitle>
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
              <div className="w-full sm:w-40">
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  placeholder="Start date"
                />
              </div>
              <div className="w-full sm:w-40">
                <Input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  placeholder="End date"
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
