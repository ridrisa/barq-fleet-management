import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { workflowTemplateFormSchema, type WorkflowTemplateFormData } from '@/schemas/workflow.schema'

export type { WorkflowTemplateFormData }

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
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<WorkflowTemplateFormData>({
    resolver: zodResolver(workflowTemplateFormSchema),
    defaultValues: {
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
    },
    mode: 'onBlur',
  })

  const formIsLoading = isLoading || isSubmitting
  const autoAssignValue = watch('auto_assign')

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
            />
          </FormField>

          <FormField label="Template Code" required error={errors.template_code?.message}>
            <Input
              {...register('template_code')}
              placeholder="WF-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Category" required>
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
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              {...register('status')}
              options={[
                { value: 'draft', label: 'Draft' },
                { value: 'active', label: 'Active' },
                { value: 'archived', label: 'Archived' },
              ]}
            />
          </FormField>

          <FormField label="Trigger Type">
            <Select
              {...register('trigger_type')}
              options={[
                { value: 'manual', label: 'Manual' },
                { value: 'automatic', label: 'Automatic' },
                { value: 'scheduled', label: 'Scheduled' },
              ]}
            />
          </FormField>

          <FormField label="Estimated Duration (hours)" required error={errors.estimated_duration?.message}>
            <Input
              type="number"
              {...register('estimated_duration', { valueAsNumber: true })}
              placeholder="24"
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
          />
        </FormField>

        <FormField label="Auto-Assign">
          <Select
            value={autoAssignValue ? 'true' : 'false'}
            onChange={(e) => setValue('auto_assign', e.target.value === 'true', { shouldValidate: true })}
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
            {...register('conditions')}
            placeholder="e.g., New courier hired, Vehicle maintenance due"
          />
        </FormField>

        <FormField
          label="Notifications"
          helperText="Who should be notified at each step (comma-separated)"
        >
          <Input
            {...register('notifications')}
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
            {...register('notes')}
            placeholder="Any additional notes about this workflow template..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={formIsLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={formIsLoading}>
          {formIsLoading ? 'Saving...' : mode === 'create' ? 'Create Workflow Template' : 'Update Workflow Template'}
        </Button>
      </FormActions>
    </Form>
  )
}
