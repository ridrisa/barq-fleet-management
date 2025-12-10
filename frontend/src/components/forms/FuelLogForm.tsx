import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { fuelLogSchema, type FuelLogFormData } from '@/schemas/fleet.schema'

export type { FuelLogFormData }

export interface FuelLogFormProps {
  initialData?: Partial<FuelLogFormData>
  onSubmit: (data: FuelLogFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  vehicles?: Array<{ id: number; plate_number: string }>
}

export const FuelLogForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  vehicles = [],
}: FuelLogFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FuelLogFormData>({
    resolver: zodResolver(fuelLogSchema),
    defaultValues: {
      vehicle_id: initialData?.vehicle_id || '',
      date: initialData?.date || new Date().toISOString().split('T')[0],
      fuel_type: initialData?.fuel_type || 'petrol',
      liters: initialData?.liters || 0,
      cost: initialData?.cost || 0,
      odometer: initialData?.odometer || 0,
      station: initialData?.station || '',
      notes: initialData?.notes || '',
    },
  })

  const onFormSubmit = async (data: FuelLogFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Fuel Log Details"
        description="Enter fuel consumption information"
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

          <FormField label="Date" required error={errors.date?.message}>
            <Input
              type="date"
              {...register('date')}
            />
          </FormField>

          <FormField label="Fuel Type" required error={errors.fuel_type?.message}>
            <Select
              {...register('fuel_type')}
              options={[
                { value: 'petrol', label: 'Petrol' },
                { value: 'diesel', label: 'Diesel' },
                { value: 'electric', label: 'Electric' },
              ]}
            />
          </FormField>

          <FormField label="Liters" required error={errors.liters?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('liters', { valueAsNumber: true })}
              placeholder="45.5"
            />
          </FormField>

          <FormField label="Cost (SAR)" required error={errors.cost?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('cost', { valueAsNumber: true })}
              placeholder="180.00"
            />
          </FormField>

          <FormField label="Odometer (km)" required error={errors.odometer?.message}>
            <Input
              type="number"
              {...register('odometer', { valueAsNumber: true })}
              placeholder="45250"
            />
          </FormField>

          <FormField label="Station" error={errors.station?.message}>
            <Input
              {...register('station')}
              placeholder="ADNOC Station, Dubai"
            />
          </FormField>

          <FormField label="Notes" error={errors.notes?.message}>
            <Input
              {...register('notes')}
              placeholder="Additional notes"
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Add Fuel Log' : 'Update Fuel Log'}
        </Button>
      </FormActions>
    </Form>
  )
}
