import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, MapPin, Users, Filter, Download } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { zonesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

export default function ZoneManagement() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingZone, setEditingZone] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    filteredData,
  } = useDataTable({
    queryKey: 'zones',
    queryFn: zonesAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'zones',
    entityName: 'Zone',
    create: zonesAPI.create,
    update: zonesAPI.update,
    delete: zonesAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingZone(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (zone: any) => {
    setEditingZone(zone)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingZone(null)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const data = {
      zone_name: formData.get('zone_name'),
      zone_code: formData.get('zone_code'),
      areas: (formData.get('areas') as string)?.split(',').map((a) => a.trim()) || [],
      assigned_couriers: parseInt(formData.get('assigned_couriers') as string) || 0,
      coverage_radius: parseFloat(formData.get('coverage_radius') as string) || 0,
      max_capacity: parseInt(formData.get('max_capacity') as string) || 100,
      status: formData.get('status') || 'active',
    }

    if (editingZone) {
      await handleUpdate(editingZone.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  const handleExportToExcel = () => {
    alert('Exporting zones to Excel...')
  }

  // Apply filters
  let displayData = filteredData
  if (statusFilter !== 'all') {
    displayData = displayData.filter((z: any) => z.status === statusFilter)
  }

  // Summary stats
  const stats = {
    totalZones: filteredData.length,
    activeZones: filteredData.filter((z: any) => z.status === 'active').length,
    totalCoverage: filteredData.reduce((sum: number, z: any) => sum + (z.coverage_radius || 0), 0),
    totalCouriers: filteredData.reduce((sum: number, z: any) => sum + (z.assigned_couriers || 0), 0),
  }

  const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      active: 'success',
      inactive: 'default',
      full: 'danger',
    }
    return variants[status] || 'default'
  }

  const getCapacityStatus = (zone: any) => {
    const current = zone.current_deliveries || 0
    const max = zone.max_capacity || 100
    const percentage = (current / max) * 100

    if (percentage >= 100) return { status: 'full', color: 'text-red-600' }
    if (percentage >= 80) return { status: 'high', color: 'text-orange-600' }
    if (percentage >= 50) return { status: 'medium', color: 'text-yellow-600' }
    return { status: 'low', color: 'text-green-600' }
  }

  const columns = [
    {
      key: 'zone_name',
      header: 'Zone Name',
      sortable: true,
      render: (row: any) => (
        <div className="font-semibold text-gray-900">
          {row.zone_name || `Zone #${row.id}`}
        </div>
      ),
    },
    {
      key: 'zone_code',
      header: 'Code',
      render: (row: any) => (
        <div className="font-mono text-sm text-blue-600">
          {row.zone_code || `ZN-${row.id?.toString().padStart(3, '0')}`}
        </div>
      ),
    },
    {
      key: 'areas',
      header: 'Areas',
      render: (row: any) => {
        const areas = row.areas || []
        return (
          <div className="text-sm">
            {areas.length > 0 ? (
              <span>{areas.slice(0, 2).join(', ')}{areas.length > 2 ? ` +${areas.length - 2}` : ''}</span>
            ) : (
              <span className="text-gray-400">No areas</span>
            )}
          </div>
        )
      },
    },
    {
      key: 'coverage_radius',
      header: 'Coverage',
      render: (row: any) => (
        <div className="flex items-center gap-1">
          <MapPin className="h-4 w-4 text-gray-400" />
          <span>{row.coverage_radius || 0} km</span>
        </div>
      ),
    },
    {
      key: 'assigned_couriers',
      header: 'Assigned Couriers',
      render: (row: any) => (
        <div className="flex items-center gap-1">
          <Users className="h-4 w-4 text-gray-400" />
          <span>{row.assigned_couriers || 0}</span>
        </div>
      ),
    },
    {
      key: 'capacity',
      header: 'Capacity',
      render: (row: any) => {
        const current = row.current_deliveries || 0
        const max = row.max_capacity || 100
        const capacityInfo = getCapacityStatus(row)
        return (
          <div className={`text-sm font-semibold ${capacityInfo.color}`}>
            {current} / {max}
          </div>
        )
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={getStatusVariant(row.status || 'active')}>
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
            onClick={() => handleOpenEditModal(row)}
            title="Edit zone"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete zone"
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
        <p className="text-red-800">Error loading zones: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Zone Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExportToExcel}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleOpenCreateModal}>
            <Plus className="h-4 w-4 mr-2" />
            Add Zone
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Zones</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalZones}</p>
              </div>
              <MapPin className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Zones</p>
                <p className="text-2xl font-bold text-green-600">{stats.activeZones}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-green-600 text-xl">✓</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Coverage Area</p>
                <p className="text-2xl font-bold text-purple-600">{stats.totalCoverage.toFixed(1)} km</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <span className="text-purple-600 text-sm font-bold">Σ</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Assigned Couriers</p>
                <p className="text-2xl font-bold text-blue-600">{stats.totalCouriers}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Zones Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Zones</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search zones by name, code, areas..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Status' },
                    { value: 'active', label: 'Active' },
                    { value: 'inactive', label: 'Inactive' },
                    { value: 'full', label: 'Full' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
            </div>

            <Table
              data={displayData.slice((currentPage - 1) * pageSize, currentPage * pageSize)}
              columns={columns}
            />

            <Pagination
              currentPage={currentPage}
              totalPages={Math.ceil(displayData.length / pageSize)}
              onPageChange={setCurrentPage}
              totalItems={displayData.length}
              pageSize={pageSize}
            />
          </div>
        </CardContent>
      </Card>

      {/* Zone Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingZone ? 'Edit Zone' : 'Add New Zone'}
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Zone Name *
              </label>
              <Input
                name="zone_name"
                defaultValue={editingZone?.zone_name || ''}
                required
                placeholder="e.g., North Zone"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Zone Code *
              </label>
              <Input
                name="zone_code"
                defaultValue={editingZone?.zone_code || ''}
                required
                placeholder="e.g., NZ-001"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Areas (comma-separated)
            </label>
            <Input
              name="areas"
              defaultValue={editingZone?.areas?.join(', ') || ''}
              placeholder="e.g., Downtown, Uptown, Midtown"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Coverage Radius (km)
              </label>
              <Input
                name="coverage_radius"
                type="number"
                step="0.1"
                defaultValue={editingZone?.coverage_radius || ''}
                placeholder="e.g., 15.5"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Assigned Couriers
              </label>
              <Input
                name="assigned_couriers"
                type="number"
                defaultValue={editingZone?.assigned_couriers || 0}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Capacity
              </label>
              <Input
                name="max_capacity"
                type="number"
                defaultValue={editingZone?.max_capacity || 100}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <Select
              name="status"
              value={editingZone?.status || 'active'}
              options={[
                { value: 'active', label: 'Active' },
                { value: 'inactive', label: 'Inactive' },
                { value: 'full', label: 'Full' },
              ]}
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button type="submit" disabled={isMutating}>
              {isMutating ? 'Saving...' : editingZone ? 'Update Zone' : 'Create Zone'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
