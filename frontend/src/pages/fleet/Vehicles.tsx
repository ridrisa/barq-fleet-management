import { useState, useMemo, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Eye } from 'lucide-react'
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
import { useCRUD } from '@/hooks/useCRUD'
import { VehicleForm, VehicleFormData } from '@/components/forms/VehicleForm'

export default function Vehicles() {
  const { t: _t } = useTranslation()
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingVehicle, setEditingVehicle] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10

  // Fetch ALL vehicles - use direct useQuery instead of useDataTable
  // This ensures we get all data for filter dropdowns and client-side pagination
  const {
    data: allVehicles = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['vehicles'],
    queryFn: () => vehiclesAPI.getAll(), // Uses default limit=2000 for all vehicles
  })

  // Apply search filter to all data
  const filteredData = useMemo(() => {
    if (!searchTerm) return allVehicles
    const lowerSearchTerm = searchTerm.toLowerCase()
    return allVehicles.filter((item: any) =>
      Object.values(item).some((value) =>
        String(value).toLowerCase().includes(lowerSearchTerm)
      )
    )
  }, [allVehicles, searchTerm])

  // Reset to page 1 when search or filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, statusFilter])

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

  // Helper to normalize status (handle both uppercase from DB and lowercase)
  const normalizeStatus = (status: string) => status?.toUpperCase?.() || ''

  // Apply status filter to filtered data
  const finalFilteredData = useMemo(() => {
    if (!statusFilter) return filteredData
    const filterUpper = statusFilter.toUpperCase()
    return filteredData.filter((v: any) => normalizeStatus(v.status) === filterUpper)
  }, [filteredData, statusFilter])

  // Paginate final filtered data
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    const end = start + pageSize
    return finalFilteredData.slice(start, end)
  }, [finalFilteredData, currentPage, pageSize])

  const totalPages = Math.ceil(finalFilteredData.length / pageSize)

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
      render: (row: any) => {
        // Normalize status to handle uppercase from backend
        const status = row.status?.toUpperCase?.() || ''
        const statusLabels: Record<string, string> = {
          ACTIVE: 'Active',
          INACTIVE: 'Inactive',
          MAINTENANCE: 'Maintenance',
          RETIRED: 'Retired',
          REPAIR: 'Repair',
        }
        return (
          <Badge
            variant={
              status === 'ACTIVE'
                ? 'success'
                : status === 'INACTIVE'
                ? 'default'
                : status === 'MAINTENANCE' || status === 'REPAIR'
                ? 'warning'
                : 'danger'
            }
          >
            {statusLabels[status] || status}
          </Badge>
        )
      },
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
            onClick={() => navigate(`/fleet/vehicles/${row.id}`)}
            title="View Details"
          >
            <Eye className="h-4 w-4 text-blue-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenEditModal(row)}
            title="Edit"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete"
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

  // Count vehicles by status (using ALL vehicles, not filtered)
  const activeVehicles = allVehicles.filter((v: any) => normalizeStatus(v.status) === 'ACTIVE').length
  const inactiveVehicles = allVehicles.filter((v: any) => normalizeStatus(v.status) === 'INACTIVE').length
  const maintenanceVehicles = allVehicles.filter((v: any) => normalizeStatus(v.status) === 'MAINTENANCE').length
  const retiredVehicles = allVehicles.filter((v: any) => normalizeStatus(v.status) === 'RETIRED').length

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
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('')}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {allVehicles.length}
              </p>
              <p className="text-sm text-gray-600">Total Vehicles</p>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('ACTIVE')}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {activeVehicles}
              </p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('INACTIVE')}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-600">
                {inactiveVehicles}
              </p>
              <p className="text-sm text-gray-600">Inactive</p>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('MAINTENANCE')}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {maintenanceVehicles}
              </p>
              <p className="text-sm text-gray-600">Maintenance</p>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setStatusFilter('RETIRED')}>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {retiredVehicles}
              </p>
              <p className="text-sm text-gray-600">Retired</p>
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
                { value: 'ACTIVE', label: 'Active' },
                { value: 'INACTIVE', label: 'Inactive' },
                { value: 'MAINTENANCE', label: 'Maintenance' },
                { value: 'RETIRED', label: 'Retired' },
                { value: 'REPAIR', label: 'Repair' },
              ]}
            />
          </div>
          <Table data={paginatedData} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={finalFilteredData.length}
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
