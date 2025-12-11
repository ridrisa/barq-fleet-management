import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Form, FormField, FormSection, FormActions } from './Form'
import { QualityChecklistField, type ChecklistItem } from './ChecklistField'
import { Checkbox } from './Checkbox'
import { qualityControlSchema, type QualityControlFormData } from '@/schemas'

export interface QualityControlFormProps {
  initialData?: Partial<QualityControlFormData & { checklist?: ChecklistItem[] }> & { id?: string }
  onSubmit: (data: QualityControlFormData & { checklist: ChecklistItem[] }) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  inspectors?: Array<{ id: string; name: string }>
}

const defaultChecklist: ChecklistItem[] = [
  { id: '1', label: 'Package properly sealed', checked: false },
  { id: '2', label: 'Correct labeling verified', checked: false },
  { id: '3', label: 'Weight matches documentation', checked: false },
  { id: '4', label: 'No visible damage', checked: false },
  { id: '5', label: 'Temperature requirements met', checked: false },
  { id: '6', label: 'Delivery timeframe acceptable', checked: false },
  { id: '7', label: 'Customer signature obtained', checked: false },
  { id: '8', label: 'Photo documentation complete', checked: false },
]

export const QualityControlForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  inspectors = []
}: QualityControlFormProps) => {
  const [checklist, setChecklist] = useState<ChecklistItem[]>(
    initialData?.checklist || defaultChecklist
  )

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<QualityControlFormData>({
    resolver: zodResolver(qualityControlSchema),
    defaultValues: {
      delivery_id: initialData?.delivery_id || '',
      inspector: initialData?.inspector || '',
      check_date: initialData?.check_date || new Date().toISOString().split('T')[0],
      passed: initialData?.passed ?? false,
      issues: initialData?.issues || '',
      corrective_action: initialData?.corrective_action || '',
      status: initialData?.status || 'pending',
    },
  })

  const passed = watch('passed')

  const inspectorOptions = [
    { value: '', label: 'Select inspector...' },
    ...inspectors.map(i => ({ value: i.id, label: i.name }))
  ]

  const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
  ]

  const passedCount = checklist.filter(item => item.checked).length
  const totalCount = checklist.length
  const passRate = totalCount > 0 ? Math.round((passedCount / totalCount) * 100) : 0

  const onFormSubmit = async (data: QualityControlFormData) => {
    await onSubmit({
      ...data,
      checklist,
    })
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="Inspection Details"
        description="Enter the delivery information for quality check"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Delivery ID" error={errors.delivery_id?.message} required>
            <Input
              {...register('delivery_id')}
              placeholder="Enter delivery ID..."
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Inspector" error={errors.inspector?.message} required>
            <Select
              {...register('inspector')}
              options={inspectorOptions}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Inspection Date" error={errors.check_date?.message} required>
            <Input
              type="date"
              {...register('check_date')}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Status" error={errors.status?.message}>
            <Select
              {...register('status')}
              options={statusOptions}
              disabled={isLoading}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Quality Checklist"
        description="Verify each quality criterion"
      >
        <QualityChecklistField
          items={checklist}
          onChange={setChecklist}
        />

        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Pass Rate</span>
            <span className={`text-lg font-bold ${passRate >= 80 ? 'text-green-600' : passRate >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
              {passRate}%
            </span>
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${passRate >= 80 ? 'bg-green-500' : passRate >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
              style={{ width: `${passRate}%` }}
            />
          </div>
        </div>
      </FormSection>

      <FormSection
        title="Result"
        description="Final inspection result and findings"
      >
        <div className="space-y-4">
          <FormField label="Passed Inspection" error={errors.passed?.message}>
            <Checkbox
              checked={passed}
              onChange={(e) => setValue('passed', e.target.checked)}
              label="Delivery passed all quality requirements"
            />
          </FormField>

          <FormField label="Issues Found" error={errors.issues?.message}>
            <Textarea
              {...register('issues')}
              placeholder="Describe any issues found during inspection..."
              rows={3}
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Corrective Action" error={errors.corrective_action?.message}>
            <Textarea
              {...register('corrective_action')}
              placeholder="Describe corrective actions to be taken..."
              rows={3}
              disabled={isLoading}
            />
          </FormField>
        </div>
      </FormSection>

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : initialData?.id ? 'Update Inspection' : 'Submit Inspection'}
        </Button>
      </FormActions>
    </Form>
  )
}

export default QualityControlForm

// Re-export the type for backward compatibility
export type { QualityControlFormData as QualityControlFormDataType }
