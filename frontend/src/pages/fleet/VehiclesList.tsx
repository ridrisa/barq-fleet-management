import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { vehiclesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { VehicleForm, type VehicleFormData } from '@/components/forms'
import type { Vehicle } from '@/types/fleet'

export default function VehiclesList() {
  const { t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null)

  // Use the reusable data table hook
  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: vehicles,
    filteredData,
  } = useDataTable({
    queryKey: 'vehicles',
    queryFn: vehiclesAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'vehicles',
    entityName: 'Vehicle',
    create: vehiclesAPI.create,
    update: vehiclesAPI.update,
    delete: vehiclesAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingVehicle(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (vehicle: Vehicle) => {
    setEditingVehicle(vehicle)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingVehicle(null)
  }

  const handleSubmit = async (data: VehicleFormData) => {
    if (editingVehicle) {
      await handleUpdate(editingVehicle.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  const columns = [
    { key: 'plate_number', header: 'Plate Number', sortable: true },
    { key: 'make', header: 'Make' },
    { key: 'model', header: 'Model' },
    { key: 'year', header: 'Year' },
    {
      key: 'mileage',
      header: 'Mileage (km)',
      render: (row: Vehicle) => row.mileage?.toLocaleString() || 'N/A',
    },
    {
      key: 'assigned_courier_id',
      header: 'Assigned To',
      render: (row: Vehicle) =>
        row.assigned_courier_id === null || row.assigned_courier_id === undefined
          ? 'Unassigned'
          : row.assigned_courier_id,
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: Vehicle) => (
        <Badge
          variant={
            row.status === 'available'
              ? 'success'
              : row.status === 'in_use'
              ? 'info'
              : row.status === 'maintenance'
              ? 'warning'
              : row.status === 'retired'
              ? 'danger'
              : 'default'
          }
        >
          {row.status || 'available'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: Vehicle) => (
        <div className="flex gap-2">
          <Button size="sm" variant="ghost" onClick={() => handleOpenEditModal(row)}>
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={async () => {
              await handleDelete(row.id)
            }}
            disabled={isMutating}
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
        <p className="text-red-800">
          Error loading vehicles: {error.message}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t('nav.vehicles')}</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Add Vehicle
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Vehicles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search vehicles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={vehicles} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}
        size="lg"
      >
        <VehicleForm
          initialData={editingVehicle}
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
        />
      </Modal>
    </div>
  )
}
