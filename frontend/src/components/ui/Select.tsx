import { SelectHTMLAttributes, forwardRef, ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { ChevronDown } from 'lucide-react'

export interface SelectOption {
  value: string
  label: string
}

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  label?: string
  error?: string
  helperText?: string
  options?: SelectOption[]
  placeholder?: string
  leftIcon?: ReactNode
  size?: 'sm' | 'md' | 'lg'
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      className,
      label,
      error,
      helperText,
      options,
      placeholder,
      disabled,
      required,
      children,
      leftIcon,
      size = 'md',
      ...props
    },
    ref
  ) => {
    const errorId = error ? `${props.id || 'select'}-error` : undefined
    const helperId = helperText ? `${props.id || 'select'}-helper` : undefined
    const describedBy = [errorId, helperId].filter(Boolean).join(' ') || undefined

    const sizes = {
      sm: 'h-[var(--input-height-sm)] text-[var(--font-size-sm)]',
      md: 'h-[var(--input-height-md)] text-[var(--font-size-base)]',
      lg: 'h-[var(--input-height-lg)] text-[var(--font-size-lg)]',
    }

    return (
      <div className="w-full">
        {label && (
          <label
            className={cn(
              "block text-[var(--font-size-sm)] font-medium text-[var(--text-primary)] mb-1.5",
              required && "after:content-['*'] after:ml-0.5 after:text-[var(--color-error)]"
            )}
            htmlFor={props.id}
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--text-muted)]">
              {leftIcon}
            </div>
          )}
          <select
            ref={ref}
            disabled={disabled}
            required={required}
            aria-describedby={describedBy}
            aria-invalid={error ? 'true' : 'false'}
            aria-required={required ? 'true' : 'false'}
            className={cn(
              'block w-full rounded-[var(--radius-lg)] border border-[var(--border-default)] bg-white pr-10',
              leftIcon ? 'pl-10' : 'px-4',
              'text-[var(--text-primary)] transition-all duration-150 ease-in-out',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--barq-amber)] focus-visible:border-[var(--barq-amber)]',
              'hover:border-[var(--border-strong)]',
              'disabled:bg-[var(--gray-50)] disabled:text-[var(--text-disabled)] disabled:cursor-not-allowed disabled:border-[var(--border-subtle)]',
              'appearance-none',
              error && 'border-[var(--color-error)] focus-visible:ring-[var(--color-error)] focus-visible:border-[var(--color-error)]',
              sizes[size],
              className
            )}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
            {children}
          </select>
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-[var(--text-muted)]">
            <ChevronDown className="h-5 w-5" aria-hidden="true" />
          </div>
        </div>
        {error && (
          <p id={errorId} className="mt-1.5 text-[var(--font-size-sm)] text-[var(--color-error)] flex items-center gap-1" role="alert">
            <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        {helperText && !error && (
          <p id={helperId} className="mt-1.5 text-[var(--font-size-sm)] text-[var(--text-secondary)]">
            {helperText}
          </p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'
