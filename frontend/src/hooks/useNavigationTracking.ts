import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { addSentryBreadcrumb } from '@/lib/sentry'

/**
 * Hook to track navigation changes in Sentry breadcrumbs.
 * This helps debug user journey when errors occur.
 */
export function useNavigationTracking() {
  const location = useLocation()

  useEffect(() => {
    addSentryBreadcrumb({
      category: 'navigation',
      message: `Navigated to ${location.pathname}`,
      level: 'info',
      data: {
        pathname: location.pathname,
        search: location.search,
        hash: location.hash,
      },
    })
  }, [location.pathname, location.search, location.hash])
}
