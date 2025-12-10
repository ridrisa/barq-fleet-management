import { useState, useMemo, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus, Search, Eye } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { assignmentsAPI, couriersAPI, vehiclesAPI } from '@/lib/api'
import { useCRUD } from '@/hooks/useCRUD'
import { AssignmentForm, AssignmentFormData } from '@/components/forms/AssignmentForm'

export default function VehicleAssignments() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingAssignment, setEditingAssignment] = useState<any>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 10

  // Fetch current assignments (from couriers.current_vehicle_id)
  const {
    data: allAssignments = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ['current-assignments'],
    queryFn: () => assignmentsAPI.getCurrentAssignments(),
  })

  // Fetch couriers for the assignment form dropdown
  const { data: couriersData = [] } = useQuery({
    queryKey: ['couriers-for-assignment'],
    queryFn: () => couriersAPI.getAll(0, 1000),
  })

  // Fetch vehicles for the assignment form dropdown
  const { data: vehiclesData = [] } = useQuery({
    queryKey: ['vehicles-for-assignment'],
    queryFn: () => vehiclesAPI.getAll(),
  })

  // Apply search filter
  const filteredData = useMemo(() => {
    if (!searchTerm) return allAssignments
    const lowerSearchTerm = searchTerm.toLowerCase()
    return allAssignments.filter((item: any) =>
      Object.values(item).some((value) =>
        String(value).toLowerCase().includes(lowerSearchTerm)
      )
    )
  }, [allAssignments, searchTerm])

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm])

  // Paginate filtered data
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize
    const end = start + pageSize
    return filteredData.slice(start, end)
  }, [filteredData, currentPage, pageSize])

  const totalPages = Math.ceil(filteredData.length / pageSize)

  const { handleCreate, isLoading: isMutating } = useCRUD({
    queryKey: 'current-assignments',
    entityName: 'Assignment',
    create: assignmentsAPI.create,
    update: assignmentsAPI.update,
    delete: assignmentsAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingAssignment(null)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingAssignment(null)
  }

  const handleFormSubmit = async (data: AssignmentFormData) => {
    const result = await handleCreate(data)
    if (result) {
      handleCloseModal()
    }
  }

  const columns = [
    {
      key: 'courier_name',
      header: 'Courier',
      sortable: true,
      render: (row: any) => (
        <div>
          <span className="font-medium">{row.courier_name}</span>
          {row.courier_employee_id && (
            <span className="text-xs text-gray-500 ml-2">({row.courier_employee_id})</span>
          )}
        </div>
      ),
    },
    {
      key: 'courier_status',
      header: 'Courier Status',
      render: (row: any) => {
        const status = row.courier_status?.toUpperCase?.() || ''
        return (
          <Badge
            variant={
              status === 'ACTIVE' ? 'success' :
              status === 'INACTIVE' ? 'default' :
              status === 'ON_LEAVE' ? 'warning' : 'danger'
            }
          >
            {status}
          </Badge>
        )
      },
    },
    {
      key: 'vehicle_plate_number',
      header: 'Vehicle',
      sortable: true,
      render: (row: any) => (
        <div>
          <span className="font-medium">{row.vehicle_plate_number}</span>
          <span className="text-xs text-gray-500 block">
            {row.vehicle_make} {row.vehicle_model}
          </span>
        </div>
      ),
    },
    {
      key: 'vehicle_status',
      header: 'Vehicle Status',
      render: (row: any) => {
        const status = row.vehicle_status?.toUpperCase?.() || ''
        return (
          <Badge
            variant={
              status === 'ACTIVE' ? 'success' :
              status === 'INACTIVE' ? 'default' :
              status === 'MAINTENANCE' || status === 'REPAIR' ? 'warning' : 'danger'
            }
          >
            {status}
          </Badge>
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
            onClick={() => navigate(`/fleet/couriers/${row.courier_id}`)}
            title="View Courier"
          >
            <Eye className="h-4 w-4 text-blue-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => navigate(`/fleet/vehicles/${row.vehicle_id}`)}
            title="View Vehicle"
          >
            <Eye className="h-4 w-4 text-green-600" />
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
        <p className="text-red-800">Error loading assignments: {(error as Error).message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t('nav.assignments')}</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          New Assignment
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {allAssignments.length}
              </p>
              <p className="text-sm text-gray-600">Total Assignments</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {allAssignments.filter((a: any) => a.courier_status?.toUpperCase() === 'ACTIVE').length}
              </p>
              <p className="text-sm text-gray-600">Active Couriers</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {allAssignments.filter((a: any) => a.vehicle_status?.toUpperCase() === 'ACTIVE').length}
              </p>
              <p className="text-sm text-gray-600">Active Vehicles</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Current Vehicle-Courier Assignments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search by courier name, employee ID, or vehicle plate..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={paginatedData} columns={columns} />
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
        title="Add New Assignment"
        size="lg"
      >
        <AssignmentForm
          initialData={editingAssignment}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode="create"
          couriers={Array.isArray(couriersData) ? couriersData.map((c: any) => ({ id: String(c.id), name: c.full_name || c.name || 'Unknown' })) : []}
          vehicles={Array.isArray(vehiclesData) ? vehiclesData.map((v: any) => ({ id: String(v.id), plate_number: v.plate_number || 'No plate' })) : []}
        />
      </Modal>
    </div>
  )
}