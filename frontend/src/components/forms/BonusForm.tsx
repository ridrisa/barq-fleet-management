import { DynamicForm } from './DynamicForm'
import {
  bonusFormConfig,
  bonusInitialData,
  bonusValidation,
  getCourierOptions,
  type BonusFormData
} from './formConfigs'

export interface BonusFormProps {
  initialData?: Partial<BonusFormData> & { id?: string }
  onSubmit: (data: BonusFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
  couriers?: Array<{ id: string; name: string }>
}

export const BonusForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  couriers = []
}: BonusFormProps) => {
  // Update config with courier options
  const config = {
    ...bonusFormConfig,
    sections: bonusFormConfig.sections.map(section => ({
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
    ...bonusInitialData,
    ...initialData
  }

  return (
    <DynamicForm
      formConfig={config}
      initialData={defaultValues}
      validationSchema={bonusValidation}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      submitButtonText={initialData?.id ? 'Update Bonus' : 'Add Bonus'}
    />
  )
}

export default BonusForm
