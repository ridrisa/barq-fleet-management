import { DynamicForm } from './DynamicForm'
import {
  penaltyFormConfig,
  penaltyInitialData,
  penaltyFormSchema,
  getCourierOptions,
  type PenaltyFormData
} from './formConfigs'

export interface PenaltyFormProps {
  initialData?: Partial<PenaltyFormData> & { id?: string }
  onSubmit: (data: PenaltyFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  couriers?: Array<{ id: string; name: string }>
}

export const PenaltyForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  couriers = []
}: PenaltyFormProps) => {
  // Update config with courier options
  const config = {
    ...penaltyFormConfig,
    sections: penaltyFormConfig.sections.map(section => ({
      ...section,
      fields: section.fields.map(field => {
        if (field.name === 'courier_id') {
          return {
            ...field,
            options: getCourierOptions(couriers)
          }
        }
        return field
      })
    }))
  }

  const defaultValues = {
    ...penaltyInitialData,
    ...initialData
  }

  return (
    <DynamicForm
      formConfig={config}
      initialData={defaultValues}
      zodSchema={penaltyFormSchema}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      submitButtonText={initialData?.id ? 'Update Penalty' : 'Add Penalty'}
    />
  )
}

export default PenaltyForm
