import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { maintenanceFormSchema, type MaintenanceFormData } from '@/schemas/fleet.schema'

export type { MaintenanceFormData }

export interface MaintenanceFormProps {
  initialData?: Partial<MaintenanceFormData>
  onSubmit: (data: MaintenanceFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  vehicles?: Array<{ id: number; plate_number: string }>
}

export const MaintenanceForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  vehicles = [],
}: MaintenanceFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<MaintenanceFormData>({
    resolver: zodResolver(maintenanceFormSchema),
    defaultValues: {
      vehicle_id: initialData?.vehicle_id || '',
      maintenance_type: initialData?.maintenance_type || 'oil_change',
      scheduled_date: initialData?.scheduled_date || '',
      completed_date: initialData?.completed_date || '',
      status: initialData?.status || 'scheduled',
      cost: initialData?.cost,
      service_provider: initialData?.service_provider || '',
      description: initialData?.description || '',
      notes: initialData?.notes || '',
    },
  })

  const status = watch('status')

  const onFormSubmit = async (data: MaintenanceFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Maintenance Details"
        description="Enter vehicle maintenance information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Vehicle" required error={errors.vehicle_id?.message}>
            <Select
              {...register('vehicle_id')}
              options={[
                { value: '', label: 'Select Vehicle' },
                ...vehicles.map((v) => ({
                  value: String(v.id),
                  label: v.plate_number,
                })),
              ]}
            />
          </FormField>

          <FormField label="Maintenance Type" required error={errors.maintenance_type?.message}>
            <Select
              {...register('maintenance_type')}
              options={[
                { value: 'oil_change', label: 'Oil Change' },
                { value: 'tire_replacement', label: 'Tire Replacement' },
                { value: 'brake_service', label: 'Brake Service' },
                { value: 'battery_replacement', label: 'Battery Replacement' },
                { value: 'inspection', label: 'Inspection' },
                { value: 'general_repair', label: 'General Repair' },
                { value: 'ac_service', label: 'AC Service' },
                { value: 'transmission', label: 'Transmission Service' },
                { value: 'other', label: 'Other' },
              ]}
            />
          </FormField>

          <FormField label="Scheduled Date" required error={errors.scheduled_date?.message}>
            <Input
              type="date"
              {...register('scheduled_date')}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
              options={[
                { value: 'scheduled', label: 'Scheduled' },
                { value: 'in_progress', label: 'In Progress' },
                { value: 'completed', label: 'Completed' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
            />
          </FormField>

          {status === 'completed' && (
            <FormField label="Completed Date" required error={errors.completed_date?.message}>
              <Input
                type="date"
                {...register('completed_date')}
              />
            </FormField>
          )}

          <FormField label="Cost (SAR)" error={errors.cost?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('cost', { valueAsNumber: true })}
              placeholder="250.00"
            />
          </FormField>

          <FormField label="Service Provider" error={errors.service_provider?.message}>
            <Input
              {...register('service_provider')}
              placeholder="ABC Auto Service"
            />
          </FormField>
        </div>

        <div className="mt-4">
          <FormField label="Description" error={errors.description?.message}>
            <Textarea
              {...register('description')}
              placeholder="Detailed description of maintenance work"
              rows={3}
            />
          </FormField>

          <FormField label="Notes" error={errors.notes?.message}>
            <Textarea
              {...register('notes')}
              placeholder="Additional notes"
              rows={2}
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Schedule Maintenance' : 'Update Maintenance'}
        </Button>
      </FormActions>
    </Form>
  )
}
