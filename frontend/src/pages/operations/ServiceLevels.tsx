import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus, Search, Edit, Trash2, Target, TrendingUp, TrendingDown, AlertCircle, Filter } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { BarChart } from '@/components/ui/BarChart'
import { serviceLevelsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { ServiceLevelForm } from '@/components/forms/ServiceLevelForm'

export default function ServiceLevels() {
  useTranslation()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingSLA, setEditingSLA] = useState<any>(null)
  const [serviceTypeFilter, setServiceTypeFilter] = useState<string>('all')
  const [performanceFilter, setPerformanceFilter] = useState<string>('all')

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
    queryKey: 'service-levels',
    queryFn: serviceLevelsAPI.getAll,
    pageSize: 10,
  })

  const { handleCreate, handleUpdate, handleDelete, isLoading: isMutating } = useCRUD({
    queryKey: 'service-levels',
    entityName: 'Service Level Agreement',
    create: serviceLevelsAPI.create,
    update: serviceLevelsAPI.update,
    delete: serviceLevelsAPI.delete,
  })

  const handleOpenCreateModal = () => {
    setEditingSLA(null)
    setIsModalOpen(true)
  }

  const handleOpenEditModal = (sla: any) => {
    setEditingSLA(sla)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setEditingSLA(null)
  }

  const handleSubmit = async (data: any) => {
    if (editingSLA) {
      await handleUpdate(editingSLA.id, data)
    } else {
      await handleCreate(data)
    }
    handleCloseModal()
  }

  // Apply filters
  let displayData = filteredData
  if (serviceTypeFilter !== 'all') {
    displayData = displayData.filter((s: any) => s.service_type === serviceTypeFilter)
  }
  if (performanceFilter !== 'all') {
    displayData = displayData.filter((s: any) => {
      const performance = s.current_performance || 0
      const target = s.target_time || 100
      const performancePercentage = (performance / target) * 100

      if (performanceFilter === 'meeting') return performancePercentage <= 100
      if (performanceFilter === 'below') return performancePercentage > 100
      return true
    })
  }

  // Get unique service types for filter
  const uniqueServiceTypes = Array.from(new Set(filteredData.map((s: any) => s.service_type).filter(Boolean)))

  // Summary stats
  const stats = {
    total: filteredData.length,
    meeting: filteredData.filter((s: any) => {
      const performance = s.current_performance || 0
      const target = s.target_time || 100
      return (performance / target) * 100 <= 100
    }).length,
    below: filteredData.filter((s: any) => {
      const performance = s.current_performance || 0
      const target = s.target_time || 100
      return (performance / target) * 100 > 100
    }).length,
    penalties: filteredData.reduce((sum: number, s: any) => sum + (s.penalty_amount || 0), 0),
  }

  const getPerformanceVariant = (sla: any): 'success' | 'warning' | 'danger' => {
    const performance = sla.current_performance || 0
    const target = sla.target_time || 100
    const percentage = (performance / target) * 100

    if (percentage <= 80) return 'success'
    if (percentage <= 100) return 'warning'
    return 'danger'
  }

  const columns = [
    {
      key: 'sla_id',
      header: 'SLA ID',
      sortable: true,
      render: (row: any) => (
        <div className="font-mono text-sm font-semibold text-blue-600">
          {row.sla_number || `SLA-${row.id?.toString().padStart(5, '0')}`}
        </div>
      ),
    },
    {
      key: 'service_type',
      header: 'Service Type',
      render: (row: any) => (
        <div>
          <div className="font-medium text-gray-900">{row.service_type || 'N/A'}</div>
          <div className="text-xs text-gray-500">{row.description || ''}</div>
        </div>
      ),
    },
    {
      key: 'target_time',
      header: 'Target Time',
      render: (row: any) => (
        <div>
          <div className="font-semibold text-gray-900">
            {row.target_time || 0} {row.time_unit || 'min'}
          </div>
          <div className="text-xs text-gray-500">{row.measurement || 'Average'}</div>
        </div>
      ),
    },
    {
      key: 'current_performance',
      header: 'Current Performance',
      render: (row: any) => {
        const performance = row.current_performance || 0
        const target = row.target_time || 100
        const percentage = Math.round((performance / target) * 100)

        return (
          <div className="flex items-center gap-2">
            <div>
              <div className="font-medium text-gray-900">
                {performance} {row.time_unit || 'min'}
              </div>
              <div className="text-xs text-gray-500">{percentage}% of target</div>
            </div>
            {percentage <= 100 ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
          </div>
        )
      },
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: any) => (
        <Badge variant={getPerformanceVariant(row)}>
          {getPerformanceVariant(row) === 'success' && 'Excellent'}
          {getPerformanceVariant(row) === 'warning' && 'Meeting Target'}
          {getPerformanceVariant(row) === 'danger' && 'Below Target'}
        </Badge>
      ),
    },
    {
      key: 'penalty',
      header: 'Penalty',
      render: (row: any) => {
        const hasPenalty = row.penalty_amount && row.penalty_amount > 0
        return hasPenalty ? (
          <div className="text-red-600 font-semibold">
            ${row.penalty_amount.toLocaleString()}
          </div>
        ) : (
          <span className="text-gray-400">-</span>
        )
      },
    },
    {
      key: 'measurement_period',
      header: 'Period',
      render: (row: any) => row.measurement_period || 'Monthly',
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
        <p className="text-red-800">Error loading service levels: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Service Level Agreements</h1>
        <Button onClick={handleOpenCreateModal}>
          <Plus className="h-4 w-4 mr-2" />
          New SLA
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">SLAs Defined</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              </div>
              <Target className="h-8 w-8 text-gray-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Meeting Target</p>
                <p className="text-2xl font-bold text-green-600">{stats.meeting}</p>
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
                <p className="text-sm font-medium text-gray-600">Below Target</p>
                <p className="text-2xl font-bold text-red-600">{stats.below}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
                <TrendingDown className="h-5 w-5 text-red-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Penalties</p>
                <p className="text-2xl font-bold text-orange-600">
                  ${stats.penalties.toLocaleString()}
                </p>
              </div>
              <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                <AlertCircle className="h-5 w-5 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Chart */}
      <Card>
        <CardHeader>
          <CardTitle>SLA Performance Overview</CardTitle>
        </CardHeader>
        <CardContent>
          {filteredData.length > 0 ? (
            <BarChart
              data={filteredData.slice(0, 10).map((sla: any) => ({
                name: sla.service_type || `SLA-${sla.id}`,
                'Target': sla.target_time || 0,
                'Actual': sla.current_performance || 0,
              }))}
              xKey="name"
              yKey={['Target', 'Actual']}
              colors={['#3b82f6', '#22c55e']}
              height={280}
            />
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              No SLA data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* SLA Table */}
      <Card>
        <CardHeader>
          <CardTitle>SLA Definitions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search SLAs..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  leftIcon={<Search className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-48">
                <Select
                  value={serviceTypeFilter}
                  onChange={(e) => setServiceTypeFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Service Types' },
                    ...uniqueServiceTypes.map(type => ({
                      value: type as string,
                      label: type as string,
                    })),
                  ]}
                  leftIcon={<Filter className="h-4 w-4 text-gray-400" />}
                />
              </div>
              <div className="w-full sm:w-40">
                <Select
                  value={performanceFilter}
                  onChange={(e) => setPerformanceFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Performance' },
                    { value: 'meeting', label: 'Meeting Target' },
                    { value: 'below', label: 'Below Target' },
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

      {/* SLA Form Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        title={editingSLA ? 'Edit SLA' : 'Define New SLA'}
        size="lg"
      >
        <ServiceLevelForm
          initialData={editingSLA}
          onSubmit={handleSubmit}
          onCancel={handleCloseModal}
          isLoading={isMutating}
        />
      </Modal>
    </div>
  )
}
