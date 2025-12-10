import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { buildingFormSchema, type BuildingFormData } from '@/schemas/admin.schema'

export type { BuildingFormData }

export interface BuildingFormProps {
  initialData?: Partial<BuildingFormData>
  onSubmit: (data: BuildingFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const BuildingForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: BuildingFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<BuildingFormData>({
    resolver: zodResolver(buildingFormSchema),
    defaultValues: {
      name: initialData?.name || '',
      building_code: initialData?.building_code || '',
      address: initialData?.address || '',
      city: initialData?.city || '',
      country: initialData?.country || 'UAE',
      capacity: initialData?.capacity || 0,
      floors: initialData?.floors || 1,
      total_rooms: initialData?.total_rooms || 0,
      amenities: initialData?.amenities || '',
      manager: initialData?.manager || '',
      manager_contact: initialData?.manager_contact || '',
      status: initialData?.status || 'active',
      construction_year: initialData?.construction_year || new Date().getFullYear(),
      monthly_rent: initialData?.monthly_rent || 0,
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const formIsLoading = isLoading || isSubmitting

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <FormSection
        title="Building Information"
        description="Enter building details and location"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Building Name" required error={errors.name?.message}>
            <Input
              {...register('name')}
              placeholder="Main Staff Housing"
            />
          </FormField>

          <FormField label="Building Code" required error={errors.building_code?.message}>
            <Input
              {...register('building_code')}
              placeholder="BLD-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              {...register('status')}
              options={[
                { value: 'active', label: 'Active' },
                { value: 'under_construction', label: 'Under Construction' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'closed', label: 'Closed' },
              ]}
            />
          </FormField>

          <FormField label="Construction Year">
            <Input
              type="number"
              {...register('construction_year', { valueAsNumber: true })}
              placeholder="2020"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Location"
        description="Building address and location details"
      >
        <div className="grid grid-cols-1 gap-4">
          <FormField label="Address" required error={errors.address?.message}>
            <Input
              {...register('address')}
              placeholder="123 Main Street"
            />
          </FormField>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="City" required error={errors.city?.message}>
              <Input
                {...register('city')}
                placeholder="Dubai"
              />
            </FormField>

            <FormField label="Country" required>
              <Input
                {...register('country')}
                placeholder="UAE"
              />
            </FormField>
          </div>
        </div>
      </FormSection>

      <FormSection
        title="Capacity & Layout"
        description="Building capacity and structure"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Total Capacity" required error={errors.capacity?.message}>
            <Input
              type="number"
              {...register('capacity', { valueAsNumber: true })}
              placeholder="100"
            />
          </FormField>

          <FormField label="Number of Floors" required error={errors.floors?.message}>
            <Input
              type="number"
              {...register('floors', { valueAsNumber: true })}
              placeholder="5"
            />
          </FormField>

          <FormField label="Total Rooms">
            <Input
              type="number"
              {...register('total_rooms', { valueAsNumber: true })}
              placeholder="50"
            />
          </FormField>

          <FormField label="Monthly Rent">
            <Input
              type="number"
              step="0.01"
              {...register('monthly_rent', { valueAsNumber: true })}
              placeholder="50000.00"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Amenities & Management"
        description="Available amenities and manager information"
      >
        <FormField
          label="Amenities"
          helperText="Comma-separated list (e.g., WiFi, Parking, Gym)"
        >
          <Input
            {...register('amenities')}
            placeholder="WiFi, Parking, Gym, Laundry"
          />
        </FormField>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Building Manager" required error={errors.manager?.message}>
            <Input
              {...register('manager')}
              placeholder="Manager name"
            />
          </FormField>

          <FormField label="Manager Contact" required error={errors.manager_contact?.message}>
            <Input
              type="tel"
              {...register('manager_contact')}
              placeholder="+971 50 123 4567"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and comments"
      >
        <FormField label="Notes">
          <Input
            {...register('notes')}
            placeholder="Any additional notes about this building..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={formIsLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={formIsLoading}>
          {formIsLoading ? 'Saving...' : mode === 'create' ? 'Create Building' : 'Update Building'}
        </Button>
      </FormActions>
    </Form>
  )
}
