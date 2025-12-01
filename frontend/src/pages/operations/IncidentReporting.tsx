import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, AlertTriangle, Filter, Image } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { incidentsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { IncidentReportingForm } from '@/components/forms/IncidentReportingForm'

export default function IncidentReporting() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingIncident, setEditingIncident] = useState<any>(null)
  const [severityFilter, setSeverityFilter] = useState<string>('all')
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
    queryKey: 'incidents',
    queryFn: incidentsAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'incidents',
    entityName: 'Incident',
    create: incidentsAPI.create,
    update: incidentsAPI.update,
    delete: incidentsAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingIncident(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (incident: any) => {
    setEditingIncident(incident)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingIncident(null)
  }

  const handleSubmit = async (data: any) => {
    if (editingIncident) {
      await handleUpdate(editingIncident.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  // Apply filters
  let displayData = filteredData
  if (severityFilter !== 'all') {
    displayData = displayData.filter((i: any) => i.severity === severityFilter)
  }
  if (statusFilter !== 'all') {
    displayData = displayData.filter((i: any) => i.status === statusFilter)
  }

  // Summary stats
  const stats = {
    total: filteredData.length,
    critical: filteredData.filter((i: any) => i.severity === 'critical').length,
    open: filteredData.filter((i: any) => i.status === 'open' || i.status === 'investigating').length,
    resolved: filteredData.filter((i: any) => i.status === 'resolved').length,
  }

  const getSeverityVariant = (severity: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      critical: 'danger',
      high: 'danger',
      medium: 'warning',
      low: 'default',
    }
    return variants[severity] || 'default'
  }

  const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      open: 'danger',
      investigating: 'warning',
      resolved: 'success',
      closed: 'default',
    }
    return variants[status] || 'default'
  }

  const columns = [
    {
      key: 'incident_id',
      header: 'Incident ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.incident_number || `INC-${row.id?.toString().padStart(5, '0')}`}
        </div>
      ),
    },
    {
      key: 'title',
      header: 'Title',
      render: (row: any) => (
        <div className="max-w-xs">
          <div className="font-medium text-gray-900">{row.title || 'Untitled Incident'}</div>
          <div className="text-xs text-gray-500 truncate">{row.description || ''}</div>
        </div>
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (row: any) => (
        <Badge variant={getSeverityVariant(row.severity || 'low')}>
          {row.severity || 'low'}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={getStatusVariant(row.status || 'open')}>
          {row.status || 'open'}
        </Badge>
      ),
    },
    {
      key: 'reported_by',
      header: 'Reported By',
      render: (row: any) => row.reporter_name || row.reported_by || 'N/A',
    },
    {
      key: 'courier_id',
      header: 'Courier',
      render: (row: any) => row.courier_name || (row.courier_id ? `Courier #${row.courier_id}` : 'N/A'),
    },
    {
      key: 'vehicle_id',
      header: 'Vehicle',
      render: (row: any) => row.vehicle_plate || (row.vehicle_id ? `Vehicle #${row.vehicle_id}` : 'N/A'),
    },
    {
      key: 'incident_date',
      header: 'Date',
      render: (row: any) => {
        const date = row.incident_date || row.created_at
        return date ? new Date(date).toLocaleDateString() : 'N/A'
      },
    },
    {
      key: 'has_photos',
      header: 'Photos',
      render: (row: any) => {
        const hasPhotos = row.photos?.length > 0 || row.has_attachments
        return hasPhotos ? (
          <Image className="h-4 w-4 text-blue-600" />
        ) : (
          <span className="text-gray-400">-</span>
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
        <p className="text-red-800">Error loading incidents: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Incident Reporting</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          Report Incident
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Incidents</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Critical</p>
                <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Open</p>
                <p className="text-2xl font-bold text-orange-600">{stats.open}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <span className="text-orange-600 text-xl">•</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Resolved</p>
                <p className="text-2xl font-bold text-green-600">{stats.resolved}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-green-600 text-xl">✓</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Incidents Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Incidents</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search incidents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Severity' },
                    { value: 'critical', label: 'Critical' },
                    { value: 'high', label: 'High' },
                    { value: 'medium', label: 'Medium' },
                    { value: 'low', label: 'Low' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Status' },
                    { value: 'open', label: 'Open' },
                    { value: 'investigating', label: 'Investigating' },
                    { value: 'resolved', label: 'Resolved' },
                    { value: 'closed', label: 'Closed' },
                  ]}
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

      {/* Incident Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingIncident ? 'Edit Incident' : 'Report New Incident'}
        size="lg"
      >
        <IncidentReportingForm
          initialData={editingIncident}
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
        />
      </Modal>
    </div>
  )
}
