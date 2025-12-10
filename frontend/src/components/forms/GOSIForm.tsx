import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { gosiBatchSchema, gosiContributionSchema, type GOSIBatchFormData, type GOSIContributionFormData } from '@/schemas'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Checkbox } from './Checkbox'
import { Form, FormField, FormSection, FormActions } from './Form'

// Individual GOSI Contribution Form
export interface GOSIContributionFormProps {
  initialData?: Partial<GOSIContributionFormData> & { id?: string | number }
  onSubmit: (data: GOSIContributionFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  couriers?: Array<{ id: number; name: string; base_salary?: number; is_saudi?: boolean }>
  mode?: 'create' | 'edit'
}

export const GOSIContributionForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  couriers = [],
  mode = 'create',
}: GOSIContributionFormProps) => {
  const currentMonth = new Date().toISOString().slice(0, 7)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<GOSIContributionFormData>({
    resolver: zodResolver(gosiContributionSchema),
    defaultValues: {
      employee_id: initialData?.employee_id || 0,
      month: initialData?.month || currentMonth,
      base_salary: initialData?.base_salary || 0,
      employee_rate: initialData?.employee_rate || 9,
      employer_rate: initialData?.employer_rate || 9,
      employee_contribution: initialData?.employee_contribution || 0,
      employer_contribution: initialData?.employer_contribution || 0,
      total_contribution: initialData?.total_contribution || 0,
      is_saudi: initialData?.is_saudi || false,
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const employeeId = watch('employee_id')
  const baseSalary = watch('base_salary')
  const employeeRate = watch('employee_rate')
  const employerRate = watch('employer_rate')
  const isSaudi = watch('is_saudi')

  // Auto-populate salary and nationality when employee is selected
  useEffect(() => {
    if (employeeId) {
      const courier = couriers.find((c) => c.id === employeeId)
      if (courier) {
        if (courier.base_salary && baseSalary === 0) {
          setValue('base_salary', courier.base_salary)
        }
        if (courier.is_saudi !== undefined) {
          setValue('is_saudi', courier.is_saudi)
        }
      }
    }
  }, [employeeId, couriers, setValue, baseSalary])

  // Auto-calculate contributions
  useEffect(() => {
    if (baseSalary > 0) {
      const empContribution = (baseSalary * employeeRate) / 100
      const emplrContribution = (baseSalary * employerRate) / 100

      setValue('employee_contribution', Math.round(empContribution * 100) / 100)
      setValue('employer_contribution', Math.round(emplrContribution * 100) / 100)
      setValue('total_contribution', Math.round((empContribution + emplrContribution) * 100) / 100)
    }
  }, [baseSalary, employeeRate, employerRate, setValue])

  const onFormSubmit = async (data: GOSIContributionFormData) => {
    await onSubmit(data)
  }

  const loading = isLoading || isSubmitting

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="GOSI Contribution Details"
        description="Record GOSI contribution for an employee"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Employee" required error={errors.employee_id?.message}>
            <Select
              value={watch('employee_id')?.toString() || ''}
              onChange={(e) => setValue('employee_id', parseInt(e.target.value) || 0, { shouldValidate: true })}
              options={[
                { value: '', label: 'Select employee...' },
                ...couriers.map((c) => ({ value: c.id.toString(), label: c.name })),
              ]}
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Month" required error={errors.month?.message}>
            <Input
              type="month"
              {...register('month')}
            />
          </FormField>

          <FormField label="Base Salary (SAR)" required error={errors.base_salary?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('base_salary', { valueAsNumber: true })}
              placeholder="5000.00"
            />
          </FormField>

          <div className="flex items-center space-x-3 pt-6">
            <Checkbox
              checked={isSaudi}
              onChange={(e) => setValue('is_saudi', e.target.checked)}
              id="is_saudi"
            />
            <label htmlFor="is_saudi" className="text-sm font-medium text-gray-700 cursor-pointer">
              Saudi National
            </label>
          </div>
        </div>
      </FormSection>

      <FormSection
        title="Contribution Rates"
        description="GOSI contribution rates for employee and employer"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Employee Rate (%)" error={errors.employee_rate?.message}>
            <Input
              type="number"
              step="0.1"
              {...register('employee_rate', { valueAsNumber: true })}
              placeholder="9"
            />
          </FormField>

          <FormField label="Employer Rate (%)" error={errors.employer_rate?.message}>
            <Input
              type="number"
              step="0.1"
              {...register('employer_rate', { valueAsNumber: true })}
              placeholder="9"
            />
          </FormField>
        </div>
      </FormSection>

      {/* Contribution Summary */}
      {baseSalary > 0 && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Contribution Summary</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Employee Contribution (9%)</p>
              <p className="text-lg font-bold text-blue-600">
                {watch('employee_contribution')?.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Employer Contribution (9%)</p>
              <p className="text-lg font-bold text-green-600">
                {watch('employer_contribution')?.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Contribution (18%)</p>
              <p className="text-lg font-bold text-purple-600">
                {watch('total_contribution')?.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </div>
        </div>
      )}

      <FormSection title="Notes">
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
            placeholder="Any additional notes..."
            rows={2}
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
          {loading ? 'Saving...' : mode === 'create' ? 'Save Contribution' : 'Update Contribution'}
        </Button>
      </FormActions>
    </Form>
  )
}

// Batch GOSI Processing Form
export interface GOSIBatchFormProps {
  initialData?: Partial<GOSIBatchFormData>
  onSubmit: (data: GOSIBatchFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  employeeSummary?: {
    saudiCount: number
    nonSaudiCount: number
    totalSalary: number
  }
}

export const GOSIBatchForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  employeeSummary,
}: GOSIBatchFormProps) => {
  const currentMonth = new Date().toISOString().slice(0, 7)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<GOSIBatchFormData>({
    resolver: zodResolver(gosiBatchSchema),
    defaultValues: {
      month: initialData?.month || currentMonth,
      include_saudis: initialData?.include_saudis ?? true,
      include_non_saudis: initialData?.include_non_saudis ?? true,
      employee_rate: initialData?.employee_rate || 9,
      employer_rate: initialData?.employer_rate || 9,
    },
    mode: 'onBlur',
  })

  const includeSaudis = watch('include_saudis')
  const includeNonSaudis = watch('include_non_saudis')
  const employeeRate = watch('employee_rate')
  const employerRate = watch('employer_rate')

  // Calculate estimated contributions
  const calculateEstimate = () => {
    if (!employeeSummary) return { employee: 0, employer: 0, total: 0 }

    let eligibleSalary = 0
    if (includeSaudis) eligibleSalary += employeeSummary.totalSalary * (employeeSummary.saudiCount / (employeeSummary.saudiCount + employeeSummary.nonSaudiCount) || 0)
    if (includeNonSaudis) eligibleSalary += employeeSummary.totalSalary * (employeeSummary.nonSaudiCount / (employeeSummary.saudiCount + employeeSummary.nonSaudiCount) || 0)

    const employeeContribution = (eligibleSalary * employeeRate) / 100
    const employerContribution = (eligibleSalary * employerRate) / 100

    return {
      employee: employeeContribution,
      employer: employerContribution,
      total: employeeContribution + employerContribution,
    }
  }

  const estimate = calculateEstimate()

  const onFormSubmit = async (data: GOSIBatchFormData) => {
    await onSubmit(data)
  }

  const loading = isLoading || isSubmitting

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Batch GOSI Processing"
        description="Generate GOSI contributions for all employees"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Month" required error={errors.month?.message}>
            <Input
              type="month"
              {...register('month')}
            />
          </FormField>

          <div /> {/* Spacer */}

          <div className="flex items-center space-x-3">
            <Checkbox
              checked={includeSaudis}
              onChange={(e) => setValue('include_saudis', e.target.checked)}
              id="include_saudis"
            />
            <label htmlFor="include_saudis" className="text-sm font-medium text-gray-700 cursor-pointer">
              Include Saudi Nationals
              {employeeSummary && (
                <span className="block text-xs text-gray-500">
                  {employeeSummary.saudiCount} employees
                </span>
              )}
            </label>
          </div>

          <div className="flex items-center space-x-3">
            <Checkbox
              checked={includeNonSaudis}
              onChange={(e) => setValue('include_non_saudis', e.target.checked)}
              id="include_non_saudis"
            />
            <label htmlFor="include_non_saudis" className="text-sm font-medium text-gray-700 cursor-pointer">
              Include Non-Saudi Employees
              {employeeSummary && (
                <span className="block text-xs text-gray-500">
                  {employeeSummary.nonSaudiCount} employees
                </span>
              )}
            </label>
          </div>

          <FormField label="Employee Rate (%)" error={errors.employee_rate?.message}>
            <Input
              type="number"
              step="0.1"
              {...register('employee_rate', { valueAsNumber: true })}
              placeholder="9"
            />
          </FormField>

          <FormField label="Employer Rate (%)" error={errors.employer_rate?.message}>
            <Input
              type="number"
              step="0.1"
              {...register('employer_rate', { valueAsNumber: true })}
              placeholder="9"
            />
          </FormField>
        </div>
      </FormSection>

      {/* Estimated Contributions */}
      {employeeSummary && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">Estimated Contributions</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-blue-700">Employee Total</p>
              <p className="text-xl font-bold text-blue-900">
                {estimate.employee.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700">Employer Total</p>
              <p className="text-xl font-bold text-blue-900">
                {estimate.employer.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
            <div>
              <p className="text-sm text-blue-700">Grand Total</p>
              <p className="text-xl font-bold text-purple-600">
                {estimate.total.toLocaleString('en-US', { minimumFractionDigits: 2 })} SAR
              </p>
            </div>
          </div>
        </div>
      )}

      {/* GOSI Info */}
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h4 className="text-sm font-medium text-gray-800">GOSI Contribution Rates (Saudi Arabia)</h4>
        <ul className="mt-2 text-sm text-gray-600 list-disc list-inside space-y-1">
          <li>Employee contribution: 9% of monthly salary</li>
          <li>Employer contribution: 9% of monthly salary</li>
          <li>Total contribution: 18% of monthly salary</li>
          <li>Covers: Retirement, disability, death, and occupational hazards</li>
        </ul>
      </div>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={loading || (!includeSaudis && !includeNonSaudis)}>
          {loading ? 'Processing...' : 'Generate GOSI Records'}
        </Button>
      </FormActions>
    </Form>
  )
}

// Default export for the main form
export default GOSIContributionForm
