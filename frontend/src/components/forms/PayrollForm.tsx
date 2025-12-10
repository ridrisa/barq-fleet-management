import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { payrollRunSchema, type PayrollRunFormData } from '@/schemas'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Checkbox } from './Checkbox'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface PayrollFormProps {
  initialData?: Partial<PayrollRunFormData> & { id?: string | number }
  onSubmit: (data: PayrollRunFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  employeeCount?: number
  totalPayroll?: number
  mode?: 'create' | 'edit'
}

export const PayrollForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  employeeCount = 0,
  totalPayroll = 0,
  mode = 'create',
}: PayrollFormProps) => {
  const currentDate = new Date()
  const currentMonth = currentDate.toISOString().slice(0, 7)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<PayrollRunFormData>({
    resolver: zodResolver(payrollRunSchema),
    defaultValues: {
      month: initialData?.month || currentMonth,
      pay_date: initialData?.pay_date || '',
      include_bonuses: initialData?.include_bonuses ?? true,
      include_deductions: initialData?.include_deductions ?? true,
      include_overtime: initialData?.include_overtime ?? true,
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const includeBonuses = watch('include_bonuses')
  const includeDeductions = watch('include_deductions')
  const includeOvertime = watch('include_overtime')

  const onFormSubmit = async (data: PayrollRunFormData) => {
    await onSubmit(data)
  }

  const loading = isLoading || isSubmitting

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Payroll Run Configuration"
        description="Configure settings for this payroll run"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Payroll Month" required error={errors.month?.message}>
            <Input
              type="month"
              {...register('month')}
            />
          </FormField>

          <FormField label="Pay Date" required error={errors.pay_date?.message}>
            <Input
              type="date"
              {...register('pay_date')}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Payroll Components"
        description="Select which components to include in this payroll run"
      >
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <Checkbox
              checked={includeBonuses}
              onChange={(e) => setValue('include_bonuses', e.target.checked)}
              id="include_bonuses"
            />
            <label htmlFor="include_bonuses" className="text-sm font-medium text-gray-700 cursor-pointer">
              Include Bonuses
              <span className="block text-xs text-gray-500">Include all approved bonuses for the selected month</span>
            </label>
          </div>

          <div className="flex items-center space-x-3">
            <Checkbox
              checked={includeDeductions}
              onChange={(e) => setValue('include_deductions', e.target.checked)}
              id="include_deductions"
            />
            <label htmlFor="include_deductions" className="text-sm font-medium text-gray-700 cursor-pointer">
              Include Deductions
              <span className="block text-xs text-gray-500">Include loan installments, penalties, and other deductions</span>
            </label>
          </div>

          <div className="flex items-center space-x-3">
            <Checkbox
              checked={includeOvertime}
              onChange={(e) => setValue('include_overtime', e.target.checked)}
              id="include_overtime"
            />
            <label htmlFor="include_overtime" className="text-sm font-medium text-gray-700 cursor-pointer">
              Include Overtime
              <span className="block text-xs text-gray-500">Calculate and include overtime pay based on attendance records</span>
            </label>
          </div>
        </div>
      </FormSection>

      {/* Payroll Summary Preview */}
      {employeeCount > 0 && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Payroll Preview</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-blue-700">Employees</p>
              <p className="text-2xl font-bold text-blue-900">{employeeCount}</p>
            </div>
            <div>
              <p className="text-sm text-blue-700">Estimated Total</p>
              <p className="text-2xl font-bold text-blue-900">
                {totalPayroll.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700">Average Salary</p>
              <p className="text-2xl font-bold text-blue-900">
                {employeeCount > 0
                  ? (totalPayroll / employeeCount).toLocaleString('en-US', { minimumFractionDigits: 2 })
                  : '0.00'} SAR
              </p>
            </div>
          </div>
        </div>
      )}

      <FormSection title="Additional Notes">
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
            placeholder="Any special instructions or notes for this payroll run..."
            rows={3}
          />
        </FormField>
      </FormSection>

      {/* Important Notice */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 className="text-sm font-medium text-yellow-800">Important</h4>
        <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside space-y-1">
          <li>Ensure all attendance records are finalized before processing</li>
          <li>Verify all bonuses and deductions are approved</li>
          <li>GOSI contributions will be automatically calculated (9%)</li>
          <li>Review the generated payroll before final approval</li>
        </ul>
      </div>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={loading}>
          {loading ? 'Processing...' : mode === 'create' ? 'Generate Payroll' : 'Update Payroll Run'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default PayrollForm
