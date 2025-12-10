import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { trackingUpdateSchema, type TrackingUpdateFormData } from '@/schemas/fleet.schema'

export type { TrackingUpdateFormData }

export interface TrackingFormProps {
  initialData?: Partial<TrackingUpdateFormData>
  onSubmit: (data: TrackingUpdateFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const TrackingForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: TrackingFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<TrackingUpdateFormData>({
    resolver: zodResolver(trackingUpdateSchema),
    defaultValues: {
      delivery_id: initialData?.delivery_id || '',
      status: initialData?.status || 'pending',
      location: initialData?.location || '',
      latitude: initialData?.latitude,
      longitude: initialData?.longitude,
      notes: initialData?.notes || '',
      photo_url: initialData?.photo_url || '',
      signature_url: initialData?.signature_url || '',
      failure_reason: initialData?.failure_reason || '',
      recipient_name: initialData?.recipient_name || '',
    },
  })

  const status = watch('status')

  const onFormSubmit = async (data: TrackingUpdateFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Tracking Update"
        description="Update delivery tracking status"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Delivery ID" required error={errors.delivery_id?.message}>
            <Input
              {...register('delivery_id')}
              placeholder="DEL-123456"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'assigned', label: 'Assigned' },
                { value: 'picked_up', label: 'Picked Up' },
                { value: 'in_transit', label: 'In Transit' },
                { value: 'out_for_delivery', label: 'Out for Delivery' },
                { value: 'delivered', label: 'Delivered' },
                { value: 'failed', label: 'Failed' },
                { value: 'returned', label: 'Returned' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Location"
        description="Current delivery location"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Location Description" error={errors.location?.message}>
            <Input
              {...register('location')}
              placeholder="e.g., At warehouse, En route to customer"
            />
          </FormField>

          <div className="col-span-1 md:col-span-2">
            <div className="grid grid-cols-2 gap-4">
              <FormField label="Latitude" error={errors.latitude?.message}>
                <Input
                  type="number"
                  step="0.000001"
                  {...register('latitude', { valueAsNumber: true })}
                  placeholder="24.7136"
                />
              </FormField>

              <FormField label="Longitude" error={errors.longitude?.message}>
                <Input
                  type="number"
                  step="0.000001"
                  {...register('longitude', { valueAsNumber: true })}
                  placeholder="46.6753"
                />
              </FormField>
            </div>
          </div>
        </div>
      </FormSection>

      {status === 'delivered' && (
        <FormSection
          title="Delivery Confirmation"
          description="Proof of delivery information"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="Recipient Name" error={errors.recipient_name?.message}>
              <Input
                {...register('recipient_name')}
                placeholder="Name of person who received the package"
              />
            </FormField>

            <FormField label="Signature URL" error={errors.signature_url?.message}>
              <Input
                {...register('signature_url')}
                placeholder="https://..."
              />
            </FormField>

            <FormField label="Photo URL" error={errors.photo_url?.message}>
              <Input
                {...register('photo_url')}
                placeholder="https://..."
              />
            </FormField>
          </div>
        </FormSection>
      )}

      {status === 'failed' && (
        <FormSection
          title="Failure Details"
          description="Reason for delivery failure"
        >
          <FormField label="Failure Reason" error={errors.failure_reason?.message}>
            <Input
              {...register('failure_reason')}
              placeholder="e.g., Customer not available, Wrong address"
            />
          </FormField>
        </FormSection>
      )}

      <FormSection
        title="Additional Notes"
        description="Any other relevant information"
      >
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
            placeholder="Additional tracking notes..."
            rows={3}
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Add Update' : 'Update Tracking'}
        </Button>
      </FormActions>
    </Form>
  )
}
