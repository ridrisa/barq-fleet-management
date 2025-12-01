/**
 * useFocusTrap Hook
 *
 * Traps focus within a container element (for modals, dialogs, etc.)
 * Ensures keyboard users can't tab out of the modal.
 */

import { useEffect, useRef, RefObject } from 'react'
import { getFocusableElements, trapFocus } from '@/lib/a11y'

interface UseFocusTrapOptions {
  /**
   * Whether the focus trap is active
   */
  isActive: boolean

  /**
   * Callback when escape key is pressed
   */
  onEscape?: () => void

  /**
   * Whether to focus first element on mount
   */
  autoFocus?: boolean

  /**
   * Whether to return focus to previously focused element on unmount
   */
  returnFocus?: boolean
}

interface UseFocusTrapReturn {
  /**
   * Ref to attach to the container element
   */
  containerRef: RefObject<HTMLDivElement>
}

export const useFocusTrap = ({
  isActive,
  onEscape,
  autoFocus = true,
  returnFocus = true,
}: UseFocusTrapOptions): UseFocusTrapReturn => {
  const containerRef = useRef<HTMLDivElement>(null)
  const previousFocusRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    if (!isActive || !containerRef.current) return

    const container = containerRef.current

    // Store previously focused element
    if (returnFocus) {
      previousFocusRef.current = document.activeElement as HTMLElement
    }

    // Focus first focusable element
    if (autoFocus) {
      const focusableElements = getFocusableElements(container)
      if (focusableElements.length > 0) {
        // Small delay to ensure modal is fully rendered
        setTimeout(() => {
          focusableElements[0].focus()
        }, 10)
      }
    }

    // Handle keyboard events
    const handleKeyDown = (event: KeyboardEvent) => {
      // Handle Escape key
      if (event.key === 'Escape' && onEscape) {
        event.preventDefault()
        onEscape()
        return
      }

      // Trap focus within container
      if (event.key === 'Tab') {
        trapFocus(container, event)
      }
    }

    // Add event listener
    document.addEventListener('keydown', handleKeyDown)

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown)

      // Return focus to previously focused element
      if (returnFocus && previousFocusRef.current) {
        // Small delay to ensure modal is fully closed
        setTimeout(() => {
          previousFocusRef.current?.focus()
        }, 10)
      }
    }
  }, [isActive, autoFocus, returnFocus, onEscape])

  return {
    containerRef,
  }
}
