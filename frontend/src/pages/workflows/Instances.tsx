import { useState } from 'react'
import { Search, Eye, XCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { workflowInstancesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

interface WorkflowStep {
  name: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  completed_at?: string
  assigned_to?: string
}

interface WorkflowInstance {
  id: number
  template_id: number
  template_name: string
  entity_type: string
  entity_id: number
  current_state: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled'
  initiated_by: string
  started_at: string
  completed_at?: string
  data: {
    steps?: WorkflowStep[]
    [key: string]: any
  }
}

export default function Instances() {
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false)
  const [selectedInstance, setSelectedInstance] = useState<WorkflowInstance | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('all')

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
    paginatedData: instances,
    filteredData,
  } = useDataTable<WorkflowInstance>({
    queryKey: 'workflow-instances',
    queryFn: workflowInstancesAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleUpdate } = useCRUD({
    queryKey: 'workflow-instances',
    entityName: 'Workflow Instance',
    create: workflowInstancesAPI.create,
    update: workflowInstancesAPI.update,
    delete: workflowInstancesAPI.delete,
  })

  // Filter by status
  const filteredInstances = instances.filter((instance) => {
    return statusFilter === 'all' || instance.status === statusFilter
  })

  // Handle view progress
  const handleViewProgress = (instance: WorkflowInstance) => {
    setSelectedInstance(instance)
    setIsProgressModalOpen(true)
  }

  // Handle cancel workflow
  const handleCancelWorkflow = async (id: number) => {
    if (window.confirm('Are you sure you want to cancel this workflow?')) {
      await handleUpdate(id, { status: 'cancelled' })
    }
  }

  // Format date
  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const columns = [
    {
      key: 'id',
      header: 'Instance ID',
      sortable: true,
      render: (row: WorkflowInstance) => (
        <span className="font-mono text-sm">#{row.id}</span>
      ),
    },
    {
      key: 'template_name',
      header: 'Template',
      sortable: true,
      render: (row: WorkflowInstance) => (
        <div>
          <p className="font-medium">{row.template_name}</p>
          <p className="text-xs text-gray-500">
            {row.entity_type} #{row.entity_id}
          </p>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: WorkflowInstance) => (
        <Badge
          variant={
            row.status === 'completed' ? 'success' :
            row.status === 'failed' ? 'danger' :
            row.status === 'cancelled' ? 'default' :
            row.status === 'in_progress' ? 'warning' : 'default'
          }
        >
          {row.status.replace('_', ' ')}
        </Badge>
      ),
    },
    {
      key: 'initiated_by',
      header: 'Started By',
      sortable: true,
    },
    {
      key: 'current_state',
      header: 'Current Step',
      render: (row: WorkflowInstance) => (
        <Badge variant="outline">{row.current_state}</Badge>
      ),
    },
    {
      key: 'started_at',
      header: 'Started Date',
      sortable: true,
      render: (row: WorkflowInstance) => formatDate(row.started_at),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: WorkflowInstance) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleViewProgress(row)}
            title="View Progress"
          >
            <Eye className="h-4 w-4" />
          </Button>
          {(row.status === 'pending' || row.status === 'in_progress') && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleCancelWorkflow(row.id)}
              title="Cancel Workflow"
            >
              <XCircle className="h-4 w-4 text-red-600" />
            </Button>
          )}
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
        <p className="text-red-800">
          Error loading workflow instances: {error.message}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflow Instances</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {instances.length}
              </p>
              <p className="text-sm text-gray-600">Total Instances</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {instances.filter((i) => i.status === 'pending').length}
              </p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {instances.filter((i) => i.status === 'in_progress').length}
              </p>
              <p className="text-sm text-gray-600">In Progress</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {instances.filter((i) => i.status === 'completed').length}
              </p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {instances.filter((i) => i.status === 'failed').length}
              </p>
              <p className="text-sm text-gray-600">Failed</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workflow Instances</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 space-y-4">
            <Input
              placeholder="Search instances..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
            <div className="flex-1">
              <Select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                options={[
                  { value: 'all', label: 'All Statuses' },
                  { value: 'pending', label: 'Pending' },
                  { value: 'in_progress', label: 'In Progress' },
                  { value: 'completed', label: 'Completed' },
                  { value: 'failed', label: 'Failed' },
                  { value: 'cancelled', label: 'Cancelled' },
                ]}
              />
            </div>
          </div>
          <Table data={filteredInstances} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Workflow Progress Modal */}
      <Modal
        isOpen={isProgressModalOpen}
        onClose={() => setIsProgressModalOpen(false)}
        title="Workflow Progress"
        size="lg"
      >
        {selectedInstance && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">{selectedInstance.template_name}</h3>
              <p className="text-sm text-gray-600">
                Instance #{selectedInstance.id} | {selectedInstance.entity_type} #{selectedInstance.entity_id}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge
                  variant={
                    selectedInstance.status === 'completed' ? 'success' :
                    selectedInstance.status === 'failed' ? 'danger' :
                    selectedInstance.status === 'in_progress' ? 'warning' : 'default'
                  }
                >
                  {selectedInstance.status.replace('_', ' ')}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Started By</p>
                <p className="font-medium">{selectedInstance.initiated_by}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Started At</p>
                <p className="font-medium">{formatDate(selectedInstance.started_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Completed At</p>
                <p className="font-medium">
                  {selectedInstance.completed_at ? formatDate(selectedInstance.completed_at) : 'In Progress'}
                </p>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-semibold mb-3">Workflow Steps</h4>
              <div className="relative">
                {selectedInstance.data?.steps && selectedInstance.data.steps.length > 0 ? (
                  selectedInstance.data.steps.map((step, index) => (
                    <div key={index} className="flex items-start mb-4">
                      <div className="flex flex-col items-center mr-4">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm ${
                            step.status === 'completed'
                              ? 'bg-green-500 text-white'
                              : step.status === 'in_progress'
                              ? 'bg-blue-500 text-white'
                              : step.status === 'failed'
                              ? 'bg-red-500 text-white'
                              : 'bg-gray-300 text-gray-700'
                          }`}
                        >
                          {index + 1}
                        </div>
                        {index < selectedInstance.data.steps!.length - 1 && (
                          <div
                            className={`w-0.5 h-12 mt-1 ${
                              step.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'
                            }`}
                          />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className="font-medium">{step.name}</p>
                          <Badge
                            variant={
                              step.status === 'completed' ? 'success' :
                              step.status === 'in_progress' ? 'warning' :
                              step.status === 'failed' ? 'danger' : 'default'
                            }
                          >
                            {step.status.replace('_', ' ')}
                          </Badge>
                        </div>
                        {step.assigned_to && (
                          <p className="text-sm text-gray-600">Assigned to: {step.assigned_to}</p>
                        )}
                        {step.completed_at && (
                          <p className="text-xs text-gray-500">{formatDate(step.completed_at)}</p>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>No step information available</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button variant="outline" onClick={() => setIsProgressModalOpen(false)}>
                Close
              </Button>
              {(selectedInstance.status === 'pending' || selectedInstance.status === 'in_progress') && (
                <Button
                  variant="danger"
                  onClick={() => {
                    handleCancelWorkflow(selectedInstance.id)
                    setIsProgressModalOpen(false)
                  }}
                >
                  Cancel Workflow
                </Button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
