import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface AttendanceFormData {
  courier_id: string
  date: string
  check_in?: string
  check_out?: string
  status: 'present' | 'absent' | 'half_day' | 'late' | 'on_leave'
  hours_worked?: number
  overtime_hours?: number
  location?: string
  notes?: string
}

export interface AttendanceFormProps {
  initialData?: Partial<AttendanceFormData>
  onSubmit: (data: AttendanceFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const AttendanceForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: AttendanceFormProps) => {
  const [formData, setFormData] = useState<AttendanceFormData>({
    courier_id: initialData?.courier_id || '',
    date: initialData?.date || new Date().toISOString().split('T')[0],
    check_in: initialData?.check_in || '',
    check_out: initialData?.check_out || '',
    status: initialData?.status || 'present',
    hours_worked: initialData?.hours_worked || 0,
    overtime_hours: initialData?.overtime_hours || 0,
    location: initialData?.location || '',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof AttendanceFormData, string>>>({})

  const calculateHours = (checkIn: string, checkOut: string): number => {
    if (!checkIn || !checkOut) return 0
    const start = new Date(`2000-01-01T${checkIn}`)
    const end = new Date(`2000-01-01T${checkOut}`)
    const diffMs = end.getTime() - start.getTime()
    const hours = diffMs / (1000 * 60 * 60)
    return Math.max(0, Math.round(hours * 100) / 100)
  }

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof AttendanceFormData, string>> = {}

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (!formData.date) {
      newErrors.date = 'Date is required'
    }

    if (formData.status === 'present' || formData.status === 'late') {
      if (!formData.check_in) {
        newErrors.check_in = 'Check-in time is required for present status'
      }
    }

    if (formData.check_in && formData.check_out) {
      const checkIn = new Date(`2000-01-01T${formData.check_in}`)
      const checkOut = new Date(`2000-01-01T${formData.check_out}`)
      if (checkOut <= checkIn) {
        newErrors.check_out = 'Check-out must be after check-in'
      }
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

  const handleChange = (field: keyof AttendanceFormData, value: string | number) => {
    const updatedData = { ...formData, [field]: value }

    // Auto-calculate hours worked when check-in/out times change
    if (field === 'check_in' || field === 'check_out') {
      const hours = calculateHours(
        field === 'check_in' ? value as string : formData.check_in || '',
        field === 'check_out' ? value as string : formData.check_out || ''
      )
      updatedData.hours_worked = hours

      // Calculate overtime (over 8 hours)
      updatedData.overtime_hours = Math.max(0, hours - 8)
    }

    setFormData(updatedData)
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Attendance Record"
        description="Record courier attendance for the day"
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

          <FormField label="Date" required error={errors.date}>
            <Input
              type="date"
              value={formData.date}
              onChange={(e) => handleChange('date', e.target.value)}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'present', label: 'Present' },
                { value: 'absent', label: 'Absent' },
                { value: 'half_day', label: 'Half Day' },
                { value: 'late', label: 'Late' },
                { value: 'on_leave', label: 'On Leave' },
              ]}
            />
          </FormField>

          <FormField label="Location">
            <Input
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
              placeholder="Work location or branch"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Time Tracking"
        description="Check-in and check-out times"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Check-in Time" error={errors.check_in}>
            <Input
              type="time"
              value={formData.check_in}
              onChange={(e) => handleChange('check_in', e.target.value)}
            />
          </FormField>

          <FormField label="Check-out Time" error={errors.check_out}>
            <Input
              type="time"
              value={formData.check_out}
              onChange={(e) => handleChange('check_out', e.target.value)}
            />
          </FormField>

          <FormField label="Hours Worked">
            <Input
              type="number"
              step="0.01"
              value={formData.hours_worked}
              onChange={(e) => handleChange('hours_worked', parseFloat(e.target.value))}
              disabled
            />
          </FormField>

          <FormField label="Overtime Hours">
            <Input
              type="number"
              step="0.01"
              value={formData.overtime_hours}
              onChange={(e) => handleChange('overtime_hours', parseFloat(e.target.value))}
              disabled
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
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any special notes or observations..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Record Attendance' : 'Update Attendance'}
        </Button>
      </FormActions>
    </Form>
  )
}
