import { useState } from 'react'
import { Plus, Search, Edit, Trash2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { couriersAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { CourierForm, CourierFormData } from '@/components/forms/CourierForm'

export default function Couriers() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingCourier, setEditingCourier] = useState<any>(null)

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
    paginatedData: couriers,
    filteredData,
  } = useDataTable({
    queryKey: 'couriers',
    queryFn: couriersAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'couriers',
    entityName: 'Courier',
    create: couriersAPI.create,
    update: couriersAPI.update,
    delete: couriersAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingCourier(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (courier: any) => {
    setEditingCourier(courier)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingCourier(null)
  }

  const handleFormSubmit = async (data: CourierFormData) => {
    if (editingCourier) {
      const result = await handleUpdate(editingCourier.id, data)
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

  const columns = [
    {
      key: 'employee_id',
      header: 'Employee ID',
      sortable: true,
    },
    {
      key: 'name',
      header: 'Name',
      sortable: true,
    },
    {
      key: 'email',
      header: 'Email',
      render: (row: any) => row.email || 'N/A',
    },
    {
      key: 'phone',
      header: 'Phone',
      render: (row: any) => row.phone || 'N/A',
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'active'
              ? 'success'
              : row.status === 'on_leave'
              ? 'warning'
              : 'danger'
          }
        >
          {row.status === 'active'
            ? 'Active'
            : row.status === 'on_leave'
            ? 'On Leave'
            : 'Terminated'}
        </Badge>
      ),
    },
    {
      key: 'vehicle_assigned',
      header: 'Vehicle Assigned',
      render: (row: any) => {
        return row.vehicle_plate_number ? (
          <Badge variant="default">{row.vehicle_plate_number}</Badge>
        ) : (
          <span className="text-gray-400">None</span>
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
          Error loading couriers: {error.message}
        </p>
      </div>
    )
  }

  const activeCouriers = couriers.filter((c: any) => c.status === 'active').length
  const onLeaveCouriers = couriers.filter((c: any) => c.status === 'on_leave').length
  const terminatedCouriers = couriers.filter((c: any) => c.status === 'terminated').length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Courier Management</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Add Courier
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {couriers.length}
              </p>
              <p className="text-sm text-gray-600">Total Couriers</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {activeCouriers}
              </p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {onLeaveCouriers}
              </p>
              <p className="text-sm text-gray-600">On Leave</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {terminatedCouriers}
              </p>
              <p className="text-sm text-gray-600">Terminated</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Couriers Table */}
      <Card>
        <CardHeader>
          <CardTitle>Couriers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search couriers by name, email, or phone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={couriers} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Courier Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingCourier ? 'Edit Courier' : 'Add New Courier'}
        size="lg"
      >
        <CourierForm
          initialData={editingCourier}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingCourier ? 'edit' : 'create'}
        />
      </Modal>
    </div>
  )
}
