import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface LoanFormData {
  courier_id: string
  amount: number
  installments: number
  installment_amount: number
  start_date: string
  end_date?: string
  interest_rate?: number
  reason?: string
  status: 'pending' | 'approved' | 'active' | 'completed' | 'rejected'
  approved_by?: string
  notes?: string
}

export interface LoanFormProps {
  initialData?: Partial<LoanFormData>
  onSubmit: (data: LoanFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const LoanForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: LoanFormProps) => {
  const [formData, setFormData] = useState<LoanFormData>({
    courier_id: initialData?.courier_id || '',
    amount: initialData?.amount || 0,
    installments: initialData?.installments || 12,
    installment_amount: initialData?.installment_amount || 0,
    start_date: initialData?.start_date || '',
    end_date: initialData?.end_date || '',
    interest_rate: initialData?.interest_rate || 0,
    reason: initialData?.reason || '',
    status: initialData?.status || 'pending',
    approved_by: initialData?.approved_by || '',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof LoanFormData, string>>>({})

  const calculateInstallmentAmount = (amount: number, installments: number, interestRate: number = 0): number => {
    if (installments === 0) return 0
    const totalAmount = amount + (amount * interestRate / 100)
    return Math.round((totalAmount / installments) * 100) / 100
  }

  const calculateEndDate = (startDate: string, installments: number): string => {
    if (!startDate || installments === 0) return ''
    const start = new Date(startDate)
    start.setMonth(start.getMonth() + installments)
    return start.toISOString().split('T')[0]
  }

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof LoanFormData, string>> = {}

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (formData.amount <= 0) {
      newErrors.amount = 'Loan amount must be greater than zero'
    }

    if (formData.installments <= 0) {
      newErrors.installments = 'Number of installments must be at least 1'
    }

    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required'
    }

    if (formData.interest_rate && formData.interest_rate < 0) {
      newErrors.interest_rate = 'Interest rate cannot be negative'
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

  const handleChange = (field: keyof LoanFormData, value: string | number) => {
    const updatedData = { ...formData, [field]: value }

    // Auto-calculate installment amount when amount, installments, or interest rate changes
    if (field === 'amount' || field === 'installments' || field === 'interest_rate') {
      updatedData.installment_amount = calculateInstallmentAmount(
        field === 'amount' ? value as number : formData.amount,
        field === 'installments' ? value as number : formData.installments,
        field === 'interest_rate' ? value as number : formData.interest_rate
      )
    }

    // Auto-calculate end date when start date or installments change
    if (field === 'start_date' || field === 'installments') {
      updatedData.end_date = calculateEndDate(
        field === 'start_date' ? value as string : formData.start_date,
        field === 'installments' ? value as number : formData.installments
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
        title="Loan Information"
        description="Create a loan request for a courier"
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

          <FormField label="Loan Amount" required error={errors.amount}>
            <Input
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) => handleChange('amount', parseFloat(e.target.value))}
              placeholder="10000.00"
            />
          </FormField>

          <FormField label="Number of Installments" required error={errors.installments}>
            <Input
              type="number"
              value={formData.installments}
              onChange={(e) => handleChange('installments', parseInt(e.target.value))}
              placeholder="12"
            />
          </FormField>

          <FormField label="Interest Rate (%)" error={errors.interest_rate}>
            <Input
              type="number"
              step="0.01"
              value={formData.interest_rate}
              onChange={(e) => handleChange('interest_rate', parseFloat(e.target.value))}
              placeholder="0.00"
            />
          </FormField>

          <FormField label="Installment Amount">
            <Input
              type="number"
              step="0.01"
              value={formData.installment_amount}
              disabled
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'approved', label: 'Approved' },
                { value: 'active', label: 'Active' },
                { value: 'completed', label: 'Completed' },
                { value: 'rejected', label: 'Rejected' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Duration"
        description="Loan period and repayment schedule"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Start Date" required error={errors.start_date}>
            <Input
              type="date"
              value={formData.start_date}
              onChange={(e) => handleChange('start_date', e.target.value)}
            />
          </FormField>

          <FormField label="End Date (Calculated)">
            <Input
              type="date"
              value={formData.end_date}
              disabled
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Details"
        description="Reason and approval information"
      >
        <FormField label="Reason">
          <Input
            value={formData.reason}
            onChange={(e) => handleChange('reason', e.target.value)}
            placeholder="Purpose of the loan..."
          />
        </FormField>

        <FormField label="Approved By">
          <Input
            value={formData.approved_by}
            onChange={(e) => handleChange('approved_by', e.target.value)}
            placeholder="Manager or approver name"
          />
        </FormField>

        <FormField label="Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Loan' : 'Update Loan'}
        </Button>
      </FormActions>
    </Form>
  )
}
