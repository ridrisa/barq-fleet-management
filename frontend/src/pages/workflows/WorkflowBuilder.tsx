import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Modal } from '@/components/ui/Modal'
import { Badge } from '@/components/ui/Badge'
import { Spinner } from '@/components/ui/Spinner'
import { Plus, Save, Trash2, ArrowLeft, Settings, Clock, User, CheckCircle } from 'lucide-react'
import { workflowTemplatesAPI } from '@/lib/api'
import toast from 'react-hot-toast'

interface WorkflowStep {
  id: string
  name: string
  type: 'start' | 'approval' | 'action' | 'notification' | 'condition' | 'end'
  x: number
  y: number
  description?: string
  sla_hours?: number
  assignee_role?: string
  required_fields?: string[]
  conditions?: string
}

interface Connection {
  from: string
  to: string
  label?: string
}

interface StepConfigModalProps {
  step: WorkflowStep | null
  isOpen: boolean
  onClose: () => void
  onSave: (step: WorkflowStep) => void
}

const StepConfigModal = ({ step, isOpen, onClose, onSave }: StepConfigModalProps) => {
  const [config, setConfig] = useState<WorkflowStep | null>(step)

  useEffect(() => {
    setConfig(step)
  }, [step])

  if (!config) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Configure Step" size="md">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Step Name</label>
          <Input
            value={config.name}
            onChange={(e) => setConfig({ ...config, name: e.target.value })}
            placeholder="Enter step name"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <Input
            value={config.description || ''}
            onChange={(e) => setConfig({ ...config, description: e.target.value })}
            placeholder="What happens in this step?"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Clock className="h-4 w-4 inline mr-1" />
              SLA (hours)
            </label>
            <Input
              type="number"
              value={config.sla_hours || ''}
              onChange={(e) => setConfig({ ...config, sla_hours: parseInt(e.target.value) || undefined })}
              placeholder="24"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <User className="h-4 w-4 inline mr-1" />
              Assignee Role
            </label>
            <Select
              value={config.assignee_role || ''}
              onChange={(e) => setConfig({ ...config, assignee_role: e.target.value })}
              options={[
                { value: '', label: 'Select role...' },
                { value: 'team_lead', label: 'Team Lead' },
                { value: 'manager', label: 'Manager' },
                { value: 'hr_director', label: 'HR Director' },
                { value: 'fleet_manager', label: 'Fleet Manager' },
                { value: 'finance', label: 'Finance Team' },
                { value: 'operations', label: 'Operations' },
                { value: 'admin', label: 'Admin' },
              ]}
            />
          </div>
        </div>
        {config.type === 'condition' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
            <Input
              value={config.conditions || ''}
              onChange={(e) => setConfig({ ...config, conditions: e.target.value })}
              placeholder="e.g., amount > 1000"
            />
          </div>
        )}
        <div className="flex justify-end gap-2 pt-4">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={() => { onSave(config); onClose(); }}>Save Changes</Button>
        </div>
      </div>
    </Modal>
  )
}

export default function WorkflowBuilder() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()
  const templateId = searchParams.get('id')

  const [steps, setSteps] = useState<WorkflowStep[]>([
    { id: '1', name: 'Start', type: 'start', x: 50, y: 200 }
  ])
  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedStep, setSelectedStep] = useState<string | null>(null)
  const [workflowName, setWorkflowName] = useState('New Workflow')
  const [workflowDescription, setWorkflowDescription] = useState('')
  const [category, setCategory] = useState<string>('general')
  const [configStep, setConfigStep] = useState<WorkflowStep | null>(null)
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false)

  // Load existing template if editing
  const { data: existingTemplate, isLoading: isLoadingTemplate } = useQuery({
    queryKey: ['workflow-template', templateId],
    queryFn: async () => {
      if (!templateId) return null
      const templates = await workflowTemplatesAPI.getAll()
      return templates.find((t: any) => t.id === parseInt(templateId))
    },
    enabled: !!templateId,
  })

  // Load template data when available
  useEffect(() => {
    if (existingTemplate) {
      setWorkflowName(existingTemplate.name || 'New Workflow')
      setWorkflowDescription(existingTemplate.description || '')
      setCategory(existingTemplate.category || 'general')

      // Parse steps from template
      if (existingTemplate.steps) {
        try {
          // Handle both JSON array and semicolon-separated string formats
          let parsedSteps: WorkflowStep[]
          if (typeof existingTemplate.steps === 'string') {
            const stepNames = existingTemplate.steps.split(';').map((s: string) => s.trim()).filter(Boolean)
            parsedSteps = [
              { id: '1', name: 'Start', type: 'start', x: 50, y: 200 },
              ...stepNames.map((name: string, index: number) => ({
                id: (index + 2).toString(),
                name,
                type: 'action' as const,
                x: 50 + (index + 1) * 200,
                y: 200,
              })),
              { id: (stepNames.length + 2).toString(), name: 'End', type: 'end' as const, x: 50 + (stepNames.length + 1) * 200, y: 200 }
            ]
          } else if (Array.isArray(existingTemplate.steps)) {
            parsedSteps = existingTemplate.steps
          } else {
            parsedSteps = [{ id: '1', name: 'Start', type: 'start', x: 50, y: 200 }]
          }
          setSteps(parsedSteps)

          // Create connections between sequential steps
          const newConnections: Connection[] = []
          for (let i = 0; i < parsedSteps.length - 1; i++) {
            newConnections.push({ from: parsedSteps[i].id, to: parsedSteps[i + 1].id })
          }
          setConnections(newConnections)
        } catch (e) {
          console.error('Error parsing steps:', e)
        }
      }
    }
  }, [existingTemplate])

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      if (templateId) {
        return workflowTemplatesAPI.update(parseInt(templateId), data)
      }
      return workflowTemplatesAPI.create(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflow-templates'] })
      toast.success(templateId ? 'Workflow updated successfully' : 'Workflow created successfully')
      navigate('/workflows/templates')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to save workflow')
    },
  })

  const addStep = (type: WorkflowStep['type']) => {
    const stepNames: Record<string, string> = {
      approval: 'Approval Step',
      action: 'Action Step',
      notification: 'Send Notification',
      condition: 'Condition',
      end: 'End',
    }

    const maxX = Math.max(...steps.map(s => s.x))
    const newStep: WorkflowStep = {
      id: Date.now().toString(),
      name: stepNames[type] || type,
      type,
      x: maxX + 200,
      y: 200,
      sla_hours: type === 'approval' ? 24 : undefined,
    }
    setSteps([...steps, newStep])

    if (selectedStep) {
      setConnections([...connections, { from: selectedStep, to: newStep.id }])
    }
    setSelectedStep(newStep.id)
  }

  const removeStep = (id: string) => {
    setSteps(steps.filter(s => s.id !== id))
    setConnections(connections.filter(c => c.from !== id && c.to !== id))
    if (selectedStep === id) setSelectedStep(null)
  }

  const updateStep = (updatedStep: WorkflowStep) => {
    setSteps(steps.map(s => s.id === updatedStep.id ? updatedStep : s))
  }

  const saveWorkflow = () => {
    if (steps.length < 2) {
      toast.error('Add at least one step before saving')
      return
    }

    if (!workflowName.trim()) {
      toast.error('Please enter a workflow name')
      return
    }

    // Convert steps to the format expected by backend
    const stepNames = steps
      .filter(s => s.type !== 'start')
      .map(s => s.name)
      .join('; ')

    // Get approval chain from approval steps
    const approvalChain = steps
      .filter(s => s.type === 'approval' && s.assignee_role)
      .map(s => s.assignee_role)
      .join(', ') || 'Team Lead'

    // Calculate estimated duration from SLA
    const estimatedDuration = steps.reduce((total, s) => total + (s.sla_hours || 0), 0) || 24

    const workflowData = {
      name: workflowName,
      template_code: templateId ? existingTemplate?.template_code : `WF-${Date.now()}`,
      description: workflowDescription || `Workflow: ${workflowName}`,
      category,
      steps: stepNames,
      approval_chain: approvalChain,
      estimated_duration: estimatedDuration,
      auto_assign: false,
      status: 'draft',
      trigger_type: 'manual',
      // Store full step config in data field for future use
      _step_config: JSON.stringify(steps),
      _connections: JSON.stringify(connections),
    }

    saveMutation.mutate(workflowData)
  }

  const getStepColor = (type: string) => {
    switch (type) {
      case 'start': return 'bg-green-100 border-green-500 text-green-700'
      case 'approval': return 'bg-blue-100 border-blue-500 text-blue-700'
      case 'action': return 'bg-purple-100 border-purple-500 text-purple-700'
      case 'notification': return 'bg-yellow-100 border-yellow-500 text-yellow-700'
      case 'condition': return 'bg-orange-100 border-orange-500 text-orange-700'
      case 'end': return 'bg-red-100 border-red-500 text-red-700'
      default: return 'bg-gray-100 border-gray-500 text-gray-700'
    }
  }

  const getStepIcon = (type: string) => {
    switch (type) {
      case 'start': return <CheckCircle className="h-4 w-4" />
      case 'approval': return <User className="h-4 w-4" />
      case 'notification': return <Settings className="h-4 w-4" />
      default: return null
    }
  }

  if (isLoadingTemplate) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/workflows/templates')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <h1 className="text-2xl font-bold">
            {templateId ? 'Edit Workflow' : 'Create Workflow'}
          </h1>
        </div>
        <Button onClick={saveWorkflow} disabled={saveMutation.isPending}>
          <Save className="h-4 w-4 mr-2" />
          {saveMutation.isPending ? 'Saving...' : 'Save Workflow'}
        </Button>
      </div>

      {/* Workflow Info */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Workflow Name</label>
              <Input
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                placeholder="Enter workflow name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <Select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                options={[
                  { value: 'courier', label: 'Courier' },
                  { value: 'vehicle', label: 'Vehicle' },
                  { value: 'delivery', label: 'Delivery' },
                  { value: 'hr', label: 'HR' },
                  { value: 'finance', label: 'Finance' },
                  { value: 'general', label: 'General' },
                ]}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <Input
                value={workflowDescription}
                onChange={(e) => setWorkflowDescription(e.target.value)}
                placeholder="Brief description"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-5 gap-6">
        {/* Step Palette */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="text-base">Add Steps</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              variant="outline"
              fullWidth
              size="sm"
              onClick={() => addStep('approval')}
              className="justify-start"
            >
              <Plus className="h-3 w-3 mr-2" />
              Approval
            </Button>
            <Button
              variant="outline"
              fullWidth
              size="sm"
              onClick={() => addStep('action')}
              className="justify-start"
            >
              <Plus className="h-3 w-3 mr-2" />
              Action
            </Button>
            <Button
              variant="outline"
              fullWidth
              size="sm"
              onClick={() => addStep('notification')}
              className="justify-start"
            >
              <Plus className="h-3 w-3 mr-2" />
              Notification
            </Button>
            <Button
              variant="outline"
              fullWidth
              size="sm"
              onClick={() => addStep('condition')}
              className="justify-start"
            >
              <Plus className="h-3 w-3 mr-2" />
              Condition
            </Button>
            <Button
              variant="outline"
              fullWidth
              size="sm"
              onClick={() => addStep('end')}
              className="justify-start"
            >
              <Plus className="h-3 w-3 mr-2" />
              End
            </Button>

            <div className="pt-4 border-t mt-4">
              <h4 className="text-sm font-semibold mb-2">Legend</h4>
              <div className="space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-100 border-2 border-green-500 rounded"></div>
                  <span>Start</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-100 border-2 border-blue-500 rounded"></div>
                  <span>Approval</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-purple-100 border-2 border-purple-500 rounded"></div>
                  <span>Action</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-yellow-100 border-2 border-yellow-500 rounded"></div>
                  <span>Notification</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-orange-100 border-2 border-orange-500 rounded"></div>
                  <span>Condition</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-red-100 border-2 border-red-500 rounded"></div>
                  <span>End</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Canvas */}
        <Card className="col-span-4">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Workflow Canvas</CardTitle>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>Steps: {steps.length}</span>
              <span>|</span>
              <span>Connections: {connections.length}</span>
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative bg-gray-50 rounded-lg p-6 min-h-[450px] border-2 border-dashed border-gray-300 overflow-x-auto">
              <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ minWidth: `${Math.max(...steps.map(s => s.x)) + 250}px` }}>
                <defs>
                  <marker
                    id="arrowhead"
                    markerWidth="10"
                    markerHeight="10"
                    refX="9"
                    refY="3"
                    orient="auto"
                  >
                    <polygon points="0 0, 10 3, 0 6" fill="#3b82f6" />
                  </marker>
                </defs>
                {connections.map((conn, index) => {
                  const fromStep = steps.find(s => s.id === conn.from)
                  const toStep = steps.find(s => s.id === conn.to)
                  if (!fromStep || !toStep) return null

                  const x1 = fromStep.x + 160
                  const y1 = fromStep.y + 35
                  const x2 = toStep.x
                  const y2 = toStep.y + 35

                  return (
                    <line
                      key={index}
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#3b82f6"
                      strokeWidth="2"
                      markerEnd="url(#arrowhead)"
                    />
                  )
                })}
              </svg>

              {steps.map((step) => (
                <div
                  key={step.id}
                  style={{
                    position: 'absolute',
                    left: step.x,
                    top: step.y
                  }}
                  className={`
                    relative p-3 rounded-lg border-2 cursor-pointer w-[160px]
                    ${getStepColor(step.type)}
                    ${selectedStep === step.id ? 'ring-4 ring-blue-300 shadow-lg' : 'shadow'}
                    transition-all duration-200
                  `}
                  onClick={() => setSelectedStep(step.id)}
                >
                  <div className="flex items-start justify-between gap-1">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1">
                        {getStepIcon(step.type)}
                        <p className="text-sm font-medium truncate">{step.name}</p>
                      </div>
                      <p className="text-xs opacity-75 capitalize">{step.type}</p>
                      {step.sla_hours && (
                        <Badge variant="outline" className="mt-1 text-xs">
                          <Clock className="h-3 w-3 mr-1" />
                          {step.sla_hours}h SLA
                        </Badge>
                      )}
                    </div>
                    {step.type !== 'start' && (
                      <div className="flex flex-col gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setConfigStep(step)
                            setIsConfigModalOpen(true)
                          }}
                          className="p-1 hover:bg-white/50 rounded"
                          title="Configure"
                        >
                          <Settings className="h-3 w-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            removeStep(step.id)
                          }}
                          className="p-1 hover:bg-white/50 rounded"
                          title="Delete"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {steps.length === 1 && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <p className="text-gray-400 text-sm">
                    Click "Add Steps" buttons to build your workflow
                  </p>
                </div>
              )}
            </div>

            {selectedStep && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-blue-900">
                    Selected: {steps.find(s => s.id === selectedStep)?.name}
                  </p>
                  <p className="text-xs text-blue-700">
                    Add a step to connect it to this one, or click Configure to set properties
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const step = steps.find(s => s.id === selectedStep)
                    if (step && step.type !== 'start') {
                      setConfigStep(step)
                      setIsConfigModalOpen(true)
                    }
                  }}
                  disabled={steps.find(s => s.id === selectedStep)?.type === 'start'}
                >
                  <Settings className="h-4 w-4 mr-1" />
                  Configure
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Workflow Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Steps</p>
              <p className="text-2xl font-bold">{steps.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Approval Steps</p>
              <p className="text-2xl font-bold text-blue-600">
                {steps.filter(s => s.type === 'approval').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total SLA (hours)</p>
              <p className="text-2xl font-bold text-orange-600">
                {steps.reduce((sum, s) => sum + (s.sla_hours || 0), 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Flow</p>
              <p className="text-sm font-medium truncate">
                {steps.map(s => s.name).join(' → ')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step Config Modal */}
      <StepConfigModal
        step={configStep}
        isOpen={isConfigModalOpen}
        onClose={() => {
          setIsConfigModalOpen(false)
          setConfigStep(null)
        }}
        onSave={updateStep}
      />
    </div>
  )
}
