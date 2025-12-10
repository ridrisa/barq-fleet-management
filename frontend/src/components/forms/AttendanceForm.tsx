import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

/**
 * Attendance status enum
 */
const attendanceStatusSchema = z.enum([
  'present',
  'absent',
  'half_day',
  'late',
  'on_leave',
])

/**
 * Attendance form validation schema
 */
export const attendanceFormSchema = z.object({
  courier_id: z.string().min(1, 'Courier is required'),
  date: z.string().min(1, 'Date is required'),
  check_in: z.string(),
  check_out: z.string(),
  status: attendanceStatusSchema,
  hours_worked: z.number().nonnegative(),
  overtime_hours: z.number().nonnegative(),
  location: z.string().max(200),
  notes: z.string().max(500),
}).refine(
  (data) => {
    // Validate check-in is required for present/late status
    if ((data.status === 'present' || data.status === 'late') && !data.check_in) {
      return false
    }
    return true
  },
  {
    message: 'Check-in time is required for present status',
    path: ['check_in'],
  }
).refine(
  (data) => {
    // Validate check-out is after check-in
    if (data.check_in && data.check_out) {
      const checkIn = new Date(`2000-01-01T${data.check_in}`)
      const checkOut = new Date(`2000-01-01T${data.check_out}`)
      return checkOut > checkIn
    }
    return true
  },
  {
    message: 'Check-out must be after check-in',
    path: ['check_out'],
  }
)

export type AttendanceFormData = z.infer<typeof attendanceFormSchema>

export interface AttendanceFormProps {
  initialData?: Partial<AttendanceFormData>
  onSubmit: (data: AttendanceFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

const calculateHours = (checkIn: string, checkOut: string): number => {
  if (!checkIn || !checkOut) return 0
  const start = new Date(`2000-01-01T${checkIn}`)
  const end = new Date(`2000-01-01T${checkOut}`)
  const diffMs = end.getTime() - start.getTime()
  const hours = diffMs / (1000 * 60 * 60)
  return Math.max(0, Math.round(hours * 100) / 100)
}

export const AttendanceForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: AttendanceFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<AttendanceFormData>({
    resolver: zodResolver(attendanceFormSchema),
    defaultValues: {
      courier_id: initialData?.courier_id || '',
      date: initialData?.date || new Date().toISOString().split('T')[0],
      check_in: initialData?.check_in || '',
      check_out: initialData?.check_out || '',
      status: initialData?.status || 'present',
      hours_worked: initialData?.hours_worked || 0,
      overtime_hours: initialData?.overtime_hours || 0,
      location: initialData?.location || '',
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const checkIn = watch('check_in')
  const checkOut = watch('check_out')
  const status = watch('status')

  // Auto-calculate hours when check-in/check-out change
  useEffect(() => {
    if (checkIn && checkOut) {
      const hours = calculateHours(checkIn, checkOut)
      setValue('hours_worked', hours)
      setValue('overtime_hours', Math.max(0, hours - 8))
    }
  }, [checkIn, checkOut, setValue])

  const onFormSubmit = async (data: AttendanceFormData) => {
    await onSubmit(data)
  }

  const loading = isLoading || isSubmitting

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Attendance Record"
        description="Record courier attendance for the day"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Courier" required error={errors.courier_id?.message}>
            <Select
              value={watch('courier_id')}
              onChange={(e) => setValue('courier_id', e.target.value, { shouldValidate: true })}
              options={[
                { value: '', label: 'Select a courier...' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Date" required error={errors.date?.message}>
            <Input
              type="date"
              {...register('date')}
            />
          </FormField>

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              value={status}
              onChange={(e) => setValue('status', e.target.value as AttendanceFormData['status'], { shouldValidate: true })}
              options={[
                { value: 'present', label: 'Present' },
                { value: 'absent', label: 'Absent' },
                { value: 'half_day', label: 'Half Day' },
                { value: 'late', label: 'Late' },
                { value: 'on_leave', label: 'On Leave' },
              ]}
            />
          </FormField>

          <FormField label="Location" error={errors.location?.message}>
            <Input
              {...register('location')}
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
          <FormField label="Check-in Time" error={errors.check_in?.message}>
            <Input
              type="time"
              {...register('check_in')}
            />
          </FormField>

          <FormField label="Check-out Time" error={errors.check_out?.message}>
            <Input
              type="time"
              {...register('check_out')}
            />
          </FormField>

          <FormField label="Hours Worked">
            <Input
              type="number"
              step="0.01"
              {...register('hours_worked', { valueAsNumber: true })}
              disabled
            />
          </FormField>

          <FormField label="Overtime Hours">
            <Input
              type="number"
              step="0.01"
              {...register('overtime_hours', { valueAsNumber: true })}
              disabled
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and comments"
      >
        <FormField label="Notes" error={errors.notes?.message}>
          <Input
            {...register('notes')}
            placeholder="Any special notes or observations..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : mode === 'create' ? 'Record Attendance' : 'Update Attendance'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default AttendanceForm
