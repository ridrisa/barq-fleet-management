import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, Users, CheckCircle, Clock } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { handoversAPI, couriersAPI, vehiclesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { HandoverForm } from '@/components/forms/HandoverForm'

export default function Handovers() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingHandover, setEditingHandover] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: handovers,
    filteredData,
  } = useDataTable({
    queryKey: 'handovers',
    queryFn: handoversAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'handovers',
    entityName: 'Handover',
    create: handoversAPI.create,
    update: handoversAPI.update,
    delete: handoversAPI.delete,
  })

  // Fetch couriers and vehicles for the form
  const { data: couriers = [], isLoading: couriersLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: couriersAPI.getAll,
  })

  const { data: vehicles = [], isLoading: vehiclesLoading } = useQuery({
    queryKey: ['vehicles'],
    queryFn: vehiclesAPI.getAll,
  })

  const handleOpenCreateModal = () => {
    setEditingHandover(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (handover: any) => {
    setEditingHandover(handover)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingHandover(null)
  }

  const handleSubmit = async (data: any) => {
    if (editingHandover) {
      await handleUpdate(editingHandover.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  // Calculate summary stats
  const stats = {
    total: filteredData.length,
    active: filteredData.filter((h: any) => h.status === 'active' || h.status === 'in_progress').length,
    completed: filteredData.filter((h: any) => h.status === 'completed').length,
    pending: filteredData.filter((h: any) => h.status === 'pending').length,
  }

  const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      completed: 'success',
      in_progress: 'warning',
      active: 'warning',
      pending: 'default',
    }
    return variants[status] || 'default'
  }

  const columns = [
    {
      key: 'handover_id',
      header: 'Handover ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.handover_number || `HO-${row.id?.toString().padStart(5, '0')}`}
        </div>
      ),
    },
    {
      key: 'from_courier',
      header: 'From',
      render: (row: any) => (
        <div className="text-sm">
          <div className="font-medium text-gray-900">
            {row.from_courier_name || `Courier #${row.from_courier_id || 'N/A'}`}
          </div>
          <div className="text-xs text-gray-500">
            {row.from_shift || 'Morning Shift'}
          </div>
        </div>
      ),
    },
    {
      key: 'to_courier',
      header: 'To',
      render: (row: any) => (
        <div className="text-sm">
          <div className="font-medium text-gray-900">
            {row.to_courier_name || `Courier #${row.to_courier_id || 'N/A'}`}
          </div>
          <div className="text-xs text-gray-500">
            {row.to_shift || 'Evening Shift'}
          </div>
        </div>
      ),
    },
    {
      key: 'vehicle_id',
      header: 'Vehicle',
      render: (row: any) => row.vehicle_plate || `Vehicle #${row.vehicle_id || 'N/A'}`,
    },
    {
      key: 'handover_date',
      header: 'Date & Time',
      render: (row: any) => {
        const date = row.handover_date || row.created_at
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
      key: 'checklist_items',
      header: 'Checklist',
      render: (row: any) => {
        const total = row.checklist_items?.length || 0
        const completed = row.checklist_items?.filter((item: any) => item.checked).length || 0
        return total > 0 ? (
          <div className="text-sm">
            <span className="font-medium">{completed}/{total}</span>
            <span className="text-xs text-gray-500 ml-1">items</span>
          </div>
        ) : (
          <span className="text-gray-400">-</span>
        )
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
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
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
        <p className="text-red-800">Error loading handovers: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Shift Handovers</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Create Handover
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Handovers</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-orange-600">{stats.active}</p>
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
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
              <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                <span className="text-gray-600 text-xl">⏳</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Handovers Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Handovers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search handovers by courier, vehicle..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={handovers} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Handover Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingHandover ? 'Edit Handover' : 'Create New Handover'}
        size="lg"
      >
        <HandoverForm
          initialData={editingHandover}
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating || couriersLoading || vehiclesLoading}
          couriers={couriers}
          vehicles={vehicles}
        />
      </Modal>
    </div>
  )
}
