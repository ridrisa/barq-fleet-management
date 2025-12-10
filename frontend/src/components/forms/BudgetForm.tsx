import { DynamicForm } from './DynamicForm'
import {
  budgetFormConfig,
  budgetInitialData,
  budgetFormSchema,
  type BudgetFormData
} from './formConfigs'

export interface BudgetFormProps {
  initialData?: Partial<BudgetFormData> & { id?: string }
  onSubmit: (data: BudgetFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
}

export const BudgetForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false
}: BudgetFormProps) => {
  const defaultValues = {
    ...budgetInitialData,
    ...initialData
  }

  return (
    <DynamicForm
      formConfig={budgetFormConfig}
      initialData={defaultValues}
      zodSchema={budgetFormSchema}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      submitButtonText={initialData?.id ? 'Update Budget' : 'Create Budget'}
    />
  )
}

export default BudgetForm
