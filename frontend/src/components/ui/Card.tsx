import { HTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/cn'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  variant?: 'default' | 'elevated' | 'outlined' | 'glass'
  hoverable?: boolean
  /** Whether to use compact padding on mobile */
  mobileCompact?: boolean
}

export const Card = ({
  className,
  children,
  variant = 'default',
  hoverable = false,
  mobileCompact = false,
  ...props
}: CardProps) => {
  const variants = {
    default: 'bg-white border border-[var(--border-default)] shadow-[var(--shadow-sm)]',
    elevated: 'bg-white border-0 shadow-[var(--shadow-md)]',
    outlined: 'bg-white border-2 border-[var(--border-default)] shadow-none',
    glass: 'bg-[var(--glass-bg)] backdrop-blur-[var(--glass-blur)] border border-[var(--glass-border)] shadow-[var(--shadow-md)]',
  }

  return (
    <div
      className={cn(
        'rounded-[var(--radius-xl)] transition-all duration-150 ease-in-out',
        // Mobile-specific: smaller border radius on small screens
        'sm:rounded-[var(--radius-xl)] rounded-[var(--radius-lg)]',
        variants[variant],
        hoverable && 'hover:shadow-[var(--shadow-lg)] hover:border-[var(--barq-amber)] cursor-pointer active:scale-[0.98]',
        mobileCompact && 'p-3 sm:p-0',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  actions?: ReactNode
}

export const CardHeader = ({ className, children, actions, ...props }: CardHeaderProps) => {
  return (
    <div
      className={cn(
        // Responsive padding: smaller on mobile
        'px-4 py-3 sm:px-6 sm:py-4 border-b border-[var(--border-subtle)]',
        actions && 'flex items-center justify-between gap-3',
        className
      )}
      {...props}
    >
      <div className="flex-1 min-w-0">{children}</div>
      {actions && <div className="flex items-center gap-2 flex-shrink-0">{actions}</div>}
    </div>
  )
}

export interface CardTitleProps extends HTMLAttributes<HTMLHeadingElement> {
  children: ReactNode
  subtitle?: string
}

export const CardTitle = ({ className, children, subtitle, ...props }: CardTitleProps) => {
  return (
    <div>
      <h3
        className={cn(
          'text-[var(--font-size-lg)] font-semibold text-[var(--text-primary)] leading-tight',
          className
        )}
        {...props}
      >
        {children}
      </h3>
      {subtitle && (
        <p className="mt-1 text-[var(--font-size-sm)] text-[var(--text-secondary)]">
          {subtitle}
        </p>
      )}
    </div>
  )
}

export interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export const CardContent = ({ className, children, ...props }: CardContentProps) => {
  return (
    <div className={cn('px-4 py-3 sm:px-6 sm:py-4', className)} {...props}>
      {children}
    </div>
  )
}

export interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
}

export const CardFooter = ({ className, children, ...props }: CardFooterProps) => {
  return (
    <div
      className={cn(
        'px-4 py-3 sm:px-6 sm:py-4 border-t border-[var(--border-subtle)] bg-[var(--gray-50)]',
        // Match the responsive border radius from Card
        'rounded-b-[var(--radius-lg)] sm:rounded-b-[var(--radius-xl)]',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export interface CardDescriptionProps extends HTMLAttributes<HTMLParagraphElement> {
  children: ReactNode
}

export const CardDescription = ({ className, children, ...props }: CardDescriptionProps) => {
  return (
    <p
      className={cn('text-[var(--font-size-sm)] text-[var(--text-secondary)]', className)}
      {...props}
    >
      {children}
    </p>
  )
}
