import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { routeSchema, type RouteFormData } from '@/schemas/fleet.schema'

export type { RouteFormData }

export interface RouteFormProps {
  initialData?: Partial<RouteFormData>
  onSubmit: (data: RouteFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const RouteForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: RouteFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RouteFormData>({
    resolver: zodResolver(routeSchema),
    defaultValues: {
      name: initialData?.name || '',
      route_code: initialData?.route_code || '',
      start_point: initialData?.start_point || '',
      end_point: initialData?.end_point || '',
      waypoints: initialData?.waypoints || '',
      distance: initialData?.distance || 0,
      estimated_duration: initialData?.estimated_duration || 0,
      status: initialData?.status || 'active',
      route_type: initialData?.route_type || 'delivery',
      assigned_courier: initialData?.assigned_courier || '',
      service_days: initialData?.service_days || '',
      notes: initialData?.notes || '',
    },
  })

  const onFormSubmit = async (data: RouteFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Route Information"
        description="Define the route details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Route Name" required error={errors.name?.message}>
            <Input
              {...register('name')}
              placeholder="Downtown Delivery Route"
            />
          </FormField>

          <FormField label="Route Code" required error={errors.route_code?.message}>
            <Input
              {...register('route_code')}
              placeholder="RT-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Route Type" required error={errors.route_type?.message}>
            <Select
              {...register('route_type')}
              options={[
                { value: 'delivery', label: 'Delivery' },
                { value: 'pickup', label: 'Pickup' },
                { value: 'mixed', label: 'Mixed (Pickup & Delivery)' },
              ]}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
              options={[
                { value: 'active', label: 'Active' },
                { value: 'inactive', label: 'Inactive' },
                { value: 'under_review', label: 'Under Review' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Route Points"
        description="Start, end, and waypoints"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Start Point" required error={errors.start_point?.message}>
            <Input
              {...register('start_point')}
              placeholder="Main Warehouse, Dubai"
            />
          </FormField>

          <FormField label="End Point" required error={errors.end_point?.message}>
            <Input
              {...register('end_point')}
              placeholder="Central Station, Abu Dhabi"
            />
          </FormField>

          <FormField
            label="Waypoints"
            helperText="Comma-separated list of stops"
            error={errors.waypoints?.message}
          >
            <Input
              {...register('waypoints')}
              placeholder="Stop 1, Stop 2, Stop 3"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Route Metrics"
        description="Distance and duration estimates"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Distance (km)" required error={errors.distance?.message}>
            <Input
              type="number"
              step="0.1"
              {...register('distance', { valueAsNumber: true })}
              placeholder="25.5"
            />
          </FormField>

          <FormField label="Estimated Duration (minutes)" required error={errors.estimated_duration?.message}>
            <Input
              type="number"
              {...register('estimated_duration', { valueAsNumber: true })}
              placeholder="60"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Assignment & Schedule"
        description="Courier assignment and service days"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Assigned Courier" error={errors.assigned_courier?.message}>
            <Select
              {...register('assigned_courier')}
              options={[
                { value: '', label: 'Not assigned' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField
            label="Service Days"
            helperText="e.g., Mon-Fri, Daily, etc."
            error={errors.service_days?.message}
          >
            <Input
              {...register('service_days')}
              placeholder="Mon-Fri"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and special instructions"
      >
        <FormField label="Notes" error={errors.notes?.message}>
          <Input
            {...register('notes')}
            placeholder="Any special route instructions or notes..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Route' : 'Update Route'}
        </Button>
      </FormActions>
    </Form>
  )
}
