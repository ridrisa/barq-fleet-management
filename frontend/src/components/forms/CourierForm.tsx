import { DynamicForm } from './DynamicForm';
import { courierFormConfig, validationSchema } from '@/config/forms/courierFormConfig';

export interface CourierFormData {
  employee_id: string;
  name: string;
  phone: string;
  email: string;
  license_number?: string;
  license_expiry?: string;
  status?: 'active' | 'on_leave' | 'terminated';
  joining_date?: string;
  emergency_contact?: string;
  address?: string;
}

export interface CourierFormProps {
  initialData?: Partial<CourierFormData>;
  onSubmit: (data: CourierFormData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
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
    license_number: '',
    license_expiry: '',
    status: 'active',
    joining_date: '',
    emergency_contact: '',
    address: '',
    ...initialData,
  };

  const finalFormConfig = { ...courierFormConfig };
  // Disable employee_id field in edit mode
  if (mode === 'edit') {
    const basicInfoSection = finalFormConfig.sections.find(s => s.title === 'Basic Information');
    const employeeIdField = basicInfoSection?.fields.find(f => f.name === 'employee_id');
    if (employeeIdField) {
        employeeIdField.disabled = true;
    }
  }

  return (
    <DynamicForm
      formConfig={finalFormConfig}
      initialData={defaultData}
      validationSchema={validationSchema}
      onSubmit={onSubmit}
      onCancel={onCancel}
      submitButtonText={mode === 'create' ? 'Create Courier' : 'Update Courier'}
    />
  );
};
