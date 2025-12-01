import { ReactNode, FormHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export interface FormProps extends FormHTMLAttributes<HTMLFormElement> {
  children: ReactNode
}

export const Form = ({ className, children, ...props }: FormProps) => {
  return (
    <form className={cn('space-y-4', className)} {...props}>
      {children}
    </form>
  )
}

export interface FormFieldProps {
  label: string
  required?: boolean
  error?: string
  helperText?: string
  children: ReactNode
}

export const FormField = ({
  label,
  required = false,
  error,
  helperText,
  children,
}: FormFieldProps) => {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  )
}

export interface FormSectionProps {
  title: string
  description?: string
  children: ReactNode
}

export const FormSection = ({
  title,
  description,
  children,
}: FormSectionProps) => {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-gray-500">{description}</p>
        )}
      </div>
      <div className="space-y-4">{children}</div>
    </div>
  )
}

export interface FormActionsProps {
  children: ReactNode
  align?: 'left' | 'center' | 'right'
}

export const FormActions = ({ children, align = 'right' }: FormActionsProps) => {
  const alignments = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  }

  return (
    <div className={cn('flex gap-3 pt-4', alignments[align])}>{children}</div>
  )
}
