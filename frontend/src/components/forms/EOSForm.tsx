import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { eosCalculationSchema, type EOSCalculationFormData } from '@/schemas'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'

interface EOSBreakdown {
  years_of_service: number
  months_of_service: number
  first_two_years: number
  next_three_years: number
  remaining_years: number
  total_eos: number
  deductions: number
  net_eos: number
}

export interface EOSFormProps {
  initialData?: Partial<EOSCalculationFormData> & {
    id?: string | number
    joining_date?: string
  }
  onSubmit: (data: EOSCalculationFormData & { breakdown: EOSBreakdown }) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  couriers?: Array<{ id: number; name: string; joining_date?: string; base_salary?: number }>
  mode?: 'create' | 'edit'
}

export const EOSForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  couriers = [],
  mode = 'create',
}: EOSFormProps) => {
  const [joiningDate, setJoiningDate] = useState<string>(initialData?.joining_date || '')
  const [breakdown, setBreakdown] = useState<EOSBreakdown | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<EOSCalculationFormData>({
    resolver: zodResolver(eosCalculationSchema),
    defaultValues: {
      courier_id: initialData?.courier_id || 0,
      termination_date: initialData?.termination_date || '',
      termination_reason: initialData?.termination_reason || 'resignation',
      final_basic_salary: initialData?.final_basic_salary || 0,
      unpaid_leave_days: initialData?.unpaid_leave_days || 0,
      pending_loan_amount: initialData?.pending_loan_amount || 0,
      other_deductions: initialData?.other_deductions || 0,
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const courierId = watch('courier_id')
  const terminationDate = watch('termination_date')
  const terminationReason = watch('termination_reason')
  const finalBasicSalary = watch('final_basic_salary')
  const unpaidLeaveDays = watch('unpaid_leave_days')
  const pendingLoanAmount = watch('pending_loan_amount')
  const otherDeductions = watch('other_deductions')

  // Auto-populate joining date and salary when courier is selected
  useEffect(() => {
    if (courierId) {
      const courier = couriers.find((c) => c.id === courierId)
      if (courier) {
        if (courier.joining_date) {
          setJoiningDate(courier.joining_date)
        }
        if (courier.base_salary && finalBasicSalary === 0) {
          setValue('final_basic_salary', courier.base_salary)
        }
      }
    }
  }, [courierId, couriers, setValue, finalBasicSalary])

  // Calculate EOS when relevant fields change
  useEffect(() => {
    if (!joiningDate || !terminationDate || !finalBasicSalary) {
      setBreakdown(null)
      return
    }

    const joining = new Date(joiningDate)
    const termination = new Date(terminationDate)

    if (termination <= joining) {
      setBreakdown(null)
      return
    }

    const diffTime = Math.abs(termination.getTime() - joining.getTime())
    const diffYears = diffTime / (1000 * 60 * 60 * 24 * 365.25)
    const years = Math.floor(diffYears)
    const months = Math.floor((diffYears - years) * 12)

    // Monthly salary for EOS calculation
    const monthlySalary = finalBasicSalary

    let firstTwoYears = 0
    let nextThreeYears = 0
    let remainingYears = 0

    // Saudi Labor Law EOS calculation
    if (diffYears < 2) {
      // Less than 2 years
      const rate = terminationReason === 'resignation' ? 0 : 0.5
      firstTwoYears = diffYears * monthlySalary * rate
    } else if (diffYears >= 2 && diffYears < 5) {
      // 2-5 years
      firstTwoYears = 2 * monthlySalary * 0.5
      nextThreeYears = (diffYears - 2) * monthlySalary
    } else {
      // 5+ years
      firstTwoYears = 2 * monthlySalary * 0.5
      nextThreeYears = 3 * monthlySalary
      remainingYears = (diffYears - 5) * monthlySalary
    }

    const totalEOS = firstTwoYears + nextThreeYears + remainingYears

    // Calculate deductions
    const dailySalary = monthlySalary / 30
    const unpaidLeaveDeduction = (unpaidLeaveDays || 0) * dailySalary
    const totalDeductions = unpaidLeaveDeduction + (pendingLoanAmount || 0) + (otherDeductions || 0)

    // Apply resignation penalty for less than 5 years
    const resignationPenalty = terminationReason === 'resignation' && diffYears < 5 ? totalEOS * 0.1 : 0

    const netEOS = totalEOS - totalDeductions - resignationPenalty

    setBreakdown({
      years_of_service: years,
      months_of_service: months,
      first_two_years: firstTwoYears,
      next_three_years: nextThreeYears,
      remaining_years: remainingYears,
      total_eos: totalEOS,
      deductions: totalDeductions + resignationPenalty,
      net_eos: Math.max(0, netEOS),
    })
  }, [joiningDate, terminationDate, terminationReason, finalBasicSalary, unpaidLeaveDays, pendingLoanAmount, otherDeductions])

  const onFormSubmit = async (data: EOSCalculationFormData) => {
    if (breakdown) {
      await onSubmit({ ...data, breakdown })
    }
  }

  const loading = isLoading || isSubmitting

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Employee Information"
        description="Select employee and termination details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

          <FormField label="Joining Date">
            <Input
              type="date"
              value={joiningDate}
              onChange={(e) => setJoiningDate(e.target.value)}
            />
          </FormField>

          <FormField label="Termination Date" required error={errors.termination_date?.message}>
            <Input
              type="date"
              {...register('termination_date')}
              min={joiningDate}
            />
          </FormField>

          <FormField label="Termination Reason" required error={errors.termination_reason?.message}>
            <Select
              value={watch('termination_reason')}
              onChange={(e) => setValue('termination_reason', e.target.value as EOSCalculationFormData['termination_reason'], { shouldValidate: true })}
              options={[
                { value: 'resignation', label: 'Resignation by Employee' },
                { value: 'termination', label: 'Termination by Employer' },
                { value: 'contract_end', label: 'Contract End' },
                { value: 'retirement', label: 'Retirement' },
                { value: 'death', label: 'Death' },
              ]}
            />
          </FormField>

          <FormField label="Final Basic Salary (SAR)" required error={errors.final_basic_salary?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('final_basic_salary', { valueAsNumber: true })}
              placeholder="5000.00"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Deductions"
        description="Any amounts to be deducted from EOS"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormField label="Unpaid Leave Days" error={errors.unpaid_leave_days?.message}>
            <Input
              type="number"
              {...register('unpaid_leave_days', { valueAsNumber: true })}
              placeholder="0"
              min={0}
            />
          </FormField>

          <FormField label="Pending Loan Amount (SAR)" error={errors.pending_loan_amount?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('pending_loan_amount', { valueAsNumber: true })}
              placeholder="0.00"
            />
          </FormField>

          <FormField label="Other Deductions (SAR)" error={errors.other_deductions?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('other_deductions', { valueAsNumber: true })}
              placeholder="0.00"
            />
          </FormField>
        </div>
      </FormSection>

      {/* EOS Calculation Result */}
      {breakdown && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">EOS Calculation Result</h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Years of Service</p>
              <p className="text-lg font-bold text-gray-900">
                {breakdown.years_of_service}y {breakdown.months_of_service}m
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">First 2 Years (0.5x)</p>
              <p className="text-lg font-medium text-gray-700">
                {breakdown.first_two_years.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Years 2-5 (1x)</p>
              <p className="text-lg font-medium text-gray-700">
                {breakdown.next_three_years.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Years 5+ (1x)</p>
              <p className="text-lg font-medium text-gray-700">
                {breakdown.remaining_years.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </div>

          <div className="border-t pt-4 grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total EOS</p>
              <p className="text-lg font-bold text-blue-600">
                {breakdown.total_eos.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Deductions</p>
              <p className="text-lg font-bold text-red-600">
                -{breakdown.deductions.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Net EOS Payable</p>
              <p className="text-xl font-bold text-green-600">
                {breakdown.net_eos.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </div>

          {terminationReason === 'resignation' && breakdown.years_of_service < 5 && (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <span className="font-medium">Note:</span> A 10% penalty has been applied for resignation before 5 years of service.
              </p>
            </div>
          )}
        </div>
      )}

      <FormSection title="Additional Notes">
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
            placeholder="Any additional notes about this EOS calculation..."
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
        <Button type="submit" disabled={loading || !breakdown}>
          {loading ? 'Processing...' : mode === 'create' ? 'Calculate & Save EOS' : 'Update EOS Calculation'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default EOSForm
