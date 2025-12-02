# Production Deployment Checklist

## BARQ Fleet Management System

This checklist ensures a safe and successful production deployment. Complete all items before, during, and after deployment.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Day Checklist](#deployment-day-checklist)
3. [Post-Deployment Verification](#post-deployment-verification)
4. [Rollback Procedures](#rollback-procedures)
5. [Emergency Contacts](#emergency-contacts)
6. [Monitoring & Alerts](#monitoring--alerts)

---

## Pre-Deployment Checklist

### 1. Code Quality

- [ ] All tests pass locally: `pytest --cov=app`
- [ ] Test coverage meets threshold (>80%): `pytest --cov-fail-under=80`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] Code formatting verified: `black --check backend/`
- [ ] Import sorting verified: `isort --check-only backend/`
- [ ] Linting passes: `flake8 backend/`
- [ ] Type checking passes: `mypy backend/app/`
- [ ] Security scan passes: `bandit -r backend/app/`

### 2. Configuration

- [ ] Environment variables documented in `.env.example`
- [ ] All secrets stored in Secret Manager (not in code)
- [ ] `SECRET_KEY` is unique and secure (generated with `openssl rand -hex 32`)
- [ ] `JWT_SECRET_KEY` is unique and secure
- [ ] `DEBUG=false` in production
- [ ] `LOG_LEVEL=INFO` or `WARNING`
- [ ] `LOG_FORMAT=json` for log aggregation
- [ ] CORS origins restricted to production domains
- [ ] Database connection string is correct
- [ ] Redis URL is correct
- [ ] Rate limiting is configured appropriately

### 3. Database

- [ ] Database backup completed and verified
- [ ] Migration scripts tested on staging
- [ ] Migration dry-run completed: `alembic upgrade head --sql > migration.sql`
- [ ] Rollback migration tested: `alembic downgrade -1`
- [ ] Indexes are in place for performance
- [ ] Connection pool settings optimized:
  - `DB_POOL_SIZE=20`
  - `DB_MAX_OVERFLOW=40`
  - `DB_POOL_RECYCLE=3600`

### 4. Infrastructure

- [ ] Load balancer health checks configured
- [ ] Auto-scaling policies configured
- [ ] SSL/TLS certificates valid and not expiring soon
- [ ] CDN configured (if applicable)
- [ ] Firewall rules reviewed
- [ ] VPC/network configuration verified

### 5. Security

- [ ] All dependencies updated: `pip list --outdated`
- [ ] No critical vulnerabilities: `pip-audit`
- [ ] API rate limiting enabled
- [ ] HTTPS enforced (no HTTP)
- [ ] Security headers configured:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - Content-Security-Policy
  - Strict-Transport-Security
- [ ] CSRF protection enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention verified

### 6. Monitoring & Logging

- [ ] Application logs streaming to aggregator
- [ ] Error tracking configured (Sentry)
- [ ] Metrics collection enabled
- [ ] Alerts configured for:
  - [ ] High error rate (>1%)
  - [ ] High latency (P95 >500ms)
  - [ ] High CPU usage (>80%)
  - [ ] High memory usage (>80%)
  - [ ] Database connection issues
  - [ ] Redis connection issues

### 7. Documentation

- [ ] API documentation up to date
- [ ] CHANGELOG.md updated
- [ ] Release notes prepared
- [ ] Runbook updated
- [ ] Team notified of deployment window

---

## Deployment Day Checklist

### Before Deployment

- [ ] Verify current production is stable
- [ ] Check monitoring dashboards - no anomalies
- [ ] Confirm deployment window with stakeholders
- [ ] Ensure rollback artifacts are ready
- [ ] Database backup verified (< 1 hour old)
- [ ] Team members available for support

### During Deployment

1. **Announce Deployment**
   - [ ] Post in #engineering Slack channel
   - [ ] Update status page (if applicable)

2. **Deploy Backend**
   ```bash
   # Run migrations
   alembic upgrade head

   # Deploy new version
   gcloud run deploy barq-fleet-api \
     --image gcr.io/barq-fleet/api:${VERSION} \
     --region us-central1 \
     --platform managed
   ```

3. **Verify Deployment**
   - [ ] Health check passes: `curl https://api.barqfleet.com/health`
   - [ ] Version endpoint returns new version
   - [ ] No errors in logs (check first 5 minutes)

4. **Deploy Frontend**
   ```bash
   # Deploy to CDN/hosting
   npm run build && npm run deploy
   ```

5. **Smoke Tests**
   - [ ] Login works
   - [ ] Core features functional
   - [ ] API responses correct

---

## Post-Deployment Verification

### Immediate (0-15 minutes)

- [ ] Health endpoints responding:
  - `GET /health` - returns `{"status": "healthy"}`
  - `GET /api/v1/health/ready` - returns `{"status": "ready"}`
  - `GET /api/v1/health/live` - returns `{"status": "alive"}`
- [ ] No increase in error rates
- [ ] Response times within SLA
- [ ] Database connections stable
- [ ] Redis connections stable

### Short-term (15-60 minutes)

- [ ] User login/logout working
- [ ] Critical workflows functional:
  - [ ] Courier management
  - [ ] Vehicle management
  - [ ] Assignment workflow
  - [ ] Attendance tracking
- [ ] No user-reported issues
- [ ] Error rate <0.1%
- [ ] P95 latency <200ms

### Extended (1-24 hours)

- [ ] Monitor error rates continuously
- [ ] Check scheduled jobs executing correctly
- [ ] Verify background tasks processing
- [ ] Review user feedback
- [ ] Confirm no performance degradation
- [ ] Check resource utilization trends

### Success Criteria

| Metric | Target | Action if Failed |
|--------|--------|------------------|
| Error Rate | <1% | Rollback |
| P95 Latency | <500ms | Investigate |
| P99 Latency | <1000ms | Investigate |
| Health Check | 100% | Rollback |
| Database CPU | <70% | Scale up |
| Memory Usage | <80% | Scale up |

---

## Rollback Procedures

### When to Rollback

Rollback immediately if:
- Error rate exceeds 5%
- Health checks failing
- Critical functionality broken
- Database corruption detected
- Security vulnerability discovered

### Rollback Steps

#### 1. Quick Rollback (Container/Image)

```bash
# Rollback to previous Cloud Run revision
gcloud run services update-traffic barq-fleet-api \
  --to-revisions=barq-fleet-api-00XXX=100 \
  --region us-central1

# Or deploy previous image
gcloud run deploy barq-fleet-api \
  --image gcr.io/barq-fleet/api:${PREVIOUS_VERSION} \
  --region us-central1
```

#### 2. Database Rollback (if migrations applied)

```bash
# Rollback one migration
alembic downgrade -1

# Or rollback to specific revision
alembic downgrade <revision_id>
```

#### 3. Full Rollback

1. **Restore Database**
   ```bash
   # Restore from backup
   gcloud sql backups restore <BACKUP_ID> \
     --restore-instance=barq-fleet-db \
     --backup-instance=barq-fleet-db
   ```

2. **Deploy Previous Version**
   ```bash
   gcloud run deploy barq-fleet-api \
     --image gcr.io/barq-fleet/api:${PREVIOUS_VERSION}
   ```

3. **Verify**
   - Check health endpoints
   - Run smoke tests
   - Monitor error rates

#### 4. Post-Rollback

- [ ] Notify stakeholders
- [ ] Document incident
- [ ] Root cause analysis
- [ ] Fix and re-test
- [ ] Schedule new deployment

---

## Emergency Contacts

### Primary On-Call

| Role | Name | Phone | Email |
|------|------|-------|-------|
| DevOps Lead | [Name] | [Phone] | devops@barq.com |
| Backend Lead | [Name] | [Phone] | backend@barq.com |
| Frontend Lead | [Name] | [Phone] | frontend@barq.com |
| DBA | [Name] | [Phone] | dba@barq.com |

### Escalation Path

1. **Level 1**: On-call engineer (0-15 min response)
2. **Level 2**: Team lead (15-30 min response)
3. **Level 3**: Engineering manager (30-60 min response)
4. **Level 4**: CTO (Critical incidents only)

### External Contacts

| Service | Support Channel | Response Time |
|---------|----------------|---------------|
| Google Cloud | support.google.com | 1 hour (Premium) |
| Sentry | support@sentry.io | 4 hours |
| PagerDuty | support.pagerduty.com | 1 hour |

---

## Monitoring & Alerts

### Dashboards

- **Application**: [Grafana Dashboard URL]
- **Infrastructure**: [Cloud Monitoring URL]
- **Error Tracking**: [Sentry URL]
- **Logs**: [Cloud Logging URL]

### Alert Channels

- Slack: #barq-alerts
- PagerDuty: barq-fleet-oncall
- Email: alerts@barq.com

### Critical Metrics to Watch

```
# API Health
- Request rate (requests/sec)
- Error rate (%)
- P50/P95/P99 latency (ms)

# Database
- Connection pool utilization
- Query latency
- Active connections
- Replication lag

# Redis
- Memory usage
- Connection count
- Hit rate

# Infrastructure
- CPU utilization
- Memory utilization
- Network I/O
- Disk I/O
```

### Alert Thresholds

| Alert | Warning | Critical | Action |
|-------|---------|----------|--------|
| Error Rate | >0.5% | >2% | Investigate / Rollback |
| P95 Latency | >300ms | >1000ms | Investigate |
| CPU Usage | >70% | >90% | Scale up |
| Memory Usage | >75% | >90% | Scale up / Investigate leak |
| DB Connections | >80% | >95% | Scale pool |
| Redis Memory | >70% | >85% | Scale / Clear cache |

---

## Deployment History

| Version | Date | Deployer | Status | Notes |
|---------|------|----------|--------|-------|
| 1.1.0 | YYYY-MM-DD | [Name] | Pending | Production readiness release |
| 1.0.0 | 2025-11-23 | [Name] | Success | Initial production release |

---

## Quick Reference Commands

```bash
# Check application health
curl https://api.barqfleet.com/health

# Check readiness
curl https://api.barqfleet.com/api/v1/health/ready

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=barq-fleet-api" --limit=100

# View active revisions
gcloud run revisions list --service=barq-fleet-api

# Scale up (if needed)
gcloud run services update barq-fleet-api --max-instances=20

# Database connection test
PGPASSWORD=xxx psql -h <host> -U <user> -d barq_fleet -c "SELECT 1;"
```

---

**Document Version**: 1.0
**Last Updated**: December 2, 2025
**Owner**: Engineering Team

---

Remember: **When in doubt, rollback first, investigate later.**
