/**
 * useDocumentTitle Hook
 *
 * Updates the document title when component mounts and restores
 * previous title when component unmounts.
 */

import { useEffect, useRef } from 'react'
import { setDocumentTitle } from '@/lib/a11y'

/**
 * Set document title for the current page
 * @param title - Page title
 * @param retainOnUnmount - Whether to keep the title when component unmounts
 */
export const useDocumentTitle = (
  title: string,
  retainOnUnmount: boolean = false
): void => {
  const defaultTitle = useRef<string>(document.title)

  useEffect(() => {
    setDocumentTitle(title)
  }, [title])

  useEffect(() => {
    return () => {
      if (!retainOnUnmount) {
        document.title = defaultTitle.current
      }
    }
  }, [retainOnUnmount])
}
