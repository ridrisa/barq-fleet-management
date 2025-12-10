import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { ChecklistField, type ChecklistItem } from './ChecklistField'
import { SignatureCapture } from './SignatureCapture'
import { handoverSchema, defaultHandoverChecklist, type HandoverFormData } from '@/schemas/fleet.schema'

// HandoverFormData is re-exported from formConfigs.ts to avoid duplicate exports

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
  const [checklist, setChecklist] = useState<ChecklistItem[]>(
    initialData?.checklist || defaultHandoverChecklist
  )
  const [signature, setSignature] = useState(initialData?.signature || '')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<HandoverFormData>({
    resolver: zodResolver(handoverSchema),
    defaultValues: {
      from_courier: initialData?.from_courier || '',
      to_courier: initialData?.to_courier || '',
      vehicle_id: initialData?.vehicle_id || '',
      handover_date: initialData?.handover_date || new Date().toISOString().split('T')[0],
      notes: initialData?.notes || '',
    },
  })

  const onFormSubmit = async (data: HandoverFormData) => {
    await onSubmit({
      ...data,
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
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Handover Details"
        description="Specify the couriers involved in this handover"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="From Courier" error={errors.from_courier?.message} required>
            <Select
              {...register('from_courier')}
              options={courierOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="To Courier" error={errors.to_courier?.message} required>
            <Select
              {...register('to_courier')}
              options={courierOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Vehicle" error={errors.vehicle_id?.message}>
            <Select
              {...register('vehicle_id')}
              options={vehicleOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Handover Date" error={errors.handover_date?.message} required>
            <Input
              type="date"
              {...register('handover_date')}
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
        <FormField label="Notes" error={errors.notes?.message}>
          <Textarea
            {...register('notes')}
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
