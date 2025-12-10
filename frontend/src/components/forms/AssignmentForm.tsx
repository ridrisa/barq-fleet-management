import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { assignmentSchema, type AssignmentFormData } from '@/schemas/fleet.schema'

export type { AssignmentFormData }

export interface AssignmentFormProps {
  initialData?: Partial<AssignmentFormData>
  onSubmit: (data: AssignmentFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
  vehicles?: Array<{ id: string; plate_number: string }>
}

export const AssignmentForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
  vehicles = [],
}: AssignmentFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AssignmentFormData>({
    resolver: zodResolver(assignmentSchema),
    defaultValues: {
      courier_id: initialData?.courier_id || '',
      vehicle_id: initialData?.vehicle_id || '',
      assignment_type: initialData?.assignment_type || 'permanent',
      start_date: initialData?.start_date || '',
      end_date: initialData?.end_date || '',
      shift: initialData?.shift,
      notes: initialData?.notes || '',
      status: initialData?.status || 'active',
    },
  })

  const assignmentType = watch('assignment_type')

  const onFormSubmit = async (data: AssignmentFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Assignment Details"
        description="Assign a courier to a vehicle"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Courier" required error={errors.courier_id?.message}>
            <Select
              {...register('courier_id')}
              options={[
                { value: '', label: 'Select a courier...' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField label="Vehicle" required error={errors.vehicle_id?.message}>
            <Select
              {...register('vehicle_id')}
              options={[
                { value: '', label: 'Select a vehicle...' },
                ...vehicles.map((v) => ({ value: v.id, label: v.plate_number })),
              ]}
            />
          </FormField>

          <FormField label="Assignment Type" required error={errors.assignment_type?.message}>
            <Select
              {...register('assignment_type')}
              options={[
                { value: 'permanent', label: 'Permanent' },
                { value: 'temporary', label: 'Temporary' },
                { value: 'shift_based', label: 'Shift Based' },
              ]}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
              options={[
                { value: 'active', label: 'Active' },
                { value: 'completed', label: 'Completed' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Duration"
        description="Set the assignment period"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Start Date" required error={errors.start_date?.message}>
            <Input
              type="date"
              {...register('start_date')}
            />
          </FormField>

          <FormField label="End Date" error={errors.end_date?.message}>
            <Input
              type="date"
              {...register('end_date')}
            />
          </FormField>

          {assignmentType === 'shift_based' && (
            <FormField label="Shift" required error={errors.shift?.message}>
              <Select
                {...register('shift')}
                options={[
                  { value: '', label: 'Select a shift...' },
                  { value: 'morning', label: 'Morning (6AM - 2PM)' },
                  { value: 'evening', label: 'Evening (2PM - 10PM)' },
                  { value: 'night', label: 'Night (10PM - 6AM)' },
                ]}
              />
            </FormField>
          )}
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and special instructions"
      >
        <FormField label="Notes" error={errors.notes?.message}>
          <Input
            {...register('notes')}
            placeholder="Any special instructions or notes..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Assignment' : 'Update Assignment'}
        </Button>
      </FormActions>
    </Form>
  )
}
