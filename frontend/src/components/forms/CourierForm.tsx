import { DynamicForm } from './DynamicForm'
import { courierFormConfig, courierSchema } from '@/config/forms/courierFormConfig'
import { CourierFormData } from '@/schemas'

export interface CourierFormProps {
  initialData?: Partial<CourierFormData>
  onSubmit: (data: CourierFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const CourierForm = ({
  initialData = {},
  onSubmit,
  onCancel,
  mode = 'create',
}: CourierFormProps) => {
  const defaultData: CourierFormData = {
    employee_id: '',
    name: '',
    phone: '',
    email: '',
    status: 'active',
    license_number: '',
    license_expiry: '',
    national_id: '',
    joining_date: '',
    emergency_contact: '',
    address: '',
    city: '',
    bank_name: '',
    bank_account_number: '',
    iban: '',
    ...initialData,
  }

  const finalFormConfig = { ...courierFormConfig }
  // Disable employee_id field in edit mode
  if (mode === 'edit') {
    const basicInfoSection = finalFormConfig.sections.find(s => s.title === 'Basic Information')
    const employeeIdField = basicInfoSection?.fields.find(f => f.name === 'employee_id')
    if (employeeIdField) {
      employeeIdField.disabled = true
    }
  }

  return (
    <DynamicForm
      formConfig={finalFormConfig}
      initialData={defaultData}
      zodSchema={courierSchema}
      onSubmit={onSubmit}
      onCancel={onCancel}
      submitButtonText={mode === 'create' ? 'Create Courier' : 'Update Courier'}
    />
  )
}

// Re-export CourierFormData for backwards compatibility
export type { CourierFormData } from '@/schemas'
