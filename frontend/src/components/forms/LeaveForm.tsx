import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface LeaveFormData {
  courier_id: string
  leave_type: 'annual' | 'sick' | 'emergency' | 'unpaid'
  start_date: string
  end_date: string
  days: number
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  approved_by?: string
  notes?: string
}

export interface LeaveFormProps {
  initialData?: Partial<LeaveFormData>
  onSubmit: (data: LeaveFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const LeaveForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: LeaveFormProps) => {
  const [formData, setFormData] = useState<LeaveFormData>({
    courier_id: initialData?.courier_id || '',
    leave_type: initialData?.leave_type || 'annual',
    start_date: initialData?.start_date || '',
    end_date: initialData?.end_date || '',
    days: initialData?.days || 1,
    reason: initialData?.reason || '',
    status: initialData?.status || 'pending',
    approved_by: initialData?.approved_by || '',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof LeaveFormData, string>>>({})

  const calculateDays = (start: string, end: string): number => {
    if (!start || !end) return 0
    const startDate = new Date(start)
    const endDate = new Date(end)
    const diffTime = Math.abs(endDate.getTime() - startDate.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays + 1 // Include both start and end dates
  }

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof LeaveFormData, string>> = {}

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required'
    }

    if (!formData.end_date) {
      newErrors.end_date = 'End date is required'
    }

    if (formData.end_date && formData.start_date) {
      const start = new Date(formData.start_date)
      const end = new Date(formData.end_date)
      if (end < start) {
        newErrors.end_date = 'End date must be after start date'
      }
    }

    if (!formData.reason.trim()) {
      newErrors.reason = 'Reason is required'
    } else if (formData.reason.trim().length < 10) {
      newErrors.reason = 'Reason must be at least 10 characters'
    }

    if (formData.days < 1) {
      newErrors.days = 'Leave must be at least 1 day'
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

  const handleChange = (field: keyof LeaveFormData, value: string | number) => {
    const updatedData = { ...formData, [field]: value }

    // Auto-calculate days when dates change
    if (field === 'start_date' || field === 'end_date') {
      updatedData.days = calculateDays(
        field === 'start_date' ? value as string : formData.start_date,
        field === 'end_date' ? value as string : formData.end_date
      )
    }

    setFormData(updatedData)
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Leave Request"
        description="Submit a leave request for a courier"
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
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Leave Type" required>
            <Select
              value={formData.leave_type}
              onChange={(e) => handleChange('leave_type', e.target.value)}
              options={[
                { value: 'annual', label: 'Annual Leave' },
                { value: 'sick', label: 'Sick Leave' },
                { value: 'emergency', label: 'Emergency Leave' },
                { value: 'unpaid', label: 'Unpaid Leave' },
              ]}
            />
          </FormField>

          <FormField label="Start Date" required error={errors.start_date}>
            <Input
              type="date"
              value={formData.start_date}
              onChange={(e) => handleChange('start_date', e.target.value)}
            />
          </FormField>

          <FormField label="End Date" required error={errors.end_date}>
            <Input
              type="date"
              value={formData.end_date}
              onChange={(e) => handleChange('end_date', e.target.value)}
            />
          </FormField>

          <FormField label="Days" required error={errors.days}>
            <Input
              type="number"
              value={formData.days}
              onChange={(e) => handleChange('days', parseInt(e.target.value))}
              disabled
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'approved', label: 'Approved' },
                { value: 'rejected', label: 'Rejected' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Details"
        description="Provide reason and additional information"
      >
        <FormField label="Reason" required error={errors.reason}>
          <Input
            value={formData.reason}
            onChange={(e) => handleChange('reason', e.target.value)}
            placeholder="Please provide a detailed reason for the leave..."
          />
        </FormField>

        <FormField label="Approved By">
          <Input
            value={formData.approved_by}
            onChange={(e) => handleChange('approved_by', e.target.value)}
            placeholder="Manager or approver name"
          />
        </FormField>

        <FormField label="Additional Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes or comments..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Submit Leave Request' : 'Update Leave Request'}
        </Button>
      </FormActions>
    </Form>
  )
}
