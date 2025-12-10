import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { leaveRequestSchema, type LeaveRequestFormData } from '@/schemas'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface LeaveFormProps {
  initialData?: Partial<LeaveRequestFormData> & { id?: string | number }
  onSubmit: (data: LeaveRequestFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const LeaveForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: LeaveFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<LeaveRequestFormData>({
    resolver: zodResolver(leaveRequestSchema),
    defaultValues: {
      leave_type: initialData?.leave_type || 'annual',
      start_date: initialData?.start_date || '',
      end_date: initialData?.end_date || '',
      reason: initialData?.reason || '',
      emergency_contact: initialData?.emergency_contact || '',
      attachment_url: initialData?.attachment_url || '',
    },
    mode: 'onBlur',
  })

  const onFormSubmit = async (data: LeaveRequestFormData) => {
    await onSubmit(data)
  }

  const loading = isLoading || isSubmitting
  const startDate = watch('start_date')
  const endDate = watch('end_date')

  // Calculate duration
  const calculateDuration = () => {
    if (!startDate || !endDate) return null
    const start = new Date(startDate)
    const end = new Date(endDate)
    if (end < start) return null
    const diffTime = Math.abs(end.getTime() - start.getTime())
    const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    return days
  }

  const duration = calculateDuration()

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Leave Request Details"
        description="Submit a request for time off"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Leave Type" required error={errors.leave_type?.message}>
            <Select
              value={watch('leave_type')}
              onChange={(e) => setValue('leave_type', e.target.value as LeaveRequestFormData['leave_type'], { shouldValidate: true })}
              options={[
                { value: 'annual', label: 'Annual Leave' },
                { value: 'sick', label: 'Sick Leave' },
                { value: 'emergency', label: 'Emergency Leave' },
                { value: 'unpaid', label: 'Unpaid Leave' },
                { value: 'maternity', label: 'Maternity Leave' },
                { value: 'paternity', label: 'Paternity Leave' },
                { value: 'bereavement', label: 'Bereavement Leave' },
                { value: 'hajj', label: 'Hajj Leave' },
              ]}
            />
          </FormField>

          <div className="hidden md:block" /> {/* Spacer */}

          <FormField label="Start Date" required error={errors.start_date?.message}>
            <Input
              type="date"
              {...register('start_date')}
            />
          </FormField>

          <FormField label="End Date" required error={errors.end_date?.message}>
            <Input
              type="date"
              {...register('end_date')}
              min={startDate}
            />
          </FormField>

          {duration && (
            <div className="col-span-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <span className="font-medium">Duration:</span> {duration} day{duration > 1 ? 's' : ''}
              </p>
            </div>
          )}
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Provide reason and emergency contact details"
      >
        <div className="space-y-4">
          <FormField label="Reason" required error={errors.reason?.message}>
            <Textarea
              {...register('reason')}
              placeholder="Please provide a detailed reason for your leave request..."
              rows={4}
            />
          </FormField>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="Emergency Contact" error={errors.emergency_contact?.message}>
              <Input
                type="tel"
                {...register('emergency_contact')}
                placeholder="+966 5X XXX XXXX"
              />
            </FormField>

            <FormField label="Attachment URL" error={errors.attachment_url?.message}>
              <Input
                type="url"
                {...register('attachment_url')}
                placeholder="https://... (e.g., medical certificate)"
              />
            </FormField>
          </div>
        </div>
      </FormSection>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={loading}>
          {loading ? 'Submitting...' : mode === 'create' ? 'Submit Leave Request' : 'Update Leave Request'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default LeaveForm
