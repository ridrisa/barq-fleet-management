import { HTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' | 'outline' | 'error' | 'primary' | 'secondary' | 'brand'
  size?: 'sm' | 'md'
  dot?: boolean
}

export const Badge = ({
  className,
  variant = 'default',
  size = 'md',
  dot = false,
  children,
  ...props
}: BadgeProps) => {
  const variants = {
    default: 'bg-[var(--gray-100)] text-[var(--gray-800)] border border-[var(--gray-200)]',
    brand: 'bg-[var(--barq-amber)] text-[var(--text-on-brand)] border border-[var(--barq-amber-dark)] font-semibold',
    primary: 'bg-[var(--color-info-bg)] text-[var(--color-info-dark)] border border-[var(--color-info-border)]',
    secondary: 'bg-[var(--gray-100)] text-[var(--text-secondary)] border border-[var(--gray-200)]',
    success: 'bg-[var(--color-success-bg)] text-[var(--color-success-dark)] border border-[var(--color-success-border)]',
    warning: 'bg-[var(--color-warning-bg)] text-[var(--color-warning-dark)] border border-[var(--color-warning-border)]',
    danger: 'bg-[var(--color-error-bg)] text-[var(--color-error-dark)] border border-[var(--color-error-border)]',
    error: 'bg-[var(--color-error-bg)] text-[var(--color-error-dark)] border border-[var(--color-error-border)]',
    info: 'bg-[var(--color-info-bg)] text-[var(--color-info-dark)] border border-[var(--color-info-border)]',
    outline: 'bg-transparent border border-[var(--border-default)] text-[var(--text-primary)]',
  }

  const sizes = {
    sm: 'h-5 px-2 text-[var(--font-size-xs)] gap-1',
    md: 'h-6 px-2.5 text-[var(--font-size-sm)] gap-1.5',
  }

  const dotColors = {
    default: 'bg-[var(--gray-600)]',
    brand: 'bg-[var(--barq-amber-dark)]',
    primary: 'bg-[var(--color-info)]',
    secondary: 'bg-[var(--gray-500)]',
    success: 'bg-[var(--color-success)]',
    warning: 'bg-[var(--color-warning)]',
    danger: 'bg-[var(--color-error)]',
    error: 'bg-[var(--color-error)]',
    info: 'bg-[var(--color-info)]',
    outline: 'bg-[var(--gray-600)]',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center font-medium rounded-full transition-colors',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full',
            dotColors[variant]
          )}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  )
}
