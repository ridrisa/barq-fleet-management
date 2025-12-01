import { useState, FormEvent } from 'react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface UserFormData {
  email: string
  full_name: string
  password?: string
  role: 'admin' | 'manager' | 'user' | 'viewer'
  is_active: boolean
  department?: string
  phone?: string
}

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
  const [formData, setFormData] = useState<UserFormData>({
    email: initialData?.email || '',
    full_name: initialData?.full_name || '',
    password: initialData?.password || '',
    role: initialData?.role || 'user',
    is_active: initialData?.is_active !== undefined ? initialData.is_active : true,
    department: initialData?.department || '',
    phone: initialData?.phone || '',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof UserFormData, string>>>({})

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const validatePhone = (phone: string): boolean => {
    if (!phone) return true // Phone is optional
    const phoneRegex = /^[+]?[\d\s\-()]{10,}$/
    return phoneRegex.test(phone)
  }

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof UserFormData, string>> = {}

    if (!formData.email || formData.email.trim().length === 0) {
      newErrors.email = 'Email is required'
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    if (!formData.full_name || formData.full_name.trim().length === 0) {
      newErrors.full_name = 'Full name is required'
    }

    if (formData.full_name.length < 2) {
      newErrors.full_name = 'Full name must be at least 2 characters'
    }

    // Password validation only for create mode
    if (mode === 'create') {
      if (!formData.password || formData.password.length === 0) {
        newErrors.password = 'Password is required'
      } else if (formData.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters'
      }
    } else if (mode === 'edit' && formData.password && formData.password.length < 8) {
      // If editing and password is provided, validate it
      newErrors.password = 'Password must be at least 8 characters if provided'
    }

    if (formData.phone && !validatePhone(formData.phone)) {
      newErrors.phone = 'Please enter a valid phone number'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()

    if (!validate()) {
      return
    }

    // Don't send password field if empty in edit mode
    const submitData = { ...formData }
    if (mode === 'edit' && !submitData.password) {
      delete submitData.password
    }

    await onSubmit(submitData)
  }

  const handleChange = (field: keyof UserFormData, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Form onSubmit={handleSubmit}>
      <FormSection
        title="User Information"
        description="Basic user account details"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField label="Email" required error={errors.email}>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="user@example.com"
              disabled={mode === 'edit'}
            />
          </FormField>

          <FormField label="Full Name" required error={errors.full_name}>
            <Input
              value={formData.full_name}
              onChange={(e) => handleChange('full_name', e.target.value)}
              placeholder="John Doe"
            />
          </FormField>

          {mode === 'create' && (
            <FormField label="Password" required error={errors.password}>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="Minimum 8 characters"
              />
            </FormField>
          )}

          {mode === 'edit' && (
            <FormField
              label="New Password"
              error={errors.password}
              helperText="Leave empty to keep current password"
            >
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => handleChange('password', e.target.value)}
                placeholder="Enter new password or leave empty"
              />
            </FormField>
          )}

          <FormField label="Role" required>
            <Select
              value={formData.role}
              onChange={(e) => handleChange('role', e.target.value)}
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
              value={formData.department}
              onChange={(e) => handleChange('department', e.target.value)}
              placeholder="e.g., Operations, HR, Finance"
            />
          </FormField>

          <FormField label="Phone" error={errors.phone}>
            <Input
              type="tel"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              placeholder="+971 50 123 4567"
            />
          </FormField>

          <div className="md:col-span-2">
            <FormField label="Account Status">
              <Select
                value={formData.is_active ? 'true' : 'false'}
                onChange={(e) => handleChange('is_active', e.target.value === 'true')}
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
