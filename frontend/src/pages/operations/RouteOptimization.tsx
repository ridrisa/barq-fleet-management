import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, Navigation, Download, MapPin, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { routesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

export default function RouteOptimization() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRoute, setEditingRoute] = useState<any>(null)

  const {
    isLoading,
    error,
    currentPage,
    pageSize,
    totalPages,
    searchTerm,
    setSearchTerm,
    setCurrentPage,
    paginatedData: routes,
    filteredData,
  } = useDataTable({
    queryKey: 'routes-optimization',
    queryFn: routesAPI.getAll,
    pageSize: 10,
  })

  const { handleDelete } = useCRUD({
    queryKey: 'routes-optimization',
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

  const handleExportRoute = (route: any) => {
    console.log('Exporting route:', route)
    alert(`Exporting route: ${route.name || route.id} to PDF`)
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
      key: 'waypoints',
      header: 'Waypoints',
      render: (row: any) => {
        const count = row.waypoints?.length || row.stops_count || 0
        return (
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-blue-600" />
            <span className="font-medium">{count} stops</span>
          </div>
        )
      },
    },
    {
      key: 'distance',
      header: 'Distance',
      render: (row: any) => {
        const distance = row.distance || row.total_distance || 0
        return (
          <span className="text-sm">
            {distance.toFixed(1)} km
          </span>
        )
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
      key: 'optimization_score',
      header: 'Optimization',
      render: (row: any) => {
        const score = row.optimization_score || 75
        const variant = score >= 80 ? 'success' : score >= 60 ? 'warning' : 'danger'
        return (
          <Badge variant={variant}>
            {score}%
          </Badge>
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
            title="Edit route"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleExportRoute(row)}
            title="Export to PDF"
          >
            <Download className="h-4 w-4 text-blue-600" />
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

  // Calculate summary stats
  const totalDistance = filteredData.reduce((sum: number, route: any) =>
    sum + (route.distance || route.total_distance || 0), 0
  )
  const avgOptimization = filteredData.length > 0
    ? filteredData.reduce((sum: number, route: any) => sum + (route.optimization_score || 75), 0) / filteredData.length
    : 0

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Route Optimization</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Create Route
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Routes</p>
                <p className="text-2xl font-bold text-gray-900">{filteredData.length}</p>
              </div>
              <Navigation className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Distance</p>
                <p className="text-2xl font-bold text-blue-600">{totalDistance.toFixed(1)} km</p>
              </div>
              <MapPin className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Optimization</p>
                <p className="text-2xl font-bold text-green-600">{avgOptimization.toFixed(1)}%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Routes</p>
                <p className="text-2xl font-bold text-orange-600">
                  {filteredData.filter((r: any) => r.status === 'active').length}
                </p>
              </div>
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <span className="text-orange-600 text-xl">→</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Routes Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Routes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search routes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={routes} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Route Visualization */}
      <Card>
        <CardHeader>
          <CardTitle>Route Visualization</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-100 rounded-lg p-12 text-center">
            <Navigation className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Interactive route map will be displayed here</p>
            <p className="text-sm text-gray-500 mt-2">
              Shows route waypoints, optimized path, and distance calculations
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Route Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingRoute ? 'Edit Route' : 'Create New Route'}
        size="lg"
      >
        <div className="space-y-4 p-4">
          <p className="text-gray-600">
            Route planning form will be here with waypoint management, distance calculation, and optimization suggestions.
          </p>
          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={handleCloseModal}>
              Cancel
            </Button>
            <Button onClick={handleCloseModal}>
              {editingRoute ? 'Update Route' : 'Create Route'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
