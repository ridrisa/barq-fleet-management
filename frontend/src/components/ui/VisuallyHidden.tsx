/**
 * VisuallyHidden Component
 *
 * Hides content visually while keeping it accessible to screen readers.
 * Commonly used for:
 * - Additional context for screen readers
 * - Skip links
 * - Hidden labels for icon-only buttons
 * - Loading/status messages
 */

import { ReactNode } from 'react'
import { cn } from '@/lib/cn'

interface VisuallyHiddenProps {
  /**
   * Content to hide visually
   */
  children: ReactNode

  /**
   * Whether to show on focus (for skip links)
   */
  focusable?: boolean

  /**
   * Additional CSS classes
   */
  className?: string

  /**
   * HTML element to render
   */
  as?: keyof JSX.IntrinsicElements

  /**
   * Additional props to pass to the element
   */
  [key: string]: any
}

/**
 * VisuallyHidden component for screen reader only content
 */
export const VisuallyHidden = ({
  children,
  focusable = false,
  className,
  as: Component = 'span',
  ...restProps
}: VisuallyHiddenProps) => {
  return (
    <Component
      className={cn(
        // Base sr-only styles
        'absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0',
        // Clip path for better support
        '[clip:rect(0,0,0,0)]',
        // Show on focus for skip links
        focusable && 'focus:not-sr-only focus:absolute focus:top-0 focus:left-0 focus:z-50 focus:p-4 focus:w-auto focus:h-auto focus:clip-auto focus:bg-blue-600 focus:text-white focus:rounded-md focus:shadow-lg',
        className
      )}
      {...restProps}
    >
      {children}
    </Component>
  )
}

/**
 * SkipLink component for keyboard navigation
 * Allows keyboard users to skip repetitive content
 */
interface SkipLinkProps {
  /**
   * Target element ID to skip to
   */
  href: string

  /**
   * Link text
   */
  children: ReactNode
}

export const SkipLink = ({ href, children }: SkipLinkProps) => {
  return (
    <VisuallyHidden as="a" focusable>
      <a href={href}>{children}</a>
    </VisuallyHidden>
  )
}
