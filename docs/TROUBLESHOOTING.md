# BARQ Fleet Management - Troubleshooting Guide

**Version:** 1.0.0
**Last Updated:** November 23, 2025

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Login & Authentication](#login--authentication)
3. [Performance Issues](#performance-issues)
4. [Database Issues](#database-issues)
5. [API Errors](#api-errors)
6. [Frontend Issues](#frontend-issues)
7. [Deployment Issues](#deployment-issues)
8. [Email & Notifications](#email--notifications)
9. [Integration Issues](#integration-issues)
10. [Getting Help](#getting-help)

---

## Quick Diagnostics

### System Health Check

Run these commands to quickly diagnose system health:

```bash
# 1. Check API health
curl https://api.barq.com/health
# Expected: {"status": "healthy", "version": "1.0.0"}

# 2. Check database connectivity
gcloud sql connect barq-production-db --user=postgres
# Should connect successfully

# 3. Check Redis connectivity
redis-cli -h [REDIS_IP] PING
# Expected: PONG

# 4. Check Cloud Run service status
gcloud run services describe barq-api --region=us-central1
# Should show SERVING status

# 5. Check recent errors
gcloud logging read "severity>=ERROR" --limit=20
```

### Common Symptoms & Quick Fixes

| Symptom | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| API returns 500 errors | Backend crash | Check logs, restart service |
| Slow response times | High load | Scale up instances |
| Cannot login | Authentication issue | Check JWT secret, database connection |
| 404 errors | Route not found | Check API endpoint, verify deployment |
| Database connection errors | Pool exhausted | Increase pool size, terminate idle connections |

---

## Login & Authentication

### Issue: Cannot Login with Email/Password

**Symptoms:**
- "Invalid credentials" error
- Login button does nothing
- Page redirects back to login

**Diagnosis:**
```bash
# Check if user exists
psql -U postgres -d barq_fleet -c "
  SELECT id, email, is_active
  FROM users
  WHERE email = 'user@example.com';
"

# Check backend logs for auth errors
gcloud logging read \
  "resource.type=cloud_run_revision AND jsonPayload.message=~'authentication'" \
  --limit=20
```

**Solutions:**

1. **Verify credentials**
   - Ensure email is correct
   - Password is case-sensitive
   - No extra spaces

2. **Reset password**
   ```bash
   # Run password reset script
   python backend/scripts/reset_password.py user@example.com
   ```

3. **Check account status**
   ```sql
   -- Ensure account is active
   UPDATE users
   SET is_active = true
   WHERE email = 'user@example.com';
   ```

4. **Clear browser cache**
   - Clear cookies and cache
   - Try incognito mode

---

### Issue: Google OAuth Not Working

**Symptoms:**
- "Sign in with Google" button fails
- Redirect error
- "Invalid OAuth token" error

**Diagnosis:**
```bash
# Check Google OAuth configuration
echo $GOOGLE_OAUTH_CLIENT_ID
echo $GOOGLE_OAUTH_CLIENT_SECRET

# Check redirect URI configuration
# Should match Google Cloud Console settings
```

**Solutions:**

1. **Verify OAuth credentials**
   - Go to Google Cloud Console
   - Check OAuth 2.0 Client ID
   - Verify redirect URIs include:
     - `https://api.barq.com/api/v1/auth/google/callback`
     - `http://localhost:8000/api/v1/auth/google/callback` (dev)

2. **Update environment variables**
   ```bash
   # Update Secret Manager
   echo -n "correct-client-id" | gcloud secrets versions add google-oauth-client-id --data-file=-
   echo -n "correct-client-secret" | gcloud secrets versions add google-oauth-client-secret --data-file=-

   # Restart service
   gcloud run services update barq-api --update-env-vars RESTART=$(date +%s)
   ```

---

### Issue: JWT Token Expired

**Symptoms:**
- "Token expired" error
- Redirected to login after short time
- API returns 401 errors

**Diagnosis:**
```bash
# Check token expiry setting
grep JWT_ACCESS_TOKEN_EXPIRE_MINUTES backend/.env

# Decode JWT token (for debugging)
# Use https://jwt.io to decode and check expiry
```

**Solutions:**

1. **Increase token expiry** (if needed)
   ```python
   # backend/app/core/security.py
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Increase from 30
   ```

2. **Implement refresh token**
   - Frontend should automatically refresh token before expiry
   - Check frontend token refresh logic

3. **Clear old tokens**
   - Logout and login again
   - Clear local storage

---

## Performance Issues

### Issue: Slow API Response Times

**Symptoms:**
- API requests taking > 2 seconds
- Timeouts
- Users reporting slow page loads

**Diagnosis:**
```bash
# Check Cloud Monitoring metrics
# - API latency (P50, P95, P99)
# - CPU utilization
# - Memory utilization

# Check slow queries
psql -U postgres -d barq_fleet -c "
  SELECT query, mean_exec_time, calls
  FROM pg_stat_statements
  ORDER BY mean_exec_time DESC
  LIMIT 10;
"

# Check Redis hit rate
redis-cli INFO stats | grep hit_rate
```

**Solutions:**

1. **Scale up Cloud Run instances**
   ```bash
   gcloud run services update barq-api \
     --min-instances=2 \
     --max-instances=20 \
     --cpu=2 \
     --memory=2Gi
   ```

2. **Optimize slow queries**
   ```sql
   -- Add index for commonly queried columns
   CREATE INDEX idx_couriers_status ON couriers(status);
   CREATE INDEX idx_deliveries_date ON deliveries(scheduled_time);

   -- Analyze query plan
   EXPLAIN ANALYZE SELECT * FROM couriers WHERE status = 'active';
   ```

3. **Increase Redis caching**
   ```python
   # Increase cache TTL
   @cache(ttl=3600)  # 1 hour instead of 5 minutes
   def get_couriers():
       ...
   ```

4. **Enable query result caching**
   ```python
   # Use Redis for query caching
   from functools import lru_cache

   @lru_cache(maxsize=128)
   def get_active_couriers():
       ...
   ```

---

### Issue: High Memory Usage

**Symptoms:**
- Containers restarting (OOM)
- Memory usage > 90%
- Slow performance

**Diagnosis:**
```bash
# Check memory metrics
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/memory/utilizations"'

# Check container logs for OOM
gcloud logging read "resource.type=cloud_run_revision AND jsonPayload.message=~'Out of memory'"
```

**Solutions:**

1. **Increase memory limit**
   ```bash
   gcloud run services update barq-api --memory=2Gi
   ```

2. **Fix memory leaks**
   - Profile application to find leaks
   - Ensure database connections are closed
   - Clear unused objects

3. **Optimize database queries**
   - Use pagination
   - Limit result sets
   - Use select_related() to avoid N+1 queries

---

## Database Issues

### Issue: Database Connection Pool Exhausted

**Symptoms:**
- "Too many connections" error
- Cannot connect to database
- Intermittent 500 errors

**Diagnosis:**
```sql
-- Check active connections
SELECT
    count(*),
    state,
    wait_event_type
FROM pg_stat_activity
GROUP BY state, wait_event_type;

-- Check connection pool settings
SHOW max_connections;
```

**Solutions:**

1. **Terminate idle connections**
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes';
   ```

2. **Increase connection pool size**
   ```python
   # backend/app/config/database.py
   SQLALCHEMY_POOL_SIZE = 30
   SQLALCHEMY_MAX_OVERFLOW = 20
   SQLALCHEMY_POOL_PRE_PING = True
   SQLALCHEMY_POOL_RECYCLE = 300
   ```

3. **Increase max_connections**
   ```bash
   # Update Cloud SQL instance
   gcloud sql instances patch barq-production-db \
     --database-flags max_connections=200
   ```

---

### Issue: Slow Database Queries

**Symptoms:**
- Specific operations taking > 5 seconds
- Database CPU high
- Query timeouts

**Diagnosis:**
```sql
-- Enable pg_stat_statements
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Check missing indexes
SELECT schemaname, tablename, attname, n_distinct
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 1000
  AND attname NOT IN (
      SELECT attname FROM pg_index
  );
```

**Solutions:**

1. **Add indexes**
   ```sql
   -- Index frequently queried columns
   CREATE INDEX idx_couriers_status_tenant ON couriers(tenant_id, status);
   CREATE INDEX idx_deliveries_courier_date ON deliveries(courier_id, scheduled_time);
   ```

2. **Optimize queries**
   ```python
   # Use select_related to avoid N+1 queries
   couriers = db.query(Courier).options(
       joinedload(Courier.vehicle),
       joinedload(Courier.assignments)
   ).all()

   # Use pagination
   couriers = db.query(Courier).limit(20).offset(0).all()
   ```

3. **Use materialized views**
   ```sql
   -- Create materialized view for complex reports
   CREATE MATERIALIZED VIEW courier_performance AS
   SELECT
       c.id,
       c.name,
       COUNT(d.id) as total_deliveries,
       AVG(d.delivery_time - d.pickup_time) as avg_delivery_time
   FROM couriers c
   LEFT JOIN deliveries d ON c.id = d.courier_id
   GROUP BY c.id, c.name;

   -- Refresh periodically
   REFRESH MATERIALIZED VIEW courier_performance;
   ```

---

## API Errors

### Issue: 500 Internal Server Error

**Symptoms:**
- API returns 500 errors
- Generic error message
- No specific details

**Diagnosis:**
```bash
# Check recent error logs
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50 \
  --format=json

# Check for exceptions
gcloud logging read \
  "resource.type=cloud_run_revision AND jsonPayload.exc_info!=null" \
  --limit=20
```

**Solutions:**

1. **Review error logs**
   - Identify specific error
   - Fix underlying issue
   - Deploy fix

2. **Add error handling**
   ```python
   @app.exception_handler(Exception)
   async def general_exception_handler(request, exc):
       logger.error(f"Unhandled exception: {exc}", exc_info=True)
       return JSONResponse(
           status_code=500,
           content={"detail": "Internal server error"}
       )
   ```

3. **Enable debug mode (dev only)**
   ```python
   # backend/.env
   DEBUG=true  # Only in development!
   ```

---

### Issue: 404 Not Found

**Symptoms:**
- API endpoint returns 404
- Route not found
- Swagger docs missing endpoint

**Diagnosis:**
```bash
# List all registered routes
python -c "from app.main import app; print('\n'.join([str(route) for route in app.routes]))"

# Check if route is in API router
grep -r "router.get\|router.post" backend/app/api/
```

**Solutions:**

1. **Verify endpoint path**
   - Check exact path in Swagger docs
   - Ensure `/api/v1` prefix
   - Check for typos

2. **Register router**
   ```python
   # backend/app/api/api.py
   from app.api.v1 import couriers

   api_router.include_router(
       couriers.router,
       prefix="/couriers",
       tags=["couriers"]
   )
   ```

3. **Redeploy**
   ```bash
   git push origin main  # Triggers deployment
   ```

---

## Frontend Issues

### Issue: Blank White Screen

**Symptoms:**
- Frontend shows blank white screen
- No content loads
- Console shows errors

**Diagnosis:**
```javascript
// Open browser console (F12)
// Check for errors

// Common errors:
// - Module not found
// - Syntax error
// - Network error
```

**Solutions:**

1. **Clear cache and reload**
   ```
   Ctrl+Shift+R (Windows/Linux)
   Cmd+Shift+R (Mac)
   ```

2. **Check console errors**
   - Fix JavaScript errors
   - Ensure all dependencies installed
   - Rebuild: `npm run build`

3. **Verify API connection**
   ```javascript
   // Check .env.local
   VITE_API_BASE_URL=http://localhost:8000
   ```

---

### Issue: API Calls Failing from Frontend

**Symptoms:**
- Network errors in console
- CORS errors
- 401 Unauthorized

**Diagnosis:**
```javascript
// Browser console (F12 > Network tab)
// Check failed requests
// Look for:
// - Status code
// - Response body
// - CORS errors
```

**Solutions:**

1. **CORS errors**
   ```python
   # backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],  # Add frontend URL
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Authentication errors**
   ```javascript
   // Ensure token is being sent
   axios.get('/api/v1/couriers', {
       headers: {
           'Authorization': `Bearer ${token}`
       }
   })
   ```

3. **Network errors**
   - Check backend is running
   - Verify API URL in .env.local
   - Check firewall/proxy settings

---

## Deployment Issues

### Issue: Cloud Build Fails

**Symptoms:**
- Deployment fails
- Cloud Build shows error
- New version not deployed

**Diagnosis:**
```bash
# Check build logs
gcloud builds log [BUILD_ID]

# Common errors:
# - Syntax errors
# - Missing dependencies
# - Docker build failures
```

**Solutions:**

1. **Syntax errors**
   ```bash
   # Test locally first
   cd backend
   python -m py_compile app/**/*.py

   cd frontend
   npm run type-check
   ```

2. **Missing dependencies**
   ```bash
   # Ensure requirements.txt is updated
   pip freeze > requirements.txt

   # Ensure package.json is updated
   npm install --save package-name
   ```

3. **Docker build failures**
   ```bash
   # Test Docker build locally
   docker build -t barq-api -f backend/Dockerfile .
   docker run -p 8000:8000 barq-api
   ```

---

### Issue: Migration Fails

**Symptoms:**
- Alembic migration fails
- Database schema out of sync
- Deployment rolls back

**Diagnosis:**
```bash
# Check migration status
alembic current

# Check migration history
alembic history

# Test migration locally
alembic upgrade head --sql > test.sql
cat test.sql  # Review SQL
```

**Solutions:**

1. **Fix migration script**
   ```python
   # Fix errors in migration file
   # backend/alembic/versions/xxx_migration.py
   ```

2. **Rollback and retry**
   ```bash
   alembic downgrade -1
   # Fix migration
   alembic upgrade head
   ```

3. **Force migration**
   ```bash
   # Mark as applied (use with caution!)
   alembic stamp head
   ```

---

## Email & Notifications

### Issue: Emails Not Sending

**Symptoms:**
- Users not receiving emails
- Password reset emails missing
- No error messages

**Diagnosis:**
```bash
# Check SMTP configuration
echo $SMTP_HOST
echo $SMTP_PORT
echo $SMTP_USERNAME

# Check email logs
gcloud logging read \
  "jsonPayload.message=~'email'" \
  --limit=20

# Test SMTP connection
python backend/scripts/test_smtp.py
```

**Solutions:**

1. **Verify SMTP credentials**
   ```bash
   # Test SMTP manually
   telnet smtp.gmail.com 587
   # Should connect successfully
   ```

2. **Check Gmail app password**
   - For Gmail, use App Password, not regular password
   - Generate at: https://myaccount.google.com/apppasswords

3. **Update SMTP settings**
   ```python
   # backend/app/config/settings.py
   SMTP_HOST = "smtp.gmail.com"
   SMTP_PORT = 587
   SMTP_USERNAME = "your-email@gmail.com"
   SMTP_PASSWORD = "app-password"  # Not regular password!
   SMTP_TLS = True
   ```

---

## Integration Issues

### Issue: BigQuery Sync Not Working

**Symptoms:**
- Data not syncing to BigQuery
- Analytics reports outdated
- Sync job failing

**Diagnosis:**
```bash
# Check BigQuery job status
bq ls -j --max_results=10

# Check service account permissions
gcloud projects get-iam-policy barq-production \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"
```

**Solutions:**

1. **Grant BigQuery permissions**
   ```bash
   gcloud projects add-iam-policy-binding barq-production \
     --member="serviceAccount:barq-api@barq-production.iam.gserviceaccount.com" \
     --role="roles/bigquery.dataEditor"
   ```

2. **Retry sync job**
   ```bash
   python backend/scripts/sync_to_bigquery.py --force
   ```

---

## Getting Help

### Self-Service Resources

1. **Documentation**
   - [Deployment Runbook](DEPLOYMENT_RUNBOOK.md)
   - [Architecture Docs](ARCHITECTURE.md)
   - [Operations Playbook](OPERATIONS_PLAYBOOK.md)
   - [API Reference](API_REFERENCE.md)

2. **Logs & Monitoring**
   - Cloud Logging: https://console.cloud.google.com/logs
   - Cloud Monitoring: https://console.cloud.google.com/monitoring
   - Error Reporting: https://console.cloud.google.com/errors

3. **Community**
   - Stack Overflow (tag: barq-fleet)
   - Internal Slack: #engineering

### Contact Support

**Development Team:**
- Email: dev@barq.com
- Slack: #engineering

**DevOps Team:**
- Email: devops@barq.com
- Slack: #devops
- On-call: PagerDuty

**Emergency:**
- P0/P1 incidents: Page on-call engineer via PagerDuty
- Security incidents: security@barq.com (24/7)

### Creating a Bug Report

When reporting a bug, include:

1. **Description:** What happened?
2. **Expected behavior:** What should happen?
3. **Steps to reproduce:**
   - Step 1
   - Step 2
   - Step 3
4. **Environment:** Production/Staging/Local
5. **Logs:** Relevant error logs
6. **Screenshots:** If applicable
7. **Impact:** How many users affected?

**Template:**
```markdown
## Bug Report

**Description:**
API returns 500 error when creating courier

**Expected Behavior:**
Courier should be created successfully

**Steps to Reproduce:**
1. Navigate to Fleet > Couriers
2. Click "+ Add Courier"
3. Fill in form
4. Click "Create"
5. Error appears

**Environment:** Production

**Error Log:**
```
[Error log here]
```

**Impact:** All users unable to create couriers (P1)
```

---

**Document Owner:** Engineering Team
**Review Cycle:** Quarterly
**Last Updated:** November 23, 2025
