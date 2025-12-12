import { useForm, UseFormReturn, FieldValues, DefaultValues } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

/**
 * Custom hook that integrates react-hook-form with Zod validation.
 * Provides type-safe form handling with Zod schema validation.
 *
 * @example
 * ```typescript
 * import { useZodForm } from '@/hooks/useZodForm';
 * import { loginSchema, LoginFormData } from '@/schemas';
 *
 * const form = useZodForm({
 *   schema: loginSchema,
 *   defaultValues: { email: '', password: '' },
 * });
 *
 * const onSubmit = form.handleSubmit((data) => {
 *   // data is fully typed as LoginFormData
 *   console.log(data);
 * });
 * ```
 */

interface UseZodFormOptions<T extends FieldValues> {
  schema: z.ZodType<T>
  defaultValues?: DefaultValues<T>
  mode?: 'onChange' | 'onBlur' | 'onSubmit' | 'onTouched' | 'all'
}

export function useZodForm<T extends FieldValues>({
  schema,
  defaultValues,
  mode = 'onBlur',
}: UseZodFormOptions<T>): UseFormReturn<T> {
  return useForm<T>({
     
    resolver: zodResolver(schema as any),
    defaultValues,
    mode,
  })
}

/**
 * Helper type to extract form data type from a Zod schema
 */
export type InferFormData<T extends z.ZodType> = z.infer<T>
