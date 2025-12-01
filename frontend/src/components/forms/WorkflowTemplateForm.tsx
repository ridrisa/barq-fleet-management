import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface WorkflowTemplateFormData {
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
  conditions?: string
  notifications?: string
  notes?: string
}

export interface WorkflowTemplateFormProps {
  initialData?: Partial<WorkflowTemplateFormData>
  onSubmit: (data: WorkflowTemplateFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const WorkflowTemplateForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: WorkflowTemplateFormProps) => {
  const [formData, setFormData] = useState<WorkflowTemplateFormData>({
    name: initialData?.name || '',
    template_code: initialData?.template_code || '',
    description: initialData?.description || '',
    category: initialData?.category || 'general',
    steps: initialData?.steps || '',
    approval_chain: initialData?.approval_chain || '',
    estimated_duration: initialData?.estimated_duration || 0,
    auto_assign: initialData?.auto_assign || false,
    status: initialData?.status || 'draft',
    trigger_type: initialData?.trigger_type || 'manual',
    conditions: initialData?.conditions || '',
    notifications: initialData?.notifications || '',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof WorkflowTemplateFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof WorkflowTemplateFormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Workflow name is required'
    }

    if (!formData.template_code.trim()) {
      newErrors.template_code = 'Template code is required'
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required'
    } else if (formData.description.trim().length < 20) {
      newErrors.description = 'Description must be at least 20 characters'
    }

    if (!formData.steps.trim()) {
      newErrors.steps = 'Workflow steps are required'
    }

    if (!formData.approval_chain.trim()) {
      newErrors.approval_chain = 'Approval chain is required'
    }

    if (formData.estimated_duration <= 0) {
      newErrors.estimated_duration = 'Estimated duration must be greater than zero'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    await onSubmit(formData)
  }

  const handleChange = (field: keyof WorkflowTemplateFormData, value: string | number | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Template Information"
        description="Define the workflow template basics"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Workflow Name" required error={errors.name}>
            <Input
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Courier Onboarding Workflow"
            />
          </FormField>

          <FormField label="Template Code" required error={errors.template_code}>
            <Input
              value={formData.template_code}
              onChange={(e) => handleChange('template_code', e.target.value)}
              placeholder="WF-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Category" required>
            <Select
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              options={[
                { value: 'courier', label: 'Courier' },
                { value: 'vehicle', label: 'Vehicle' },
                { value: 'delivery', label: 'Delivery' },
                { value: 'hr', label: 'HR' },
                { value: 'finance', label: 'Finance' },
                { value: 'general', label: 'General' },
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'draft', label: 'Draft' },
                { value: 'active', label: 'Active' },
                { value: 'archived', label: 'Archived' },
              ]}
            />
          </FormField>

          <FormField label="Trigger Type">
            <Select
              value={formData.trigger_type}
              onChange={(e) => handleChange('trigger_type', e.target.value)}
              options={[
                { value: 'manual', label: 'Manual' },
                { value: 'automatic', label: 'Automatic' },
                { value: 'scheduled', label: 'Scheduled' },
              ]}
            />
          </FormField>

          <FormField label="Estimated Duration (hours)" required error={errors.estimated_duration}>
            <Input
              type="number"
              value={formData.estimated_duration}
              onChange={(e) => handleChange('estimated_duration', parseInt(e.target.value))}
              placeholder="24"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Description"
        description="Detailed description of the workflow"
      >
        <FormField label="Description" required error={errors.description}>
          <Input
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Provide a detailed description of this workflow template..."
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Workflow Steps"
        description="Define the steps and approval process"
      >
        <FormField
          label="Steps"
          required
          error={errors.steps}
          helperText="List workflow steps separated by semicolons (e.g., Step 1: Document review; Step 2: Manager approval)"
        >
          <Input
            value={formData.steps}
            onChange={(e) => handleChange('steps', e.target.value)}
            placeholder="Step 1: Document collection; Step 2: Background check; Step 3: Final approval"
          />
        </FormField>

        <FormField
          label="Approval Chain"
          required
          error={errors.approval_chain}
          helperText="List approvers in order, separated by commas (e.g., Team Lead, Department Manager, HR Director)"
        >
          <Input
            value={formData.approval_chain}
            onChange={(e) => handleChange('approval_chain', e.target.value)}
            placeholder="Team Lead, Department Manager, HR Director"
          />
        </FormField>

        <FormField label="Auto-Assign">
          <Select
            value={formData.auto_assign ? 'true' : 'false'}
            onChange={(e) => handleChange('auto_assign', e.target.value === 'true')}
            options={[
              { value: 'false', label: 'Manual Assignment' },
              { value: 'true', label: 'Auto-Assign' },
            ]}
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Conditions & Notifications"
        description="Trigger conditions and notification settings"
      >
        <FormField
          label="Trigger Conditions"
          helperText="Define conditions that trigger this workflow (optional)"
        >
          <Input
            value={formData.conditions}
            onChange={(e) => handleChange('conditions', e.target.value)}
            placeholder="e.g., New courier hired, Vehicle maintenance due"
          />
        </FormField>

        <FormField
          label="Notifications"
          helperText="Who should be notified at each step (comma-separated)"
        >
          <Input
            value={formData.notifications}
            onChange={(e) => handleChange('notifications', e.target.value)}
            placeholder="Manager, HR, Requestor"
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and comments"
      >
        <FormField label="Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes about this workflow template..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Workflow Template' : 'Update Workflow Template'}
        </Button>
      </FormActions>
    </Form>
  )
}
