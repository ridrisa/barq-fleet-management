import { onCLS, onINP, onFCP, onLCP, onTTFB, Metric } from 'web-vitals';

interface PerformanceMetrics {
  cls: number | null;
  inp: number | null;
  fcp: number | null;
  lcp: number | null;
  ttfb: number | null;
}

const metrics: PerformanceMetrics = {
  cls: null,
  inp: null,
  fcp: null,
  lcp: null,
  ttfb: null,
};

/**
 * Send metric to analytics endpoint
 */
function sendToAnalytics(metric: Metric): void {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
    timestamp: Date.now(),
    url: window.location.href,
    userAgent: navigator.userAgent,
  });

  // Use beacon API if available for reliability
  if (navigator.sendBeacon) {
    navigator.sendBeacon('/api/analytics/web-vitals', body);
  } else {
    // Fallback to fetch with keepalive
    fetch('/api/analytics/web-vitals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      keepalive: true,
    }).catch(() => {
      // Silently fail analytics
      console.debug('Failed to send web vitals metric');
    });
  }
}

/**
 * Log metric to console in development
 */
function logMetric(metric: Metric): void {
  if (import.meta.env.DEV) {
    const color = metric.rating === 'good' ? 'green' : metric.rating === 'needs-improvement' ? 'orange' : 'red';
    console.log(
      `%c${metric.name}: ${metric.value.toFixed(2)}ms (${metric.rating})`,
      `color: ${color}; font-weight: bold;`
    );
  }

  // Store metric
  switch (metric.name) {
    case 'CLS':
      metrics.cls = metric.value;
      break;
    case 'INP':
      metrics.inp = metric.value;
      break;
    case 'FCP':
      metrics.fcp = metric.value;
      break;
    case 'LCP':
      metrics.lcp = metric.value;
      break;
    case 'TTFB':
      metrics.ttfb = metric.value;
      break;
  }
}

/**
 * Handle metric collection
 */
function handleMetric(metric: Metric): void {
  logMetric(metric);
  sendToAnalytics(metric);
}

/**
 * Initialize performance monitoring
 * Collects Web Vitals and custom performance metrics
 */
export function initPerformanceMonitoring(): void {
  // Core Web Vitals
  onCLS(handleMetric);
  onINP(handleMetric);
  onFCP(handleMetric);
  onLCP(handleMetric);
  onTTFB(handleMetric);

  // Custom performance marks
  if (performance && performance.mark) {
    // Mark when app becomes interactive
    window.addEventListener('load', () => {
      performance.mark('app-load-complete');

      // Measure time to interactive
      const navigationEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigationEntry) {
        const tti = navigationEntry.domInteractive - navigationEntry.fetchStart;
        console.log(`%cTime to Interactive: ${tti.toFixed(2)}ms`, 'color: blue; font-weight: bold;');
      }
    });
  }

  // Monitor long tasks
  if ('PerformanceObserver' in window) {
    try {
      const longTaskObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (import.meta.env.DEV) {
            console.warn('Long task detected:', entry.duration.toFixed(2) + 'ms');
          }
        }
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });
    } catch (e) {
      // Long task API not supported
      console.debug('Long task monitoring not supported');
    }
  }

  // Report current metrics on visibility change
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      // Report all collected metrics when page becomes hidden
      if (import.meta.env.DEV) {
        console.log('Final Performance Metrics:', metrics);
      }
    }
  });
}

/**
 * Get current performance metrics
 */
export function getPerformanceMetrics(): PerformanceMetrics {
  return { ...metrics };
}

/**
 * Mark a custom performance point
 */
export function mark(name: string): void {
  if (performance && performance.mark) {
    performance.mark(name);
  }
}

/**
 * Measure time between two marks
 */
export function measure(name: string, startMark: string, endMark?: string): number | null {
  if (performance && performance.measure) {
    try {
      performance.measure(name, startMark, endMark);
      const measure = performance.getEntriesByName(name, 'measure')[0];
      return measure ? measure.duration : null;
    } catch (e) {
      console.error('Failed to measure performance:', e);
      return null;
    }
  }
  return null;
}
