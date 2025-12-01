import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface SalaryFormData {
  courier_id: string
  month: string
  base_salary: number
  allowances: number
  deductions: number
  overtime_pay: number
  bonus: number
  net_salary: number
  currency: 'SAR' | 'USD' | 'EUR'
  payment_date?: string
  payment_method: 'bank_transfer' | 'cash' | 'check'
  status: 'pending' | 'processed' | 'paid'
  notes?: string
}

export interface SalaryFormProps {
  initialData?: Partial<SalaryFormData>
  onSubmit: (data: SalaryFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const SalaryForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: SalaryFormProps) => {
  const [formData, setFormData] = useState<SalaryFormData>({
    courier_id: initialData?.courier_id || '',
    month: initialData?.month || new Date().toISOString().slice(0, 7),
    base_salary: initialData?.base_salary || 0,
    allowances: initialData?.allowances || 0,
    deductions: initialData?.deductions || 0,
    overtime_pay: initialData?.overtime_pay || 0,
    bonus: initialData?.bonus || 0,
    net_salary: initialData?.net_salary || 0,
    currency: initialData?.currency || 'SAR',
    payment_date: initialData?.payment_date || '',
    payment_method: initialData?.payment_method || 'bank_transfer',
    status: initialData?.status || 'pending',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof SalaryFormData, string>>>({})

  const calculateNetSalary = (
    baseSalary: number,
    allowances: number,
    deductions: number,
    overtimePay: number,
    bonus: number
  ): number => {
    return Math.max(0, baseSalary + allowances + overtimePay + bonus - deductions)
  }

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof SalaryFormData, string>> = {}

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (!formData.month) {
      newErrors.month = 'Month is required'
    }

    if (formData.base_salary <= 0) {
      newErrors.base_salary = 'Base salary must be greater than zero'
    }

    if (formData.deductions < 0) {
      newErrors.deductions = 'Deductions cannot be negative'
    }

    if (formData.allowances < 0) {
      newErrors.allowances = 'Allowances cannot be negative'
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

  const handleChange = (field: keyof SalaryFormData, value: string | number) => {
    const updatedData = { ...formData, [field]: value }

    // Auto-calculate net salary
    if (['base_salary', 'allowances', 'deductions', 'overtime_pay', 'bonus'].includes(field)) {
      updatedData.net_salary = calculateNetSalary(
        field === 'base_salary' ? value as number : formData.base_salary,
        field === 'allowances' ? value as number : formData.allowances,
        field === 'deductions' ? value as number : formData.deductions,
        field === 'overtime_pay' ? value as number : formData.overtime_pay,
        field === 'bonus' ? value as number : formData.bonus
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
        title="Salary Information"
        description="Process courier salary for the month"
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

          <FormField label="Month" required error={errors.month}>
            <Input
              type="month"
              value={formData.month}
              onChange={(e) => handleChange('month', e.target.value)}
            />
          </FormField>

          <FormField label="Currency" required>
            <Select
              value={formData.currency}
              onChange={(e) => handleChange('currency', e.target.value)}
              options={[
                { value: 'SAR', label: 'SAR (Saudi Riyal)' },
                { value: 'USD', label: 'USD (US Dollar)' },
                { value: 'EUR', label: 'EUR (Euro)' },
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'processed', label: 'Processed' },
                { value: 'paid', label: 'Paid' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Salary Breakdown"
        description="Base salary, allowances, and deductions"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Base Salary" required error={errors.base_salary}>
            <Input
              type="number"
              step="0.01"
              value={formData.base_salary}
              onChange={(e) => handleChange('base_salary', parseFloat(e.target.value))}
              placeholder="5000.00"
            />
          </FormField>

          <FormField label="Allowances" error={errors.allowances}>
            <Input
              type="number"
              step="0.01"
              value={formData.allowances}
              onChange={(e) => handleChange('allowances', parseFloat(e.target.value))}
              placeholder="500.00"
            />
          </FormField>

          <FormField label="Overtime Pay">
            <Input
              type="number"
              step="0.01"
              value={formData.overtime_pay}
              onChange={(e) => handleChange('overtime_pay', parseFloat(e.target.value))}
              placeholder="200.00"
            />
          </FormField>

          <FormField label="Bonus">
            <Input
              type="number"
              step="0.01"
              value={formData.bonus}
              onChange={(e) => handleChange('bonus', parseFloat(e.target.value))}
              placeholder="300.00"
            />
          </FormField>

          <FormField label="Deductions" error={errors.deductions}>
            <Input
              type="number"
              step="0.01"
              value={formData.deductions}
              onChange={(e) => handleChange('deductions', parseFloat(e.target.value))}
              placeholder="100.00"
            />
          </FormField>

          <FormField label="Net Salary">
            <Input
              type="number"
              step="0.01"
              value={formData.net_salary}
              disabled
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Payment Details"
        description="Payment method and date"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Payment Method" required>
            <Select
              value={formData.payment_method}
              onChange={(e) => handleChange('payment_method', e.target.value)}
              options={[
                { value: 'bank_transfer', label: 'Bank Transfer' },
                { value: 'cash', label: 'Cash' },
                { value: 'check', label: 'Check' },
              ]}
            />
          </FormField>

          <FormField label="Payment Date">
            <Input
              type="date"
              value={formData.payment_date}
              onChange={(e) => handleChange('payment_date', e.target.value)}
            />
          </FormField>

          <FormField label="Notes">
            <Input
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Any additional notes..."
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Process Salary' : 'Update Salary'}
        </Button>
      </FormActions>
    </Form>
  )
}
