import { useForm, FieldValues, Path, PathValue, DefaultValues } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { Checkbox } from './Checkbox'
import { Form, FormField, FormSection, FormActions } from './Form'

export interface FormFieldConfig {
  name: string
  label: string
  type: 'text' | 'email' | 'tel' | 'number' | 'date' | 'select' | 'textarea' | 'checkbox'
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  disabled?: boolean
}

export interface FormConfig {
  sections: {
    title: string
    description?: string
    fields: FormFieldConfig[]
  }[]
}

interface DynamicFormProps<T extends FieldValues> {
  formConfig: FormConfig
  initialData: T
  zodSchema: z.ZodType<T>
  onSubmit: (data: T) => Promise<void> | void
  onCancel?: () => void
  submitButtonText?: string
  isLoading?: boolean
  renderBeforeActions?: React.ReactNode
}

export const DynamicForm = <T extends FieldValues>({
  formConfig,
  initialData,
  zodSchema,
  onSubmit,
  onCancel,
  submitButtonText = 'Submit',
  isLoading: externalLoading = false,
  renderBeforeActions,
}: DynamicFormProps<T>) => {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<T>({
     
    resolver: zodResolver(zodSchema as any),
    defaultValues: initialData as DefaultValues<T>,
    mode: 'onBlur',
  })

  const isLoading = externalLoading || isSubmitting

  const onFormSubmit = async (data: T) => {
    await onSubmit(data)
  }

  const renderField = (fieldConfig: FormFieldConfig) => {
    const { name, type, placeholder, options, disabled } = fieldConfig
    const fieldName = name as Path<T>
    const value = watch(fieldName)

    switch (type) {
      case 'select':
        return (
          <Select
            value={String(value || '')}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              setValue(fieldName, e.target.value as PathValue<T, Path<T>>, { shouldValidate: true })
            }
            options={options || []}
            disabled={disabled}
          />
        )
      case 'textarea':
        return (
          <Textarea
            {...register(fieldName)}
            placeholder={placeholder}
            disabled={disabled}
          />
        )
      case 'date':
        return (
          <Input
            type="date"
            {...register(fieldName)}
            disabled={disabled}
          />
        )
      case 'checkbox':
        return (
          <Checkbox
            checked={Boolean(value)}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setValue(fieldName, e.target.checked as PathValue<T, Path<T>>, { shouldValidate: true })
            }
            disabled={disabled}
          />
        )
      case 'number':
        return (
          <Input
            type="number"
            {...register(fieldName, { valueAsNumber: true })}
            placeholder={placeholder}
            disabled={disabled}
          />
        )
      default:
        return (
          <Input
            type={type}
            {...register(fieldName)}
            placeholder={placeholder}
            disabled={disabled}
          />
        )
    }
  }

  return (
    <Form onSubmit={handleSubmit(onFormSubmit)}>
      {formConfig.sections.map((section, sectionIndex) => (
        <FormSection
          key={sectionIndex}
          title={section.title}
          description={section.description}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {section.fields.map((field) => {
              const fieldError = errors[field.name as keyof T]
              return (
                <FormField
                  key={field.name}
                  label={field.label}
                  required={field.required}
                  error={fieldError?.message as string | undefined}
                >
                  {renderField(field)}
                </FormField>
              )
            })}
          </div>
        </FormSection>
      ))}

      {renderBeforeActions}

      <FormActions>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving...' : submitButtonText}
        </Button>
      </FormActions>
    </Form>
  )
}
