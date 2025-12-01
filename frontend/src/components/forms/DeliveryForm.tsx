import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface DeliveryFormData {
  courier_id: string
  tracking_number: string
  status: 'pending' | 'assigned' | 'in_transit' | 'delivered' | 'failed' | 'cancelled'
  priority: 'low' | 'normal' | 'high' | 'urgent'
  pickup_address: string
  delivery_address: string
  recipient_name: string
  recipient_phone: string
  package_type?: string
  weight?: number
  dimensions?: string
  scheduled_date?: string
  delivered_date?: string
  delivery_proof?: string
  notes?: string
}

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
  const [formData, setFormData] = useState<DeliveryFormData>({
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
  })

  const [errors, setErrors] = useState<Partial<Record<keyof DeliveryFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof DeliveryFormData, string>> = {}

    if (!formData.tracking_number.trim()) {
      newErrors.tracking_number = 'Tracking number is required'
    }

    if (!formData.pickup_address.trim()) {
      newErrors.pickup_address = 'Pickup address is required'
    }

    if (!formData.delivery_address.trim()) {
      newErrors.delivery_address = 'Delivery address is required'
    }

    if (!formData.recipient_name.trim()) {
      newErrors.recipient_name = 'Recipient name is required'
    }

    if (!formData.recipient_phone.trim()) {
      newErrors.recipient_phone = 'Recipient phone is required'
    } else if (!/^\+?[\d\s-()]+$/.test(formData.recipient_phone)) {
      newErrors.recipient_phone = 'Invalid phone number format'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    await onSubmit(formData)
  }

  const handleChange = (field: keyof DeliveryFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Delivery Information"
        description="Enter delivery details and tracking information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Tracking Number" required error={errors.tracking_number}>
            <Input
              value={formData.tracking_number}
              onChange={(e) => handleChange('tracking_number', e.target.value)}
              placeholder="TRK-123456"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Courier">
            <Select
              value={formData.courier_id}
              onChange={(e) => handleChange('courier_id', e.target.value)}
              options={[
                { value: '', label: 'Not assigned' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
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

          <FormField label="Priority" required>
            <Select
              value={formData.priority}
              onChange={(e) => handleChange('priority', e.target.value)}
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
          <FormField label="Pickup Address" required error={errors.pickup_address}>
            <Input
              value={formData.pickup_address}
              onChange={(e) => handleChange('pickup_address', e.target.value)}
              placeholder="123 Main St, Dubai, UAE"
            />
          </FormField>

          <FormField label="Delivery Address" required error={errors.delivery_address}>
            <Input
              value={formData.delivery_address}
              onChange={(e) => handleChange('delivery_address', e.target.value)}
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
          <FormField label="Recipient Name" required error={errors.recipient_name}>
            <Input
              value={formData.recipient_name}
              onChange={(e) => handleChange('recipient_name', e.target.value)}
              placeholder="John Doe"
            />
          </FormField>

          <FormField label="Recipient Phone" required error={errors.recipient_phone}>
            <Input
              type="tel"
              value={formData.recipient_phone}
              onChange={(e) => handleChange('recipient_phone', e.target.value)}
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
          <FormField label="Package Type">
            <Input
              value={formData.package_type}
              onChange={(e) => handleChange('package_type', e.target.value)}
              placeholder="Box, Envelope, etc."
            />
          </FormField>

          <FormField label="Weight (kg)">
            <Input
              type="number"
              step="0.01"
              value={formData.weight}
              onChange={(e) => handleChange('weight', parseFloat(e.target.value))}
              placeholder="2.5"
            />
          </FormField>

          <FormField label="Dimensions (LxWxH cm)">
            <Input
              value={formData.dimensions}
              onChange={(e) => handleChange('dimensions', e.target.value)}
              placeholder="30x20x10"
            />
          </FormField>

          <FormField label="Scheduled Date">
            <Input
              type="date"
              value={formData.scheduled_date}
              onChange={(e) => handleChange('scheduled_date', e.target.value)}
            />
          </FormField>

          {formData.status === 'delivered' && (
            <FormField label="Delivered Date">
              <Input
                type="date"
                value={formData.delivered_date}
                onChange={(e) => handleChange('delivered_date', e.target.value)}
              />
            </FormField>
          )}

          {formData.status === 'delivered' && (
            <FormField label="Delivery Proof">
              <Input
                value={formData.delivery_proof}
                onChange={(e) => handleChange('delivery_proof', e.target.value)}
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
        <FormField label="Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
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
