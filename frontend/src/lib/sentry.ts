import * as Sentry from '@sentry/react';

/**
 * Initialize Sentry error tracking and performance monitoring
 */
export function initSentry(): void {
  const dsn = import.meta.env.VITE_SENTRY_DSN;

  // Only initialize if DSN is configured
  if (!dsn) {
    console.info('[Sentry] No DSN configured, skipping initialization');
    return;
  }

  Sentry.init({
    dsn,
    environment: import.meta.env.MODE,
    release: `barq-fleet-frontend@${import.meta.env.VITE_APP_VERSION || '1.0.0'}`,

    // Performance Monitoring
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        // Mask all text in replay recordings
        maskAllText: true,
        // Block all media in replay recordings
        blockAllMedia: true,
      }),
    ],

    // Set tracesSampleRate to 1.0 to capture 100%
    // of transactions for performance monitoring.
    // We recommend adjusting this value in production
    tracesSampleRate: parseFloat(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || '1.0'),

    // Capture Replay for 10% of all sessions,
    // plus for 100% of sessions with an error
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,

    // Don't send PII data
    sendDefaultPii: false,

    // Filter out specific errors
    beforeSend(event, hint) {
      const error = hint.originalException;

      // Ignore network errors that users commonly encounter
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        return null;
      }

      // Ignore aborted requests
      if (error instanceof DOMException && error.name === 'AbortError') {
        return null;
      }

      return event;
    },

    // Filter out specific transactions
    beforeSendTransaction(event) {
      // Filter out health check endpoints from transactions
      if (event.transaction?.includes('/health')) {
        return null;
      }
      return event;
    },
  });

  console.info('[Sentry] Initialized successfully');
}

/**
 * Set user context for Sentry
 */
export function setSentryUser(user: { id: string; email?: string; username?: string } | null): void {
  if (user) {
    Sentry.setUser({
      id: user.id,
      email: user.email,
      username: user.username,
    });
  } else {
    Sentry.setUser(null);
  }
}

/**
 * Breadcrumb options for tracking user actions
 */
interface BreadcrumbOptions {
  category?: string;
  message: string;
  level?: 'debug' | 'info' | 'warning' | 'error' | 'fatal';
  data?: Record<string, unknown>;
}

/**
 * Add breadcrumb for tracking user actions
 */
export function addSentryBreadcrumb(options: BreadcrumbOptions): void {
  Sentry.addBreadcrumb({
    message: options.message,
    category: options.category || 'app',
    level: options.level || 'info',
    data: options.data,
    timestamp: Date.now() / 1000,
  });
}

/**
 * Capture a message for Sentry
 */
export function captureMessage(message: string, level: Sentry.SeverityLevel = 'info'): void {
  Sentry.captureMessage(message, level);
}

/**
 * Capture an exception for Sentry
 */
export function captureException(error: Error, context?: Record<string, unknown>): void {
  Sentry.captureException(error, {
    extra: context,
  });
}

/**
 * Set extra context for Sentry
 */
export function setSentryContext(key: string, context: Record<string, unknown>): void {
  Sentry.setContext(key, context);
}

// Export Sentry for direct access if needed
export { Sentry };
