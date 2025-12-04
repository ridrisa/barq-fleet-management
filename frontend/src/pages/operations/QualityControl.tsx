import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, CheckCircle, XCircle, Filter, TrendingUp } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { AreaChart } from '@/components/charts/AreaChart'
import { qualityControlAPI, couriersAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { QualityControlForm } from '@/components/forms/QualityControlForm'

export default function QualityControl() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingInspection, setEditingInspection] = useState<any>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [inspectorFilter, setInspectorFilter] = useState<string>('all')

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
    queryKey: 'quality-inspections',
    queryFn: qualityControlAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'quality-inspections',
    entityName: 'Quality Inspection',
    create: qualityControlAPI.create,
    update: qualityControlAPI.update,
    delete: qualityControlAPI.delete,
  })

  // Fetch couriers (as inspectors) and deliveries for the form
  const { data: couriers = [], isLoading: couriersLoading } = useQuery({
    queryKey: ['couriers'],
    queryFn: () => couriersAPI.getAll(),
  })

  const handleOpenCreateModal = () => {
    setEditingInspection(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (inspection: any) => {
    setEditingInspection(inspection)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingInspection(null)
  }

  const handleSubmit = async (data: any) => {
    if (editingInspection) {
      await handleUpdate(editingInspection.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  // Apply filters
  let displayData = filteredData
  if (statusFilter !== 'all') {
    displayData = displayData.filter((i: any) => {
      if (statusFilter === 'passed') return i.passed === true
      if (statusFilter === 'failed') return i.passed === false
      if (statusFilter === 'pending') return i.corrective_action === 'pending'
      return true
    })
  }
  if (inspectorFilter !== 'all') {
    displayData = displayData.filter((i: any) => i.inspector === inspectorFilter)
  }

  // Get unique inspectors for filter
  const uniqueInspectors = Array.from(new Set(filteredData.map((i: any) => i.inspector).filter(Boolean)))

  // Summary stats
  const stats = {
    total: filteredData.length,
    passRate: filteredData.length > 0
      ? Math.round((filteredData.filter((i: any) => i.passed === true).length / filteredData.length) * 100)
      : 0,
    failed: filteredData.filter((i: any) => i.passed === false).length,
    pendingAction: filteredData.filter((i: any) => i.corrective_action === 'pending').length,
  }

  const getStatusVariant = (passed: boolean): 'success' | 'danger' => {
    return passed ? 'success' : 'danger'
  }

  const columns = [
    {
      key: 'inspection_id',
      header: 'Inspection ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.inspection_number || `QC-${row.id?.toString().padStart(5, '0')}`}
        </div>
      ),
    },
    {
      key: 'delivery_id',
      header: 'Delivery ID',
      render: (row: any) => (
        <div className="font-mono text-sm">
          {row.delivery_number || (row.delivery_id ? `DEL-${row.delivery_id?.toString().padStart(5, '0')}` : 'N/A')}
        </div>
      ),
    },
    {
      key: 'inspector',
      header: 'Inspector',
      render: (row: any) => (
        <div>
          <div className="font-medium text-gray-900">{row.inspector || 'N/A'}</div>
          <div className="text-xs text-gray-500">{row.inspector_email || ''}</div>
        </div>
      ),
    },
    {
      key: 'check_date',
      header: 'Check Date',
      sortable: true,
      render: (row: any) => {
        const date = row.check_date || row.created_at
        return date ? new Date(date).toLocaleDateString() : 'N/A'
      },
    },
    {
      key: 'passed',
      header: 'Result',
      render: (row: any) => (
        <Badge variant={getStatusVariant(row.passed)}>
          {row.passed ? (
            <span className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3" />
              Passed
            </span>
          ) : (
            <span className="flex items-center gap-1">
              <XCircle className="h-3 w-3" />
              Failed
            </span>
          )}
        </Badge>
      ),
    },
    {
      key: 'issues',
      header: 'Issues Found',
      render: (row: any) => (
        <div className="max-w-xs">
          <div className="text-sm text-gray-900 truncate">{row.issues || 'None'}</div>
          {row.issue_count && (
            <div className="text-xs text-gray-500">{row.issue_count} issue(s)</div>
          )}
        </div>
      ),
    },
    {
      key: 'corrective_action',
      header: 'Corrective Action',
      render: (row: any) => {
        if (!row.passed && row.corrective_action) {
          const status = row.corrective_action_status || 'pending'
          return (
            <Badge variant={status === 'completed' ? 'success' : 'warning'}>
              {status}
            </Badge>
          )
        }
        return <span className="text-gray-400">-</span>
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
        <p className="text-red-800">Error loading quality inspections: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Quality Control</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          New Inspection
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Inspections</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pass Rate</p>
                <p className="text-2xl font-bold text-green-600">{stats.passRate}%</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Failed</p>
                <p className="text-2xl font-bold text-red-600">{stats.failed}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending Action</p>
                <p className="text-2xl font-bold text-orange-600">{stats.pendingAction}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <span className="text-orange-600 text-xl">!</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quality Metrics Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Quality Metrics Trend</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredData.length > 0 ? (
            <AreaChart
              data={(() => {
                // Group by date and calculate pass rate
                const dateGroups: Record<string, { total: number; passed: number }> = {}
                filteredData.forEach((i: any) => {
                  const date = new Date(i.check_date || i.created_at).toISOString().split('T')[0]
                  if (!dateGroups[date]) dateGroups[date] = { total: 0, passed: 0 }
                  dateGroups[date].total++
                  if (i.passed) dateGroups[date].passed++
                })
                return Object.entries(dateGroups)
                  .sort(([a], [b]) => a.localeCompare(b))
                  .slice(-14)
                  .map(([date, data]) => ({
                    date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    'Pass Rate': data.total > 0 ? Math.round((data.passed / data.total) * 100) : 0,
                    'Inspections': data.total,
                  }))
              })()}
              xKey="date"
              yKeys={['Pass Rate', 'Inspections']}
              colors={['#22c55e', '#3b82f6']}
              height={280}
            />
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No quality inspection data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Inspections Table */}
      <Card>
        <CardHeader>
          <CardTitle>Inspection Records</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search inspections..."
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
                    { value: 'passed', label: 'Passed' },
                    { value: 'failed', label: 'Failed' },
                    { value: 'pending', label: 'Pending Action' },
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={inspectorFilter}
                  onChange={(e) => setInspectorFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Inspectors' },
                    ...uniqueInspectors.map(inspector => ({
                      value: inspector as string,
                      label: inspector as string,
                    })),
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

      {/* Inspection Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingInspection ? 'Edit Inspection' : 'New Quality Inspection'}
        size="lg"
      >
        <QualityControlForm
          initialData={editingInspection}
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating || couriersLoading}
          inspectors={couriers}
        />
      </Modal>
    </div>
  )
}
