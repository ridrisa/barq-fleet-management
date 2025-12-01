/**
 * useKeyboardNavigation Hook
 *
 * Provides keyboard navigation utilities for lists, tables, and other
 * navigable components.
 */

import { useState, useEffect, useCallback, RefObject } from 'react'

interface UseKeyboardNavigationOptions {
  /**
   * Total number of items
   */
  itemCount: number

  /**
   * Initial selected index
   */
  initialIndex?: number

  /**
   * Whether navigation loops (goes from last to first and vice versa)
   */
  loop?: boolean

  /**
   * Callback when an item is selected with Enter or Space
   */
  onSelect?: (index: number) => void

  /**
   * Callback when an item is activated (Enter key)
   */
  onActivate?: (index: number) => void

  /**
   * Whether the navigation is currently active
   */
  isActive?: boolean

  /**
   * Container ref to listen for keyboard events
   */
  containerRef?: RefObject<HTMLElement>
}

interface UseKeyboardNavigationReturn {
  /**
   * Current focused index
   */
  focusedIndex: number

  /**
   * Set the focused index
   */
  setFocusedIndex: (index: number) => void

  /**
   * Move focus to next item
   */
  focusNext: () => void

  /**
   * Move focus to previous item
   */
  focusPrevious: () => void

  /**
   * Move focus to first item
   */
  focusFirst: () => void

  /**
   * Move focus to last item
   */
  focusLast: () => void

  /**
   * Get props to spread on navigable items
   */
  getItemProps: (index: number) => {
    tabIndex: number
    'data-index': number
    onKeyDown: (e: React.KeyboardEvent) => void
    onFocus: () => void
  }
}

export const useKeyboardNavigation = ({
  itemCount,
  initialIndex = 0,
  loop = true,
  onSelect,
  onActivate,
  isActive = true,
  containerRef,
}: UseKeyboardNavigationOptions): UseKeyboardNavigationReturn => {
  const [focusedIndex, setFocusedIndex] = useState(initialIndex)

  const focusNext = useCallback(() => {
    setFocusedIndex((prev) => {
      if (prev >= itemCount - 1) {
        return loop ? 0 : prev
      }
      return prev + 1
    })
  }, [itemCount, loop])

  const focusPrevious = useCallback(() => {
    setFocusedIndex((prev) => {
      if (prev <= 0) {
        return loop ? itemCount - 1 : 0
      }
      return prev - 1
    })
  }, [itemCount, loop])

  const focusFirst = useCallback(() => {
    setFocusedIndex(0)
  }, [])

  const focusLast = useCallback(() => {
    setFocusedIndex(itemCount - 1)
  }, [itemCount])

  const handleKeyDown = useCallback(
    (e: KeyboardEvent | React.KeyboardEvent, index: number) => {
      if (!isActive) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          focusNext()
          break
        case 'ArrowUp':
          e.preventDefault()
          focusPrevious()
          break
        case 'Home':
          e.preventDefault()
          focusFirst()
          break
        case 'End':
          e.preventDefault()
          focusLast()
          break
        case 'Enter':
          e.preventDefault()
          onActivate?.(index)
          onSelect?.(index)
          break
        case ' ':
          e.preventDefault()
          onSelect?.(index)
          break
      }
    },
    [isActive, focusNext, focusPrevious, focusFirst, focusLast, onActivate, onSelect]
  )

  // Add keyboard event listener to container if provided
  useEffect(() => {
    if (!containerRef?.current || !isActive) return

    const container = containerRef.current

    const handleContainerKeyDown = (e: KeyboardEvent) => {
      handleKeyDown(e, focusedIndex)
    }

    container.addEventListener('keydown', handleContainerKeyDown)

    return () => {
      container.removeEventListener('keydown', handleContainerKeyDown)
    }
  }, [containerRef, isActive, focusedIndex, handleKeyDown])

  const getItemProps = useCallback(
    (index: number) => {
      return {
        tabIndex: index === focusedIndex ? 0 : -1,
        'data-index': index,
        onKeyDown: (e: React.KeyboardEvent) => handleKeyDown(e, index),
        onFocus: () => setFocusedIndex(index),
      }
    },
    [focusedIndex, handleKeyDown]
  )

  return {
    focusedIndex,
    setFocusedIndex,
    focusNext,
    focusPrevious,
    focusFirst,
    focusLast,
    getItemProps,
  }
}
