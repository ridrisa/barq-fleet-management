import { DynamicForm } from './DynamicForm'
import {
  expenseFormConfig,
  expenseInitialData,
  expenseFormSchema,
  type ExpenseFormData
} from './formConfigs'

export interface ExpenseFormProps {
  initialData?: Partial<ExpenseFormData> & { id?: string }
  onSubmit: (data: ExpenseFormData) => Promise<void> | void
  onCancel?: () => void
  isLoading?: boolean
}

export const ExpenseForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false
}: ExpenseFormProps) => {
  const defaultValues = {
    ...expenseInitialData,
    ...initialData
  }

  return (
    <DynamicForm
      formConfig={expenseFormConfig}
      initialData={defaultValues}
      zodSchema={expenseFormSchema}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
      submitButtonText={initialData?.id ? 'Update Expense' : 'Add Expense'}
    />
  )
}

export default ExpenseForm
