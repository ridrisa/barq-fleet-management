import { useState, useCallback } from 'react';

// A generic validation schema
export interface ValidationSchema<T> {
  [key: string]: (value: T) => string | null;
}

// A generic function to run the validation
const validate = <T>(formData: T, schema: ValidationSchema<T>): Partial<Record<keyof T, string>> => {
  const newErrors: Partial<Record<keyof T, string>> = {};
  for (const key in schema) {
    const error = schema[key](formData);
    if (error) {
      newErrors[key as keyof T] = error;
    }
  }
  return newErrors;
}

interface UseFormProps<T> {
  initialData: T;
  validationSchema: ValidationSchema<T>;
  onSubmit: (data: T) => Promise<void> | void;
}

export const useForm = <T>({ initialData, validationSchema, onSubmit }: UseFormProps<T>) => {
  const [formData, setFormData] = useState<T>(initialData);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = useCallback((field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field as keyof T]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  }, [errors]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    const validationErrors = validate(formData, validationSchema);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setIsLoading(false);
      return;
    }

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error("Submission failed", error);
      // Optionally, you could set a general form error here
    } finally {
      setIsLoading(false);
    }
  };

  return {
    formData,
    errors,
    isLoading,
    handleChange,
    handleSubmit,
  };
};
