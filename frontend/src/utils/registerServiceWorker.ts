/**
 * Service Worker Registration Utility
 * Registers and manages the service worker for offline functionality
 */

export function registerServiceWorker(): void {
  // Only register in production or when explicitly enabled
  if (
    !('serviceWorker' in navigator) ||
    (!import.meta.env.PROD && import.meta.env.VITE_ENABLE_SW !== 'true')
  ) {
    console.log('[SW] Service worker not enabled in this environment');
    return;
  }

  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('[SW] Service worker registered:', registration.scope);

        // Check for updates every hour
        setInterval(() => {
          registration.update();
        }, 60 * 60 * 1000);

        // Handle updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;

          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (
                newWorker.state === 'installed' &&
                navigator.serviceWorker.controller
              ) {
                // New service worker available
                showUpdateNotification();
              }
            });
          }
        });
      })
      .catch((error) => {
        console.error('[SW] Service worker registration failed:', error);
      });

    // Handle controller change (new service worker activated)
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      console.log('[SW] New service worker activated');
      // Optionally reload the page
      // window.location.reload();
    });
  });
}

/**
 * Show notification when update is available
 */
function showUpdateNotification(): void {
  // You can integrate this with your toast notification system
  const shouldUpdate = confirm(
    'A new version of the app is available. Reload to update?'
  );

  if (shouldUpdate) {
    // Tell the service worker to skip waiting
    navigator.serviceWorker.controller?.postMessage({ type: 'SKIP_WAITING' });

    // Reload the page
    window.location.reload();
  }
}

/**
 * Unregister service worker (useful for development)
 */
export async function unregisterServiceWorker(): Promise<void> {
  if ('serviceWorker' in navigator) {
    const registrations = await navigator.serviceWorker.getRegistrations();

    for (const registration of registrations) {
      await registration.unregister();
      console.log('[SW] Service worker unregistered');
    }
  }
}

/**
 * Clear all caches (useful for troubleshooting)
 */
export async function clearAllCaches(): Promise<void> {
  if ('caches' in window) {
    const cacheNames = await caches.keys();

    await Promise.all(
      cacheNames.map((cacheName) => {
        console.log('[SW] Deleting cache:', cacheName);
        return caches.delete(cacheName);
      })
    );

    console.log('[SW] All caches cleared');
  }
}
