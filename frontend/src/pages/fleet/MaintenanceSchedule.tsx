import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, AlertCircle, Calendar } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { maintenanceAPI, vehiclesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { MaintenanceForm, MaintenanceFormData } from '@/components/forms/MaintenanceForm'

export default function MaintenanceSchedule() {
  const { t: _t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingMaintenance, setEditingMaintenance] = useState<any>(null)
  const [vehicles, setVehicles] = useState<Array<{ id: number; plate_number: string }>>([])
  const [upcomingMaintenance, setUpcomingMaintenance] = useState<any[]>([])

  // Load vehicles for the form
  useEffect(() => {
    const loadVehicles = async () => {
      try {
        const data = await vehiclesAPI.getAll()
        setVehicles(data)
      } catch (error) {
        console.error('Failed to load vehicles:', error)
      }
    }
    loadVehicles()
  }, [])

  // Load upcoming maintenance
  useEffect(() => {
    const loadUpcoming = async () => {
      try {
        const data = await maintenanceAPI.getUpcoming(30)
        setUpcomingMaintenance(data)
      } catch (error) {
        console.error('Failed to load upcoming maintenance:', error)
      }
    }
    loadUpcoming()
  }, [])

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
    paginatedData: maintenanceRecords,
    filteredData,
  } = useDataTable({
    queryKey: 'maintenance',
    queryFn: maintenanceAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook with toast notifications
  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'maintenance',
    entityName: 'Maintenance',
    create: maintenanceAPI.create,
    update: maintenanceAPI.update,
    delete: maintenanceAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingMaintenance(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (maintenance: any) => {
    setEditingMaintenance(maintenance)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingMaintenance(null)
  }

  const handleFormSubmit = async (data: MaintenanceFormData) => {
    if (editingMaintenance) {
      const result = await handleUpdate(editingMaintenance.id, data)
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

  const getVehiclePlate = (vehicleId: number) => {
    const vehicle = vehicles.find((v) => v.id === vehicleId)
    return vehicle?.plate_number || `Vehicle ${vehicleId}`
  }

  const isOverdue = (scheduledDate: string, status: string) => {
    if (status === 'completed' || status === 'cancelled') return false
    const today = new Date()
    const scheduled = new Date(scheduledDate)
    return scheduled < today
  }

  const columns = [
    {
      key: 'vehicle_id',
      header: 'Vehicle',
      sortable: true,
      render: (row: any) => getVehiclePlate(row.vehicle_id),
    },
    {
      key: 'maintenance_type',
      header: 'Type',
      render: (row: any) => {
        const typeLabels: Record<string, string> = {
          oil_change: 'Oil Change',
          tire_replacement: 'Tire Replacement',
          brake_service: 'Brake Service',
          battery_replacement: 'Battery Replacement',
          inspection: 'Inspection',
          general_repair: 'General Repair',
          ac_service: 'AC Service',
          transmission: 'Transmission',
          other: 'Other',
        }
        return typeLabels[row.maintenance_type] || row.maintenance_type
      },
    },
    {
      key: 'scheduled_date',
      header: 'Scheduled Date',
      sortable: true,
      render: (row: any) => {
        if (!row.scheduled_date) return 'N/A'
        const date = new Date(row.scheduled_date).toLocaleDateString()
        const overdue = isOverdue(row.scheduled_date, row.status)
        return (
          <div className="flex items-center gap-2">
            {date}
            {overdue && <AlertCircle className="h-4 w-4 text-red-600" />}
          </div>
        )
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => {
        const overdue = isOverdue(row.scheduled_date, row.status)
        const variant =
          row.status === 'completed'
            ? 'success'
            : row.status === 'in_progress'
            ? 'warning'
            : row.status === 'cancelled'
            ? 'danger'
            : overdue
            ? 'danger'
            : 'default'

        return (
          <Badge variant={variant}>
            {overdue && row.status === 'scheduled' ? 'OVERDUE' : row.status?.toUpperCase() || 'SCHEDULED'}
          </Badge>
        )
      },
    },
    {
      key: 'cost',
      header: 'Cost',
      render: (row: any) => row.cost ? `SAR ${row.cost.toFixed(2)}` : 'N/A',
    },
    {
      key: 'service_provider',
      header: 'Service Provider',
      render: (row: any) => row.service_provider || 'N/A',
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
        <p className="text-red-800">Error loading maintenance records: {error.message}</p>
      </div>
    )
  }

  const scheduledCount = maintenanceRecords.filter((m: any) => m.status === 'scheduled').length
  const inProgressCount = maintenanceRecords.filter((m: any) => m.status === 'in_progress').length
  const completedCount = maintenanceRecords.filter((m: any) => m.status === 'completed').length
  const overdueCount = maintenanceRecords.filter((m: any) => isOverdue(m.scheduled_date, m.status)).length

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Maintenance Schedule</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Schedule Maintenance
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {scheduledCount}
              </p>
              <p className="text-sm text-gray-600">Scheduled</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {inProgressCount}
              </p>
              <p className="text-sm text-gray-600">In Progress</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {completedCount}
              </p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {overdueCount}
              </p>
              <p className="text-sm text-gray-600">Overdue</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Maintenance Alert */}
      {upcomingMaintenance.length > 0 && (
        <Card className="border-yellow-300 bg-yellow-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-800">
              <Calendar className="h-5 w-5" />
              Upcoming Maintenance (Next 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {upcomingMaintenance.slice(0, 5).map((m: any) => (
                <div key={m.id} className="flex justify-between items-center text-sm">
                  <span className="font-medium">{getVehiclePlate(m.vehicle_id)}</span>
                  <span className="text-gray-600">{m.maintenance_type}</span>
                  <span className="text-gray-600">
                    {new Date(m.scheduled_date).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Maintenance Records Table */}
      <Card>
        <CardHeader>
          <CardTitle>Maintenance Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search maintenance records..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={maintenanceRecords} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Maintenance Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingMaintenance ? 'Edit Maintenance' : 'Schedule Maintenance'}
        size="lg"
      >
        <MaintenanceForm
          initialData={editingMaintenance}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingMaintenance ? 'edit' : 'create'}
          vehicles={vehicles}
        />
      </Modal>
    </div>
  )
}
