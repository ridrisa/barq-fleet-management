import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface AssetFormData {
  asset_name: string
  asset_type: 'vehicle' | 'equipment' | 'device' | 'furniture' | 'other'
  asset_code: string
  purchase_date: string
  value: number
  assigned_to?: string
  condition: 'new' | 'good' | 'fair' | 'poor'
  status: 'available' | 'assigned' | 'maintenance' | 'disposed'
  warranty_expiry?: string
  supplier?: string
  serial_number?: string
  notes?: string
}

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
  const [formData, setFormData] = useState<AssetFormData>({
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
  })

  const [errors, setErrors] = useState<Partial<Record<keyof AssetFormData, string>>>({})

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof AssetFormData, string>> = {}

    if (!formData.asset_name.trim()) {
      newErrors.asset_name = 'Asset name is required'
    }

    if (!formData.asset_code.trim()) {
      newErrors.asset_code = 'Asset code is required'
    }

    if (!formData.purchase_date) {
      newErrors.purchase_date = 'Purchase date is required'
    }

    if (formData.value <= 0) {
      newErrors.value = 'Asset value must be greater than zero'
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

  const handleChange = (field: keyof AssetFormData, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Asset Information"
        description="Enter basic asset details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Asset Name" required error={errors.asset_name}>
            <Input
              value={formData.asset_name}
              onChange={(e) => handleChange('asset_name', e.target.value)}
              placeholder="Delivery Bike"
            />
          </FormField>

          <FormField label="Asset Code" required error={errors.asset_code}>
            <Input
              value={formData.asset_code}
              onChange={(e) => handleChange('asset_code', e.target.value)}
              placeholder="AST-001"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Asset Type" required>
            <Select
              value={formData.asset_type}
              onChange={(e) => handleChange('asset_type', e.target.value)}
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
              value={formData.serial_number}
              onChange={(e) => handleChange('serial_number', e.target.value)}
              placeholder="SN123456789"
            />
          </FormField>

          <FormField label="Purchase Date" required error={errors.purchase_date}>
            <Input
              type="date"
              value={formData.purchase_date}
              onChange={(e) => handleChange('purchase_date', e.target.value)}
            />
          </FormField>

          <FormField label="Value" required error={errors.value}>
            <Input
              type="number"
              step="0.01"
              value={formData.value}
              onChange={(e) => handleChange('value', parseFloat(e.target.value))}
              placeholder="5000.00"
            />
          </FormField>

          <FormField label="Supplier">
            <Input
              value={formData.supplier}
              onChange={(e) => handleChange('supplier', e.target.value)}
              placeholder="Supplier name"
            />
          </FormField>

          <FormField label="Warranty Expiry">
            <Input
              type="date"
              value={formData.warranty_expiry}
              onChange={(e) => handleChange('warranty_expiry', e.target.value)}
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
              value={formData.condition}
              onChange={(e) => handleChange('condition', e.target.value)}
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
              value={formData.status}
              onChange={(e) => handleChange('status', e.target.value)}
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
              value={formData.assigned_to}
              onChange={(e) => handleChange('assigned_to', e.target.value)}
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
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Any additional notes about this asset..."
          />
        </FormField>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create Asset' : 'Update Asset'}
        </Button>
      </FormActions>
    </Form>
  )
}
