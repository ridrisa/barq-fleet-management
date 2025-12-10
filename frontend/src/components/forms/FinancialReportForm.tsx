import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { financialReportSchema, type FinancialReportFormData } from '@/schemas'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Checkbox } from './Checkbox'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface FinancialReportFormProps {
  initialData?: Partial<FinancialReportFormData> & { id?: string | number }
  onSubmit: (data: FinancialReportFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const FinancialReportForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: FinancialReportFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<FinancialReportFormData>({
    resolver: zodResolver(financialReportSchema),
    defaultValues: {
      report_type: initialData?.report_type || 'income_statement',
      start_date: initialData?.start_date || '',
      end_date: initialData?.end_date || '',
      group_by: initialData?.group_by || 'month',
      department: initialData?.department,
      category: initialData?.category || '',
      include_projections: initialData?.include_projections || false,
      compare_previous_period: initialData?.compare_previous_period || false,
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const reportType = watch('report_type')
  const startDate = watch('start_date')
  const endDate = watch('end_date')
  const includeProjections = watch('include_projections')
  const comparePreviousPeriod = watch('compare_previous_period')

  const onFormSubmit = async (data: FinancialReportFormData) => {
    await onSubmit(data)
  }

  const loading = isLoading || isSubmitting

  // Report type descriptions
  const reportDescriptions: Record<string, string> = {
    income_statement: 'Shows revenue, expenses, and profit/loss for a period',
    balance_sheet: 'Shows assets, liabilities, and equity at a point in time',
    cash_flow: 'Shows cash inflows and outflows for a period',
    expense_report: 'Detailed breakdown of all expenses by category',
    budget_variance: 'Compares actual vs budgeted amounts',
    payroll_summary: 'Summary of all payroll costs for a period',
    gosi_summary: 'Summary of GOSI contributions and compliance',
  }

  // Category options based on report type
  const getCategoryOptions = () => {
    switch (reportType) {
      case 'expense_report':
      case 'budget_variance':
        return [
          { value: '', label: 'All Categories' },
          { value: 'payroll', label: 'Payroll' },
          { value: 'operations', label: 'Operations' },
          { value: 'maintenance', label: 'Maintenance' },
          { value: 'fuel', label: 'Fuel' },
          { value: 'accommodation', label: 'Accommodation' },
          { value: 'other', label: 'Other' },
        ]
      case 'payroll_summary':
        return [
          { value: '', label: 'All Components' },
          { value: 'base_salary', label: 'Base Salary' },
          { value: 'allowances', label: 'Allowances' },
          { value: 'overtime', label: 'Overtime' },
          { value: 'bonuses', label: 'Bonuses' },
          { value: 'deductions', label: 'Deductions' },
        ]
      default:
        return [{ value: '', label: 'Not Applicable' }]
    }
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Report Configuration"
        description="Select the type of financial report to generate"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Report Type" required error={errors.report_type?.message}>
            <Select
              value={reportType}
              onChange={(e) => setValue('report_type', e.target.value as FinancialReportFormData['report_type'], { shouldValidate: true })}
              options={[
                { value: 'income_statement', label: 'Income Statement' },
                { value: 'balance_sheet', label: 'Balance Sheet' },
                { value: 'cash_flow', label: 'Cash Flow Statement' },
                { value: 'expense_report', label: 'Expense Report' },
                { value: 'budget_variance', label: 'Budget Variance' },
                { value: 'payroll_summary', label: 'Payroll Summary' },
                { value: 'gosi_summary', label: 'GOSI Summary' },
              ]}
            />
          </FormField>

          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              {reportDescriptions[reportType]}
            </p>
          </div>
        </div>
      </FormSection>

      <FormSection
        title="Date Range"
        description="Select the period for this report"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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

          <FormField label="Group By" error={errors.group_by?.message}>
            <Select
              value={watch('group_by')}
              onChange={(e) => setValue('group_by', e.target.value as FinancialReportFormData['group_by'], { shouldValidate: true })}
              options={[
                { value: 'day', label: 'Daily' },
                { value: 'week', label: 'Weekly' },
                { value: 'month', label: 'Monthly' },
                { value: 'quarter', label: 'Quarterly' },
                { value: 'year', label: 'Yearly' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Filters"
        description="Optional filters to narrow down the report"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Department" error={errors.department?.message}>
            <Select
              value={watch('department') || ''}
              onChange={(e) => setValue('department', e.target.value as FinancialReportFormData['department'] || undefined, { shouldValidate: true })}
              options={[
                { value: '', label: 'All Departments' },
                { value: 'operations', label: 'Operations' },
                { value: 'fleet', label: 'Fleet Management' },
                { value: 'hr', label: 'Human Resources' },
                { value: 'finance', label: 'Finance' },
                { value: 'it', label: 'IT' },
                { value: 'marketing', label: 'Marketing' },
                { value: 'admin', label: 'Administration' },
                { value: 'logistics', label: 'Logistics' },
              ]}
            />
          </FormField>

          <FormField label="Category" error={errors.category?.message}>
            <Select
              value={watch('category') || ''}
              onChange={(e) => setValue('category', e.target.value, { shouldValidate: true })}
              options={getCategoryOptions()}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Report Options"
        description="Additional options for the report"
      >
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <Checkbox
              checked={includeProjections}
              onChange={(e) => setValue('include_projections', e.target.checked)}
              id="include_projections"
            />
            <label htmlFor="include_projections" className="text-sm font-medium text-gray-700 cursor-pointer">
              Include Projections
              <span className="block text-xs text-gray-500">Add forecasted data based on historical trends</span>
            </label>
          </div>

          <div className="flex items-center space-x-3">
            <Checkbox
              checked={comparePreviousPeriod}
              onChange={(e) => setValue('compare_previous_period', e.target.checked)}
              id="compare_previous_period"
            />
            <label htmlFor="compare_previous_period" className="text-sm font-medium text-gray-700 cursor-pointer">
              Compare with Previous Period
              <span className="block text-xs text-gray-500">Show variance analysis against the previous period</span>
            </label>
          </div>
        </div>
      </FormSection>

      {/* Period Summary */}
      {startDate && endDate && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Report Period</h3>
          <p className="text-sm text-gray-600">
            {new Date(startDate).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
            {' to '}
            {new Date(endDate).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
          {comparePreviousPeriod && (
            <p className="text-xs text-gray-500 mt-1">
              Will compare with the equivalent previous period
            </p>
          )}
        </div>
      )}

      <FormSection title="Notes">
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
            placeholder="Any additional notes or instructions for this report..."
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
          {loading ? 'Generating...' : mode === 'create' ? 'Generate Report' : 'Update Report'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default FinancialReportForm
