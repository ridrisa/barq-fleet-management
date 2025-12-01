import { lazy, ComponentType } from 'react';

/**
 * Lazy load component with retry mechanism for failed chunk loads
 * Retries up to 3 times with exponential backoff before falling back to error
 */
export function lazyWithRetry<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  retries = 3,
  interval = 1000
): React.LazyExoticComponent<T> {
  return lazy(() => {
    return new Promise<{ default: T }>((resolve, reject) => {
      const attemptImport = (retriesLeft: number) => {
        importFunc()
          .then(resolve)
          .catch((error) => {
            // Check if this is a chunk load error
            const isChunkLoadError =
              error?.message?.includes('Failed to fetch') ||
              error?.message?.includes('dynamically imported module');

            if (retriesLeft === 0 || !isChunkLoadError) {
              reject(error);
              return;
            }

            console.warn(
              `Chunk load failed, retrying... (${retries - retriesLeft + 1}/${retries})`,
              error
            );

            // Exponential backoff
            const delay = interval * Math.pow(2, retries - retriesLeft);
            setTimeout(() => attemptImport(retriesLeft - 1), delay);
          });
      };

      attemptImport(retries);
    });
  });
}

/**
 * Prefetch a lazy-loaded component
 * Useful for route-based prefetching on hover or on mount
 */
export function prefetchComponent(
  importFunc: () => Promise<{ default: ComponentType<any> }>
): void {
  // Check if the browser is idle before prefetching
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      importFunc().catch(() => {
        // Silently fail prefetch attempts
        console.debug('Prefetch failed, will load on demand');
      });
    });
  } else {
    // Fallback for browsers without requestIdleCallback
    setTimeout(() => {
      importFunc().catch(() => {
        console.debug('Prefetch failed, will load on demand');
      });
    }, 100);
  }
}
