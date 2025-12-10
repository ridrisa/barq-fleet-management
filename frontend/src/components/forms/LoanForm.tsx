import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { loanRequestSchema, LoanRequestFormData } from '@/schemas'

export interface LoanFormProps {
  initialData?: Partial<LoanRequestFormData>
  onSubmit: (data: LoanRequestFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: number; name: string }>
}

export const LoanForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: LoanFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    watch,
    setValue,
  } = useForm<LoanRequestFormData>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(loanRequestSchema as any),
    defaultValues: {
      loan_type: initialData?.loan_type || 'salary_advance',
      amount: initialData?.amount || 0,
      installments: initialData?.installments || 12,
      reason: initialData?.reason || '',
      start_date: initialData?.start_date || '',
      guarantor_name: initialData?.guarantor_name || '',
      guarantor_phone: initialData?.guarantor_phone || '',
    },
    mode: 'onBlur',
  })

  const loading = isLoading || isSubmitting
  const amount = watch('amount')
  const installments = watch('installments')

  // Calculate monthly installment amount
  const installmentAmount = installments > 0 ? Math.round((amount / installments) * 100) / 100 : 0

  // Calculate end date based on start date and installments
  const startDate = watch('start_date')
  const endDate = startDate && installments > 0
    ? (() => {
        const date = new Date(startDate)
        date.setMonth(date.getMonth() + installments)
        return date.toISOString().split('T')[0]
      })()
    : ''

  const onFormSubmit = async (data: LoanRequestFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Loan Information"
        description="Create a loan request for an employee"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Loan Type" required error={errors.loan_type?.message}>
            <Select
              value={watch('loan_type')}
              onChange={(e) => setValue('loan_type', e.target.value as LoanRequestFormData['loan_type'], { shouldValidate: true })}
              options={[
                { value: 'salary_advance', label: 'Salary Advance' },
                { value: 'personal', label: 'Personal' },
                { value: 'emergency', label: 'Emergency' },
                { value: 'housing', label: 'Housing' },
                { value: 'vehicle', label: 'Vehicle' },
              ]}
            />
          </FormField>

          <FormField label="Loan Amount (SAR)" required error={errors.amount?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('amount', { valueAsNumber: true })}
              placeholder="10000.00"
            />
          </FormField>

          <FormField label="Number of Installments" required error={errors.installments?.message}>
            <Input
              type="number"
              {...register('installments', { valueAsNumber: true })}
              placeholder="12"
            />
          </FormField>

          <FormField label="Monthly Installment (Calculated)">
            <Input
              type="number"
              value={installmentAmount}
              disabled
            />
          </FormField>

          <FormField label="Start Date" required error={errors.start_date?.message}>
            <Input
              type="date"
              {...register('start_date')}
            />
          </FormField>

          <FormField label="End Date (Calculated)">
            <Input
              type="date"
              value={endDate}
              disabled
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Details"
        description="Reason and guarantor information"
      >
        <div className="space-y-4">
          <FormField label="Reason" required error={errors.reason?.message}>
            <Textarea
              {...register('reason')}
              placeholder="Please provide a detailed reason for the loan request..."
              rows={4}
            />
          </FormField>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormField label="Guarantor Name" error={errors.guarantor_name?.message}>
              <Input
                {...register('guarantor_name')}
                placeholder="Full name of guarantor"
              />
            </FormField>

            <FormField label="Guarantor Phone" error={errors.guarantor_phone?.message}>
              <Input
                type="tel"
                {...register('guarantor_phone')}
                placeholder="+966 50 123 4567"
              />
            </FormField>
          </div>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : mode === 'create' ? 'Submit Request' : 'Update Request'}
        </Button>
      </FormActions>
    </Form>
  )
}

// Re-export for backwards compatibility
export type { LoanRequestFormData as LoanFormData } from '@/schemas'
