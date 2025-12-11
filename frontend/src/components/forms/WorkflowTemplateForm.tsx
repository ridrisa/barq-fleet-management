import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { workflowTemplateSchema, type WorkflowTemplateFormData } from '@/schemas'

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
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<WorkflowTemplateFormData>({
    resolver: zodResolver(workflowTemplateSchema),
    defaultValues: {
      name: initialData?.name || '',
      template_code: initialData?.template_code || '',
      description: initialData?.description || '',
      category: initialData?.category || 'general',
      steps: initialData?.steps || '',
      approval_chain: initialData?.approval_chain || '',
      estimated_duration: initialData?.estimated_duration || 1,
      auto_assign: initialData?.auto_assign || false,
      status: initialData?.status || 'draft',
      trigger_type: initialData?.trigger_type || 'manual',
      conditions: initialData?.conditions || '',
      notifications: initialData?.notifications || '',
      notes: initialData?.notes || '',
    },
  })

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <FormSection
        title="Template Information"
        description="Define the workflow template basics"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Workflow Name" required error={errors.name?.message}>
            <Input
              {...register('name')}
              placeholder="Courier Onboarding Workflow"
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Template Code" required error={errors.template_code?.message}>
            <Input
              {...register('template_code')}
              placeholder="WF-001"
              disabled={mode === 'edit' || isLoading}
            />
          </FormField>

          <FormField label="Category" required error={errors.category?.message}>
            <Select
              {...register('category')}
              options={[
                { value: 'courier', label: 'Courier' },
                { value: 'vehicle', label: 'Vehicle' },
                { value: 'delivery', label: 'Delivery' },
                { value: 'hr', label: 'HR' },
                { value: 'finance', label: 'Finance' },
                { value: 'general', label: 'General' },
              ]}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
              options={[
                { value: 'draft', label: 'Draft' },
                { value: 'active', label: 'Active' },
                { value: 'archived', label: 'Archived' },
              ]}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Trigger Type" error={errors.trigger_type?.message}>
            <Select
              {...register('trigger_type')}
              options={[
                { value: 'manual', label: 'Manual' },
                { value: 'automatic', label: 'Automatic' },
                { value: 'scheduled', label: 'Scheduled' },
              ]}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Estimated Duration (hours)" required error={errors.estimated_duration?.message}>
            <Input
              type="number"
              {...register('estimated_duration', { valueAsNumber: true })}
              placeholder="24"
              disabled={isLoading}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Description"
        description="Detailed description of the workflow"
      >
        <FormField label="Description" required error={errors.description?.message}>
          <Input
            {...register('description')}
            placeholder="Provide a detailed description of this workflow template..."
            disabled={isLoading}
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
          error={errors.steps?.message}
          helperText="List workflow steps separated by semicolons (e.g., Step 1: Document review; Step 2: Manager approval)"
        >
          <Input
            {...register('steps')}
            placeholder="Step 1: Document collection; Step 2: Background check; Step 3: Final approval"
            disabled={isLoading}
          />
        </FormField>

        <FormField
          label="Approval Chain"
          required
          error={errors.approval_chain?.message}
          helperText="List approvers in order, separated by commas (e.g., Team Lead, Department Manager, HR Director)"
        >
          <Input
            {...register('approval_chain')}
            placeholder="Team Lead, Department Manager, HR Director"
            disabled={isLoading}
          />
        </FormField>

        <FormField label="Auto-Assign" error={errors.auto_assign?.message}>
          <Select
            {...register('auto_assign', {
              setValueAs: (v) => v === 'true' || v === true,
            })}
            options={[
              { value: 'false', label: 'Manual Assignment' },
              { value: 'true', label: 'Auto-Assign' },
            ]}
            disabled={isLoading}
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Conditions & Notifications"
        description="Trigger conditions and notification settings"
      >
        <FormField
          label="Trigger Conditions"
          error={errors.conditions?.message}
          helperText="Define conditions that trigger this workflow (optional)"
        >
          <Input
            {...register('conditions')}
            placeholder="e.g., New courier hired, Vehicle maintenance due"
            disabled={isLoading}
          />
        </FormField>

        <FormField
          label="Notifications"
          error={errors.notifications?.message}
          helperText="Who should be notified at each step (comma-separated)"
        >
          <Input
            {...register('notifications')}
            placeholder="Manager, HR, Requestor"
            disabled={isLoading}
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and comments"
      >
        <FormField label="Notes" error={errors.notes?.message}>
          <Input
            {...register('notes')}
            placeholder="Any additional notes about this workflow template..."
            disabled={isLoading}
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

// Re-export the type for backward compatibility
export type { WorkflowTemplateFormData }
