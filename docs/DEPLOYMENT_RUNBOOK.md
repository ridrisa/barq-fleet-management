# BARQ Fleet Management - Deployment Runbook

**Version:** 1.0.0
**Last Updated:** November 23, 2025
**Target Environment:** Google Cloud Platform (Cloud Run)

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Migration](#database-migration)
4. [Deployment Steps](#deployment-steps)
5. [Post-Deployment Verification](#post-deployment-verification)
6. [Rollback Procedures](#rollback-procedures)
7. [Common Issues](#common-issues)
8. [Emergency Contacts](#emergency-contacts)

---

## Pre-Deployment Checklist

Complete this checklist before **every** deployment:

### Code Quality

- [ ] All tests passing (`pytest` for backend, `npm test` for frontend)
- [ ] Code coverage meets threshold (>80%)
- [ ] ESLint/Black code formatting applied
- [ ] TypeScript compilation successful (no errors)
- [ ] No security vulnerabilities (`npm audit`, `safety check`)

### Configuration

- [ ] Environment variables verified in Secret Manager
- [ ] Database connection strings updated
- [ ] API keys and secrets rotated (if needed)
- [ ] CORS origins configured correctly
- [ ] Rate limits configured

### Database

- [ ] Migration scripts reviewed and tested
- [ ] Database backup created
- [ ] Migration rollback plan ready
- [ ] No breaking schema changes (or migration plan ready)

### Documentation

- [ ] Changelog updated
- [ ] API documentation current
- [ ] Deployment notes prepared
- [ ] Known issues documented

### Stakeholder Communication

- [ ] Deployment window communicated to team
- [ ] Maintenance notification sent to users (if downtime expected)
- [ ] Rollback plan communicated
- [ ] On-call engineer identified

### Infrastructure

- [ ] Cloud Run service configuration reviewed
- [ ] Load balancer health checks configured
- [ ] Monitoring alerts active
- [ ] Logs aggregation verified

---

## Environment Setup

### Local Development

```bash
# Clone repository
git clone https://github.com/barq/fleet-management.git
cd fleet-management

# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# Setup environment variables
cp backend/.env.example backend/.env
# Edit .env with actual values

# Start database
docker-compose up -d postgres redis

# Run migrations
cd backend
alembic upgrade head

# Start services
# Terminal 1 (Backend)
cd backend
uvicorn app.main:app --reload

# Terminal 2 (Frontend)
cd frontend
npm run dev
```

### Staging Environment

**URL:** https://staging-api.barq.com

**Access:**
- Requires VPN connection
- Staging credentials in Secret Manager: `staging-db-credentials`

### Production Environment

**URL:** https://api.barq.com

**Access:**
- Requires production VPN
- Admin access only
- All changes via CI/CD pipeline

---

## Database Migration

### Pre-Migration Steps

1. **Create Database Backup**

```bash
# Connect to Cloud SQL
gcloud sql connect barq-production --user=postgres

# Create backup
pg_dump -U postgres -d barq_fleet -F c -f backup_$(date +%Y%m%d_%H%M%S).dump

# Upload to Cloud Storage
gsutil cp backup_*.dump gs://barq-backups/pre-deployment/
```

2. **Review Migration Scripts**

```bash
# List pending migrations
cd backend
alembic current
alembic history

# Review migration SQL
alembic upgrade head --sql > migration.sql
cat migration.sql  # Review changes
```

3. **Test Migration on Staging**

```bash
# Deploy to staging first
gcloud builds submit --config cloudbuild-staging.yaml

# Verify migration
gcloud sql connect barq-staging --user=postgres
\dt  # List tables
SELECT * FROM alembic_version;  # Check version
```

### Migration Execution

#### Option 1: Automatic (via Cloud Build)

Migration runs automatically during deployment:

```yaml
# cloudbuild.yaml includes:
- name: 'python:3.11'
  entrypoint: bash
  args:
    - '-c'
    - |
      cd backend
      alembic upgrade head
```

#### Option 2: Manual Migration

For complex migrations, run manually:

```bash
# 1. Scale down application (prevent concurrent writes)
gcloud run services update barq-api --min-instances=0 --max-instances=0

# 2. Run migration via Cloud Build
gcloud builds submit --config cloudbuild-migrate.yaml

# 3. Verify migration
gcloud sql connect barq-production --user=postgres
SELECT * FROM alembic_version;

# 4. Scale up application
gcloud run services update barq-api --min-instances=1 --max-instances=10
```

### Migration Rollback

If migration fails:

```bash
# Downgrade one version
alembic downgrade -1

# Or restore from backup
gsutil cp gs://barq-backups/pre-deployment/backup_TIMESTAMP.dump .
pg_restore -U postgres -d barq_fleet backup_TIMESTAMP.dump
```

---

## Deployment Steps

### Step 1: Prepare Release

```bash
# 1. Create release branch
git checkout main
git pull origin main
git checkout -b release/v1.2.0

# 2. Update version numbers
# backend/app/__init__.py
__version__ = "1.2.0"

# frontend/package.json
"version": "1.2.0"

# 3. Update CHANGELOG.md
# Add release notes

# 4. Commit and tag
git add .
git commit -m "chore: release v1.2.0"
git tag v1.2.0
git push origin release/v1.2.0 --tags
```

### Step 2: Deploy to Staging

```bash
# 1. Trigger staging deployment
git push origin release/v1.2.0

# 2. Monitor Cloud Build
gcloud builds list --ongoing

# 3. View logs
gcloud builds log [BUILD_ID] --stream

# 4. Wait for completion (typically 5-10 minutes)
```

### Step 3: Verify Staging

```bash
# 1. Check health endpoint
curl https://staging-api.barq.com/health

# 2. Run smoke tests
cd backend
pytest tests/smoke/ -v

# 3. Manual verification
# - Login to staging UI
# - Create test courier
# - Create test delivery
# - Generate test payroll
# - Check dashboard

# 4. Performance check
# - Response times < 500ms
# - No 5xx errors
# - Database connections stable
```

### Step 4: Deploy to Production

**IMPORTANT:** Only deploy during approved maintenance windows.

```bash
# 1. Create pull request: release/v1.2.0 -> main
gh pr create --title "Release v1.2.0" --body "Production deployment"

# 2. Get approval from:
# - Tech Lead
# - Product Manager
# - DevOps Engineer

# 3. Merge to main
gh pr merge --squash

# 4. Production deployment triggers automatically
# Monitor at: https://console.cloud.google.com/cloud-build

# 5. Watch deployment logs
gcloud builds log [BUILD_ID] --stream
```

### Step 5: Production Deployment Process

The CI/CD pipeline performs these steps automatically:

1. **Build Backend Image**
   - Docker image built
   - Pushed to Container Registry: `gcr.io/barq-production/api:v1.2.0`

2. **Build Frontend**
   - React app built
   - Static files uploaded to Cloud Storage
   - CDN cache invalidated

3. **Database Migration**
   - Alembic migrations run
   - Schema updated

4. **Deploy to Cloud Run**
   - New revision deployed
   - Traffic gradually shifted (0% -> 10% -> 50% -> 100%)
   - Old revision kept for rollback

5. **Health Checks**
   - Health endpoint monitored
   - Error rate checked
   - Rollback if issues detected

**Expected Duration:** 10-15 minutes

---

## Post-Deployment Verification

### Immediate Checks (0-5 minutes)

```bash
# 1. Health check
curl https://api.barq.com/health
# Expected: {"status": "healthy", "version": "1.2.0"}

# 2. Check Cloud Run service
gcloud run services describe barq-api --region=us-central1

# 3. Monitor error logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 --format=json | jq '.[] | select(.severity=="ERROR")'

# 4. Check database connections
# Should see new connections from new revision
```

### Functional Tests (5-15 minutes)

```bash
# Run automated E2E tests
cd backend
pytest tests/e2e/ -v --production

# Key workflows to test manually:
# 1. User login (JWT + Google OAuth)
# 2. Create courier
# 3. Assign vehicle
# 4. Create delivery
# 5. Approve workflow
# 6. Generate payroll
```

### Performance Monitoring (15-30 minutes)

Monitor these metrics in Cloud Monitoring:

1. **Response Times**
   - P50: < 200ms
   - P95: < 500ms
   - P99: < 1000ms

2. **Error Rates**
   - 4xx errors: < 1%
   - 5xx errors: < 0.1%

3. **Database Performance**
   - Connection pool: < 80% usage
   - Query times: < 100ms average

4. **Resource Usage**
   - CPU: < 70%
   - Memory: < 80%
   - Container instances: Auto-scaling working

### User Acceptance (30+ minutes)

- [ ] Admin dashboard loads correctly
- [ ] All navigation menus functional
- [ ] Data displays correctly
- [ ] Forms submit successfully
- [ ] Reports generate correctly
- [ ] No JavaScript errors in console
- [ ] Mobile responsive working

---

## Rollback Procedures

### When to Rollback

Rollback immediately if:
- Critical bug affecting > 10% of users
- Database corruption detected
- Security vulnerability discovered
- Error rate > 5%
- Performance degradation > 50%

### Rollback Steps

#### Quick Rollback (Application Only)

```bash
# 1. Revert to previous Cloud Run revision
gcloud run services update-traffic barq-api \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1

# Verification
gcloud run revisions list --service=barq-api

# Expected: Traffic shifted to previous revision in < 1 minute
```

#### Full Rollback (Application + Database)

```bash
# 1. Scale down application
gcloud run services update barq-api --min-instances=0 --max-instances=0

# 2. Restore database from backup
gsutil cp gs://barq-backups/pre-deployment/backup_TIMESTAMP.dump .
pg_restore -U postgres -d barq_fleet --clean backup_TIMESTAMP.dump

# 3. Revert application code
git revert [COMMIT_HASH]
git push origin main

# 4. Deploy reverted code
# (CI/CD pipeline triggers automatically)

# 5. Verify
curl https://api.barq.com/health
```

#### Emergency Rollback

If normal rollback fails:

```bash
# 1. Enable maintenance mode
gcloud run services update barq-api \
  --set-env-vars MAINTENANCE_MODE=true

# 2. Restore from backup
# Follow full rollback procedure above

# 3. Disable maintenance mode
gcloud run services update barq-api \
  --set-env-vars MAINTENANCE_MODE=false
```

### Post-Rollback

1. **Communicate**
   - Notify team in #engineering Slack channel
   - Update status page
   - Email affected users (if needed)

2. **Investigate**
   - Review logs for root cause
   - Create incident report
   - Schedule post-mortem

3. **Fix Forward**
   - Create hotfix branch
   - Apply fix
   - Test thoroughly
   - Deploy hotfix

---

## Common Issues

### Issue 1: Migration Timeout

**Symptom:** Database migration takes > 5 minutes

**Solution:**
```bash
# 1. Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

# 2. Terminate blocking queries
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle in transaction' AND query_start < NOW() - INTERVAL '5 minutes';

# 3. Retry migration
alembic upgrade head
```

### Issue 2: Cloud Run Timeout

**Symptom:** Deployment fails with "timeout" error

**Solution:**
```bash
# Increase timeout
gcloud run services update barq-api \
  --timeout=300s \
  --region=us-central1
```

### Issue 3: Memory Issues

**Symptom:** Container OOM (Out of Memory)

**Solution:**
```bash
# Increase memory limit
gcloud run services update barq-api \
  --memory=2Gi \
  --region=us-central1
```

### Issue 4: Database Connection Pool Exhausted

**Symptom:** "Too many connections" error

**Solution:**
```bash
# 1. Check active connections
SELECT count(*) FROM pg_stat_activity;

# 2. Terminate idle connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle' AND query_start < NOW() - INTERVAL '10 minutes';

# 3. Increase pool size in settings
# backend/app/config/settings.py
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 10
```

### Issue 5: Secret Manager Access Denied

**Symptom:** "Permission denied" when accessing secrets

**Solution:**
```bash
# Grant Cloud Run service account access
gcloud secrets add-iam-policy-binding [SECRET_NAME] \
  --member="serviceAccount:[SERVICE_ACCOUNT]" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Monitoring & Alerts

### Key Dashboards

1. **Cloud Monitoring Dashboard**
   - URL: https://console.cloud.google.com/monitoring/dashboards
   - Metrics: Response time, error rate, CPU, memory

2. **Cloud Logging**
   - URL: https://console.cloud.google.com/logs
   - Filters: `resource.type="cloud_run_revision"`

3. **Error Reporting**
   - URL: https://console.cloud.google.com/errors
   - Real-time error tracking

### Critical Alerts

Configured in Cloud Monitoring:

1. **High Error Rate**
   - Condition: Error rate > 5% for 5 minutes
   - Action: PagerDuty alert to on-call engineer

2. **High Response Time**
   - Condition: P95 latency > 2 seconds for 5 minutes
   - Action: Slack notification to #engineering

3. **Database Connection Failure**
   - Condition: Cannot connect to database
   - Action: PagerDuty alert (critical)

4. **Memory Usage High**
   - Condition: Memory > 90% for 5 minutes
   - Action: Auto-scale + Slack notification

---

## Emergency Contacts

### On-Call Rotation

- **Primary:** Check PagerDuty schedule
- **Secondary:** Check PagerDuty escalation policy

### Key Personnel

| Role | Name | Contact | Timezone |
|------|------|---------|----------|
| Tech Lead | TBD | tech-lead@barq.com | UTC+3 |
| DevOps Engineer | TBD | devops@barq.com | UTC+3 |
| Database Admin | TBD | dba@barq.com | UTC+3 |
| Product Manager | TBD | pm@barq.com | UTC+3 |

### Escalation Path

1. **Level 1:** On-call engineer (respond within 15 minutes)
2. **Level 2:** Tech Lead (respond within 30 minutes)
3. **Level 3:** CTO (respond within 1 hour)

### Communication Channels

- **Incidents:** #incidents Slack channel
- **Deployments:** #deployments Slack channel
- **Engineering:** #engineering Slack channel
- **Status Page:** https://status.barq.com

---

## Deployment Schedule

### Allowed Deployment Windows

**Production:**
- **Weekdays:** 10:00 AM - 2:00 PM UTC+3 (low traffic)
- **NOT ALLOWED:** Fridays after 12:00 PM
- **NOT ALLOWED:** Weekends and holidays
- **Emergency Hotfix:** Anytime (requires CTO approval)

**Staging:**
- Anytime

### Deployment Frequency

- **Regular Releases:** Every 2 weeks (Sprint cycle)
- **Hotfixes:** As needed
- **Security Patches:** Within 24 hours of discovery

---

## Compliance & Auditing

### Deployment Logs

All deployments automatically logged to:
- Cloud Build logs (90-day retention)
- Audit logs (7-year retention)
- CHANGELOG.md (permanent)

### Required Approvals

| Environment | Approvals Required |
|-------------|-------------------|
| Development | None |
| Staging | 1 (any engineer) |
| Production | 2 (Tech Lead + PM) |

### Audit Trail

Every deployment creates:
- Git tag with version number
- Cloud Build log with full output
- Deployment entry in database
- CHANGELOG update
- Slack notification

---

## Best Practices

1. **Always deploy to staging first**
2. **Run full test suite before deployment**
3. **Create database backup before migrations**
4. **Monitor for 30 minutes post-deployment**
5. **Deploy during low-traffic windows**
6. **Have rollback plan ready**
7. **Communicate with team**
8. **Document any issues encountered**

---

## Appendix

### Useful Commands

```bash
# Check Cloud Run service status
gcloud run services describe barq-api --region=us-central1

# View recent logs
gcloud logging read "resource.type=cloud_run_revision" --limit=100

# List Cloud Run revisions
gcloud run revisions list --service=barq-api

# Check database connection
psql postgresql://user:pass@host:5432/barq_fleet

# View Cloud Build history
gcloud builds list --limit=10

# Get service account email
gcloud iam service-accounts list
```

### Environment Variables

Key environment variables in Secret Manager:

```bash
DATABASE_URL
REDIS_URL
JWT_SECRET_KEY
GOOGLE_OAUTH_CLIENT_ID
GOOGLE_OAUTH_CLIENT_SECRET
SMTP_HOST
SMTP_USERNAME
SMTP_PASSWORD
```

---

**Document Owner:** DevOps Team
**Review Cycle:** Monthly
**Last Reviewed:** November 23, 2025
**Next Review:** December 23, 2025
