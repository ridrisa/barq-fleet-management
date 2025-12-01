import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea';
import { Form, FormField, FormSection, FormActions } from './Form'

export interface MaintenanceFormData {
  vehicle_id: number | string
  maintenance_type: string
  scheduled_date: string
  completed_date?: string
  status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled'
  cost?: number | string
  service_provider?: string
  description?: string
  notes?: string
}

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
  const [formData, setFormData] = useState<MaintenanceFormData>({
    vehicle_id: initialData?.vehicle_id || '',
    maintenance_type: initialData?.maintenance_type || 'oil_change',
    scheduled_date: initialData?.scheduled_date || '',
    completed_date: initialData?.completed_date || '',
    status: initialData?.status || 'scheduled',
    cost: initialData?.cost || '',
    service_provider: initialData?.service_provider || '',
    description: initialData?.description || '',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof MaintenanceFormData, string>>>({})

  // Basic validation
  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof MaintenanceFormData, string>> = {}

    if (!formData.vehicle_id) {
      newErrors.vehicle_id = 'Vehicle is required'
    }

    if (!formData.scheduled_date) {
      newErrors.scheduled_date = 'Scheduled date is required'
    }

    if (formData.status === 'completed' && !formData.completed_date) {
      newErrors.completed_date = 'Completed date is required when status is completed'
    }

    if (formData.cost && Number(formData.cost) < 0) {
      newErrors.cost = 'Cost cannot be negative'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    // Convert string values to numbers where needed
    const submitData: MaintenanceFormData = {
      ...formData,
      vehicle_id: Number(formData.vehicle_id),
      cost: formData.cost ? Number(formData.cost) : undefined,
    }

    await onSubmit(submitData)
  }

  const handleChange = (field: keyof MaintenanceFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Maintenance Details"
        description="Enter vehicle maintenance information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Vehicle" required error={errors.vehicle_id}>
            <Select
              value={String(formData.vehicle_id)}
              onChange={(e) => handleChange('vehicle_id', e.target.value)}
              options={[
                { value: '', label: 'Select Vehicle' },
                ...vehicles.map((v) => ({
                  value: String(v.id),
                  label: v.plate_number,
                })),
              ]}
            />
          </FormField>

          <FormField label="Maintenance Type" required>
            <Select
              value={formData.maintenance_type}
              onChange={(e) => handleChange('maintenance_type', e.target.value)}
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

          <FormField label="Scheduled Date" required error={errors.scheduled_date}>
            <Input
              type="date"
              value={formData.scheduled_date}
              onChange={(e) => handleChange('scheduled_date', e.target.value)}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'scheduled', label: 'Scheduled' },
                { value: 'in_progress', label: 'In Progress' },
                { value: 'completed', label: 'Completed' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
            />
          </FormField>

          {formData.status === 'completed' && (
            <FormField label="Completed Date" required={formData.status === 'completed'} error={errors.completed_date}>
              <Input
                type="date"
                value={formData.completed_date}
                onChange={(e) => handleChange('completed_date', e.target.value)}
              />
            </FormField>
          )}

          <FormField label="Cost (SAR)" error={errors.cost}>
            <Input
              type="number"
              step="0.01"
              value={formData.cost}
              onChange={(e) => handleChange('cost', e.target.value)}
              placeholder="250.00"
            />
          </FormField>

          <FormField label="Service Provider">
            <Input
              value={formData.service_provider}
              onChange={(e) => handleChange('service_provider', e.target.value)}
              placeholder="ABC Auto Service"
            />
          </FormField>
        </div>

        <div className="mt-4">
          <FormField label="Description">
            <Textarea
              value={formData.description}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleChange('description', e.target.value)}
              placeholder="Detailed description of maintenance work"
              rows={3}
            />
          </FormField>

          <FormField label="Notes">
            <Textarea
              value={formData.notes}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleChange('notes', e.target.value)}
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
