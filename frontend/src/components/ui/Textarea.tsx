import { TextareaHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/cn'

export interface TextareaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  helperText?: string
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, helperText, disabled, required, resize = 'vertical', ...props }, ref) => {
    const errorId = error ? `${props.id || 'textarea'}-error` : undefined
    const helperId = helperText ? `${props.id || 'textarea'}-helper` : undefined
    const describedBy = [errorId, helperId].filter(Boolean).join(' ') || undefined

    const resizeClasses = {
      none: 'resize-none',
      vertical: 'resize-y',
      horizontal: 'resize-x',
      both: 'resize',
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
        <textarea
          ref={ref}
          disabled={disabled}
          required={required}
          aria-describedby={describedBy}
          aria-invalid={error ? 'true' : 'false'}
          aria-required={required ? 'true' : 'false'}
          className={cn(
            'block w-full rounded-[var(--radius-lg)] border border-[var(--border-default)] bg-white px-4 py-3',
            'text-[var(--text-primary)] placeholder:text-[var(--text-muted)]',
            'text-[var(--font-size-base)] transition-all duration-150 ease-in-out',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--barq-amber)] focus-visible:border-[var(--barq-amber)]',
            'hover:border-[var(--border-strong)]',
            'disabled:bg-[var(--gray-50)] disabled:text-[var(--text-disabled)] disabled:cursor-not-allowed disabled:border-[var(--border-subtle)]',
            'min-h-[100px]',
            resizeClasses[resize],
            error && 'border-[var(--color-error)] focus-visible:ring-[var(--color-error)] focus-visible:border-[var(--color-error)]',
            className
          )}
          {...props}
        />
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

Textarea.displayName = 'Textarea'
