import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { deliveryFormSchema, type DeliveryFormData } from '@/schemas/fleet.schema'

export type { DeliveryFormData }

export interface DeliveryFormProps {
  initialData?: Partial<DeliveryFormData>
  onSubmit: (data: DeliveryFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const DeliveryForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: DeliveryFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<DeliveryFormData>({
    resolver: zodResolver(deliveryFormSchema),
    defaultValues: {
      courier_id: initialData?.courier_id || '',
      tracking_number: initialData?.tracking_number || '',
      status: initialData?.status || 'pending',
      priority: initialData?.priority || 'normal',
      pickup_address: initialData?.pickup_address || '',
      delivery_address: initialData?.delivery_address || '',
      recipient_name: initialData?.recipient_name || '',
      recipient_phone: initialData?.recipient_phone || '',
      package_type: initialData?.package_type || '',
      weight: initialData?.weight || 0,
      dimensions: initialData?.dimensions || '',
      scheduled_date: initialData?.scheduled_date || '',
      delivered_date: initialData?.delivered_date || '',
      delivery_proof: initialData?.delivery_proof || '',
      notes: initialData?.notes || '',
    },
  })

  const status = watch('status')

  const onFormSubmit = async (data: DeliveryFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Delivery Information"
        description="Enter delivery details and tracking information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Tracking Number" required error={errors.tracking_number?.message}>
            <Input
              {...register('tracking_number')}
              placeholder="TRK-123456"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Courier">
            <Select
              {...register('courier_id')}
              options={[
                { value: '', label: 'Not assigned' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'assigned', label: 'Assigned' },
                { value: 'in_transit', label: 'In Transit' },
                { value: 'delivered', label: 'Delivered' },
                { value: 'failed', label: 'Failed' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
            />
          </FormField>

          <FormField label="Priority" required error={errors.priority?.message}>
            <Select
              {...register('priority')}
              options={[
                { value: 'low', label: 'Low' },
                { value: 'normal', label: 'Normal' },
                { value: 'high', label: 'High' },
                { value: 'urgent', label: 'Urgent' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Addresses"
        description="Pickup and delivery locations"
      >
        <div className="grid grid-cols-1 gap-4">
          <FormField label="Pickup Address" required error={errors.pickup_address?.message}>
            <Input
              {...register('pickup_address')}
              placeholder="123 Main St, Dubai, UAE"
            />
          </FormField>

          <FormField label="Delivery Address" required error={errors.delivery_address?.message}>
            <Input
              {...register('delivery_address')}
              placeholder="456 Park Ave, Abu Dhabi, UAE"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Recipient Information"
        description="Delivery recipient details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Recipient Name" required error={errors.recipient_name?.message}>
            <Input
              {...register('recipient_name')}
              placeholder="John Doe"
            />
          </FormField>

          <FormField label="Recipient Phone" required error={errors.recipient_phone?.message}>
            <Input
              type="tel"
              {...register('recipient_phone')}
              placeholder="+971 50 123 4567"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Package Details"
        description="Package type, weight, and dimensions"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Package Type" error={errors.package_type?.message}>
            <Input
              {...register('package_type')}
              placeholder="Box, Envelope, etc."
            />
          </FormField>

          <FormField label="Weight (kg)" error={errors.weight?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('weight', { valueAsNumber: true })}
              placeholder="2.5"
            />
          </FormField>

          <FormField label="Dimensions (LxWxH cm)" error={errors.dimensions?.message}>
            <Input
              {...register('dimensions')}
              placeholder="30x20x10"
            />
          </FormField>

          <FormField label="Scheduled Date" error={errors.scheduled_date?.message}>
            <Input
              type="date"
              {...register('scheduled_date')}
            />
          </FormField>

          {status === 'delivered' && (
            <FormField label="Delivered Date" error={errors.delivered_date?.message}>
              <Input
                type="date"
                {...register('delivered_date')}
              />
            </FormField>
          )}

          {status === 'delivered' && (
            <FormField label="Delivery Proof" error={errors.delivery_proof?.message}>
              <Input
                {...register('delivery_proof')}
                placeholder="Signature, Photo URL, etc."
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
            placeholder="Any special delivery instructions..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Delivery' : 'Update Delivery'}
        </Button>
      </FormActions>
    </Form>
  )
}
