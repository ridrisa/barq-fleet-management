import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'
import {
  userCreateSchema,
  userEditSchema,
  type UserCreateFormData,
  type UserEditFormData,
} from '@/schemas/admin.schema'

export type UserFormData = UserCreateFormData | UserEditFormData

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
  const schema = mode === 'create' ? userCreateSchema : userEditSchema

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<UserFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: initialData?.email || '',
      full_name: initialData?.full_name || '',
      password: initialData?.password || '',
      role: initialData?.role || 'user',
      is_active: initialData?.is_active !== undefined ? initialData.is_active : true,
      department: initialData?.department || '',
      phone: initialData?.phone || '',
    },
    mode: 'onBlur',
  })

  const formIsLoading = isLoading || isSubmitting

  const onFormSubmit = async (data: UserFormData) => {
    // Don't send password field if empty in edit mode
    const submitData = { ...data }
    if (mode === 'edit' && !submitData.password) {
      delete submitData.password
    }
    await onSubmit(submitData)
  }

  const isActiveValue = watch('is_active')

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
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Full Name" required error={errors.full_name?.message}>
            <Input
              {...register('full_name')}
              placeholder="John Doe"
            />
          </FormField>

          {mode === 'create' && (
            <FormField label="Password" required error={errors.password?.message}>
              <Input
                type="password"
                {...register('password')}
                placeholder="Minimum 8 characters"
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
                {...register('password')}
                placeholder="Enter new password or leave empty"
              />
            </FormField>
          )}

          <FormField label="Role" required>
            <Select
              {...register('role')}
              options={[
                { value: 'viewer', label: 'Viewer' },
                { value: 'user', label: 'User' },
                { value: 'manager', label: 'Manager' },
                { value: 'admin', label: 'Admin' },
              ]}
            />
          </FormField>
        </div>
      </FormSection>

      <FormSection
        title="Additional Information"
        description="Department and contact details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Department">
            <Input
              {...register('department')}
              placeholder="e.g., Operations, HR, Finance"
            />
          </FormField>

          <FormField label="Phone" error={errors.phone?.message}>
            <Input
              type="tel"
              {...register('phone')}
              placeholder="+971 50 123 4567"
            />
          </FormField>

          <div className="md:col-span-2">
            <FormField label="Account Status">
              <Select
                value={isActiveValue ? 'true' : 'false'}
                onChange={(e) => setValue('is_active', e.target.value === 'true', { shouldValidate: true })}
                options={[
                  { value: 'true', label: 'Active' },
                  { value: 'false', label: 'Inactive' },
                ]}
              />
            </FormField>
          </div>
        </div>
      </FormSection>

      <FormActions>
        <Button type="button" variant="outline" onClick={onCancel} disabled={formIsLoading}>
          Cancel
        </Button>
        <Button type="submit" disabled={formIsLoading}>
          {formIsLoading ? 'Saving...' : mode === 'create' ? 'Create User' : 'Update User'}
        </Button>
      </FormActions>
    </Form>
  )
}
