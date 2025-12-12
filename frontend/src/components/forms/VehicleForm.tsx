import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { vehicleSchema, VehicleFormData } from '@/schemas'

export interface VehicleFormProps {
  initialData?: Partial<VehicleFormData>
  onSubmit: (data: VehicleFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const VehicleForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: VehicleFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue,
  } = useForm<VehicleFormData>({
     
    resolver: zodResolver(vehicleSchema as any),
    defaultValues: {
      plate_number: initialData?.plate_number || '',
      type: initialData?.type || 'sedan',
      make: initialData?.make || '',
      model: initialData?.model || '',
      year: initialData?.year || new Date().getFullYear(),
      color: initialData?.color || '',
      fuel_type: initialData?.fuel_type || 'gasoline',
      ownership: initialData?.ownership || 'owned',
      status: initialData?.status || 'available',
      purchase_date: initialData?.purchase_date || '',
      registration_expiry: initialData?.registration_expiry || '',
      insurance_expiry: initialData?.insurance_expiry || '',
      mileage: initialData?.mileage || undefined,
      vin: initialData?.vin || '',
      gps_device_id: initialData?.gps_device_id || '',
      assigned_to_city: initialData?.assigned_to_city || '',
    },
    mode: 'onBlur',
  })

  const loading = isLoading || isSubmitting

  const onFormSubmit = async (data: VehicleFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Vehicle Information"
        description="Enter the vehicle's basic details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Plate Number" required error={errors.plate_number?.message}>
            <Input
              {...register('plate_number')}
              placeholder="ABC-1234"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Type" required error={errors.type?.message}>
            <Select
              value={watch('type')}
              onChange={(e) => setValue('type', e.target.value as VehicleFormData['type'], { shouldValidate: true })}
              options={[
                { value: 'sedan', label: 'Sedan' },
                { value: 'van', label: 'Van' },
                { value: 'truck', label: 'Truck' },
                { value: 'motorcycle', label: 'Motorcycle' },
                { value: 'bicycle', label: 'Bicycle' },
              ]}
            />
          </FormField>

          <FormField label="Make" required error={errors.make?.message}>
            <Input
              {...register('make')}
              placeholder="Toyota"
            />
          </FormField>

          <FormField label="Model" required error={errors.model?.message}>
            <Input
              {...register('model')}
              placeholder="Camry"
            />
          </FormField>

          <FormField label="Year" required error={errors.year?.message}>
            <Input
              type="number"
              {...register('year', { valueAsNumber: true })}
              placeholder="2023"
            />
          </FormField>

          <FormField label="Color" error={errors.color?.message}>
            <Input
              {...register('color')}
              placeholder="White"
            />
          </FormField>

          <FormField label="VIN" error={errors.vin?.message}>
            <Input
              {...register('vin')}
              placeholder="1HGBH41JXMN109186"
            />
          </FormField>

          <FormField label="Mileage" error={errors.mileage?.message}>
            <Input
              type="number"
              {...register('mileage', { valueAsNumber: true })}
              placeholder="50000"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Operational Details"
        description="Fuel type, ownership, and status"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Fuel Type" required error={errors.fuel_type?.message}>
            <Select
              value={watch('fuel_type')}
              onChange={(e) => setValue('fuel_type', e.target.value as VehicleFormData['fuel_type'], { shouldValidate: true })}
              options={[
                { value: 'gasoline', label: 'Gasoline' },
                { value: 'diesel', label: 'Diesel' },
                { value: 'electric', label: 'Electric' },
                { value: 'hybrid', label: 'Hybrid' },
              ]}
            />
          </FormField>

          <FormField label="Ownership" required error={errors.ownership?.message}>
            <Select
              value={watch('ownership')}
              onChange={(e) => setValue('ownership', e.target.value as VehicleFormData['ownership'], { shouldValidate: true })}
              options={[
                { value: 'owned', label: 'Owned' },
                { value: 'leased', label: 'Leased' },
                { value: 'rented', label: 'Rented' },
              ]}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              value={watch('status') || 'available'}
              onChange={(e) => setValue('status', e.target.value as VehicleFormData['status'], { shouldValidate: true })}
              options={[
                { value: 'available', label: 'Available' },
                { value: 'in_use', label: 'In Use' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'retired', label: 'Retired' },
              ]}
            />
          </FormField>

          <FormField label="Purchase Date" error={errors.purchase_date?.message}>
            <Input
              type="date"
              {...register('purchase_date')}
            />
          </FormField>

          <FormField label="GPS Device ID" error={errors.gps_device_id?.message}>
            <Input
              {...register('gps_device_id')}
              placeholder="GPS-001"
            />
          </FormField>

          <FormField label="Assigned City" error={errors.assigned_to_city?.message}>
            <Input
              {...register('assigned_to_city')}
              placeholder="Dubai"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Registration & Maintenance"
        description="Important dates and maintenance records"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Registration Expiry" error={errors.registration_expiry?.message}>
            <Input
              type="date"
              {...register('registration_expiry')}
            />
          </FormField>

          <FormField label="Insurance Expiry" error={errors.insurance_expiry?.message}>
            <Input
              type="date"
              {...register('insurance_expiry')}
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : mode === 'create' ? 'Create Vehicle' : 'Update Vehicle'}
        </Button>
      </FormActions>
    </Form>
  )
}

// Re-export for backwards compatibility
export type { VehicleFormData } from '@/schemas'
