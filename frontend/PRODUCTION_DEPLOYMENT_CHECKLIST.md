# Production Deployment Checklist - BARQ Fleet Management Frontend

**Date:** November 23, 2025
**Version:** 1.0.0

---

## Pre-Deployment Checklist

### Code Quality
- [ ] All TypeScript errors resolved (`npm run type-check`)
- [ ] ESLint warnings addressed (`npm run lint`)
- [ ] Unit tests passing (`npm run test:run`)
- [ ] E2E tests passing (`npm run test:e2e`)
- [ ] Code reviewed and approved
- [ ] No console.log statements (removed in build)
- [ ] No debug code or test data

### Performance Optimization
- [ ] All routes using `lazyWithRetry()`
- [ ] Bundle analyzed (`npm run analyze`)
- [ ] Initial bundle < 200KB (gzipped)
- [ ] Critical vendor chunks optimized
- [ ] Heavy libraries (charts, documents) lazy loaded
- [ ] Images optimized (compressed, WebP where possible)
- [ ] Service worker tested
- [ ] Performance monitoring configured

### Environment Configuration
- [ ] `.env.production` configured with correct values
  - [ ] `VITE_API_URL` points to production API
  - [ ] `VITE_CDN_URL` configured (if using CDN)
  - [ ] `VITE_ENABLE_SW=true`
  - [ ] `VITE_ENABLE_PERF_MONITORING=true`
  - [ ] `VITE_ENABLE_ANALYTICS=true`
- [ ] API endpoints verified
- [ ] CORS configured on backend
- [ ] Rate limiting tested

### Security
- [ ] No hardcoded secrets or API keys
- [ ] Environment variables properly configured
- [ ] HTTPS enforced
- [ ] Content Security Policy configured
- [ ] XSS protection enabled
- [ ] CSRF protection enabled
- [ ] Secure headers configured

### Build Process
- [ ] Production build successful (`npm run build:prod`)
- [ ] Build warnings reviewed
- [ ] Gzip compression working (`.gz` files generated)
- [ ] Brotli compression working (`.br` files generated)
- [ ] Asset hashing working (files have hash in name)
- [ ] Source maps disabled (or configured correctly)

---

## Build & Test

### 1. Clean Build

```bash
# Remove old artifacts
rm -rf dist/
rm -rf node_modules/.vite/

# Fresh install (optional, if dependencies changed)
rm -rf node_modules/
npm install

# Type check
npm run type-check

# Run tests
npm run test:run

# Build for production
npm run build:prod
```

**Expected Output:**
```
✓ 1234 modules transformed.
dist/index.html                  0.50 kB
dist/assets/vendor-react-[hash].js   140 kB │ gzip: 35 kB
dist/assets/vendor-ui-[hash].js      80 kB │ gzip: 20 kB
...
✓ built in 45.23s
```

### 2. Bundle Analysis

```bash
npm run analyze
```

**Verify:**
- [ ] No unexpected large chunks
- [ ] No duplicate dependencies
- [ ] Charts and documents in separate chunks
- [ ] Each route in its own chunk

### 3. Preview Build Locally

```bash
npm run preview
```

**Test:**
- [ ] All routes load correctly
- [ ] Lazy loading working (check Network tab)
- [ ] Service worker registers
- [ ] Offline mode works
- [ ] Images load properly
- [ ] Forms submit correctly
- [ ] Authentication works
- [ ] API calls successful

### 4. Performance Testing

**Lighthouse Audit:**
- [ ] Open Chrome DevTools
- [ ] Go to Lighthouse tab
- [ ] Run audit in Incognito mode
- [ ] Performance score > 90
- [ ] Accessibility score > 90
- [ ] Best Practices score > 90
- [ ] SEO score > 90

**Web Vitals:**
- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1

**Network Testing:**
- [ ] Test on Slow 3G (DevTools throttling)
- [ ] Page loads in < 5s on 3G
- [ ] Critical content visible < 2s

---

## Server Configuration

### Nginx Configuration

Create/update `/etc/nginx/sites-available/barq-fleet`:

```nginx
server {
    listen 80;
    server_name app.barqfleet.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.barqfleet.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # Root directory
    root /var/www/barq-fleet/dist;
    index index.html;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss;

    # Brotli compression
    brotli on;
    brotli_comp_level 6;
    brotli_types text/plain text/css text/xml text/javascript
                 application/json application/javascript application/xml+rss;

    # Static file compression (pre-compressed files)
    gzip_static on;
    brotli_static on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Service worker - no cache
    location = /service-worker.js {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        expires 0;
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, must-revalidate";
    }

    # API proxy (if needed)
    location /api {
        proxy_pass https://api.barqfleet.com;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Checklist:**
- [ ] SSL certificates installed
- [ ] HTTP redirects to HTTPS
- [ ] Compression enabled (gzip + brotli)
- [ ] Static file caching configured
- [ ] Security headers added
- [ ] Service worker cache headers correct
- [ ] SPA routing configured
- [ ] API proxy configured (if needed)

### Apache Configuration (Alternative)

Create/update `.htaccess` in dist folder:

```apache
# Enable compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Enable pre-compressed files
<IfModule mod_rewrite.c>
  RewriteEngine On

  # Serve brotli if available
  RewriteCond %{HTTP:Accept-Encoding} br
  RewriteCond %{REQUEST_FILENAME}.br -f
  RewriteRule ^(.*)$ $1.br [L]

  # Serve gzip if available
  RewriteCond %{HTTP:Accept-Encoding} gzip
  RewriteCond %{REQUEST_FILENAME}.gz -f
  RewriteRule ^(.*)$ $1.gz [L]
</IfModule>

# Cache static assets
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType image/svg+xml "access plus 1 year"
  ExpiresByType text/css "access plus 1 year"
  ExpiresByType text/javascript "access plus 1 year"
  ExpiresByType application/javascript "access plus 1 year"
  ExpiresByType font/woff2 "access plus 1 year"
</IfModule>

# SPA routing
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>

# Security headers
<IfModule mod_headers.c>
  Header set X-Frame-Options "SAMEORIGIN"
  Header set X-Content-Type-Options "nosniff"
  Header set X-XSS-Protection "1; mode=block"
</IfModule>
```

---

## Deployment Process

### Option 1: Manual Deployment

```bash
# 1. Build
npm run build:prod

# 2. Verify build
ls -lh dist/

# 3. Copy to server
scp -r dist/* user@server:/var/www/barq-fleet/dist/

# 4. Set permissions
ssh user@server "chmod -R 755 /var/www/barq-fleet/dist"

# 5. Reload nginx
ssh user@server "sudo nginx -t && sudo systemctl reload nginx"
```

### Option 2: Docker Deployment

```bash
# Build Docker image
docker build -t barq-fleet-frontend:latest -f Dockerfile.prod .

# Run container
docker run -d -p 80:80 -p 443:443 \
  --name barq-fleet-frontend \
  barq-fleet-frontend:latest

# Or use docker-compose
docker-compose up -d
```

### Option 3: CI/CD (GitHub Actions Example)

See `.github/workflows/deploy.yml` (if configured)

```bash
# Trigger deployment
git tag v1.0.0
git push origin v1.0.0
```

---

## Post-Deployment Verification

### Functional Testing

**Homepage:**
- [ ] Loads without errors
- [ ] Service worker registers
- [ ] Performance metrics collected

**Authentication:**
- [ ] Login works
- [ ] Logout works
- [ ] Token refresh works
- [ ] Protected routes redirect

**Key Features:**
- [ ] Dashboard loads
- [ ] Fleet management works
- [ ] HR & Finance features accessible
- [ ] Workflows functional
- [ ] Reports generate
- [ ] Forms submit correctly

**Network:**
- [ ] All API calls succeed
- [ ] WebSocket connection works (if applicable)
- [ ] No CORS errors
- [ ] No 404 errors

### Performance Verification

**Browser DevTools:**
- [ ] Open Network tab
- [ ] Hard reload (Cmd+Shift+R)
- [ ] Verify:
  - [ ] Compressed assets served (.gz or .br)
  - [ ] Cached assets return 304
  - [ ] Initial bundle < 200KB (gzipped)
  - [ ] Page loads < 3s

**Service Worker:**
- [ ] Open Application tab
- [ ] Verify service worker registered
- [ ] Check caches populated
- [ ] Test offline mode

**Lighthouse:**
- [ ] Run Lighthouse audit
- [ ] Performance > 90
- [ ] Accessibility > 90
- [ ] Best Practices > 90
- [ ] SEO > 90

### Monitoring Setup

**Web Vitals:**
- [ ] Check `/api/analytics/web-vitals` endpoint
- [ ] Verify metrics are being sent
- [ ] Set up monitoring dashboard

**Error Tracking:**
- [ ] Configure error monitoring (Sentry, etc.)
- [ ] Test error reporting
- [ ] Set up alerts

**Analytics:**
- [ ] Verify analytics tracking
- [ ] Test key events
- [ ] Check real-time data

---

## Rollback Plan

### If Issues Arise

**Quick Rollback:**
```bash
# Restore previous version
cd /var/www/barq-fleet
mv dist dist-broken
mv dist-backup dist

# Reload nginx
sudo systemctl reload nginx
```

**Docker Rollback:**
```bash
# Stop current container
docker stop barq-fleet-frontend

# Start previous version
docker run -d -p 80:80 -p 443:443 \
  --name barq-fleet-frontend \
  barq-fleet-frontend:v1.0.0-previous
```

**Common Issues & Fixes:**

| Issue | Solution |
|-------|----------|
| White screen | Check browser console for errors |
| 404 errors | Verify SPA routing configured |
| Slow loading | Check compression enabled |
| Service worker errors | Clear caches, unregister SW |
| API errors | Check CORS, verify API URL |

---

## Post-Deployment Tasks

### Week 1
- [ ] Monitor error rates daily
- [ ] Check Web Vitals metrics
- [ ] Review user feedback
- [ ] Monitor performance trends
- [ ] Check service worker adoption

### Week 2-4
- [ ] Analyze performance data
- [ ] Review bundle sizes
- [ ] Check for optimization opportunities
- [ ] Update documentation if needed
- [ ] Plan improvements

---

## Success Criteria

### Performance
- ✅ Lighthouse Performance > 90
- ✅ LCP < 2.5s
- ✅ FID < 100ms
- ✅ CLS < 0.1
- ✅ Initial bundle < 200KB (gzipped)

### Functionality
- ✅ All features working
- ✅ No console errors
- ✅ Service worker active
- ✅ Offline mode functional
- ✅ Authentication working

### Monitoring
- ✅ Web Vitals tracking
- ✅ Error monitoring active
- ✅ Analytics collecting data
- ✅ Alerts configured

---

## Contact & Support

**Frontend Team:**
- Lead: [Name]
- Email: [Email]
- Slack: #frontend-team

**DevOps:**
- Lead: [Name]
- Email: [Email]
- Slack: #devops

**Emergency:**
- On-call: [Phone]
- Escalation: [Manager]

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Version:** 1.0.0
**Status:** [ ] Success [ ] Rollback [ ] Issues

**Notes:**
_________________________________________________
_________________________________________________
_________________________________________________
