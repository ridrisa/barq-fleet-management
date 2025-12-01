import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, Download, DollarSign, Filter, CheckCircle, XCircle } from 'lucide-react'
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
import { codAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { CODForm } from '@/components/forms/CODForm'

export default function CODManagement() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCOD, setEditingCOD] = useState<any>(null)
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
    queryKey: 'cod-all',
    queryFn: codAPI.getAll,
    pageSize: 15,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'cod-all',
    entityName: 'COD Transaction',
    create: codAPI.create,
    update: codAPI.update,
    delete: codAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingCOD(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (cod: any) => {
    setEditingCOD(cod)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingCOD(null)
  }

  const handleExportToExcel = () => {
    alert('Exporting COD records to Excel for accounting...')
  }

  const handleReconcile = async (codId: number) => {
    if (window.confirm('Mark this COD transaction as reconciled?')) {
      await handleUpdate(codId, { reconciled: true, reconciliation_date: new Date().toISOString().split('T')[0] })
    }
  }

  // Apply filters
  let displayData = filteredData
  if (statusFilter !== 'all') {
    displayData = displayData.filter((c: any) => c.status === statusFilter)
  }
  if (dateFilter) {
    displayData = displayData.filter((c: any) => {
      const codDate = new Date(c.collection_date || c.created_at).toISOString().split('T')[0]
      return codDate === dateFilter
    })
  }

  // Summary stats
  const stats = {
    total: filteredData.reduce((sum: number, c: any) => sum + (parseFloat(c.amount) || 0), 0),
    collected: filteredData
      .filter((c: any) => c.collected || c.status === 'collected' || c.status === 'reconciled')
      .reduce((sum: number, c: any) => sum + (parseFloat(c.amount) || 0), 0),
    pending: filteredData
      .filter((c: any) => !c.collected && c.status === 'pending')
      .reduce((sum: number, c: any) => sum + (parseFloat(c.amount) || 0), 0),
    reconciled: filteredData
      .filter((c: any) => c.reconciled || c.status === 'reconciled')
      .reduce((sum: number, c: any) => sum + (parseFloat(c.amount) || 0), 0),
  }

  const variance = stats.collected - stats.reconciled

  const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      reconciled: 'success',
      collected: 'warning',
      pending: 'default',
      disputed: 'danger',
    }
    return variants[status] || 'default'
  }

  const columns = [
    {
      key: 'delivery_id',
      header: 'Delivery ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.delivery_id || `DEL-${row.id?.toString().padStart(6, '0')}`}
        </div>
      ),
    },
    {
      key: 'courier_id',
      header: 'Courier',
      render: (row: any) => row.courier_name || `Courier #${row.courier_id || 'N/A'}`,
    },
    {
      key: 'amount',
      header: 'Amount',
      render: (row: any) => (
        <span className="font-semibold text-green-600">
          SAR {parseFloat(row.amount || 0).toFixed(2)}
        </span>
      ),
    },
    {
      key: 'collected',
      header: 'Collected',
      render: (row: any) => (
        row.collected || row.status === 'collected' || row.status === 'reconciled' ? (
          <CheckCircle className="h-5 w-5 text-green-600" />
        ) : (
          <XCircle className="h-5 w-5 text-gray-400" />
        )
      ),
    },
    {
      key: 'collection_date',
      header: 'Collection Date',
      render: (row: any) => {
        const date = row.collection_date || row.collected_date
        return date ? new Date(date).toLocaleDateString() : '-'
      },
    },
    {
      key: 'reconciled',
      header: 'Reconciled',
      render: (row: any) => (
        row.reconciled || row.status === 'reconciled' ? (
          <CheckCircle className="h-5 w-5 text-green-600" />
        ) : (
          <XCircle className="h-5 w-5 text-gray-400" />
        )
      ),
    },
    {
      key: 'reconciliation_date',
      header: 'Reconciliation Date',
      render: (row: any) => {
        const date = row.reconciliation_date
        return date ? new Date(date).toLocaleDateString() : '-'
      },
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
      key: 'actions',
      header: 'Actions',
      render: (row: any) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
            title="Edit COD"
          >
            <Edit className="h-4 w-4" />
          </Button>
          {!row.reconciled && row.status !== 'reconciled' && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleReconcile(row.id)}
              title="Mark as reconciled"
            >
              <CheckCircle className="h-4 w-4 text-green-600" />
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete COD"
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
        <p className="text-red-800">Error loading COD records: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Cash on Delivery (COD) Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportToExcel}>
            <Download className="h-4 w-4 mr-2" />
            Export for Accounting
          </Button>
          <Button onClick={handleOpenCreateModal}>
            <Plus className="h-4 w-4 mr-2" />
            Record COD
          </Button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KPICard
          title="Total COD"
          value={`SAR ${stats.total.toFixed(2)}`}
          icon={<DollarSign className="h-6 w-6" />}
          color="blue"
          loading={isLoading}
        />
        <KPICard
          title="Collected"
          value={`SAR ${stats.collected.toFixed(2)}`}
          icon={<CheckCircle className="h-6 w-6" />}
          color="green"
          loading={isLoading}
        />
        <KPICard
          title="Pending"
          value={`SAR ${stats.pending.toFixed(2)}`}
          icon={<XCircle className="h-6 w-6" />}
          color="yellow"
          loading={isLoading}
        />
        <KPICard
          title="Reconciled"
          value={`SAR ${stats.reconciled.toFixed(2)}`}
          icon={<CheckCircle className="h-6 w-6" />}
          color="purple"
          loading={isLoading}
        />
        <KPICard
          title={variance >= 0 ? 'To Reconcile' : 'Over Reconciled'}
          value={`SAR ${Math.abs(variance).toFixed(2)}`}
          icon={<DollarSign className="h-6 w-6" />}
          color={variance >= 0 ? 'indigo' : 'red'}
          loading={isLoading}
        />
      </div>

      {/* COD Records Table */}
      <Card>
        <CardHeader>
          <CardTitle>All COD Transactions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search by delivery ID, courier, amount..."
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
                    { value: 'collected', label: 'Collected' },
                    { value: 'reconciled', label: 'Reconciled' },
                    { value: 'disputed', label: 'Disputed' },
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

      {/* COD Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingCOD ? 'Edit COD Transaction' : 'Record New COD'}
        size="lg"
      >
        <CODForm
          initialData={editingCOD}
          onSubmit={async (data) => {
            if (editingCOD) {
              await handleUpdate(editingCOD.id, data)
            } else {
              await handleCreate(data)
            }
            handleCloseModal()
          }}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingCOD ? 'edit' : 'create'}
          couriers={[]}
        />
      </Modal>
    </div>
  )
}
