import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface AssignmentFormData {
  courier_id: string
  vehicle_id: string
  assignment_type: 'permanent' | 'temporary' | 'shift_based'
  start_date: string
  end_date?: string
  shift?: 'morning' | 'evening' | 'night'
  notes?: string
  status: 'active' | 'completed' | 'cancelled'
}

export interface AssignmentFormProps {
  initialData?: Partial<AssignmentFormData>
  onSubmit: (data: AssignmentFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
  vehicles?: Array<{ id: string; plate_number: string }>
}

export const AssignmentForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
  vehicles = [],
}: AssignmentFormProps) => {
  const [formData, setFormData] = useState<AssignmentFormData>({
    courier_id: initialData?.courier_id || '',
    vehicle_id: initialData?.vehicle_id || '',
    assignment_type: initialData?.assignment_type || 'permanent',
    start_date: initialData?.start_date || '',
    end_date: initialData?.end_date || '',
    shift: initialData?.shift,
    notes: initialData?.notes || '',
    status: initialData?.status || 'active',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof AssignmentFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof AssignmentFormData, string>> = {}

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (!formData.vehicle_id) {
      newErrors.vehicle_id = 'Vehicle is required'
    }

    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required'
    }

    if (formData.end_date && formData.start_date) {
      const start = new Date(formData.start_date)
      const end = new Date(formData.end_date)
      if (end < start) {
        newErrors.end_date = 'End date must be after start date'
      }
    }

    if (formData.assignment_type === 'shift_based' && !formData.shift) {
      newErrors.shift = 'Shift is required for shift-based assignments'
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

  const handleChange = (field: keyof AssignmentFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Assignment Details"
        description="Assign a courier to a vehicle"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Courier" required error={errors.courier_id}>
            <Select
              value={formData.courier_id}
              onChange={(e) => handleChange('courier_id', e.target.value)}
              options={[
                { value: '', label: 'Select a courier...' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField label="Vehicle" required error={errors.vehicle_id}>
            <Select
              value={formData.vehicle_id}
              onChange={(e) => handleChange('vehicle_id', e.target.value)}
              options={[
                { value: '', label: 'Select a vehicle...' },
                ...vehicles.map((v) => ({ value: v.id, label: v.plate_number })),
              ]}
            />
          </FormField>

          <FormField label="Assignment Type" required>
            <Select
              value={formData.assignment_type}
              onChange={(e) => handleChange('assignment_type', e.target.value)}
              options={[
                { value: 'permanent', label: 'Permanent' },
                { value: 'temporary', label: 'Temporary' },
                { value: 'shift_based', label: 'Shift Based' },
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'active', label: 'Active' },
                { value: 'completed', label: 'Completed' },
                { value: 'cancelled', label: 'Cancelled' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Duration"
        description="Set the assignment period"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Start Date" required error={errors.start_date}>
            <Input
              type="date"
              value={formData.start_date}
              onChange={(e) => handleChange('start_date', e.target.value)}
            />
          </FormField>

          <FormField label="End Date" error={errors.end_date}>
            <Input
              type="date"
              value={formData.end_date}
              onChange={(e) => handleChange('end_date', e.target.value)}
            />
          </FormField>

          {formData.assignment_type === 'shift_based' && (
            <FormField label="Shift" required error={errors.shift}>
              <Select
                value={formData.shift || ''}
                onChange={(e) => handleChange('shift', e.target.value)}
                options={[
                  { value: '', label: 'Select a shift...' },
                  { value: 'morning', label: 'Morning (6AM - 2PM)' },
                  { value: 'evening', label: 'Evening (2PM - 10PM)' },
                  { value: 'night', label: 'Night (10PM - 6AM)' },
                ]}
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
            placeholder="Any special instructions or notes..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Assignment' : 'Update Assignment'}
        </Button>
      </FormActions>
    </Form>
  )
}
