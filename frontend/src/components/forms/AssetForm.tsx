import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import { assetFormSchema, type AssetFormData } from '@/schemas/admin.schema'

export type { AssetFormData }

export interface AssetFormProps {
  initialData?: Partial<AssetFormData>
  onSubmit: (data: AssetFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
  couriers?: Array<{ id: string; name: string }>
}

export const AssetForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
  couriers = [],
}: AssetFormProps) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<AssetFormData>({
    resolver: zodResolver(assetFormSchema),
    defaultValues: {
      asset_name: initialData?.asset_name || '',
      asset_type: initialData?.asset_type || 'equipment',
      asset_code: initialData?.asset_code || '',
      purchase_date: initialData?.purchase_date || '',
      value: initialData?.value || 0,
      assigned_to: initialData?.assigned_to || '',
      condition: initialData?.condition || 'new',
      status: initialData?.status || 'available',
      warranty_expiry: initialData?.warranty_expiry || '',
      supplier: initialData?.supplier || '',
      serial_number: initialData?.serial_number || '',
      notes: initialData?.notes || '',
    },
    mode: 'onBlur',
  })

  const formIsLoading = isLoading || isSubmitting

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <FormSection
        title="Asset Information"
        description="Enter basic asset details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Asset Name" required error={errors.asset_name?.message}>
            <Input
              {...register('asset_name')}
              placeholder="Delivery Bike"
            />
          </FormField>

          <FormField label="Asset Code" required error={errors.asset_code?.message}>
            <Input
              {...register('asset_code')}
              placeholder="AST-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Asset Type" required>
            <Select
              {...register('asset_type')}
              options={[
                { value: 'vehicle', label: 'Vehicle' },
                { value: 'equipment', label: 'Equipment' },
                { value: 'device', label: 'Device' },
                { value: 'furniture', label: 'Furniture' },
                { value: 'other', label: 'Other' },
              ]}
            />
          </FormField>

          <FormField label="Serial Number">
            <Input
              {...register('serial_number')}
              placeholder="SN123456789"
            />
          </FormField>

          <FormField label="Purchase Date" required error={errors.purchase_date?.message}>
            <Input
              type="date"
              {...register('purchase_date')}
            />
          </FormField>

          <FormField label="Value" required error={errors.value?.message}>
            <Input
              type="number"
              step="0.01"
              {...register('value', { valueAsNumber: true })}
              placeholder="5000.00"
            />
          </FormField>

          <FormField label="Supplier">
            <Input
              {...register('supplier')}
              placeholder="Supplier name"
            />
          </FormField>

          <FormField label="Warranty Expiry">
            <Input
              type="date"
              {...register('warranty_expiry')}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Status & Assignment"
        description="Current status and assignment information"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Condition" required>
            <Select
              {...register('condition')}
              options={[
                { value: 'new', label: 'New' },
                { value: 'good', label: 'Good' },
                { value: 'fair', label: 'Fair' },
                { value: 'poor', label: 'Poor' },
              ]}
            />
          </FormField>

          <FormField label="Status" required>
            <Select
              {...register('status')}
              options={[
                { value: 'available', label: 'Available' },
                { value: 'assigned', label: 'Assigned' },
                { value: 'maintenance', label: 'Maintenance' },
                { value: 'disposed', label: 'Disposed' },
              ]}
            />
          </FormField>

          <FormField label="Assigned To">
            <Select
              value={watch('assigned_to') || ''}
              onChange={(e) => setValue('assigned_to', e.target.value, { shouldValidate: true })}
              options={[
                { value: '', label: 'Not assigned' },
                ...couriers.map((c) => ({ value: c.id, label: c.name })),
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
            {...register('notes')}
            placeholder="Any additional notes about this asset..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={formIsLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={formIsLoading}>
          {formIsLoading ? 'Saving...' : mode === 'create' ? 'Create Asset' : 'Update Asset'}
        </Button>
      </FormActions>
    </Form>
  )
}
