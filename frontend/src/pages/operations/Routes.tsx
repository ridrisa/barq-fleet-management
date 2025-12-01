import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, Navigation, MapPin, Clock, Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { KPICard } from '@/components/ui/KPICard'
import { routesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { RouteForm } from '@/components/forms/RouteForm'
import { Select } from '@/components/ui/Select'
import { Download, Filter, Map } from 'lucide-react'

export default function Routes() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRoute, setEditingRoute] = useState<any>(null)
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
    queryKey: 'routes',
    queryFn: routesAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'routes',
    entityName: 'Route',
    create: routesAPI.create,
    update: routesAPI.update,
    delete: routesAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingRoute(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (route: any) => {
    setEditingRoute(route)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingRoute(null)
  }

  const handleExportToExcel = () => {
    alert('Exporting routes to Excel...')
  }

  const columns = [
    {
      key: 'name',
      header: 'Route Name',
      sortable: true,
      render: (row: any) => (
        <div className="font-semibold text-gray-900">
          {row.name || `Route #${row.id}`}
        </div>
      ),
    },
    {
      key: 'code',
      header: 'Route Code',
      render: (row: any) => (
        <div className="font-mono text-sm text-blue-600">
          {row.code || row.route_code || `RT-${row.id?.toString().padStart(4, '0')}`}
        </div>
      ),
    },
    {
      key: 'description',
      header: 'Description',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.description || '-'}
        </div>
      ),
    },
    {
      key: 'distance',
      header: 'Distance',
      render: (row: any) => {
        const distance = row.distance || row.total_distance || 0
        return <span className="text-sm">{distance.toFixed(1)} km</span>
      },
    },
    {
      key: 'estimated_time',
      header: 'Est. Time',
      render: (row: any) => {
        const minutes = row.estimated_time || row.duration_minutes || 0
        const hours = Math.floor(minutes / 60)
        const mins = minutes % 60
        return (
          <span className="text-sm">
            {hours > 0 ? `${hours}h ` : ''}{mins}m
          </span>
        )
      },
    },
    {
      key: 'stops',
      header: 'Stops',
      render: (row: any) => {
        const count = row.waypoints?.length || row.stops_count || 0
        return (
          <div className="flex items-center gap-1">
            <MapPin className="h-4 w-4 text-gray-400" />
            <span>{count}</span>
          </div>
        )
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={row.status === 'active' ? 'success' : 'default'}>
          {row.status || 'draft'}
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
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOptimizeRoute(row.id)}
            title="Optimize route"
          >
            <Zap className="h-4 w-4 text-yellow-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => alert('View route on map')}
            title="View on map"
          >
            <Map className="h-4 w-4 text-green-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete route"
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
        <p className="text-red-800">Error loading routes: {error.message}</p>
      </div>
    )
  }

  // Apply filters
  let displayData = filteredData
  if (statusFilter !== 'all') {
    displayData = displayData.filter((r: any) => r.status === statusFilter)
  }

  // Calculate stats
  const stats = {
    total: filteredData.length,
    active: filteredData.filter((r: any) => r.status === 'active').length,
    completed: filteredData.filter((r: any) => r.status === 'completed').length,
    totalDistance: filteredData.reduce((sum: number, r: any) => sum + (r.distance || r.total_distance || 0), 0),
    avgDistance: filteredData.length > 0 ? filteredData.reduce((sum: number, r: any) => sum + (r.distance || r.total_distance || 0), 0) / filteredData.length : 0,
    avgTime: filteredData.length > 0 ? filteredData.reduce((sum: number, r: any) => sum + (r.estimated_time || r.duration_minutes || 0), 0) / filteredData.length : 0,
  }

  const handleOptimizeRoute = (routeId: number) => {
    alert(`Optimizing route ${routeId}... This feature will use AI-based route optimization.`)
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Route Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => alert('Map view coming soon!')}>
            <Map className="h-4 w-4 mr-2" />
            Map View
          </Button>
          <Button variant="outline" onClick={handleExportToExcel}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleOpenCreateModal}>
            <Plus className="h-4 w-4 mr-2" />
            Add Route
          </Button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KPICard
          title="Total Routes"
          value={stats.total}
          icon={<MapPin className="h-6 w-6" />}
          color="blue"
          loading={isLoading}
        />
        <KPICard
          title="Active Routes"
          value={stats.active}
          icon={<Navigation className="h-6 w-6" />}
          color="green"
          loading={isLoading}
        />
        <KPICard
          title="Avg Distance"
          value={`${stats.avgDistance.toFixed(1)} km`}
          icon={<MapPin className="h-6 w-6" />}
          color="purple"
          loading={isLoading}
        />
        <KPICard
          title="Avg Time"
          value={`${Math.floor(stats.avgTime)}m`}
          icon={<Clock className="h-6 w-6" />}
          color="indigo"
          loading={isLoading}
        />
        <KPICard
          title="Completed Today"
          value={stats.completed}
          icon={<Navigation className="h-6 w-6" />}
          color="yellow"
          loading={isLoading}
        />
      </div>

      {/* Routes Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Routes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search routes by name, code, courier..."
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
                    { value: 'under_review', label: 'Under Review' },
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

      {/* Route Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingRoute ? 'Edit Route' : 'Add New Route'}
        size="lg"
      >
        <RouteForm
          initialData={editingRoute}
          onSubmit={async (data) => {
            if (editingRoute) {
              await handleUpdate(editingRoute.id, data)
            } else {
              await handleCreate(data)
            }
            handleCloseModal()
          }}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingRoute ? 'edit' : 'create'}
          couriers={[]}
        />
      </Modal>
    </div>
  )
}
