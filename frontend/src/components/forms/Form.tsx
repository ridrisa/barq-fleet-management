import { ReactNode, FormHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'
import { useMobile } from '@/hooks/useMobile'

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
  className?: string
}

export const FormField = ({
  label,
  required = false,
  error,
  helperText,
  children,
  className,
}: FormFieldProps) => {
  return (
    <div className={cn('space-y-1.5', className)}>
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
  className?: string
}

export const FormSection = ({
  title,
  description,
  children,
  className,
}: FormSectionProps) => {
  return (
    <div className={cn('space-y-4', className)}>
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
  className?: string
  // Stack buttons on mobile
  stackOnMobile?: boolean
}

export const FormActions = ({
  children,
  align = 'right',
  className,
  stackOnMobile = true,
}: FormActionsProps) => {
  const isMobile = useMobile('sm')

  const alignments = {
    left: 'justify-start',
    center: 'justify-center',
    right: 'justify-end',
  }

  return (
    <div
      className={cn(
        'flex gap-3 pt-4',
        stackOnMobile && isMobile ? 'flex-col-reverse' : alignments[align],
        className
      )}
    >
      {children}
    </div>
  )
}

// Responsive form grid for multi-column layouts
export interface FormGridProps {
  children: ReactNode
  columns?: 1 | 2 | 3 | 4
  className?: string
}

export const FormGrid = ({
  children,
  columns = 2,
  className,
}: FormGridProps) => {
  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4',
  }

  return (
    <div className={cn('grid gap-4', columnClasses[columns], className)}>
      {children}
    </div>
  )
}

// Form row for inline form elements
export interface FormRowProps {
  children: ReactNode
  className?: string
}

export const FormRow = ({ children, className }: FormRowProps) => {
  return (
    <div
      className={cn(
        'flex flex-col sm:flex-row sm:items-end gap-3',
        className
      )}
    >
      {children}
    </div>
  )
}

// Divider with optional label
export interface FormDividerProps {
  label?: string
  className?: string
}

export const FormDivider = ({ label, className }: FormDividerProps) => {
  if (label) {
    return (
      <div className={cn('relative py-4', className)}>
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center">
          <span className="px-3 bg-white text-sm text-gray-500">{label}</span>
        </div>
      </div>
    )
  }

  return <hr className={cn('border-gray-200 my-6', className)} />
}
