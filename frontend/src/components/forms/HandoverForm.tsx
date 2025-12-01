import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { ChecklistField, type ChecklistItem } from './ChecklistField'
import { SignatureCapture } from './SignatureCapture'
import { defaultHandoverChecklist, type HandoverFormData } from './formConfigs'

export interface HandoverFormProps {
  initialData?: Partial<HandoverFormData> & { id?: string }
  onSubmit: (data: HandoverFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  couriers?: Array<{ id: string; name: string }>
  vehicles?: Array<{ id: string; plate_number: string }>
}

export const HandoverForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  couriers = [],
  vehicles = []
}: HandoverFormProps) => {
  const [formData, setFormData] = useState({
    from_courier: initialData?.from_courier || '',
    to_courier: initialData?.to_courier || '',
    vehicle_id: initialData?.vehicle_id || '',
    handover_date: initialData?.handover_date || new Date().toISOString().split('T')[0],
    notes: initialData?.notes || '',
  })
  const [checklist, setChecklist] = useState<ChecklistItem[]>(
    initialData?.checklist || defaultHandoverChecklist
  )
  const [signature, setSignature] = useState(initialData?.signature || '')
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}
    if (!formData.from_courier) newErrors.from_courier = 'From courier is required'
    if (!formData.to_courier) newErrors.to_courier = 'To courier is required'
    if (!formData.handover_date) newErrors.handover_date = 'Date is required'
    if (formData.from_courier === formData.to_courier && formData.from_courier) {
      newErrors.to_courier = 'Cannot hand over to the same courier'
    }
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    await onSubmit({
      ...formData,
      checklist,
      signature,
    })
  }

  const courierOptions = [
    { value: '', label: 'Select courier...' },
    ...couriers.map(c => ({ value: c.id, label: c.name }))
  ]

  const vehicleOptions = [
    { value: '', label: 'Select vehicle...' },
    ...vehicles.map(v => ({ value: v.id, label: v.plate_number }))
  ]

  const allItemsChecked = checklist.every(item => item.checked)

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="Handover Details"
        description="Specify the couriers involved in this handover"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="From Courier" error={errors.from_courier} required>
            <Select
              value={formData.from_courier}
              onChange={(e) => handleChange('from_courier', e.target.value)}
              options={courierOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="To Courier" error={errors.to_courier} required>
            <Select
              value={formData.to_courier}
              onChange={(e) => handleChange('to_courier', e.target.value)}
              options={courierOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Vehicle" error={errors.vehicle_id}>
            <Select
              value={formData.vehicle_id}
              onChange={(e) => handleChange('vehicle_id', e.target.value)}
              options={vehicleOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Handover Date" error={errors.handover_date} required>
            <Input
              type="date"
              value={formData.handover_date}
              onChange={(e) => handleChange('handover_date', e.target.value)}
              disabled={isLoading}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Handover Checklist"
        description="Complete all items before signing off"
      >
        <ChecklistField
          items={checklist}
          onChange={setChecklist}
          allowAdd={false}
          allowRemove={false}
          title="Required Items"
        />
      </FormSection>

      <FormSection
        title="Signature"
        description="Signature to complete the handover"
      >
        <SignatureCapture
          value={signature}
          onChange={setSignature}
          label="Handover Signature"
          required
          disabled={isLoading}
        />
      </FormSection>

      <FormSection
        title="Additional Notes"
        description="Any other information about this handover"
      >
        <FormField label="Notes" error={errors.notes}>
          <Textarea
            value={formData.notes}
            onChange={(e) => handleChange('notes', e.target.value)}
            placeholder="Add any additional notes about this handover..."
            rows={4}
            disabled={isLoading}
          />
        </FormField>
      </FormSection>

      {!allItemsChecked && (
        <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            Please complete all checklist items before submitting the handover.
          </p>
        </div>
      )}

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading || !allItemsChecked || !signature}>
          {isLoading ? 'Saving...' : initialData?.id ? 'Update Handover' : 'Complete Handover'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default HandoverForm
