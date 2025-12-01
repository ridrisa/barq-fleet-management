import { useState, useMemo } from 'react'
import { Plus, Search, Edit, Trash2, Eye } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { roomsAPI, buildingsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { RoomForm, RoomFormData } from '@/components/forms/RoomForm'
import { useQuery } from '@tanstack/react-query'

export default function Rooms() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false)
  const [selectedRoom, setSelectedRoom] = useState<any>(null)
  const [buildingFilter, setBuildingFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [editingRoom, setEditingRoom] = useState<any>(null)

  // Fetch buildings for filter and form
  const { data: buildings = [] } = useQuery({
    queryKey: ['buildings'],
    queryFn: () => buildingsAPI.getAll(0, 100),
  })

  // Use the reusable data table hook
  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages: _totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: _rooms,
    filteredData,
  } = useDataTable({
    queryKey: 'rooms',
    queryFn: roomsAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleDelete, handleCreate, handleUpdate } = useCRUD({
    queryKey: 'rooms',
    entityName: 'Room',
    create: roomsAPI.create,
    update: roomsAPI.update,
    delete: roomsAPI.delete,
  })

  // Filter by building and status
  const doubleFilteredData = useMemo(() => {
    let filtered = filteredData

    if (buildingFilter !== 'all') {
      filtered = filtered.filter((r: any) => String(r.building_id) === buildingFilter)
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((r: any) => r.status === statusFilter)
    }

    return filtered
  }, [filteredData, buildingFilter, statusFilter])

  const paginatedFilteredData = doubleFilteredData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const handleFormSubmit = async (data: RoomFormData) => {
    if (editingRoom) {
      await handleUpdate(editingRoom.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setEditingRoom(null)
  }

  const handleEdit = (room: any) => {
    setEditingRoom(room)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingRoom(null)
  }

  const handleViewDetails = (room: any) => {
    setSelectedRoom(room)
    setIsDetailsModalOpen(true)
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'available':
        return 'success'
      case 'occupied':
        return 'default'
      case 'full':
        return 'danger'
      case 'maintenance':
        return 'warning'
      default:
        return 'default'
    }
  }

  const getTypeBadgeVariant = (type: string) => {
    switch (type) {
      case 'single':
        return 'info'
      case 'shared':
        return 'default'
      case 'dormitory':
        return 'secondary'
      case 'suite':
        return 'success'
      default:
        return 'default'
    }
  }

  const columns = [
    {
      key: 'room_number',
      header: 'Room Number',
      sortable: true,
      render: (row: any) => (
        <div>
          <div className="font-medium">{row.room_number}</div>
          <div className="text-sm text-gray-500">Floor {row.floor || 'N/A'}</div>
        </div>
      ),
    },
    {
      key: 'building',
      header: 'Building',
      render: (row: any) => {
        const building = buildings.find((b: any) => b.id === row.building_id)
        return building?.name || `Building #${row.building_id}`
      },
    },
    {
      key: 'capacity',
      header: 'Capacity',
      sortable: true,
      render: (row: any) => {
        const capacity = row.capacity || 0
        const occupied = row.current_occupancy || 0
        return `${occupied}/${capacity} beds`
      },
    },
    {
      key: 'occupancy',
      header: 'Occupied',
      sortable: true,
      render: (row: any) => {
        const capacity = row.capacity || 0
        const occupied = row.current_occupancy || 0
        const percentage = capacity > 0 ? Math.round((occupied / capacity) * 100) : 0
        return (
          <div className="flex items-center gap-2">
            <div className="w-20 bg-gray-200 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  percentage >= 100 ? 'bg-red-500' :
                  percentage >= 75 ? 'bg-yellow-500' :
                  percentage > 0 ? 'bg-blue-500' :
                  'bg-gray-300'
                }`}
                style={{ width: `${Math.min(percentage, 100)}%` }}
              />
            </div>
            <span className="text-sm text-gray-600">{percentage}%</span>
          </div>
        )
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const capacity = row.capacity || 0
        const occupied = row.current_occupancy || 0
        let status = row.status

        if (occupied >= capacity && capacity > 0) {
          status = 'full'
        } else if (occupied > 0) {
          status = 'occupied'
        }

        return (
          <Badge variant={getStatusBadgeVariant(status)}>
            {status}
          </Badge>
        )
      },
    },
    {
      key: 'type',
      header: 'Type',
      render: (row: any) => (
        <Badge variant={getTypeBadgeVariant(row.type)}>
          {row.type || 'N/A'}
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
            onClick={() => handleViewDetails(row)}
            title="View Details"
          >
            <Eye className="h-4 w-4" />
          </Button>
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
          Error loading rooms: {error.message}
        </p>
      </div>
    )
  }

  const totalRooms = filteredData.length
  const availableRooms = filteredData.filter((r: any) => {
    const occupied = r.current_occupancy || 0
    const capacity = r.capacity || 0
    return occupied < capacity && r.status !== 'maintenance'
  }).length
  const totalCapacity = filteredData.reduce((sum: number, r: any) => sum + (r.capacity || 0), 0)
  const totalOccupied = filteredData.reduce((sum: number, r: any) => sum + (r.current_occupancy || 0), 0)
  const occupancyPercentage = totalCapacity > 0 ? Math.round((totalOccupied / totalCapacity) * 100) : 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Rooms</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Room
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {totalRooms}
              </p>
              <p className="text-sm text-gray-600">Total Rooms</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {availableRooms}
              </p>
              <p className="text-sm text-gray-600">Available Rooms</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {occupancyPercentage}%
              </p>
              <p className="text-sm text-gray-600">Occupancy Rate</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Rooms</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex gap-4">
            <Input
              placeholder="Search rooms..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              className="flex-1"
            />
            <Select
              value={buildingFilter}
              onChange={(e) => setBuildingFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Buildings' },
                ...buildings.map((b: any) => ({ value: String(b.id), label: b.name })),
              ]}
              className="w-48"
            />
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Status' },
                { value: 'available', label: 'Available' },
                { value: 'occupied', label: 'Occupied' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'reserved', label: 'Reserved' },
              ]}
              className="w-48"
            />
          </div>
          <Table data={paginatedFilteredData} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={Math.ceil(doubleFilteredData.length / pageSize)}
            onPageChange={setCurrentPage}
            totalItems={doubleFilteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Room Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingRoom ? 'Edit Room' : 'New Room'}
        size="lg"
      >
        <RoomForm
          initialData={editingRoom}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          mode={editingRoom ? 'edit' : 'create'}
          buildings={buildings.map((b: any) => ({ id: String(b.id), name: b.name }))}
        />
      </Modal>

      {/* Room Details Modal */}
      <Modal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false)
          setSelectedRoom(null)
        }}
        title="Room Details"
        size="md"
      >
        {selectedRoom && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Room Number</p>
                <p className="font-medium">{selectedRoom.room_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Floor</p>
                <p className="font-medium">{selectedRoom.floor}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Type</p>
                <Badge variant={getTypeBadgeVariant(selectedRoom.type)}>
                  {selectedRoom.type}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge variant={getStatusBadgeVariant(selectedRoom.status)}>
                  {selectedRoom.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Capacity</p>
                <p className="font-medium">{selectedRoom.capacity} beds</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Current Occupancy</p>
                <p className="font-medium">{selectedRoom.current_occupancy} beds</p>
              </div>
            </div>

            {/* Bed Layout Visualization */}
            <div className="border-t pt-4">
              <p className="text-sm text-gray-600 mb-2">Bed Layout</p>
              <div className="grid grid-cols-4 gap-2">
                {Array.from({ length: selectedRoom.capacity }).map((_, index) => (
                  <div
                    key={index}
                    className={`p-4 border-2 rounded flex items-center justify-center ${
                      index < selectedRoom.current_occupancy
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-300 bg-gray-50'
                    }`}
                  >
                    <svg
                      className={`w-8 h-8 ${
                        index < selectedRoom.current_occupancy
                          ? 'text-blue-600'
                          : 'text-gray-400'
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M3 21v-4m0 0V5a2 2 0 012-2h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2zm0 0h18"
                      />
                    </svg>
                  </div>
                ))}
              </div>
              <div className="flex gap-4 mt-3 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-blue-500 bg-blue-50 rounded"></div>
                  <span className="text-gray-600">Occupied</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-gray-300 bg-gray-50 rounded"></div>
                  <span className="text-gray-600">Available</span>
                </div>
              </div>
            </div>

            {selectedRoom.amenities && (
              <div className="border-t pt-4">
                <p className="text-sm text-gray-600 mb-2">Amenities</p>
                <div className="flex flex-wrap gap-2">
                  {selectedRoom.amenities.split(',').map((amenity: string, idx: number) => (
                    <Badge key={idx} variant="secondary">
                      {amenity.trim()}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {selectedRoom.notes && (
              <div className="border-t pt-4">
                <p className="text-sm text-gray-600 mb-1">Notes</p>
                <p className="text-sm">{selectedRoom.notes}</p>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}
