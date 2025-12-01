import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface CODFormData {
  delivery_id: string
  courier_id: string
  amount: number
  currency: 'SAR' | 'USD' | 'EUR'
  collected: boolean
  collection_date?: string
  reconciled: boolean
  reconciliation_date?: string
  payment_method: 'cash' | 'card' | 'online'
  reference_number?: string
  status: 'pending' | 'collected' | 'reconciled' | 'disputed'
  notes?: string
}

export interface CODFormProps {
  initialData?: Partial<CODFormData>
  onSubmit: (data: CODFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const CODForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: CODFormProps) => {
  const [formData, setFormData] = useState<CODFormData>({
    delivery_id: initialData?.delivery_id || '',
    courier_id: initialData?.courier_id || '',
    amount: initialData?.amount || 0,
    currency: initialData?.currency || 'SAR',
    collected: initialData?.collected || false,
    collection_date: initialData?.collection_date || '',
    reconciled: initialData?.reconciled || false,
    reconciliation_date: initialData?.reconciliation_date || '',
    payment_method: initialData?.payment_method || 'cash',
    reference_number: initialData?.reference_number || '',
    status: initialData?.status || 'pending',
    notes: initialData?.notes || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof CODFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof CODFormData, string>> = {}

    if (!formData.delivery_id.trim()) {
      newErrors.delivery_id = 'Delivery ID is required'
    }

    if (!formData.courier_id) {
      newErrors.courier_id = 'Courier is required'
    }

    if (formData.amount <= 0) {
      newErrors.amount = 'Amount must be greater than zero'
    }

    if (formData.collected && !formData.collection_date) {
      newErrors.collection_date = 'Collection date is required when marked as collected'
    }

    if (formData.reconciled && !formData.reconciliation_date) {
      newErrors.reconciliation_date = 'Reconciliation date is required when marked as reconciled'
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

  const handleChange = (field: keyof CODFormData, value: string | number | boolean) => {
    const updatedData = { ...formData, [field]: value }

    // Auto-update status based on collected and reconciled flags
    if (field === 'collected' || field === 'reconciled') {
      if (updatedData.reconciled) {
        updatedData.status = 'reconciled'
      } else if (updatedData.collected) {
        updatedData.status = 'collected'
      } else {
        updatedData.status = 'pending'
      }
    }

    // Set collection date when marking as collected
    if (field === 'collected' && value === true && !formData.collection_date) {
      updatedData.collection_date = new Date().toISOString().split('T')[0]
    }

    // Set reconciliation date when marking as reconciled
    if (field === 'reconciled' && value === true && !formData.reconciliation_date) {
      updatedData.reconciliation_date = new Date().toISOString().split('T')[0]
    }

    setFormData(updatedData)
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="COD Transaction"
        description="Cash on Delivery transaction details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Delivery ID" required error={errors.delivery_id}>
            <Input
              value={formData.delivery_id}
              onChange={(e) => handleChange('delivery_id', e.target.value)}
              placeholder="DEL-123456"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Courier" required error={errors.courier_id}>
            <Select
              value={formData.courier_id}
              onChange={(e) => handleChange('courier_id', e.target.value)}
              options={[
                { value: '', label: 'Select a courier...' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField label="Amount" required error={errors.amount}>
            <Input
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) => handleChange('amount', parseFloat(e.target.value))}
              placeholder="100.00"
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

          <FormField label="Payment Method" required>
            <Select
              value={formData.payment_method}
              onChange={(e) => handleChange('payment_method', e.target.value)}
              options={[
                { value: 'cash', label: 'Cash' },
                { value: 'card', label: 'Card' },
                { value: 'online', label: 'Online' },
              ]}
            />
          </FormField>

          <FormField label="Reference Number">
            <Input
              value={formData.reference_number}
              onChange={(e) => handleChange('reference_number', e.target.value)}
              placeholder="REF-123456"
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Collection Status"
        description="Payment collection information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Collected">
            <Select
              value={formData.collected ? 'true' : 'false'}
              onChange={(e) => handleChange('collected', e.target.value === 'true')}
              options={[
                { value: 'false', label: 'Not Collected' },
                { value: 'true', label: 'Collected' },
              ]}
            />
          </FormField>

          {formData.collected && (
            <FormField label="Collection Date" error={errors.collection_date}>
              <Input
                type="date"
                value={formData.collection_date}
                onChange={(e) => handleChange('collection_date', e.target.value)}
              />
            </FormField>
          )}

          <FormField label="Reconciled">
            <Select
              value={formData.reconciled ? 'true' : 'false'}
              onChange={(e) => handleChange('reconciled', e.target.value === 'true')}
              options={[
                { value: 'false', label: 'Not Reconciled' },
                { value: 'true', label: 'Reconciled' },
              ]}
            />
          </FormField>

          {formData.reconciled && (
            <FormField label="Reconciliation Date" error={errors.reconciliation_date}>
              <Input
                type="date"
                value={formData.reconciliation_date}
                onChange={(e) => handleChange('reconciliation_date', e.target.value)}
              />
            </FormField>
          )}

          <FormField label="Status" required>
            <Select
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
              options={[
                { value: 'pending', label: 'Pending' },
                { value: 'collected', label: 'Collected' },
                { value: 'reconciled', label: 'Reconciled' },
                { value: 'disputed', label: 'Disputed' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Notes and comments"
      >
        <FormField label="Notes">
          <Input
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes about this COD transaction..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Record COD' : 'Update COD'}
        </Button>
      </FormActions>
    </Form>
  )
}
