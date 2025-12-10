import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { priorityQueueSchema, type PriorityQueueFormData } from '@/schemas/fleet.schema'

export type { PriorityQueueFormData }

export interface PriorityQueueFormProps {
  initialData?: Partial<PriorityQueueFormData>
  onSubmit: (data: PriorityQueueFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const PriorityQueueForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: PriorityQueueFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PriorityQueueFormData>({
    resolver: zodResolver(priorityQueueSchema),
    defaultValues: {
      delivery_id: initialData?.delivery_id || '',
      priority: initialData?.priority || 'standard',
      sla_deadline: initialData?.sla_deadline || '',
      courier_id: initialData?.courier_id || '',
      reason: initialData?.reason || '',
      notes: initialData?.notes || '',
    },
  })

  const onFormSubmit = async (data: PriorityQueueFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Priority Assignment"
        description="Set delivery priority and SLA"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Delivery ID" required error={errors.delivery_id?.message}>
            <Input
              {...register('delivery_id')}
              placeholder="DEL-123456"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Priority Level" required error={errors.priority?.message}>
            <Select
              {...register('priority')}
              options={[
                { value: 'express', label: 'Express (1-2 hours)' },
                { value: 'same_day', label: 'Same Day' },
                { value: 'standard', label: 'Standard (1-2 days)' },
                { value: 'deferred', label: 'Deferred (3+ days)' },
              ]}
            />
          </FormField>

          <FormField label="SLA Deadline" error={errors.sla_deadline?.message}>
            <Input
              type="datetime-local"
              {...register('sla_deadline')}
            />
          </FormField>

          <FormField label="Assign Courier" error={errors.courier_id?.message}>
            <Select
              {...register('courier_id')}
              options={[
                { value: '', label: 'Auto-assign' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Priority Reason"
        description="Explain why this delivery needs priority"
      >
        <FormField label="Reason" error={errors.reason?.message}>
          <Input
            {...register('reason')}
            placeholder="e.g., Customer request, VIP client, Perishable goods"
          />
        </FormField>

        <FormField label="Additional Notes" error={errors.notes?.message}>
          <Input
            {...register('notes')}
            placeholder="Any additional notes..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Set Priority' : 'Update Priority'}
        </Button>
      </FormActions>
    </Form>
  )
}
