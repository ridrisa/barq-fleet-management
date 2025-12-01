import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, Download, Printer, Filter, Package, TrendingUp, Map } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { KPICard } from '@/components/ui/KPICard'
import { deliveriesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { DeliveryForm } from '@/components/forms/DeliveryForm'

export default function Deliveries() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingDelivery, setEditingDelivery] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
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
    queryKey: 'deliveries-all',
    queryFn: deliveriesAPI.getAll,
    pageSize: 15,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'deliveries-all',
    entityName: 'Delivery',
    create: deliveriesAPI.create,
    update: deliveriesAPI.update,
    delete: deliveriesAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingDelivery(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (delivery: any) => {
    setEditingDelivery(delivery)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingDelivery(null)
  }

  const handleExportToExcel = () => {
    alert('Exporting deliveries to Excel...')
  }

  const handlePrintReceipt = (delivery: any) => {
    alert(`Printing receipt for delivery: ${delivery.tracking_number || delivery.id}`)
  }

  // Apply filters
  let displayData = filteredData
  if (statusFilter !== 'all') {
    displayData = displayData.filter((d: any) => d.status === statusFilter)
  }
  if (dateFilter) {
    displayData = displayData.filter((d: any) => {
      const deliveryDate = new Date(d.delivery_date || d.created_at).toISOString().split('T')[0]
      return deliveryDate === dateFilter
    })
  }

  // Summary stats
  const stats = {
    total: filteredData.length,
    completed: filteredData.filter((d: any) => d.status === 'delivered').length,
    inProgress: filteredData.filter((d: any) => d.status === 'in_transit' || d.status === 'pending').length,
    failed: filteredData.filter((d: any) => d.status === 'failed' || d.status === 'returned').length,
  }

  const successRate = stats.total > 0 ? ((stats.completed / stats.total) * 100).toFixed(1) : '0.0'

  const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      delivered: 'success',
      in_transit: 'warning',
      pending: 'default',
      failed: 'danger',
      returned: 'danger',
      cancelled: 'danger',
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
      header: 'Pickup',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.pickup_address || 'N/A'}
        </div>
      ),
    },
    {
      key: 'delivery_address',
      header: 'Delivery',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.delivery_address || 'N/A'}
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
    {
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
            title="Edit delivery"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handlePrintReceipt(row)}
            title="Print receipt"
          >
            <Printer className="h-4 w-4 text-blue-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete delivery"
          >
            <Trash2 className="h-4 w-4 text-red-600" />
          </Button>
        </div>
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
        <p className="text-red-800">Error loading deliveries: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Delivery Records</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => alert('Map view coming soon!')}>
            <Map className="h-4 w-4 mr-2" />
            Map View
          </Button>
          <Button variant="outline" onClick={handleExportToExcel}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleOpenCreateModal}>
            <Plus className="h-4 w-4 mr-2" />
            Add Delivery
          </Button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KPICard
          title="Total Deliveries"
          value={stats.total}
          icon={<Package className="h-6 w-6" />}
          color="blue"
          loading={isLoading}
        />
        <KPICard
          title="Success Rate"
          value={`${successRate}%`}
          icon={<TrendingUp className="h-6 w-6" />}
          color="green"
          trend={parseFloat(successRate) >= 80 ? 'up' : 'down'}
          loading={isLoading}
        />
        <KPICard
          title="Completed"
          value={stats.completed}
          icon={<Package className="h-6 w-6" />}
          color="green"
          loading={isLoading}
        />
        <KPICard
          title="In Progress"
          value={stats.inProgress}
          icon={<Package className="h-6 w-6" />}
          color="yellow"
          loading={isLoading}
        />
        <KPICard
          title="Failed"
          value={stats.failed}
          icon={<Package className="h-6 w-6" />}
          color="red"
          loading={isLoading}
        />
      </div>

      {/* Deliveries Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Deliveries</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search deliveries by tracking number, customer, courier..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Status' },
                    { value: 'pending', label: 'Pending' },
                    { value: 'in_transit', label: 'In Transit' },
                    { value: 'delivered', label: 'Delivered' },
                    { value: 'failed', label: 'Failed' },
                    { value: 'returned', label: 'Returned' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
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

      {/* Delivery Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingDelivery ? 'Edit Delivery' : 'Add New Delivery'}
        size="lg"
      >
        <DeliveryForm
          initialData={editingDelivery}
          onSubmit={async (data) => {
            if (editingDelivery) {
              await handleUpdate(editingDelivery.id, data)
            } else {
              await handleCreate(data)
            }
            handleCloseModal()
          }}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingDelivery ? 'edit' : 'create'}
          couriers={[]}
        />
      </Modal>
    </div>
  )
}
