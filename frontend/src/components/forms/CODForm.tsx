import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useEffect } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { codSchema, type CODFormData } from '@/schemas/fleet.schema'

export type { CODFormData }

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
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    control,
    formState: { errors },
  } = useForm<CODFormData>({
    resolver: zodResolver(codSchema),
    defaultValues: {
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
    },
  })

  const collected = watch('collected')
  const reconciled = watch('reconciled')
  const collectionDate = watch('collection_date')
  const reconciliationDate = watch('reconciliation_date')

  // Auto-update status based on collected and reconciled flags
  useEffect(() => {
    if (reconciled) {
      setValue('status', 'reconciled')
    } else if (collected) {
      setValue('status', 'collected')
    }
  }, [collected, reconciled, setValue])

  // Set collection date when marking as collected
  useEffect(() => {
    if (collected && !collectionDate) {
      setValue('collection_date', new Date().toISOString().split('T')[0])
    }
  }, [collected, collectionDate, setValue])

  // Set reconciliation date when marking as reconciled
  useEffect(() => {
    if (reconciled && !reconciliationDate) {
      setValue('reconciliation_date', new Date().toISOString().split('T')[0])
    }
  }, [reconciled, reconciliationDate, setValue])

  const onFormSubmit = async (data: CODFormData) => {
    await onSubmit(data)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="COD Transaction"
        description="Cash on Delivery transaction details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Delivery ID" required error={errors.delivery_id?.message}>
            <Input
              {...register('delivery_id')}
              placeholder="DEL-123456"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Courier" required error={errors.courier_id?.message}>
            <Select
              {...register('courier_id')}
              options={[
                { value: '', label: 'Select a courier...' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
              ]}
            />
          </FormField>

          <FormField label="Amount" required error={errors.amount?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('amount', { valueAsNumber: true })}
              placeholder="100.00"
            />
          </FormField>

          <FormField label="Currency" required error={errors.currency?.message}>
            <Select
              {...register('currency')}
              options={[
                { value: 'SAR', label: 'SAR (Saudi Riyal)' },
                { value: 'USD', label: 'USD (US Dollar)' },
                { value: 'EUR', label: 'EUR (Euro)' },
              ]}
            />
          </FormField>

          <FormField label="Payment Method" required error={errors.payment_method?.message}>
            <Select
              {...register('payment_method')}
              options={[
                { value: 'cash', label: 'Cash' },
                { value: 'card', label: 'Card' },
                { value: 'online', label: 'Online' },
              ]}
            />
          </FormField>

          <FormField label="Reference Number" error={errors.reference_number?.message}>
            <Input
              {...register('reference_number')}
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
            <Controller
              name="collected"
              control={control}
              render={({ field }) => (
                <Select
                  value={field.value ? 'true' : 'false'}
                  onChange={(e) => field.onChange(e.target.value === 'true')}
                  options={[
                    { value: 'false', label: 'Not Collected' },
                    { value: 'true', label: 'Collected' },
                  ]}
                />
              )}
            />
          </FormField>

          {collected && (
            <FormField label="Collection Date" error={errors.collection_date?.message}>
              <Input
                type="date"
                {...register('collection_date')}
              />
            </FormField>
          )}

          <FormField label="Reconciled">
            <Controller
              name="reconciled"
              control={control}
              render={({ field }) => (
                <Select
                  value={field.value ? 'true' : 'false'}
                  onChange={(e) => field.onChange(e.target.value === 'true')}
                  options={[
                    { value: 'false', label: 'Not Reconciled' },
                    { value: 'true', label: 'Reconciled' },
                  ]}
                />
              )}
            />
          </FormField>

          {reconciled && (
            <FormField label="Reconciliation Date" error={errors.reconciliation_date?.message}>
              <Input
                type="date"
                {...register('reconciliation_date')}
              />
            </FormField>
          )}

          <FormField label="Status" required error={errors.status?.message}>
            <Select
              {...register('status')}
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
        <FormField label="Notes" error={errors.notes?.message}>
          <Input
            {...register('notes')}
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
