import { DynamicForm } from './DynamicForm'
import {
  serviceLevelFormConfig,
  serviceLevelInitialData,
  serviceLevelValidation,
  type ServiceLevelFormData
} from './formConfigs'

export interface ServiceLevelFormProps {
  initialData?: Partial<ServiceLevelFormData> & { id?: string }
  onSubmit: (data: ServiceLevelFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
}

export const ServiceLevelForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false
}: ServiceLevelFormProps) => {
  const defaultValues = {
    ...serviceLevelInitialData,
    ...initialData
  }

  return (
    <DynamicForm
      formConfig={serviceLevelFormConfig}
      initialData={defaultValues}
      validationSchema={serviceLevelValidation}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      submitButtonText={initialData?.id ? 'Update SLA' : 'Create SLA'}
    />
  )
}

export default ServiceLevelForm
