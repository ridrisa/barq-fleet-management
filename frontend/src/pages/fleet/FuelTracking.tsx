import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { fuelTrackingAPI, vehiclesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { FuelLogForm, FuelLogFormData } from '@/components/forms/FuelLogForm'

export default function FuelTracking() {
  const { t: _t } = useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingFuelLog, setEditingFuelLog] = useState<any>(null)
  const [vehicles, setVehicles] = useState<Array<{ id: number; plate_number: string }>>([])
  const [summary, setSummary] = useState({
    totalFuel: 0,
    totalCost: 0,
    averageEfficiency: 0,
  })

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

  // Load fuel summary
  useEffect(() => {
    const loadSummary = async () => {
      try {
        const data = await fuelTrackingAPI.getSummary()
        setSummary(data)
      } catch (error) {
        console.error('Failed to load fuel summary:', error)
      }
    }
    loadSummary()
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
    paginatedData: fuelLogs,
    filteredData,
  } = useDataTable({
    queryKey: 'fuelLogs',
    queryFn: fuelTrackingAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook with toast notifications
  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'fuelLogs',
    entityName: 'Fuel Log',
    create: fuelTrackingAPI.create,
    update: fuelTrackingAPI.update,
    delete: fuelTrackingAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingFuelLog(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (fuelLog: any) => {
    setEditingFuelLog(fuelLog)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingFuelLog(null)
  }

  const handleFormSubmit = async (data: FuelLogFormData) => {
    if (editingFuelLog) {
      const result = await handleUpdate(editingFuelLog.id, data)
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

  const columns = [
    {
      key: 'date',
      header: 'Date',
      sortable: true,
      render: (row: any) => {
        if (!row.date) return 'N/A'
        return new Date(row.date).toLocaleDateString()
      },
    },
    {
      key: 'vehicle_id',
      header: 'Vehicle',
      render: (row: any) => getVehiclePlate(row.vehicle_id),
    },
    {
      key: 'fuel_type',
      header: 'Fuel Type',
      render: (row: any) => (
        <Badge variant="default">
          {row.fuel_type?.toUpperCase() || 'N/A'}
        </Badge>
      ),
    },
    {
      key: 'liters',
      header: 'Liters',
      render: (row: any) => `${row.liters?.toFixed(2) || 0} L`,
    },
    {
      key: 'cost',
      header: 'Cost',
      render: (row: any) => `SAR ${row.cost?.toFixed(2) || 0}`,
    },
    {
      key: 'odometer',
      header: 'Odometer',
      render: (row: any) => `${row.odometer?.toLocaleString() || 0} km`,
    },
    {
      key: 'station',
      header: 'Station',
      render: (row: any) => row.station || 'N/A',
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
        <p className="text-red-800">Error loading fuel logs: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Fuel Tracking</h1>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleOpenCreateModal}>
            <Plus className="h-4 w-4 mr-2" />
            Add Fuel Record
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {summary.totalFuel?.toLocaleString() || 0} L
              </p>
              <p className="text-sm text-gray-600">Total Fuel This Month</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                SAR {summary.totalCost?.toLocaleString() || 0}
              </p>
              <p className="text-sm text-gray-600">Total Cost This Month</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {summary.averageEfficiency?.toFixed(1) || 0} km/L
              </p>
              <p className="text-sm text-gray-600">Average Efficiency</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fuel Records Table */}
      <Card>
        <CardHeader>
          <CardTitle>Fuel Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search fuel records..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={fuelLogs} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Fuel Log Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingFuelLog ? 'Edit Fuel Log' : 'Add Fuel Record'}
        size="lg"
      >
        <FuelLogForm
          initialData={editingFuelLog}
          onSubmit={handleFormSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingFuelLog ? 'edit' : 'create'}
          vehicles={vehicles}
        />
      </Modal>
    </div>
  )
}
