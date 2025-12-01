import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Edit, Trash2, Copy, Eye, Power, PowerOff, Play, PenTool } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { workflowTemplatesAPI, workflowInstancesAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'
import { WorkflowTemplateForm, WorkflowTemplateFormData } from '@/components/forms/WorkflowTemplateForm'
import toast from 'react-hot-toast'

interface WorkflowTemplate {
  id: number
  name: string
  template_code: string
  description: string
  category: 'courier' | 'vehicle' | 'delivery' | 'hr' | 'finance' | 'general'
  steps: string
  approval_chain: string
  estimated_duration: number
  auto_assign: boolean
  status: 'active' | 'draft' | 'archived'
  trigger_type?: 'manual' | 'automatic' | 'scheduled'
  created_at: string
  updated_at: string
}

export default function Templates() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false)
  const [isStartModalOpen, setIsStartModalOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<WorkflowTemplate | null>(null)
  const [previewTemplate, setPreviewTemplate] = useState<WorkflowTemplate | null>(null)
  const [startTemplate, setStartTemplate] = useState<WorkflowTemplate | null>(null)
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
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
    paginatedData: templates,
    filteredData,
  } = useDataTable<WorkflowTemplate>({
    queryKey: 'workflow-templates',
    queryFn: workflowTemplatesAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleCreate, handleUpdate, handleDelete, isLoading: isSaving } = useCRUD({
    queryKey: 'workflow-templates',
    entityName: 'Workflow Template',
    create: workflowTemplatesAPI.create,
    update: workflowTemplatesAPI.update,
    delete: workflowTemplatesAPI.delete,
  })

  // Filter by category and status
  const filteredTemplates = templates.filter((template) => {
    const categoryMatch = categoryFilter === 'all' || template.category === categoryFilter
    const statusMatch = statusFilter === 'all' || template.status === statusFilter
    return categoryMatch && statusMatch
  })

  // Handle activate/deactivate toggle
  const handleToggleStatus = async (template: WorkflowTemplate) => {
    const newStatus = template.status === 'active' ? 'draft' : 'active'
    await handleUpdate(template.id, { status: newStatus })
  }

  // Start workflow mutation
  const startWorkflowMutation = useMutation({
    mutationFn: async (templateId: number) => {
      return workflowInstancesAPI.create({
        template_id: templateId,
        status: 'in_progress',
        data: {},
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow-instances'] })
      toast.success('Workflow started successfully!')
      setIsStartModalOpen(false)
      setStartTemplate(null)
      navigate('/workflows/instances')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start workflow')
    },
  })

  // Handle clone template
  const handleClone = async (template: WorkflowTemplate) => {
    const clonedData: Partial<WorkflowTemplateFormData> = {
      name: `${template.name} (Copy)`,
      template_code: `${template.template_code}-COPY`,
      description: template.description,
      category: template.category,
      steps: template.steps,
      approval_chain: template.approval_chain,
      estimated_duration: template.estimated_duration,
      auto_assign: template.auto_assign,
      status: 'draft',
      trigger_type: template.trigger_type,
    }
    await handleCreate(clonedData)
  }

  // Handle start workflow
  const handleStartWorkflow = (template: WorkflowTemplate) => {
    if (template.status !== 'active') {
      toast.error('Only active templates can be started')
      return
    }
    setStartTemplate(template)
    setIsStartModalOpen(true)
  }

  // Handle open in builder
  const handleOpenInBuilder = (template: WorkflowTemplate) => {
    navigate(`/workflows/builder?id=${template.id}`)
  }

  // Handle preview
  const handlePreview = (template: WorkflowTemplate) => {
    setPreviewTemplate(template)
    setIsPreviewModalOpen(true)
  }

  // Handle edit
  const handleEdit = (template: WorkflowTemplate) => {
    setEditingTemplate(template)
    setIsModalOpen(true)
  }

  // Handle form submit
  const handleFormSubmit = async (data: WorkflowTemplateFormData) => {
    if (editingTemplate) {
      await handleUpdate(editingTemplate.id, data)
    } else {
      await handleCreate(data)
    }
    setIsModalOpen(false)
    setEditingTemplate(null)
  }

  // Handle modal close
  const handleModalClose = () => {
    setIsModalOpen(false)
    setEditingTemplate(null)
  }

  const columns = [
    {
      key: 'template_code',
      header: 'Code',
      sortable: true,
      render: (row: WorkflowTemplate) => (
        <span className="font-mono text-sm">{row.template_code}</span>
      ),
    },
    {
      key: 'name',
      header: 'Template Name',
      sortable: true,
      render: (row: WorkflowTemplate) => (
        <div>
          <p className="font-medium">{row.name}</p>
          <p className="text-xs text-gray-500 truncate max-w-xs">{row.description}</p>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      render: (row: WorkflowTemplate) => (
        <Badge variant="default">
          {row.category}
        </Badge>
      ),
    },
    {
      key: 'trigger_type',
      header: 'Trigger Type',
      render: (row: WorkflowTemplate) => (
        <Badge
          variant={
            row.trigger_type === 'automatic' ? 'success' :
            row.trigger_type === 'scheduled' ? 'warning' : 'default'
          }
        >
          {row.trigger_type || 'manual'}
        </Badge>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: WorkflowTemplate) => (
        <Badge
          variant={
            row.status === 'active' ? 'success' :
            row.status === 'draft' ? 'warning' : 'default'
          }
        >
          {row.status}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Created Date',
      sortable: true,
      render: (row: WorkflowTemplate) => {
        if (!row.created_at) return 'N/A'
        return new Date(row.created_at).toLocaleDateString()
      },
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: WorkflowTemplate) => (
        <div className="flex gap-1">
          {row.status === 'active' && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => handleStartWorkflow(row)}
              title="Start Workflow"
              className="text-green-600 hover:text-green-700 hover:bg-green-50"
            >
              <Play className="h-4 w-4" />
            </Button>
          )}
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handlePreview(row)}
            title="Preview"
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleOpenInBuilder(row)}
            title="Open in Builder"
            className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
          >
            <PenTool className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleToggleStatus(row)}
            title={row.status === 'active' ? 'Deactivate' : 'Activate'}
          >
            {row.status === 'active' ? (
              <PowerOff className="h-4 w-4 text-orange-600" />
            ) : (
              <Power className="h-4 w-4 text-green-600" />
            )}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleClone(row)}
            title="Clone"
          >
            <Copy className="h-4 w-4 text-blue-600" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleEdit(row)}
            title="Edit"
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleDelete(row.id)}
            title="Delete"
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
        <p className="text-red-800">
          Error loading workflow templates: {error.message}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Workflow Templates</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => navigate('/workflows/builder')}>
            <PenTool className="h-4 w-4 mr-2" />
            Visual Builder
          </Button>
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Template
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">
                {templates.length}
              </p>
              <p className="text-sm text-gray-600">Total Templates</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {templates.filter((t) => t.status === 'active').length}
              </p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">
                {templates.filter((t) => t.status === 'draft').length}
              </p>
              <p className="text-sm text-gray-600">Draft</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-600">
                {templates.filter((t) => t.status === 'archived').length}
              </p>
              <p className="text-sm text-gray-600">Archived</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workflow Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 space-y-4">
            <Input
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
            <div className="flex gap-4">
              <div className="flex-1">
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Categories' },
                    { value: 'courier', label: 'Courier' },
                    { value: 'vehicle', label: 'Vehicle' },
                    { value: 'delivery', label: 'Delivery' },
                    { value: 'hr', label: 'HR' },
                    { value: 'finance', label: 'Finance' },
                    { value: 'general', label: 'General' },
                  ]}
                />
              </div>
              <div className="flex-1">
                <Select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  options={[
                    { value: 'all', label: 'All Statuses' },
                    { value: 'active', label: 'Active' },
                    { value: 'draft', label: 'Draft' },
                    { value: 'archived', label: 'Archived' },
                  ]}
                />
              </div>
            </div>
          </div>
          <Table data={filteredTemplates} columns={columns} />
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
            totalItems={filteredData.length}
            pageSize={pageSize}
          />
        </CardContent>
      </Card>

      {/* Create/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        title={editingTemplate ? 'Edit Template' : 'New Template'}
        size="lg"
      >
        <WorkflowTemplateForm
          initialData={editingTemplate || undefined}
          onSubmit={handleFormSubmit}
          onCancel={handleModalClose}
          isLoading={isSaving}
          mode={editingTemplate ? 'edit' : 'create'}
        />
      </Modal>

      {/* Preview Modal */}
      <Modal
        isOpen={isPreviewModalOpen}
        onClose={() => setIsPreviewModalOpen(false)}
        title="Template Preview"
        size="lg"
      >
        {previewTemplate && (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">{previewTemplate.name}</h3>
              <p className="text-sm text-gray-600">{previewTemplate.description}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-700">Code</p>
                <p className="text-sm font-mono">{previewTemplate.template_code}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Category</p>
                <Badge variant="default">{previewTemplate.category}</Badge>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Status</p>
                <Badge variant={previewTemplate.status === 'active' ? 'success' : 'warning'}>
                  {previewTemplate.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Trigger Type</p>
                <Badge variant="default">{previewTemplate.trigger_type || 'manual'}</Badge>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Est. Duration</p>
                <p className="text-sm">{previewTemplate.estimated_duration} hours</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700">Auto-Assign</p>
                <p className="text-sm">{previewTemplate.auto_assign ? 'Yes' : 'No'}</p>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Steps</p>
              <div className="space-y-2">
                {previewTemplate.steps.split(';').map((step, index) => (
                  <Card key={index}>
                    <CardContent className="p-3">
                      <div className="flex items-center gap-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                          {index + 1}
                        </div>
                        <p className="text-sm">{step.trim()}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Approval Chain</p>
              <div className="flex items-center gap-2">
                {previewTemplate.approval_chain.split(',').map((approver, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Badge variant="outline">{approver.trim()}</Badge>
                    {index < previewTemplate.approval_chain.split(',').length - 1 && (
                      <span className="text-gray-400">→</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Start Workflow Confirmation Modal */}
      <Modal
        isOpen={isStartModalOpen}
        onClose={() => {
          setIsStartModalOpen(false)
          setStartTemplate(null)
        }}
        title="Start Workflow"
        size="md"
      >
        {startTemplate && (
          <div className="space-y-4">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-3">
                <Play className="h-8 w-8 text-green-600" />
                <div>
                  <h3 className="font-semibold text-green-900">{startTemplate.name}</h3>
                  <p className="text-sm text-green-700">{startTemplate.description}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Category</p>
                <Badge variant="default">{startTemplate.category}</Badge>
              </div>
              <div>
                <p className="text-gray-600">Est. Duration</p>
                <p className="font-medium">{startTemplate.estimated_duration} hours</p>
              </div>
              <div className="col-span-2">
                <p className="text-gray-600">Approval Chain</p>
                <p className="font-medium">{startTemplate.approval_chain}</p>
              </div>
            </div>

            <div className="pt-4 border-t">
              <p className="text-sm text-gray-600 mb-4">
                Are you sure you want to start this workflow? A new instance will be created and assigned for processing.
              </p>
              <div className="flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setIsStartModalOpen(false)
                    setStartTemplate(null)
                  }}
                >
                  Cancel
                </Button>
                <Button
                  onClick={() => startWorkflowMutation.mutate(startTemplate.id)}
                  disabled={startWorkflowMutation.isPending}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Play className="h-4 w-4 mr-2" />
                  {startWorkflowMutation.isPending ? 'Starting...' : 'Start Workflow'}
                </Button>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
