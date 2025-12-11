import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

// Define schema inline to avoid complex type inference issues
const userFormSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
  full_name: z.string().min(1, 'Full name is required').min(2, 'Full name must be at least 2 characters'),
  password: z.string().optional(),
  role: z.enum(['admin', 'manager', 'user', 'viewer']),
  is_active: z.boolean(),
  department: z.string().optional(),
  phone: z.string().optional(),
})

type UserFormValues = z.infer<typeof userFormSchema>

export type UserFormData = UserFormValues

export interface UserFormProps {
  initialData?: Partial<UserFormData>
  onSubmit: (data: UserFormData) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
  mode?: 'create' | 'edit'
}

export const UserForm = ({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create',
}: UserFormProps) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<UserFormValues>({
    resolver: zodResolver(userFormSchema),
    defaultValues: {
      email: initialData?.email || '',
      full_name: initialData?.full_name || '',
      password: '',
      role: initialData?.role || 'user',
      is_active: initialData?.is_active !== undefined ? initialData.is_active : true,
      department: initialData?.department || '',
      phone: initialData?.phone || '',
    },
  })

  const onFormSubmit = async (data: UserFormValues) => {
    // Validate password for create mode
    if (mode === 'create' && (!data.password || data.password.length < 8)) {
      return // Form validation will handle this
    }

    // Don't send password field if empty in edit mode
    const submitData = { ...data }
    if (mode === 'edit' && !data.password) {
      delete submitData.password
    }
    await onSubmit(submitData)
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      <FormSection
        title="User Information"
        description="Basic user account details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Email" required error={errors.email?.message}>
            <Input
              type="email"
              {...register('email')}
              placeholder="user@example.com"
              disabled={mode === 'edit' || isLoading}
            />
          </FormField>

          <FormField label="Full Name" required error={errors.full_name?.message}>
            <Input
              {...register('full_name')}
              placeholder="John Doe"
              disabled={isLoading}
            />
          </FormField>

          {mode === 'create' && (
            <FormField label="Password" required error={errors.password?.message}>
              <Input
                type="password"
                {...register('password', {
                  validate: (value) => {
                    if (mode === 'create' && (!value || value.length < 8)) {
                      return 'Password must be at least 8 characters'
                    }
                    return true
                  }
                })}
                placeholder="Minimum 8 characters"
                disabled={isLoading}
              />
            </FormField>
          )}

          {mode === 'edit' && (
            <FormField
              label="New Password"
              error={errors.password?.message}
              helperText="Leave empty to keep current password"
            >
              <Input
                type="password"
                {...register('password', {
                  validate: (value) => {
                    if (value && value.length < 8) {
                      return 'Password must be at least 8 characters if provided'
                    }
                    return true
                  }
                })}
                placeholder="Enter new password or leave empty"
                disabled={isLoading}
              />
            </FormField>
          )}

          <FormField label="Role" required error={errors.role?.message}>
            <Select
              {...register('role')}
              options={[
                { value: 'viewer', label: 'Viewer' },
                { value: 'user', label: 'User' },
                { value: 'manager', label: 'Manager' },
                { value: 'admin', label: 'Admin' },
              ]}
              disabled={isLoading}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Department and contact details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Department" error={errors.department?.message}>
            <Input
              {...register('department')}
              placeholder="e.g., Operations, HR, Finance"
              disabled={isLoading}
            />
          </FormField>

          <FormField label="Phone" error={errors.phone?.message}>
            <Input
              type="tel"
              {...register('phone')}
              placeholder="+971 50 123 4567"
              disabled={isLoading}
            />
          </FormField>

          <div className="md:col-span-2">
            <FormField label="Account Status" error={errors.is_active?.message}>
              <Select
                {...register('is_active', {
                  setValueAs: (v) => v === 'true' || v === true,
                })}
                options={[
                  { value: 'true', label: 'Active' },
                  { value: 'false', label: 'Inactive' },
                ]}
                disabled={isLoading}
              />
            </FormField>
          </div>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : mode === 'create' ? 'Create User' : 'Update User'}
        </Button>
      </FormActions>
    </Form>
  )
}
