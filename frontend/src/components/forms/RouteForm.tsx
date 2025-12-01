import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface RouteFormData {
  name: string
  route_code: string
  start_point: string
  end_point: string
  waypoints?: string
  distance: number
  estimated_duration: number
  status: 'active' | 'inactive' | 'under_review'
  route_type: 'delivery' | 'pickup' | 'mixed'
  assigned_courier?: string
  service_days?: string
  notes?: string
}

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
  const [formData, setFormData] = useState<RouteFormData>({
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
  })

  const [errors, setErrors] = useState<Partial<Record<keyof RouteFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof RouteFormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Route name is required'
    }

    if (!formData.route_code.trim()) {
      newErrors.route_code = 'Route code is required'
    }

    if (!formData.start_point.trim()) {
      newErrors.start_point = 'Start point is required'
    }

    if (!formData.end_point.trim()) {
      newErrors.end_point = 'End point is required'
    }

    if (formData.distance <= 0) {
      newErrors.distance = 'Distance must be greater than zero'
    }

    if (formData.estimated_duration <= 0) {
      newErrors.estimated_duration = 'Estimated duration must be greater than zero'
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

  const handleChange = (field: keyof RouteFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Route Information"
        description="Define the route details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Route Name" required error={errors.name}>
            <Input
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Downtown Delivery Route"
            />
          </FormField>

          <FormField label="Route Code" required error={errors.route_code}>
            <Input
              value={formData.route_code}
              onChange={(e) => handleChange('route_code', e.target.value)}
              placeholder="RT-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Route Type" required>
            <Select
              value={formData.route_type}
              onChange={(e) => handleChange('route_type', e.target.value)}
              options={[
                { value: 'delivery', label: 'Delivery' },
                { value: 'pickup', label: 'Pickup' },
                { value: 'mixed', label: 'Mixed (Pickup & Delivery)' },
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
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
          <FormField label="Start Point" required error={errors.start_point}>
            <Input
              value={formData.start_point}
              onChange={(e) => handleChange('start_point', e.target.value)}
              placeholder="Main Warehouse, Dubai"
            />
          </FormField>

          <FormField label="End Point" required error={errors.end_point}>
            <Input
              value={formData.end_point}
              onChange={(e) => handleChange('end_point', e.target.value)}
              placeholder="Central Station, Abu Dhabi"
            />
          </FormField>

          <FormField
            label="Waypoints"
            helperText="Comma-separated list of stops"
          >
            <Input
              value={formData.waypoints}
              onChange={(e) => handleChange('waypoints', e.target.value)}
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
          <FormField label="Distance (km)" required error={errors.distance}>
            <Input
              type="number"
              step="0.1"
              value={formData.distance}
              onChange={(e) => handleChange('distance', parseFloat(e.target.value))}
              placeholder="25.5"
            />
          </FormField>

          <FormField label="Estimated Duration (minutes)" required error={errors.estimated_duration}>
            <Input
              type="number"
              value={formData.estimated_duration}
              onChange={(e) => handleChange('estimated_duration', parseInt(e.target.value))}
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
          <FormField label="Assigned Courier">
            <Select
              value={formData.assigned_courier}
              onChange={(e) => handleChange('assigned_courier', e.target.value)}
              options={[
                { value: '', label: 'Not assigned' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField
            label="Service Days"
            helperText="e.g., Mon-Fri, Daily, etc."
          >
            <Input
              value={formData.service_days}
              onChange={(e) => handleChange('service_days', e.target.value)}
              placeholder="Mon-Fri"
            />
          </FormField>
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
