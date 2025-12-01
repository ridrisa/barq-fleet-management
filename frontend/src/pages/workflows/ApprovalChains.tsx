import { useState } from 'react'
import { Plus, Search, Edit, Trash2, GripVertical, Play } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Table } from '@/components/ui/Table'
import { Badge } from '@/components/ui/Badge'
import { Modal } from '@/components/ui/Modal'
import { Pagination } from '@/components/ui/Pagination'
import { Spinner } from '@/components/ui/Spinner'
import { Select } from '@/components/ui/Select'
import { approvalChainsAPI } from '@/lib/api'
import { useDataTable } from '@/hooks/useDataTable'
import { useCRUD } from '@/hooks/useCRUD'

interface ApprovalStep {
  id: string
  name: string
  role: string
  approver_type: 'user' | 'role' | 'department'
  approver_id?: string
  approver_name: string
  timeout_hours?: number
  required: boolean
}

interface ApprovalChain {
  id: number
  name: string
  description: string
  steps: ApprovalStep[]
  auto_escalate: boolean
  escalation_hours?: number
  active: boolean
  created_at: string
  updated_at: string
}

export default function ApprovalChains() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingChain, setEditingChain] = useState<ApprovalChain | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    auto_escalate: false,
    escalation_hours: 24,
    active: true,
  })
  const [steps, setSteps] = useState<ApprovalStep[]>([])
  const [newStep, setNewStep] = useState({
    name: '',
    role: '',
    approver_type: 'role' as 'user' | 'role' | 'department',
    approver_name: '',
    timeout_hours: 24,
    required: true,
  })

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
    paginatedData: chains,
    filteredData,
  } = useDataTable<ApprovalChain>({
    queryKey: 'approval-chains',
    queryFn: approvalChainsAPI.getAll,
    pageSize: 10,
  })

  // Use the reusable CRUD hook
  const { handleCreate, handleUpdate, handleDelete, isLoading: isSaving } = useCRUD({
    queryKey: 'approval-chains',
    entityName: 'Approval Chain',
    create: approvalChainsAPI.create,
    update: approvalChainsAPI.update,
    delete: approvalChainsAPI.delete,
  })

  // Handle add step
  const handleAddStep = () => {
    if (!newStep.name || !newStep.approver_name) return

    const step: ApprovalStep = {
      id: `step-${Date.now()}`,
      ...newStep,
    }

    setSteps([...steps, step])
    setNewStep({
      name: '',
      role: '',
      approver_type: 'role',
      approver_name: '',
      timeout_hours: 24,
      required: true,
    })
  }

  // Handle remove step
  const handleRemoveStep = (stepId: string) => {
    setSteps(steps.filter((s) => s.id !== stepId))
  }

  // Handle move step
  const handleMoveStep = (index: number, direction: 'up' | 'down') => {
    const newSteps = [...steps]
    const targetIndex = direction === 'up' ? index - 1 : index + 1

    if (targetIndex < 0 || targetIndex >= steps.length) return

    [newSteps[index], newSteps[targetIndex]] = [newSteps[targetIndex], newSteps[index]]
    setSteps(newSteps)
  }

  // Handle form submit
  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const data = {
      ...formData,
      steps,
    }

    if (editingChain) {
      await handleUpdate(editingChain.id, data)
    } else {
      await handleCreate(data)
    }

    resetForm()
    setIsModalOpen(false)
  }

  // Handle edit
  const handleEdit = (chain: ApprovalChain) => {
    setEditingChain(chain)
    setFormData({
      name: chain.name,
      description: chain.description,
      auto_escalate: chain.auto_escalate,
      escalation_hours: chain.escalation_hours || 24,
      active: chain.active,
    })
    setSteps(chain.steps || [])
    setIsModalOpen(true)
  }

  // Handle test
  const handleTest = async (chain: ApprovalChain) => {
    alert(`Testing approval chain: ${chain.name}\nThis would simulate the approval process through all steps.`)
  }

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      auto_escalate: false,
      escalation_hours: 24,
      active: true,
    })
    setSteps([])
    setEditingChain(null)
  }

  // Handle modal close
  const handleModalClose = () => {
    resetForm()
    setIsModalOpen(false)
  }

  const columns = [
    {
      key: 'name',
      header: 'Chain Name',
      sortable: true,
      render: (row: ApprovalChain) => (
        <div>
          <p className="font-medium">{row.name}</p>
          <p className="text-xs text-gray-500 truncate max-w-xs">{row.description}</p>
        </div>
      ),
    },
    {
      key: 'steps',
      header: 'Steps',
      render: (row: ApprovalChain) => (
        <Badge variant="outline">{row.steps?.length || 0} steps</Badge>
      ),
    },
    {
      key: 'approvers',
      header: 'Approvers',
      render: (row: ApprovalChain) => (
        <div className="flex items-center gap-1 flex-wrap">
          {row.steps?.slice(0, 3).map((step, index) => (
            <Badge key={index} variant="default" className="text-xs">
              {step.approver_name}
            </Badge>
          ))}
          {row.steps?.length > 3 && (
            <span className="text-xs text-gray-500">+{row.steps.length - 3} more</span>
          )}
        </div>
      ),
    },
    {
      key: 'auto_escalate',
      header: 'Auto-Escalate',
      render: (row: ApprovalChain) => (
        <Badge variant={row.auto_escalate ? 'success' : 'default'}>
          {row.auto_escalate ? 'Yes' : 'No'}
        </Badge>
      ),
    },
    {
      key: 'active',
      header: 'Active',
      render: (row: ApprovalChain) => (
        <Badge variant={row.active ? 'success' : 'default'}>
          {row.active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (row: ApprovalChain) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="ghost"
            onClick={() => handleTest(row)}
            title="Test Chain"
          >
            <Play className="h-4 w-4 text-blue-600" />
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
        <p className="text-red-800">Error loading approval chains: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Approval Chains</h1>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Approval Chain
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{chains.length}</p>
              <p className="text-sm text-gray-600">Total Chains</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {chains.filter((c) => c.active).length}
              </p>
              <p className="text-sm text-gray-600">Active</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {chains.filter((c) => c.auto_escalate).length}
              </p>
              <p className="text-sm text-gray-600">Auto-Escalate</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Approval Chains</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <Input
              placeholder="Search approval chains..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="h-4 w-4 text-gray-400" />}
            />
          </div>
          <Table data={chains} columns={columns} />
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
        title={editingChain ? 'Edit Approval Chain' : 'New Approval Chain'}
        size="lg"
      >
        <form onSubmit={handleFormSubmit} className="space-y-6">
          {/* Basic Info */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Chain Name
              </label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Leave Approval Chain"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe the approval chain"
                rows={2}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Auto-Escalate
                </label>
                <Select
                  value={formData.auto_escalate ? 'true' : 'false'}
                  onChange={(e) =>
                    setFormData({ ...formData, auto_escalate: e.target.value === 'true' })
                  }
                  options={[
                    { value: 'false', label: 'No' },
                    { value: 'true', label: 'Yes' },
                  ]}
                />
              </div>
              {formData.auto_escalate && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Escalation Hours
                  </label>
                  <Input
                    type="number"
                    value={formData.escalation_hours}
                    onChange={(e) =>
                      setFormData({ ...formData, escalation_hours: parseInt(e.target.value) })
                    }
                    min="1"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Steps Builder */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Approval Steps</h3>
              <span className="text-sm text-gray-500">{steps.length} steps</span>
            </div>

            {/* Existing Steps */}
            <div className="space-y-2">
              {steps.map((step, index) => (
                <Card key={step.id}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <div className="flex flex-col gap-1">
                        <Button
                          type="button"
                          size="sm"
                          variant="ghost"
                          onClick={() => handleMoveStep(index, 'up')}
                          disabled={index === 0}
                        >
                          <GripVertical className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold">{step.name}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="default">{step.approver_name}</Badge>
                          <Badge variant="outline">{step.approver_type}</Badge>
                          {step.timeout_hours && (
                            <span className="text-xs text-gray-500">
                              {step.timeout_hours}h timeout
                            </span>
                          )}
                        </div>
                      </div>
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemoveStep(step.id)}
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Add New Step */}
            <Card className="border-dashed">
              <CardContent className="p-4">
                <h4 className="text-sm font-semibold mb-3">Add Step</h4>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-3">
                    <Input
                      placeholder="Step name"
                      value={newStep.name}
                      onChange={(e) => setNewStep({ ...newStep, name: e.target.value })}
                    />
                    <Input
                      placeholder="Role (e.g., HR Manager)"
                      value={newStep.role}
                      onChange={(e) => setNewStep({ ...newStep, role: e.target.value })}
                    />
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <Select
                      value={newStep.approver_type}
                      onChange={(e) =>
                        setNewStep({
                          ...newStep,
                          approver_type: e.target.value as 'user' | 'role' | 'department',
                        })
                      }
                      options={[
                        { value: 'user', label: 'User' },
                        { value: 'role', label: 'Role' },
                        { value: 'department', label: 'Department' },
                      ]}
                    />
                    <Input
                      placeholder="Approver name"
                      value={newStep.approver_name}
                      onChange={(e) => setNewStep({ ...newStep, approver_name: e.target.value })}
                    />
                    <Input
                      type="number"
                      placeholder="Timeout (hours)"
                      value={newStep.timeout_hours}
                      onChange={(e) =>
                        setNewStep({ ...newStep, timeout_hours: parseInt(e.target.value) })
                      }
                    />
                  </div>
                  <Button type="button" variant="outline" onClick={handleAddStep} className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Step
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button type="button" variant="ghost" onClick={handleModalClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSaving || steps.length === 0}>
              {isSaving ? 'Saving...' : editingChain ? 'Update Chain' : 'Create Chain'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
