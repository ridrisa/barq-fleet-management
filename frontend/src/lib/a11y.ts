/**
 * Accessibility Utilities
 *
 * Provides helper functions and utilities for improving accessibility
 * throughout the BARQ Fleet Management application.
 */

/**
 * Generate a unique ID for ARIA attributes
 * @param prefix - Prefix for the ID
 * @returns Unique ID string
 */
export const generateId = (prefix: string): string => {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * Get all focusable elements within a container
 * @param container - Container element to search within
 * @returns Array of focusable elements
 */
export const getFocusableElements = (container: HTMLElement): HTMLElement[] => {
  const selector = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
  ].join(', ')

  return Array.from(container.querySelectorAll<HTMLElement>(selector))
}

/**
 * Trap focus within a container (for modals, dialogs, etc.)
 * @param container - Container to trap focus within
 * @param event - Keyboard event
 */
export const trapFocus = (container: HTMLElement, event: KeyboardEvent): void => {
  if (event.key !== 'Tab') return

  const focusableElements = getFocusableElements(container)

  if (focusableElements.length === 0) return

  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]

  if (event.shiftKey && document.activeElement === firstElement) {
    event.preventDefault()
    lastElement.focus()
  } else if (!event.shiftKey && document.activeElement === lastElement) {
    event.preventDefault()
    firstElement.focus()
  }
}

/**
 * Announce message to screen readers using aria-live region
 * @param message - Message to announce
 * @param priority - Priority level (polite or assertive)
 */
export const announceToScreenReader = (
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
): void => {
  const liveRegion = document.getElementById('a11y-announcer') || createLiveRegion()

  liveRegion.setAttribute('aria-live', priority)

  // Clear previous message
  liveRegion.textContent = ''

  // Set new message after a brief delay to ensure it's announced
  setTimeout(() => {
    liveRegion.textContent = message
  }, 100)

  // Clear message after it's been announced
  setTimeout(() => {
    liveRegion.textContent = ''
  }, 5000)
}

/**
 * Create a live region for screen reader announcements
 * @returns The created live region element
 */
const createLiveRegion = (): HTMLElement => {
  const liveRegion = document.createElement('div')
  liveRegion.id = 'a11y-announcer'
  liveRegion.className = 'sr-only'
  liveRegion.setAttribute('role', 'status')
  liveRegion.setAttribute('aria-live', 'polite')
  liveRegion.setAttribute('aria-atomic', 'true')
  document.body.appendChild(liveRegion)
  return liveRegion
}

/**
 * Check if element is visible to screen readers
 * @param element - Element to check
 * @returns True if visible to screen readers
 */
export const isVisibleToScreenReader = (element: HTMLElement): boolean => {
  const ariaHidden = element.getAttribute('aria-hidden') === 'true'
  const style = window.getComputedStyle(element)
  const visuallyHidden = style.display === 'none' || style.visibility === 'hidden'

  return !ariaHidden && !visuallyHidden
}

/**
 * Set document title with app name
 * @param pageTitle - Title for the current page
 */
export const setDocumentTitle = (pageTitle: string): void => {
  document.title = `${pageTitle} - BARQ Fleet Management`
}

/**
 * Get ARIA sort attribute value based on sort state
 * @param isSorted - Whether column is currently sorted
 * @param direction - Sort direction
 * @returns ARIA sort attribute value
 */
export const getAriaSortValue = (
  isSorted: boolean,
  direction?: 'asc' | 'desc'
): 'ascending' | 'descending' | 'none' | undefined => {
  if (!isSorted) return 'none'
  return direction === 'asc' ? 'ascending' : 'descending'
}

/**
 * Format number for screen readers
 * @param value - Number to format
 * @param options - Formatting options
 * @returns Formatted string
 */
export const formatNumberForScreenReader = (
  value: number,
  options?: Intl.NumberFormatOptions
): string => {
  return new Intl.NumberFormat('en-US', options).format(value)
}

/**
 * Format date for screen readers
 * @param date - Date to format
 * @param options - Formatting options
 * @returns Formatted string
 */
export const formatDateForScreenReader = (
  date: Date | string,
  options?: Intl.DateTimeFormatOptions
): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'long',
    ...options,
  }).format(dateObj)
}

/**
 * Create descriptive label for icon button
 * @param action - Action the button performs
 * @param entityName - Name of entity being acted upon
 * @param entityLabel - Optional label/identifier for the entity
 * @returns Descriptive label
 */
export const createIconButtonLabel = (
  action: string,
  entityName: string,
  entityLabel?: string
): string => {
  if (entityLabel) {
    return `${action} ${entityName} ${entityLabel}`
  }
  return `${action} ${entityName}`
}

/**
 * Handle escape key to close modal/dialog
 * @param callback - Function to call when escape is pressed
 * @returns Cleanup function
 */
export const handleEscapeKey = (callback: () => void): (() => void) => {
  const handler = (event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      callback()
    }
  }

  document.addEventListener('keydown', handler)

  return () => {
    document.removeEventListener('keydown', handler)
  }
}

/**
 * Check if contrast ratio meets WCAG AA standards
 * @param foreground - Foreground color (hex)
 * @param background - Background color (hex)
 * @param fontSize - Font size in pixels
 * @returns True if contrast ratio is sufficient
 */
export const meetsContrastRequirement = (
  foreground: string,
  background: string,
  fontSize: number = 16
): boolean => {
  const ratio = calculateContrastRatio(foreground, background)
  const isLargeText = fontSize >= 18 || (fontSize >= 14 && false) // TODO: check if bold

  // WCAG AA requires 4.5:1 for normal text, 3:1 for large text
  const requiredRatio = isLargeText ? 3 : 4.5

  return ratio >= requiredRatio
}

/**
 * Calculate contrast ratio between two colors
 * @param color1 - First color (hex)
 * @param color2 - Second color (hex)
 * @returns Contrast ratio
 */
const calculateContrastRatio = (color1: string, color2: string): number => {
  const lum1 = getRelativeLuminance(color1)
  const lum2 = getRelativeLuminance(color2)

  const lighter = Math.max(lum1, lum2)
  const darker = Math.min(lum1, lum2)

  return (lighter + 0.05) / (darker + 0.05)
}

/**
 * Get relative luminance of a color
 * @param hex - Hex color string
 * @returns Relative luminance
 */
const getRelativeLuminance = (hex: string): number => {
  const rgb = hexToRgb(hex)
  if (!rgb) return 0

  const [r, g, b] = rgb.map(value => {
    const channel = value / 255
    return channel <= 0.03928
      ? channel / 12.92
      : Math.pow((channel + 0.055) / 1.055, 2.4)
  })

  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/**
 * Convert hex color to RGB
 * @param hex - Hex color string
 * @returns RGB array or null
 */
const hexToRgb = (hex: string): [number, number, number] | null => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16),
      ]
    : null
}

/**
 * Debounce function for performance
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 * @returns Debounced function
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout | null = null

  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}

/**
 * Check if user prefers reduced motion
 * @returns True if user prefers reduced motion
 */
export const prefersReducedMotion = (): boolean => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Get appropriate animation duration based on user preference
 * @param defaultDuration - Default animation duration in ms
 * @returns Animation duration (0 if reduced motion preferred)
 */
export const getAnimationDuration = (defaultDuration: number): number => {
  return prefersReducedMotion() ? 0 : defaultDuration
}
