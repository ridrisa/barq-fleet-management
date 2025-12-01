import { useState } from 'react'
import { Plus, Search, Edit, Trash2, UserPlus, UserMinus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

// Mock beds API
const bedsAPI = {
  getAll: async () => {
    // Mock data with comprehensive bed information
    return [
      {
        id: 1,
        bed_id: 'B-DT-101-01',
        room_id: 101,
        room_number: '101',
        building_id: 1,
        building_name: 'Downtown Residence',
        bed_number: 1,
        status: 'occupied',
        assigned_to: 'John Doe',
        assigned_to_id: 'C-12345',
        assignment_date: '2024-10-15',
        created_at: '2024-01-15',
      },
      {
        id: 2,
        bed_id: 'B-DT-101-02',
        room_id: 101,
        room_number: '101',
        building_id: 1,
        building_name: 'Downtown Residence',
        bed_number: 2,
        status: 'occupied',
        assigned_to: 'Jane Smith',
        assigned_to_id: 'C-12346',
        assignment_date: '2024-10-15',
        created_at: '2024-01-15',
      },
      {
        id: 3,
        bed_id: 'B-DT-102-01',
        room_id: 102,
        room_number: '102',
        building_id: 1,
        building_name: 'Downtown Residence',
        bed_number: 1,
        status: 'available',
        assigned_to: null,
        assigned_to_id: null,
        assignment_date: null,
        created_at: '2024-01-15',
      },
      {
        id: 4,
        bed_id: 'B-DT-102-02',
        room_id: 102,
        room_number: '102',
        building_id: 1,
        building_name: 'Downtown Residence',
        bed_number: 2,
        status: 'occupied',
        assigned_to: 'Ahmed Ali',
        assigned_to_id: 'C-12347',
        assignment_date: '2024-11-01',
        created_at: '2024-01-15',
      },
      {
        id: 5,
        bed_id: 'B-DT-103-01',
        room_id: 103,
        room_number: '103',
        building_id: 1,
        building_name: 'Downtown Residence',
        bed_number: 1,
        status: 'maintenance',
        assigned_to: null,
        assigned_to_id: null,
        assignment_date: null,
        created_at: '2024-01-15',
      },
      {
        id: 6,
        bed_id: 'B-MT-301-01',
        room_id: 301,
        room_number: '301',
        building_id: 2,
        building_name: 'Marina Tower',
        bed_number: 1,
        status: 'reserved',
        assigned_to: 'Sara Mohammed',
        assigned_to_id: 'C-12348',
        assignment_date: '2024-11-10',
        created_at: '2024-02-20',
      },
      {
        id: 7,
        bed_id: 'B-MT-302-01',
        room_id: 302,
        room_number: '302',
        building_id: 2,
        building_name: 'Marina Tower',
        bed_number: 1,
        status: 'available',
        assigned_to: null,
        assigned_to_id: null,
        assignment_date: null,
        created_at: '2024-02-20',
      },
      {
        id: 8,
        bed_id: 'B-MT-302-02',
        room_id: 302,
        room_number: '302',
        building_id: 2,
        building_name: 'Marina Tower',
        bed_number: 2,
        status: 'available',
        assigned_to: null,
        assigned_to_id: null,
        assignment_date: null,
        created_at: '2024-02-20',
      },
    ]
  },
  create: async (data: any) => {
    console.log('Creating bed:', data)
    return { id: Date.now(), ...data }
  },
  update: async (id: number, data: any) => {
    console.log('Updating bed:', id, data)
    return { id, ...data }
  },
  delete: async (id: number) => {
    console.log('Deleting bed:', id)
  },
}

interface BedFormData {
  bed_id: string
  room_id: number
  building_id: number
  bed_number: number
  status: string
}

export default function Beds() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false)
  const [editingBed, setEditingBed] = useState<any>(null)
  const [selectedBed, setSelectedBed] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [buildingFilter, setBuildingFilter] = useState<string>('all')
  const [roomFilter, setRoomFilter] = useState<string>('')

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
    paginatedData: _paginatedData,
    filteredData,
  } = useDataTable({
    queryKey: 'beds',
    queryFn: bedsAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleDelete, handleCreate, handleUpdate } = useCRUD({
    queryKey: 'beds',
    entityName: 'Bed',
    create: bedsAPI.create,
    update: bedsAPI.update,
    delete: bedsAPI.delete,
  })

  // Apply filters
  const multiFilteredData = filteredData.filter((bed: any) => {
    const matchesStatus = statusFilter === 'all' || bed.status === statusFilter
    const matchesBuilding = buildingFilter === 'all' || bed.building_id.toString() === buildingFilter
    const matchesRoom = !roomFilter || bed.room_number.includes(roomFilter)
    return matchesStatus && matchesBuilding && matchesRoom
  })

  const paginatedFilteredData = multiFilteredData.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data: BedFormData = {
      bed_id: formData.get('bed_id') as string,
      room_id: parseInt(formData.get('room_id') as string),
      building_id: parseInt(formData.get('building_id') as string),
      bed_number: parseInt(formData.get('bed_number') as string),
      status: formData.get('status') as string,
    }

    if (editingBed) {
      await handleUpdate(editingBed.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  const handleAssignSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const courierData = {
      assigned_to: formData.get('assigned_to') as string,
      assigned_to_id: formData.get('assigned_to_id') as string,
      assignment_date: formData.get('assignment_date') as string,
      status: 'occupied',
    }

    if (selectedBed) {
      await handleUpdate(selectedBed.id, courierData)
    }
    handleCloseAssignModal()
  }

  const handleUnassign = async (bed: any) => {
    if (window.confirm(`Are you sure you want to unassign ${bed.assigned_to} from this bed?`)) {
      await handleUpdate(bed.id, {
        assigned_to: null,
        assigned_to_id: null,
        assignment_date: null,
        status: 'available',
      })
    }
  }

  const handleEdit = (bed: any) => {
    setEditingBed(bed)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingBed(null)
  }

  const handleAssign = (bed: any) => {
    setSelectedBed(bed)
    setIsAssignModalOpen(true)
  }

  const handleCloseAssignModal = () => {
    setIsAssignModalOpen(false)
    setSelectedBed(null)
  }

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'available':
        return 'success'
      case 'occupied':
        return 'primary'
      case 'maintenance':
        return 'warning'
      case 'reserved':
        return 'info'
      default:
        return 'default'
    }
  }

  const columns = [
    {
      key: 'bed_id',
      header: 'Bed ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm">{row.bed_id}</div>
      ),
    },
    {
      key: 'location',
      header: 'Location',
      render: (row: any) => (
        <div>
          <div className="font-medium">{row.building_name}</div>
          <div className="text-sm text-gray-500">
            Room {row.room_number} - Bed {row.bed_number}
          </div>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (row: any) => (
        <Badge variant={getStatusBadgeVariant(row.status)}>
          {row.status}
        </Badge>
      ),
    },
    {
      key: 'assigned_to',
      header: 'Assigned To',
      render: (row: any) => row.assigned_to ? (
        <div>
          <div className="font-medium">{row.assigned_to}</div>
          <div className="text-sm text-gray-500">{row.assigned_to_id}</div>
        </div>
      ) : (
        <span className="text-gray-400">Unassigned</span>
      ),
    },
    {
      key: 'assignment_date',
      header: 'Assignment Date',
      sortable: true,
      render: (row: any) => row.assignment_date ? (
        new Date(row.assignment_date).toLocaleDateString()
      ) : (
        <span className="text-gray-400">-</span>
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
          {row.status === 'available' || row.status === 'reserved' ? (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleAssign(row)}
              title="Assign"
              className="text-green-600"
            >
              <UserPlus className="h-4 w-4" />
            </Button>
          ) : row.status === 'occupied' ? (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleUnassign(row)}
              title="Unassign"
              className="text-orange-600"
            >
              <UserMinus className="h-4 w-4" />
            </Button>
          ) : null}
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
          Error loading beds: {error.message}
        </p>
      </div>
    )
  }

  // Calculate summary statistics
  const totalBeds = multiFilteredData.length
  const occupiedBeds = multiFilteredData.filter((b: any) => b.status === 'occupied').length
  const availableBeds = multiFilteredData.filter((b: any) => b.status === 'available').length
  const maintenanceBeds = multiFilteredData.filter((b: any) => b.status === 'maintenance').length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Bed Management</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Bed
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{totalBeds}</p>
              <p className="text-sm text-gray-600">Total Beds</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{occupiedBeds}</p>
              <p className="text-sm text-gray-600">Occupied</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{availableBeds}</p>
              <p className="text-sm text-gray-600">Available</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{maintenanceBeds}</p>
              <p className="text-sm text-gray-600">Maintenance</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Beds</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex flex-wrap gap-4">
            <Input
              placeholder="Search beds..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
              className="flex-1 min-w-[200px]"
            />
            <Select
              value={buildingFilter}
              onChange={(e) => setBuildingFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Buildings' },
                { value: '1', label: 'Downtown Residence' },
                { value: '2', label: 'Marina Tower' },
              ]}
              className="w-48"
            />
            <Input
              placeholder="Room number..."
              value={roomFilter}
              onChange={(e) => setRoomFilter(e.target.value)}
              className="w-40"
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
              className="w-40"
            />
          </div>
          <Table data={paginatedFilteredData} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={multiFilteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Bed Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingBed ? 'Edit Bed' : 'New Bed'}
        size="lg"
      >
        <form onSubmit={handleFormSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Bed ID</label>
            <Input
              name="bed_id"
              required
              defaultValue={editingBed?.bed_id || ''}
              placeholder="B-DT-101-01"
            />
            <p className="text-xs text-gray-500 mt-1">
              Format: B-[BuildingCode]-[RoomNumber]-[BedNumber]
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Building</label>
              <Select
                name="building_id"
                required
                defaultValue={editingBed?.building_id || ''}
                options={[
                  { value: '', label: 'Select Building' },
                  { value: '1', label: 'Downtown Residence' },
                  { value: '2', label: 'Marina Tower' },
                ]}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Room ID</label>
              <Input
                name="room_id"
                type="number"
                required
                defaultValue={editingBed?.room_id || ''}
                placeholder="101"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Bed Number</label>
              <Input
                name="bed_number"
                type="number"
                required
                defaultValue={editingBed?.bed_number || 1}
                placeholder="1"
                min="1"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <Select
                name="status"
                required
                defaultValue={editingBed?.status || 'available'}
                options={[
                  { value: 'available', label: 'Available' },
                  { value: 'occupied', label: 'Occupied' },
                  { value: 'maintenance', label: 'Maintenance' },
                  { value: 'reserved', label: 'Reserved' },
                ]}
              />
            </div>
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              {editingBed ? 'Update Bed' : 'Create Bed'}
            </Button>
            <Button type="button" variant="outline" onClick={handleCloseModal}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>

      {/* Assignment Modal */}
      <Modal
        isOpen={isAssignModalOpen}
        onClose={handleCloseAssignModal}
        title="Assign Bed to Courier"
        size="md"
      >
        <form onSubmit={handleAssignSubmit} className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <div className="text-sm">
              <div className="font-medium text-blue-900">Bed: {selectedBed?.bed_id}</div>
              <div className="text-blue-700">
                {selectedBed?.building_name} - Room {selectedBed?.room_number}
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Courier Name</label>
            <Input
              name="assigned_to"
              required
              placeholder="Enter courier name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Courier ID</label>
            <Input
              name="assigned_to_id"
              required
              placeholder="C-12345"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Assignment Date</label>
            <input
              type="date"
              name="assignment_date"
              required
              defaultValue={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex gap-2 pt-4">
            <Button type="submit" className="flex-1">
              Assign Bed
            </Button>
            <Button type="button" variant="outline" onClick={handleCloseAssignModal}>
              Cancel
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
