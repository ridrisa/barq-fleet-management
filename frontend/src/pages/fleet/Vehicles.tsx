import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { vehiclesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { VehicleForm, VehicleFormData } from '@/components/forms/VehicleForm'

export default function Vehicles() {
  const { t: _t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')

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

  const handleOpenEditModal = (vehicle: any) => {
    setEditingVehicle(vehicle)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingVehicle(null)
  }

  const handleFormSubmit = async (data: VehicleFormData) => {
    if (editingVehicle) {
      const result = await handleUpdate(editingVehicle.id, data)
      if (result) {
        handleCloseModal()
      }
    } else {
      const result = await handleCreate(data)
      if (result) {
        handleCloseModal()
      }
    }
  }

  // Filter by status
  const filteredByStatus = statusFilter
    ? vehicles.filter((v: any) => v.status === statusFilter)
    : vehicles

  const columns = [
    {
      key: 'plate_number',
      header: 'Plate Number',
      sortable: true,
      render: (row: any) => (
        <span className="font-medium">{row.plate_number}</span>
      ),
    },
    {
      key: 'make',
      header: 'Make',
      sortable: true,
    },
    {
      key: 'model',
      header: 'Model',
      sortable: true,
    },
    {
      key: 'year',
      header: 'Year',
      sortable: true,
    },
    {
      key: 'type',
      header: 'Type',
      render: (row: any) => {
        const typeLabels: Record<string, string> = {
          sedan: 'Sedan',
          van: 'Van',
          truck: 'Truck',
          motorcycle: 'Motorcycle',
          bicycle: 'Bicycle',
        }
        return (
          <Badge variant="default">
            {typeLabels[row.type] || row.type}
          </Badge>
        )
      },
    },
    {
      key: 'current_mileage',
      header: 'Mileage (km)',
      render: (row: any) => row.current_mileage?.toLocaleString() || 'N/A',
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'available'
              ? 'success'
              : row.status === 'in_use'
              ? 'warning'
              : row.status === 'maintenance'
              ? 'danger'
              : 'default'
          }
        >
          {row.status === 'available'
            ? 'Available'
            : row.status === 'in_use'
            ? 'In Use'
            : row.status === 'maintenance'
            ? 'Maintenance'
            : 'Retired'}
        </Badge>
      ),
    },
    {
      key: 'assigned_to',
      header: 'Assigned To',
      render: (row: any) => {
        return row.assigned_courier_name ? (
          <span className="text-sm">{row.assigned_courier_name}</span>
        ) : (
          <span className="text-gray-400">Unassigned</span>
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
        <p className="text-red-800">
          Error loading vehicles: {error.message}
        </p>
      </div>
    )
  }

  const availableVehicles = vehicles.filter((v: any) => v.status === 'available').length
  const inUseVehicles = vehicles.filter((v: any) => v.status === 'in_use').length
  const maintenanceVehicles = vehicles.filter((v: any) => v.status === 'maintenance').length
  // Note: retiredVehicles count available if needed
  // const retiredVehicles = vehicles.filter((v: any) => v.status === 'retired').length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Vehicle Management</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Add Vehicle
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {vehicles.length}
              </p>
              <p className="text-sm text-gray-600">Total Vehicles</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {availableVehicles}
              </p>
              <p className="text-sm text-gray-600">Available</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {inUseVehicles}
              </p>
              <p className="text-sm text-gray-600">In Use</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {maintenanceVehicles}
              </p>
              <p className="text-sm text-gray-600">Maintenance</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Vehicles Table */}
      <Card>
        <CardHeader>
          <CardTitle>Vehicles</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search vehicles by plate number, make, or model..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              />
            </div>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { value: '', label: 'All Status' },
                { value: 'available', label: 'Available' },
                { value: 'in_use', label: 'In Use' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'retired', label: 'Retired' },
              ]}
            />
          </div>
          <Table data={filteredByStatus} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Vehicle Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}
        size="lg"
      >
        <VehicleForm
          initialData={editingVehicle}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingVehicle ? 'edit' : 'create'}
        />
      </Modal>
    </div>
  )
}
