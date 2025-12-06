import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cn } from '@/lib/cn'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost' | 'outline' | 'destructive'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  fullWidth?: boolean
  as?: string // For polymorphic usage (ignored, renders as button)
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      fullWidth = false,
      disabled,
      children,
      as: _as, // Destructure and ignore
      ...props
    },
    ref
  ) => {
    const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-150 ease-in-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none'

    const variants = {
      primary: 'bg-[var(--barq-amber)] text-[var(--text-on-brand)] hover:bg-[var(--barq-amber-dark)] active:bg-[var(--barq-amber-darker)] focus-visible:ring-[var(--barq-amber)] shadow-[var(--shadow-brand-sm)] hover:shadow-[var(--shadow-brand-md)] disabled:shadow-none',
      secondary: 'bg-white text-[var(--text-primary)] border border-[var(--border-default)] hover:bg-[var(--gray-50)] active:bg-[var(--gray-100)] focus-visible:ring-[var(--barq-amber)] shadow-[var(--shadow-sm)] hover:shadow-[var(--shadow-md)]',
      danger: 'bg-[var(--color-error)] text-white hover:bg-[var(--color-error-dark)] active:bg-[var(--color-error-dark)] focus-visible:ring-[var(--color-error)] shadow-sm hover:shadow-md',
      destructive: 'bg-[var(--color-error)] text-white hover:bg-[var(--color-error-dark)] active:bg-[var(--color-error-dark)] focus-visible:ring-[var(--color-error)] shadow-sm hover:shadow-md',
      success: 'bg-[var(--color-success)] text-white hover:bg-[var(--color-success-dark)] active:bg-[var(--color-success-dark)] focus-visible:ring-[var(--color-success)] shadow-sm hover:shadow-md',
      ghost: 'bg-transparent hover:bg-[var(--gray-100)] active:bg-[var(--gray-200)] text-[var(--text-primary)] focus-visible:ring-[var(--barq-amber)]',
      outline: 'bg-transparent border-2 border-[var(--barq-amber)] text-[var(--barq-amber)] hover:bg-[var(--barq-amber)] hover:text-[var(--text-on-brand)] active:bg-[var(--barq-amber-dark)] focus-visible:ring-[var(--barq-amber)]',
    }

    const sizes = {
      sm: 'h-[var(--button-height-sm)] px-3 text-[var(--font-size-sm)] min-w-[var(--button-height-sm)]',
      md: 'h-[var(--button-height-md)] px-4 text-[var(--font-size-base)] min-w-[var(--button-height-md)]',
      lg: 'h-[var(--button-height-lg)] px-6 text-[var(--font-size-lg)] min-w-[var(--button-height-lg)]',
    }

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          baseStyles,
          variants[variant],
          sizes[size],
          fullWidth && 'w-full',
          className
        )}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    )
  }
)

Button.displayName = 'Button'
