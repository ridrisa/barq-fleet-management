import { useState } from 'react'
import { Plus, Search, Edit, Trash2, FileText, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { buildingsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { BuildingForm, BuildingFormData } from '@/components/forms/BuildingForm'
import { FileUpload } from '@/components/ui/FileUpload'

export default function Buildings() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isFloorPlanModalOpen, setIsFloorPlanModalOpen] = useState(false)
  const [selectedBuilding, setSelectedBuilding] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [editingBuilding, setEditingBuilding] = useState<any>(null)

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
    paginatedData: _buildings,
    filteredData,
  } = useDataTable({
    queryKey: 'buildings',
    queryFn: buildingsAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleDelete, handleCreate, handleUpdate } = useCRUD({
    queryKey: 'buildings',
    entityName: 'Building',
    create: buildingsAPI.create,
    update: buildingsAPI.update,
    delete: buildingsAPI.delete,
  })

  // Filter by status
  const statusFilteredData = statusFilter === 'all'
    ? filteredData
    : filteredData.filter((b: any) => {
        if (statusFilter === 'full') {
          return b.occupied >= b.capacity
        }
        return b.status === statusFilter
      })

  const paginatedFilteredData = statusFilteredData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const handleFormSubmit = async (data: BuildingFormData) => {
    if (editingBuilding) {
      await handleUpdate(editingBuilding.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setEditingBuilding(null)
  }

  const handleEdit = (building: any) => {
    setEditingBuilding(building)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingBuilding(null)
  }

  const handleFloorPlanUpload = async (files: File[]) => {
    // TODO: Implement floor plan upload to cloud storage
    console.log('Uploading floor plan:', files)
  }

  const getOccupancyPercentage = (occupied: number, capacity: number) => {
    return capacity > 0 ? Math.round((occupied / capacity) * 100) : 0
  }

  const getOccupancyBadgeVariant = (percentage: number) => {
    if (percentage >= 90) return 'danger'
    if (percentage >= 75) return 'warning'
    return 'success'
  }

  const columns = [
    {
      key: 'name',
      header: 'Building Name',
      sortable: true,
      render: (row: any) => (
        <div>
          <div className="font-medium">{row.name}</div>
          <div className="text-sm text-gray-500">{row.building_code || 'N/A'}</div>
        </div>
      ),
    },
    {
      key: 'location',
      header: 'Location',
      render: (row: any) => (
        <div>
          <div>{row.address || 'N/A'}</div>
          <div className="text-sm text-gray-500">{row.city}, {row.country}</div>
        </div>
      ),
    },
    {
      key: 'total_rooms',
      header: 'Total Rooms',
      sortable: true,
      render: (row: any) => row.total_rooms || 0,
    },
    {
      key: 'occupied',
      header: 'Occupied',
      sortable: true,
      render: (row: any) => {
        const occupied = row.occupied || 0
        const capacity = row.capacity || 0
        return `${occupied}/${capacity}`
      },
    },
    {
      key: 'capacity',
      header: 'Capacity',
      sortable: true,
      render: (row: any) => {
        const occupied = row.occupied || 0
        const capacity = row.capacity || 0
        const percentage = getOccupancyPercentage(occupied, capacity)
        return (
          <div className="space-y-1">
            <Badge variant={getOccupancyBadgeVariant(percentage)}>
              {percentage}%
            </Badge>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  percentage >= 90 ? 'bg-red-500' :
                  percentage >= 75 ? 'bg-yellow-500' :
                  'bg-green-500'
                }`}
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        )
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge
          variant={
            row.status === 'active' ? 'success' :
            row.status === 'maintenance' ? 'warning' :
            row.status === 'under_construction' ? 'info' :
            'default'
          }
        >
          {row.status || 'active'}
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
            onClick={() => handleEdit(row)}
            title="Edit"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setSelectedBuilding(row)
              setIsFloorPlanModalOpen(true)
            }}
            title="Floor Plan"
          >
            <FileText className="h-4 w-4" />
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
          Error loading buildings: {error.message}
        </p>
      </div>
    )
  }

  const totalBuildings = filteredData.length
  const totalCapacity = filteredData.reduce((sum: number, b: any) => sum + (b.capacity || 0), 0)
  const totalOccupied = filteredData.reduce((sum: number, b: any) => sum + (b.occupied || 0), 0)
  const occupancyRate = totalCapacity > 0 ? Math.round((totalOccupied / totalCapacity) * 100) : 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Buildings</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Building
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {totalBuildings}
              </p>
              <p className="text-sm text-gray-600">Total Buildings</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {totalCapacity}
              </p>
              <p className="text-sm text-gray-600">Total Capacity</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {occupancyRate}%
              </p>
              <p className="text-sm text-gray-600">Occupancy Rate</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Buildings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <Input
              placeholder="Search buildings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              className="flex-1"
            />
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Status' },
                { value: 'active', label: 'Active' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'under_construction', label: 'Under Construction' },
                { value: 'full', label: 'Full' },
              ]}
              className="w-48"
            />
          </div>
          <Table data={paginatedFilteredData} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={statusFilteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Building Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingBuilding ? 'Edit Building' : 'New Building'}
        size="lg"
      >
        <BuildingForm
          initialData={editingBuilding}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          mode={editingBuilding ? 'edit' : 'create'}
        />
      </Modal>

      {/* Floor Plan Modal */}
      <Modal
        isOpen={isFloorPlanModalOpen}
        onClose={() => {
          setIsFloorPlanModalOpen(false)
          setSelectedBuilding(null)
        }}
        title="Floor Plan"
        size="lg"
      >
        <div className="space-y-4">
          {selectedBuilding?.floor_plan_url ? (
            <div>
              <img
                src={selectedBuilding.floor_plan_url}
                alt="Floor plan"
                className="max-w-full rounded-lg border"
              />
              <div className="mt-4 flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => window.open(selectedBuilding.floor_plan_url, '_blank')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Floor Plan
                </Button>
              </div>
            </div>
          ) : (
            <div>
              <p className="text-sm text-gray-600 mb-4">
                Upload a floor plan for {selectedBuilding?.name}
              </p>
              <FileUpload
                onFilesSelected={handleFloorPlanUpload}
                accept={{ 'image/*': ['.png', '.jpg', '.jpeg'], 'application/pdf': ['.pdf'] }}
                maxFiles={1}
                maxSize={5 * 1024 * 1024}
              />
            </div>
          )}
        </div>
      </Modal>
    </div>
  )
}
