import { FormConfig } from '@/components/forms/DynamicForm';
import { ValidationSchema } from '@/hooks/useForm';
import { CourierFormData } from '@/components/forms/CourierForm';

export const courierFormConfig: FormConfig = {
  sections: [
    {
      title: 'Basic Information',
      description: "Enter the courier's basic details",
      fields: [
        { name: 'employee_id', label: 'Employee ID', type: 'text', required: true, placeholder: 'EMP-001' },
        { name: 'name', label: 'Full Name', type: 'text', required: true, placeholder: 'John Doe' },
        { name: 'phone', label: 'Phone', type: 'tel', required: true, placeholder: '+971 50 123 4567' },
        { name: 'email', label: 'Email', type: 'email', required: true, placeholder: 'john.doe@example.com' },
        {
          name: 'status',
          label: 'Status',
          type: 'select',
          options: [
            { value: 'active', label: 'Active' },
            { value: 'on_leave', label: 'On Leave' },
            { value: 'terminated', label: 'Terminated' },
          ],
        },
        { name: 'joining_date', label: 'Joining Date', type: 'date' },
      ],
    },
    {
      title: 'License Information',
      description: "Driver's license details",
      fields: [
        { name: 'license_number', label: 'License Number', type: 'text', placeholder: 'DL-123456' },
        { name: 'license_expiry', label: 'License Expiry', type: 'date' },
      ],
    },
    {
      title: 'Additional Information',
      description: 'Emergency contact and address',
      fields: [
        { name: 'emergency_contact', label: 'Emergency Contact', type: 'tel', placeholder: '+971 50 999 8888' },
        { name: 'address', label: 'Address', type: 'textarea', placeholder: 'Dubai, UAE' },
      ],
    },
  ],
};

export const validationSchema: ValidationSchema<CourierFormData> = {
    employee_id: (data) => (!data.employee_id?.trim() ? 'Employee ID is required' : null),
    name: (data) => {
        if (!data.name?.trim()) return 'Name is required';
        if (data.name.trim().length < 2) return 'Name must be at least 2 characters';
        return null;
    },
    phone: (data) => {
        if (!data.phone?.trim()) return 'Phone is required';
        if (!/^\+?[\d\s-()]+$/.test(data.phone)) return 'Invalid phone number format';
        return null;
    },
    email: (data) => {
        if (!data.email?.trim()) return 'Email is required';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) return 'Invalid email format';
        return null;
    },
    license_expiry: (data) => {
        if (data.license_expiry && new Date(data.license_expiry) < new Date()) {
            return 'License has expired';
        }
        return null;
    }
};
