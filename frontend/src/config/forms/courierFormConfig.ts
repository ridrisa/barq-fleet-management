import { FormConfig } from '@/components/forms/DynamicForm'
import { courierSchema } from '@/schemas'

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
            { value: 'suspended', label: 'Suspended' },
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
        { name: 'national_id', label: 'National ID (10 digits)', type: 'text', placeholder: '1234567890' },
      ],
    },
    {
      title: 'Additional Information',
      description: 'Emergency contact and address',
      fields: [
        { name: 'emergency_contact', label: 'Emergency Contact', type: 'tel', placeholder: '+971 50 999 8888' },
        { name: 'address', label: 'Address', type: 'textarea', placeholder: 'Dubai, UAE' },
        { name: 'city', label: 'City', type: 'text', placeholder: 'Dubai' },
      ],
    },
    {
      title: 'Banking Information',
      description: 'Bank account details for salary payments',
      fields: [
        { name: 'bank_name', label: 'Bank Name', type: 'text', placeholder: 'Emirates NBD' },
        { name: 'bank_account_number', label: 'Account Number', type: 'text', placeholder: '1234567890' },
        { name: 'iban', label: 'IBAN', type: 'text', placeholder: 'AE070331234567890123456' },
      ],
    },
  ],
}

// Export the Zod schema for validation
export { courierSchema }
