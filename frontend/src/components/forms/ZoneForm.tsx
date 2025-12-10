import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { zoneSchema, type ZoneFormData } from '@/schemas/fleet.schema'

export type { ZoneFormData }

export interface ZoneFormProps {
  initialData?: Partial<ZoneFormData>
  onSubmit: (data: ZoneFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const ZoneForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: ZoneFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ZoneFormData>({
    resolver: zodResolver(zoneSchema),
    defaultValues: {
      zone_name: initialData?.zone_name || '',
      zone_code: initialData?.zone_code || '',
      areas: initialData?.areas || '',
      coverage_radius: initialData?.coverage_radius,
      assigned_couriers: initialData?.assigned_couriers || 0,
      max_capacity: initialData?.max_capacity || 100,
      status: initialData?.status || 'active',
      notes: initialData?.notes || '',
    },
  })

  const onFormSubmit = async (data: ZoneFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Zone Information"
        description="Define the delivery zone details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Zone Name" required error={errors.zone_name?.message}>
            <Input
              {...register('zone_name')}
              placeholder="Downtown Zone"
            />
          </FormField>

          <FormField label="Zone Code" required error={errors.zone_code?.message}>
            <Input
              {...register('zone_code')}
              placeholder="ZONE-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
              options={[
                { value: 'active', label: 'Active' },
                { value: 'inactive', label: 'Inactive' },
                { value: 'full', label: 'Full (At Capacity)' },
              ]}
            />
          </FormField>

          <FormField label="Coverage Radius (km)" error={errors.coverage_radius?.message}>
            <Input
              type="number"
              step="0.1"
              {...register('coverage_radius', { valueAsNumber: true })}
              placeholder="5.0"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Capacity"
        description="Zone capacity and courier assignments"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Assigned Couriers" error={errors.assigned_couriers?.message}>
            <Input
              type="number"
              {...register('assigned_couriers', { valueAsNumber: true })}
              placeholder="0"
            />
          </FormField>

          <FormField label="Max Capacity" error={errors.max_capacity?.message}>
            <Input
              type="number"
              {...register('max_capacity', { valueAsNumber: true })}
              placeholder="100"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Coverage Areas"
        description="List of areas covered by this zone"
      >
        <FormField
          label="Areas"
          helperText="Comma-separated list of neighborhoods or areas"
          error={errors.areas?.message}
        >
          <Textarea
            {...register('areas')}
            placeholder="Al Olaya, Al Malaz, Al Wurud, King Fahd District"
            rows={3}
          />
        </FormField>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and special instructions"
      >
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
            placeholder="Any special zone notes or instructions..."
            rows={3}
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Zone' : 'Update Zone'}
        </Button>
      </FormActions>
    </Form>
  )
}
