import { InputHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/cn'

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string
  error?: string
  helperText?: string
  icon?: React.ReactNode
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  size?: 'sm' | 'md' | 'lg'
  'aria-label'?: string
  'aria-describedby'?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      type = 'text',
      label,
      error,
      helperText,
      icon,
      leftIcon,
      rightIcon,
      size = 'md',
      disabled,
      required,
      'aria-label': ariaLabel,
      'aria-describedby': ariaDescribedBy,
      ...props
    },
    ref
  ) => {
    // Allow icon as alias for leftIcon
    const effectiveLeftIcon = leftIcon || icon
    const errorId = error ? `${props.id || 'input'}-error` : undefined
    const helperId = helperText ? `${props.id || 'input'}-helper` : undefined
    const describedBy = ariaDescribedBy || [errorId, helperId].filter(Boolean).join(' ') || undefined

    const sizes = {
      sm: 'h-[var(--input-height-sm)] px-3 text-[var(--font-size-sm)]',
      md: 'h-[var(--input-height-md)] px-4 text-[var(--font-size-base)]',
      lg: 'h-[var(--input-height-lg)] px-5 text-[var(--font-size-lg)]',
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
          {effectiveLeftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[var(--text-muted)]">
              {effectiveLeftIcon}
            </div>
          )}
          <input
            type={type}
            ref={ref}
            disabled={disabled}
            required={required}
            aria-label={ariaLabel || (label ? undefined : 'Input field')}
            aria-describedby={describedBy}
            aria-invalid={error ? 'true' : 'false'}
            aria-required={required ? 'true' : 'false'}
            className={cn(
              'block w-full rounded-[var(--radius-lg)] border border-[var(--border-default)] bg-white',
              'text-[var(--text-primary)] placeholder:text-[var(--text-muted)]',
              'transition-all duration-150 ease-in-out',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--barq-amber)] focus-visible:border-[var(--barq-amber)]',
              'hover:border-[var(--border-strong)]',
              'disabled:bg-[var(--gray-50)] disabled:text-[var(--text-disabled)] disabled:cursor-not-allowed disabled:border-[var(--border-subtle)]',
              error && 'border-[var(--color-error)] focus-visible:ring-[var(--color-error)] focus-visible:border-[var(--color-error)]',
              sizes[size],
              effectiveLeftIcon && 'pl-10',
              rightIcon && 'pr-10',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-[var(--text-muted)]">
              {rightIcon}
            </div>
          )}
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

Input.displayName = 'Input'
