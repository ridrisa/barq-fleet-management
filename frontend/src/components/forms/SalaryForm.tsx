import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { salaryRecordSchema, type SalaryRecordFormData } from '@/schemas'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface SalaryFormProps {
  initialData?: Partial<SalaryRecordFormData> & { id?: string | number }
  onSubmit: (data: SalaryRecordFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  couriers?: Array<{ id: number; name: string }>
  mode?: 'create' | 'edit'
}

export const SalaryForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  couriers = [],
  mode = 'create',
}: SalaryFormProps) => {
  const currentDate = new Date()
  const currentMonth = currentDate.getMonth() + 1
  const currentYear = currentDate.getFullYear()

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<SalaryRecordFormData>({
    resolver: zodResolver(salaryRecordSchema),
    defaultValues: {
      courier_id: initialData?.courier_id || 0,
      month: initialData?.month || currentMonth,
      year: initialData?.year || currentYear,
      basic_salary: initialData?.basic_salary || 0,
      housing_allowance: initialData?.housing_allowance || 0,
      transportation_allowance: initialData?.transportation_allowance || 0,
      food_allowance: initialData?.food_allowance || 0,
      overtime_hours: initialData?.overtime_hours || 0,
      overtime_rate: initialData?.overtime_rate || 1.5,
      bonus: initialData?.bonus || 0,
      commission: initialData?.commission || 0,
      deductions: initialData?.deductions || 0,
      loan_deduction: initialData?.loan_deduction || 0,
      gosi_deduction: initialData?.gosi_deduction || 0,
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const basicSalary = watch('basic_salary')
  const housingAllowance = watch('housing_allowance')
  const transportationAllowance = watch('transportation_allowance')
  const foodAllowance = watch('food_allowance')
  const overtimeHours = watch('overtime_hours')
  const overtimeRate = watch('overtime_rate')
  const bonus = watch('bonus')
  const commission = watch('commission')
  const deductions = watch('deductions')
  const loanDeduction = watch('loan_deduction')
  const gosiDeduction = watch('gosi_deduction')

  // Auto-calculate GOSI when basic salary changes
  useEffect(() => {
    if (basicSalary > 0) {
      const gosiAmount = basicSalary * 0.09
      setValue('gosi_deduction', Math.round(gosiAmount * 100) / 100)
    }
  }, [basicSalary, setValue])

  // Calculate totals
  const hourlyRate = basicSalary / 240 // Assuming 240 working hours per month
  const overtimePay = (overtimeHours || 0) * hourlyRate * (overtimeRate || 1.5)
  const totalAllowances = (housingAllowance || 0) + (transportationAllowance || 0) + (foodAllowance || 0)
  const totalEarnings = basicSalary + totalAllowances + overtimePay + (bonus || 0) + (commission || 0)
  const totalDeductions = (deductions || 0) + (loanDeduction || 0) + (gosiDeduction || 0)
  const netSalary = totalEarnings - totalDeductions

  const onFormSubmit = async (data: SalaryRecordFormData) => {
    await onSubmit(data)
  }

  const loading = isLoading || isSubmitting

  const monthOptions = [
    { value: '1', label: 'January' },
    { value: '2', label: 'February' },
    { value: '3', label: 'March' },
    { value: '4', label: 'April' },
    { value: '5', label: 'May' },
    { value: '6', label: 'June' },
    { value: '7', label: 'July' },
    { value: '8', label: 'August' },
    { value: '9', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' },
  ]

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Employee & Period"
        description="Select employee and salary period"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormField label="Employee" required error={errors.courier_id?.message}>
            <Select
              value={watch('courier_id')?.toString() || ''}
              onChange={(e) => setValue('courier_id', parseInt(e.target.value) || 0, { shouldValidate: true })}
              options={[
                { value: '', label: 'Select employee...' },
                ...couriers.map((c) => ({ value: c.id.toString(), label: c.name })),
              ]}
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Month" required error={errors.month?.message}>
            <Select
              value={watch('month')?.toString() || ''}
              onChange={(e) => setValue('month', parseInt(e.target.value), { shouldValidate: true })}
              options={monthOptions}
            />
          </FormField>

          <FormField label="Year" required error={errors.year?.message}>
            <Input
              type="number"
              {...register('year', { valueAsNumber: true })}
              min={2020}
              max={2100}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Earnings"
        description="Basic salary and allowances"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FormField label="Basic Salary (SAR)" required error={errors.basic_salary?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('basic_salary', { valueAsNumber: true })}
              placeholder="5000.00"
            />
          </FormField>

          <FormField label="Housing Allowance (SAR)" error={errors.housing_allowance?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('housing_allowance', { valueAsNumber: true })}
              placeholder="1250.00"
            />
          </FormField>

          <FormField label="Transportation Allowance (SAR)" error={errors.transportation_allowance?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('transportation_allowance', { valueAsNumber: true })}
              placeholder="500.00"
            />
          </FormField>

          <FormField label="Food Allowance (SAR)" error={errors.food_allowance?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('food_allowance', { valueAsNumber: true })}
              placeholder="300.00"
            />
          </FormField>

          <FormField label="Overtime Hours" error={errors.overtime_hours?.message}>
            <Input
              type="number"
              step="0.5"
              {...register('overtime_hours', { valueAsNumber: true })}
              placeholder="0"
            />
          </FormField>

          <FormField label="Overtime Rate (x)" error={errors.overtime_rate?.message}>
            <Input
              type="number"
              step="0.1"
              {...register('overtime_rate', { valueAsNumber: true })}
              placeholder="1.5"
            />
          </FormField>

          <FormField label="Bonus (SAR)" error={errors.bonus?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('bonus', { valueAsNumber: true })}
              placeholder="0.00"
            />
          </FormField>

          <FormField label="Commission (SAR)" error={errors.commission?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('commission', { valueAsNumber: true })}
              placeholder="0.00"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Deductions"
        description="Salary deductions and withholdings"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FormField label="GOSI Deduction (9%)" error={errors.gosi_deduction?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('gosi_deduction', { valueAsNumber: true })}
              placeholder="Auto-calculated"
            />
          </FormField>

          <FormField label="Loan Deduction (SAR)" error={errors.loan_deduction?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('loan_deduction', { valueAsNumber: true })}
              placeholder="0.00"
            />
          </FormField>

          <FormField label="Other Deductions (SAR)" error={errors.deductions?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('deductions', { valueAsNumber: true })}
              placeholder="0.00"
            />
          </FormField>
        </div>
      </FormSection>

      {/* Salary Summary */}
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg space-y-3">
        <h3 className="text-lg font-semibold text-gray-900">Salary Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Total Earnings</p>
            <p className="text-lg font-bold text-green-600">
              {totalEarnings.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Deductions</p>
            <p className="text-lg font-bold text-red-600">
              -{totalDeductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Overtime Pay</p>
            <p className="text-lg font-bold text-blue-600">
              {overtimePay.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Net Salary</p>
            <p className="text-xl font-bold text-gray-900">
              {netSalary.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
            </p>
          </div>
        </div>
      </div>

      <FormSection
        title="Additional Notes"
      >
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
            placeholder="Any additional notes about this salary record..."
            rows={3}
          />
        </FormField>
      </FormSection>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={loading}>
          {loading ? 'Saving...' : mode === 'create' ? 'Save Salary Record' : 'Update Salary Record'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default SalaryForm
