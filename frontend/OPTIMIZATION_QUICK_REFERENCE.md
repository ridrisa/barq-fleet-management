# Frontend Optimization - Quick Reference

## Build Commands

```bash
# Development
npm run dev

# Production build
npm run build:prod

# Build with analysis
npm run build:analyze
npm run analyze  # Opens stats.html automatically

# Preview production build
npm run preview

# Type checking
npm run type-check
```

---

## Performance Monitoring

### View Metrics in Development

```javascript
import { getPerformanceMetrics } from '@/utils/performanceMonitoring';

// Get current metrics
const metrics = getPerformanceMetrics();
console.log(metrics);
// { cls, fid, fcp, lcp, ttfb }
```

### Custom Performance Marks

```javascript
import { mark, measure } from '@/utils/performanceMonitoring';

// Mark a point in time
mark('feature-start');

// ... do work ...

mark('feature-end');

// Measure duration
const duration = measure('feature-duration', 'feature-start', 'feature-end');
console.log(`Feature took ${duration}ms`);
```

---

## Service Worker Management

### Register Service Worker

```typescript
import { registerServiceWorker } from '@/utils/registerServiceWorker';

registerServiceWorker(); // Already called in main.tsx
```

### Unregister Service Worker (Development)

```typescript
import { unregisterServiceWorker } from '@/utils/registerServiceWorker';

await unregisterServiceWorker();
```

### Clear All Caches

```typescript
import { clearAllCaches } from '@/utils/registerServiceWorker';

await clearAllCaches();
```

### Send Commands to Service Worker

```javascript
// Skip waiting and activate new SW
navigator.serviceWorker.controller?.postMessage({
  type: 'SKIP_WAITING'
});

// Clear all caches
navigator.serviceWorker.controller?.postMessage({
  type: 'CLEAR_CACHE'
});
```

---

## Lazy Loading

### Add New Lazy Route

```typescript
// In routes.tsx
import { lazyWithRetry } from '@/utils/lazyWithRetry';

const MyNewPage = lazyWithRetry(() => import('@/pages/MyNewPage'));

// Then add to routes array
{ path: 'my-new-page', element: <MyNewPage /> }
```

### Prefetch a Route

```typescript
import { prefetchComponent } from '@/utils/lazyWithRetry';

// Prefetch on hover or mount
prefetchComponent(() => import('@/pages/Dashboard'));
```

---

## Optimized Images

### Basic Usage

```tsx
import { OptimizedImage } from '@/components/ui/OptimizedImage';

<OptimizedImage
  src="/path/to/image.jpg"
  alt="Description"
/>
```

### Advanced Usage

```tsx
<OptimizedImage
  src="/path/to/image.jpg"
  alt="Description"
  lazy={true}                    // Enable lazy loading
  aspectRatio="16/9"             // Set aspect ratio
  objectFit="cover"              // How image fills container
  blur={true}                    // Blur-up effect
  fallbackSrc="/placeholder.png" // Fallback on error
  className="rounded-lg"         // Additional classes
/>
```

---

## Bundle Analysis

### Generate Bundle Report

```bash
npm run analyze
```

This will:
1. Build the production bundle
2. Generate `dist/stats.html`
3. Open it in your browser automatically

### What to Look For

- **Large chunks:** > 500KB uncompressed
- **Duplicate code:** Same library in multiple chunks
- **Unused code:** Tree shaking opportunities
- **Heavy dependencies:** Consider alternatives

---

## Environment Variables

### Development (.env.development)

```env
VITE_API_URL=http://localhost:8000
VITE_ENABLE_SW=false
VITE_ENABLE_PERF_MONITORING=true
VITE_ENABLE_ANALYTICS=false
```

### Production (.env.production)

```env
VITE_API_URL=https://api.barqfleet.com
VITE_CDN_URL=https://cdn.barqfleet.com
VITE_ENABLE_SW=true
VITE_ENABLE_PERF_MONITORING=true
VITE_ENABLE_ANALYTICS=true
```

### Access in Code

```typescript
const apiUrl = import.meta.env.VITE_API_URL;
const isProd = import.meta.env.PROD;
const isDev = import.meta.env.DEV;
```

---

## Debugging

### Check Service Worker Status

```javascript
// In browser console
navigator.serviceWorker.getRegistrations()
  .then(regs => console.log(regs));
```

### View Cached Resources

1. Open DevTools
2. Application tab
3. Cache Storage → barq-*
4. View cached entries

### Monitor Network Performance

1. Open DevTools
2. Network tab
3. Throttle to "Slow 3G"
4. Check load times

### Lighthouse Audit

1. Open DevTools
2. Lighthouse tab
3. Select "Performance"
4. Generate report

---

## Compression

### Verify Compression is Working

```bash
# Check if .gz and .br files are generated
ls -lh dist/assets/js/

# Should see:
# vendor-react-abc123.js
# vendor-react-abc123.js.gz
# vendor-react-abc123.js.br
```

### Nginx Configuration

```nginx
# Enable gzip static
gzip_static on;

# Enable brotli static
brotli_static on;

# Compression levels
gzip_comp_level 6;
brotli_comp_level 6;
```

---

## Common Issues & Solutions

### Issue: Chunk load error

**Solution:**
- `lazyWithRetry()` automatically retries 3 times
- Check network connection
- Verify files exist in dist/

### Issue: Service worker not registering

**Solution:**
```javascript
// Check if enabled
console.log(import.meta.env.VITE_ENABLE_SW);

// Manually unregister
await unregisterServiceWorker();

// Re-register
registerServiceWorker();
```

### Issue: Large bundle size

**Solution:**
```bash
# Analyze bundle
npm run analyze

# Check for:
# 1. Duplicate dependencies
# 2. Unused code
# 3. Heavy libraries that can be lazy loaded
```

### Issue: Performance metrics not showing

**Solution:**
```javascript
// Check if monitoring is enabled
console.log(import.meta.env.VITE_ENABLE_PERF_MONITORING);

// Manually initialize
import { initPerformanceMonitoring } from '@/utils/performanceMonitoring';
initPerformanceMonitoring();
```

---

## Best Practices

### ✅ Do

- Use `lazyWithRetry()` for all routes
- Analyze bundle regularly
- Monitor Web Vitals in production
- Test on slow connections
- Lazy load heavy libraries (charts, documents)
- Use OptimizedImage for all images
- Enable service worker in production
- Compress images before adding to project

### ❌ Don't

- Import entire libraries (use tree-shakeable imports)
- Add large dependencies without analysis
- Skip lazy loading for new routes
- Disable compression
- Ignore bundle size warnings
- Load charts on initial bundle
- Disable service worker without reason

---

## Performance Targets

| Metric | Target | Check With |
|--------|--------|------------|
| LCP | < 2.5s | Lighthouse, Web Vitals |
| FID | < 100ms | Web Vitals |
| CLS | < 0.1 | Lighthouse, Web Vitals |
| TTI | < 3.5s | Lighthouse |
| Initial Bundle | < 200KB (gzipped) | Bundle analysis |
| Lighthouse Score | > 90 | Lighthouse audit |

---

## Quick Deployment Checklist

```bash
# 1. Type check
npm run type-check

# 2. Run tests
npm run test:run

# 3. Build for production
npm run build:prod

# 4. Analyze bundle (optional)
npm run analyze

# 5. Preview build
npm run preview

# 6. Deploy dist/ folder
# Copy to web server or CDN
```

---

## Useful Resources

### Documentation
- [Vite Build Optimization](https://vitejs.dev/guide/build.html)
- [Web Vitals](https://web.dev/vitals/)
- [Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

### Tools
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Bundle Analyzer](https://github.com/webpack-contrib/webpack-bundle-analyzer)

---

**Last Updated:** November 23, 2025
**Optimizations Version:** 1.0.0
