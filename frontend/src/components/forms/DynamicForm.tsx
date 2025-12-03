import { useForm, ValidationSchema } from '@/hooks/useForm';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Textarea } from '@/components/ui/Textarea';
import { Checkbox } from './Checkbox';
import { Form, FormField, FormSection, FormActions } from './Form';

export interface FormFieldConfig {
  name: string;
  label: string;
  type: 'text' | 'email' | 'tel' | 'number' | 'date' | 'select' | 'textarea' | 'checkbox';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  disabled?: boolean;
}

export interface FormConfig {
  sections: {
    title: string;
    description?: string;
    fields: FormFieldConfig[];
  }[];
}

interface DynamicFormProps<T> {
  formConfig: FormConfig;
  initialData: T;
  validationSchema: ValidationSchema<T>;
  onSubmit: (data: T) => Promise<void> | void;
  onCancel?: () => void;
  submitButtonText?: string;
  isLoading?: boolean;
  renderBeforeActions?: React.ReactNode;
}

const renderField = <T extends object>(
  fieldConfig: FormFieldConfig,
  formData: T,
  handleChange: (field: string, value: unknown) => void
) => {
  const { name, type, placeholder, options } = fieldConfig;

  const data = formData as Record<string, unknown>;
  switch (type) {
    case 'select':
      return (
        <Select
          value={String(data[name] || '')}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleChange(name, e.target.value)}
          options={options || []}
          disabled={fieldConfig.disabled}
        />
      );
    case 'textarea':
        return (
            <Textarea
                value={String(data[name] || '')}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleChange(name, e.target.value)}
                placeholder={placeholder}
                disabled={fieldConfig.disabled}
            />
        );
    case 'date':
        return(
            <Input
                type="date"
                value={String(data[name] || '')}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(name, e.target.value)}
                disabled={fieldConfig.disabled}
            />
        )
    case 'checkbox':
        return (
            <Checkbox
                checked={Boolean(data[name])}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(name, e.target.checked)}
                disabled={fieldConfig.disabled}
            />
        )
    default:
      return (
        <Input
          type={type}
          value={String(data[name] || '')}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(name, e.target.value)}
          placeholder={placeholder}
          disabled={fieldConfig.disabled}
        />
      );
  }
};

export const DynamicForm = <T extends object>({
  formConfig,
  initialData,
  validationSchema,
  onSubmit,
  onCancel,
  submitButtonText = "Submit",
  isLoading: externalLoading = false,
  renderBeforeActions,
}: DynamicFormProps<T>) => {
  const { formData, errors, isLoading: formLoading, handleChange, handleSubmit } = useForm({
    initialData,
    validationSchema,
    onSubmit,
  });

  const isLoading = externalLoading || formLoading;

  return (
    <Form onSubmit={handleSubmit}>
      {formConfig.sections.map((section, sectionIndex) => (
        <FormSection
          key={sectionIndex}
          title={section.title}
          description={section.description}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {section.fields.map((field) => (
              <FormField
                key={field.name}
                label={field.label}
                required={field.required}
                error={errors[field.name as keyof T]}
              >
                {renderField(field, formData, handleChange)}
              </FormField>
            ))}
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
  );
};
