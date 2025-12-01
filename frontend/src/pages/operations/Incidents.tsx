import { useState } from 'react'
import { Plus, Search, Edit, Trash2, AlertTriangle, Filter, Download, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { KPICard } from '@/components/ui/KPICard'
import { incidentsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { IncidentForm } from '@/components/forms/IncidentForm'

export default function Incidents() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingIncident, setEditingIncident] = useState<any>(null)
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [severityFilter, setSeverityFilter] = useState<string>('all')

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
    queryKey: 'incidents-all',
    queryFn: incidentsAPI.getAll,
    pageSize: 15,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'incidents-all',
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

  const handleExport = () => {
    alert('Exporting incidents to Excel...')
  }

  // Apply filters
  let displayData = filteredData
  if (typeFilter !== 'all') {
    displayData = displayData.filter((i: any) => i.incident_type === typeFilter)
  }
  if (severityFilter !== 'all') {
    displayData = displayData.filter((i: any) => i.severity === severityFilter)
  }

  // Summary stats
  const stats = {
    total: filteredData.length,
    reported: filteredData.filter((i: any) => i.status === 'reported' || i.resolution_status === 'reported').length,
    investigating: filteredData.filter((i: any) => i.status === 'investigating' || i.resolution_status === 'investigating').length,
    resolved: filteredData.filter((i: any) => i.status === 'resolved' || i.resolution_status === 'resolved').length,
    critical: filteredData.filter((i: any) => i.severity === 'critical').length,
  }

  const getSeverityVariant = (severity: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      critical: 'danger',
      major: 'danger',
      moderate: 'warning',
      minor: 'default',
    }
    return variants[severity] || 'default'
  }

  const getStatusVariant = (status: string): 'success' | 'warning' | 'danger' | 'default' => {
    const variants: Record<string, 'success' | 'warning' | 'danger' | 'default'> = {
      closed: 'success',
      resolved: 'success',
      investigating: 'warning',
      reported: 'default',
    }
    return variants[status] || 'default'
  }

  const columns = [
    {
      key: 'id',
      header: 'Incident #',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          INC-{row.id?.toString().padStart(5, '0')}
        </div>
      ),
    },
    {
      key: 'incident_type',
      header: 'Type',
      render: (row: any) => (
        <span className="text-sm capitalize">{row.incident_type || 'N/A'}</span>
      ),
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (row: any) => (
        <Badge variant={getSeverityVariant(row.severity || 'minor')}>
          {row.severity || 'minor'}
        </Badge>
      ),
    },
    {
      key: 'courier_id',
      header: 'Courier',
      render: (row: any) => row.courier_name || `Courier #${row.courier_id || 'N/A'}`,
    },
    {
      key: 'location',
      header: 'Location',
      render: (row: any) => (
        <div className="max-w-xs truncate text-sm text-gray-600">
          {row.location || 'N/A'}
        </div>
      ),
    },
    {
      key: 'date',
      header: 'Date',
      render: (row: any) => {
        const date = row.date || row.incident_date || row.created_at
        return date ? new Date(date).toLocaleDateString() : 'N/A'
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={getStatusVariant(row.status || row.resolution_status || 'reported')}>
          {row.status || row.resolution_status || 'reported'}
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
            title="Edit incident"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete incident"
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
        <h1 className="text-2xl font-bold">Incident Management</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleOpenCreateModal}>
            <Plus className="h-4 w-4 mr-2" />
            Report Incident
          </Button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <KPICard
          title="Total Incidents"
          value={stats.total}
          icon={<AlertTriangle className="h-6 w-6" />}
          color="blue"
          loading={isLoading}
        />
        <KPICard
          title="Reported"
          value={stats.reported}
          icon={<AlertTriangle className="h-6 w-6" />}
          color="yellow"
          loading={isLoading}
        />
        <KPICard
          title="Investigating"
          value={stats.investigating}
          icon={<AlertTriangle className="h-6 w-6" />}
          color="yellow"
          loading={isLoading}
        />
        <KPICard
          title="Resolved"
          value={stats.resolved}
          icon={<CheckCircle className="h-6 w-6" />}
          color="green"
          loading={isLoading}
        />
        <KPICard
          title="Critical"
          value={stats.critical}
          icon={<AlertTriangle className="h-6 w-6" />}
          color="red"
          loading={isLoading}
        />
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
                  placeholder="Search incidents by type, courier, location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Types' },
                    { value: 'accident', label: 'Accident' },
                    { value: 'theft', label: 'Theft' },
                    { value: 'damage', label: 'Damage' },
                    { value: 'violation', label: 'Violation' },
                    { value: 'other', label: 'Other' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Severity' },
                    { value: 'critical', label: 'Critical' },
                    { value: 'major', label: 'Major' },
                    { value: 'moderate', label: 'Moderate' },
                    { value: 'minor', label: 'Minor' },
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
        <IncidentForm
          initialData={editingIncident}
          onSubmit={async (data) => {
            if (editingIncident) {
              await handleUpdate(editingIncident.id, data)
            } else {
              await handleCreate(data)
            }
            handleCloseModal()
          }}
          onCancel={handleCloseModal}
          isLoading={isMutating}
          mode={editingIncident ? 'edit' : 'create'}
          couriers={[]}
          vehicles={[]}
        />
      </Modal>
    </div>
  )
}
