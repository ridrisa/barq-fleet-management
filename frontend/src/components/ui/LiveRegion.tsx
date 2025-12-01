/**
 * LiveRegion Component
 *
 * Creates an ARIA live region for dynamic content announcements.
 * Used for:
 * - Loading states
 * - Status messages
 * - Dynamic content updates
 * - Form submission results
 */

import { useEffect, useState } from 'react'
import { VisuallyHidden } from './VisuallyHidden'

interface LiveRegionProps {
  /**
   * Message to announce
   */
  message?: string

  /**
   * Priority level (polite or assertive)
   */
  priority?: 'polite' | 'assertive'

  /**
   * Role for the live region
   */
  role?: 'status' | 'alert' | 'log'

  /**
   * Whether the entire region should be read when changed
   */
  atomic?: boolean

  /**
   * Whether relevant additions should be announced
   */
  relevant?: 'additions' | 'removals' | 'text' | 'all'

  /**
   * Auto-clear message after delay (in ms)
   */
  clearAfter?: number
}

/**
 * LiveRegion component for screen reader announcements
 */
export const LiveRegion = ({
  message = '',
  priority = 'polite',
  role = 'status',
  atomic = true,
  relevant = 'additions',
  clearAfter,
}: LiveRegionProps) => {
  const [currentMessage, setCurrentMessage] = useState(message)

  useEffect(() => {
    if (message) {
      setCurrentMessage(message)

      if (clearAfter) {
        const timer = setTimeout(() => {
          setCurrentMessage('')
        }, clearAfter)

        return () => clearTimeout(timer)
      }
    }
  }, [message, clearAfter])

  return (
    <VisuallyHidden
      as="div"
      aria-live={priority}
      aria-atomic={atomic}
      aria-relevant={relevant}
      role={role}
    >
      {currentMessage}
    </VisuallyHidden>
  )
}

/**
 * Hook to manage live region announcements
 */
export const useLiveRegion = () => {
  const [message, setMessage] = useState('')
  const [priority, setPriority] = useState<'polite' | 'assertive'>('polite')

  const announce = (
    text: string,
    announcePriority: 'polite' | 'assertive' = 'polite'
  ) => {
    setPriority(announcePriority)
    setMessage(text)
  }

  const clear = () => {
    setMessage('')
  }

  return {
    message,
    priority,
    announce,
    clear,
    LiveRegion: () => <LiveRegion message={message} priority={priority} clearAfter={5000} />,
  }
}
