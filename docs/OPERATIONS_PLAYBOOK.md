# BARQ Fleet Management - Operations Playbook

**Version:** 1.0.0
**Last Updated:** November 23, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Daily Operations](#daily-operations)
3. [Monitoring](#monitoring)
4. [Incident Response](#incident-response)
5. [Common Issues & Solutions](#common-issues--solutions)
6. [Maintenance Tasks](#maintenance-tasks)
7. [On-Call Procedures](#on-call-procedures)
8. [Escalation](#escalation)
9. [Runbooks](#runbooks)
10. [Tools & Resources](#tools--resources)

---

## Overview

### Purpose

This playbook provides operational procedures for:
- Day-to-day system operations
- Incident response and troubleshooting
- Maintenance activities
- On-call support

### Service Level Objectives (SLOs)

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| Uptime | 99.9% | < 99.5% |
| API Response Time (P95) | < 500ms | > 2000ms |
| Error Rate | < 0.1% | > 1% |
| Database Query Time | < 100ms | > 500ms |

---

## Daily Operations

### Morning Checklist (9:00 AM UTC+3)

```bash
# 1. Check system health
curl https://api.barq.com/health
# Expected: {"status": "healthy"}

# 2. Review overnight alerts
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=100 \
  --format=json \
  --filter='severity>=ERROR AND timestamp>="2025-11-23T00:00:00Z"'

# 3. Check service status
gcloud run services describe barq-api --region=us-central1

# 4. Review database performance
# Access Cloud SQL Insights dashboard
# Check slow queries, connection pool usage

# 5. Check error rate (last 24 hours)
# Access Cloud Monitoring dashboard
# Verify error rate < 0.1%

# 6. Review deployment status
gcloud builds list --limit=5
```

**Action Items:**
- [ ] All health checks passing
- [ ] No critical errors in logs
- [ ] Error rate within acceptable range
- [ ] No slow queries (> 1 second)
- [ ] Recent deployments successful

### End of Day Checklist (6:00 PM UTC+3)

```bash
# 1. Review daily metrics
# - Total requests
# - Error count
# - Average response time
# - Active users

# 2. Check backup status
gcloud sql backups list --instance=barq-production-db

# 3. Review support tickets
# - Open tickets
# - Pending tickets
# - Critical issues

# 4. Plan next day maintenance (if any)

# 5. Hand off to on-call engineer
```

---

## Monitoring

### Key Dashboards

#### 1. Cloud Monitoring Dashboard

**URL:** https://console.cloud.google.com/monitoring/dashboards

**Key Metrics:**
- Request rate (requests/second)
- Error rate (%)
- Response time (P50, P95, P99)
- CPU utilization (%)
- Memory usage (%)
- Database connections
- Cache hit rate (%)

#### 2. Cloud SQL Dashboard

**Key Metrics:**
- Connection count
- Query per second
- Transaction per second
- Disk usage (%)
- Replication lag (if applicable)

#### 3. Application Logs

**Query Patterns:**

```bash
# Error logs (last 1 hour)
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=100 \
  --format=json

# Slow queries
gcloud logging read \
  "resource.type=cloud_run_revision AND jsonPayload.duration_ms>1000" \
  --limit=50

# Authentication failures
gcloud logging read \
  "resource.type=cloud_run_revision AND jsonPayload.message=~'authentication failed'" \
  --limit=50
```

### Alerts

#### Critical Alerts (PagerDuty)

1. **Service Down**
   - Condition: Health check fails for 2 consecutive checks
   - Response: < 5 minutes

2. **High Error Rate**
   - Condition: Error rate > 5% for 5 minutes
   - Response: < 15 minutes

3. **Database Connection Failure**
   - Condition: Cannot connect to database
   - Response: < 5 minutes (critical)

#### Warning Alerts (Slack)

1. **High Response Time**
   - Condition: P95 latency > 2 seconds for 5 minutes
   - Response: < 30 minutes

2. **High Memory Usage**
   - Condition: Memory > 90% for 5 minutes
   - Response: < 1 hour

3. **Disk Space Low**
   - Condition: Database disk > 80%
   - Response: < 4 hours

---

## Incident Response

### Incident Classification

| Severity | Definition | Response Time | Examples |
|----------|-----------|---------------|----------|
| **P0 - Critical** | Complete service outage | < 15 minutes | API down, database unreachable |
| **P1 - High** | Major degradation | < 30 minutes | High error rate, slow response |
| **P2 - Medium** | Partial degradation | < 2 hours | Feature not working for some users |
| **P3 - Low** | Minor issue | < 24 hours | Non-critical bug, UI glitch |

### Incident Response Process

#### 1. Detection & Acknowledgment

```bash
# Acknowledge alert in PagerDuty
# Create incident in incident tracking system
# Join #incidents Slack channel
```

#### 2. Initial Assessment

**Gather Information:**
- What is broken?
- How many users affected?
- When did it start?
- Recent changes (deployments, config)?

**Quick Checks:**
```bash
# Health check
curl https://api.barq.com/health

# Check service status
gcloud run services describe barq-api --region=us-central1

# Recent errors
gcloud logging read "severity>=ERROR" --limit=20

# Recent deployments
gcloud builds list --limit=5
```

#### 3. Communication

**Update Stakeholders:**
```
Subject: [P0] API Service Degradation

Status: Investigating
Impact: API response times elevated, affecting all users
Started: 2025-11-23 14:30 UTC+3
Team: On-call engineer investigating

Next update: 15 minutes
```

**Channels:**
- #incidents Slack channel
- Status page (if customer-facing)
- Email (for P0/P1 incidents)

#### 4. Mitigation

**Quick Wins:**
```bash
# Scale up instances (if resource issue)
gcloud run services update barq-api --max-instances=20

# Restart service (if hung)
gcloud run services update barq-api --update-env-vars RESTART=true

# Rollback (if recent deployment caused issue)
gcloud run services update-traffic barq-api \
  --to-revisions=PREVIOUS_REVISION=100
```

#### 5. Resolution

**Verify Fix:**
```bash
# Check health
curl https://api.barq.com/health

# Monitor error rate
# Should return to < 0.1%

# Test critical flows
# - Login
# - Create courier
# - View dashboard
```

**Update Stakeholders:**
```
Subject: [P0 - RESOLVED] API Service Degradation

Status: Resolved
Resolution: Rolled back to previous version
Duration: 15 minutes
Root Cause: Recent deployment introduced bug

Post-mortem: Will be published within 48 hours
```

#### 6. Post-Incident

**Post-Mortem (required for P0/P1):**
- Timeline of events
- Root cause analysis
- Impact assessment
- Action items (with owners)
- Lessons learned

**Template:** Use `/docs/templates/post-mortem-template.md`

---

## Common Issues & Solutions

### Issue 1: High Response Time

**Symptoms:**
- API response time > 2 seconds
- Users reporting slow page loads

**Diagnosis:**
```bash
# Check CPU/Memory
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/cpu/utilizations"'

# Check database
# - Slow queries
# - Connection pool exhaustion
# - Lock contention

# Check Redis
redis-cli --stat
```

**Solutions:**

1. **Scale up instances**
   ```bash
   gcloud run services update barq-api --max-instances=20
   ```

2. **Optimize slow queries**
   ```sql
   -- Find slow queries
   SELECT query, mean_exec_time
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```

3. **Increase cache TTL**
   ```python
   # Increase Redis cache expiry
   redis.setex(key, 3600, value)  # 1 hour
   ```

4. **Enable connection pooling**
   ```python
   SQLALCHEMY_POOL_SIZE = 20
   SQLALCHEMY_MAX_OVERFLOW = 10
   ```

---

### Issue 2: Database Connection Pool Exhausted

**Symptoms:**
- "Too many connections" errors
- Cannot connect to database

**Diagnosis:**
```bash
# Check active connections
psql -U postgres -d barq_fleet -c "
  SELECT count(*), state
  FROM pg_stat_activity
  GROUP BY state;
"

# Check connection pool settings
cat backend/app/config/database.py | grep POOL
```

**Solutions:**

1. **Terminate idle connections**
   ```sql
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND query_start < NOW() - INTERVAL '10 minutes';
   ```

2. **Increase pool size**
   ```python
   # backend/app/config/database.py
   SQLALCHEMY_POOL_SIZE = 30
   SQLALCHEMY_MAX_OVERFLOW = 20
   ```

3. **Optimize queries**
   - Use connection pooling properly
   - Close connections after use
   - Reduce transaction duration

---

### Issue 3: Memory Leak

**Symptoms:**
- Memory usage increasing over time
- Container restarting (OOM)

**Diagnosis:**
```bash
# Check memory trends
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/container/memory/utilizations"'

# Check container restarts
gcloud run revisions describe REVISION_NAME
```

**Solutions:**

1. **Immediate: Increase memory**
   ```bash
   gcloud run services update barq-api --memory=2Gi
   ```

2. **Short-term: Restart service**
   ```bash
   gcloud run services update barq-api --update-env-vars RESTART=$(date +%s)
   ```

3. **Long-term: Fix memory leak**
   - Profile application
   - Fix leaking code
   - Deploy fix

---

### Issue 4: Rate Limit Exceeded

**Symptoms:**
- Users receiving 429 errors
- "Rate limit exceeded" messages

**Diagnosis:**
```bash
# Check rate limit logs
gcloud logging read \
  "jsonPayload.message=~'rate limit exceeded'" \
  --limit=50
```

**Solutions:**

1. **Whitelist IP (if legitimate)**
   ```python
   # Add to rate limit whitelist
   RATE_LIMIT_WHITELIST = ["1.2.3.4"]
   ```

2. **Increase rate limits (temporarily)**
   ```python
   limiter.limit("2000/hour")  # Increase from 1000
   ```

3. **Block abusive IPs (Cloud Armor)**
   ```bash
   gcloud compute security-policies rules create 1000 \
     --security-policy=barq-security-policy \
     --expression="origin.ip == '1.2.3.4'" \
     --action=deny-403
   ```

---

### Issue 5: Failed Deployment

**Symptoms:**
- Cloud Build fails
- New revision not serving traffic

**Diagnosis:**
```bash
# Check build logs
gcloud builds log [BUILD_ID]

# Check revision status
gcloud run revisions describe [REVISION_NAME]

# Check container logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

**Solutions:**

1. **Build failure**
   - Review build logs
   - Fix syntax errors
   - Ensure all dependencies installed

2. **Container crashes**
   - Check startup logs
   - Verify environment variables
   - Test locally with Docker

3. **Health check failures**
   - Verify health endpoint working
   - Check database connectivity
   - Increase startup timeout

---

## Maintenance Tasks

### Daily

- [ ] Review monitoring dashboards
- [ ] Check error logs
- [ ] Review support tickets
- [ ] Verify backups completed

### Weekly

- [ ] Review slow queries and optimize
- [ ] Check disk space usage
- [ ] Update dependencies (security patches)
- [ ] Review and close old tickets
- [ ] On-call handoff meeting

### Monthly

- [ ] Review access logs and remove unused accounts
- [ ] Analyze usage patterns and optimize
- [ ] Review and update documentation
- [ ] Test disaster recovery procedures
- [ ] Rotate secrets (if not auto-rotated)

### Quarterly

- [ ] Security audit
- [ ] Performance review
- [ ] Cost optimization review
- [ ] Disaster recovery drill
- [ ] Update runbooks

---

## On-Call Procedures

### On-Call Rotation

**Schedule:** 1-week rotations
**Coverage:** 24/7
**Tool:** PagerDuty

### On-Call Responsibilities

1. **Respond to alerts**
   - P0: < 15 minutes
   - P1: < 30 minutes

2. **Monitor system health**
   - Check dashboards daily
   - Review error logs

3. **Handle incidents**
   - Follow incident response process
   - Escalate if needed

4. **Update documentation**
   - Document new issues
   - Update runbooks

### Handoff Process

**Before your shift:**
- Review recent incidents
- Check open tickets
- Read handoff notes

**During your shift:**
- Document all incidents
- Update runbook as needed
- Note any ongoing issues

**After your shift:**
- Write handoff notes
- Brief next on-call
- Close out incidents

---

## Escalation

### Escalation Path

```
Level 1: On-Call Engineer
   ↓ (If unresolved after 30 minutes or beyond expertise)
Level 2: Tech Lead
   ↓ (If critical or requires architectural decision)
Level 3: CTO
```

### When to Escalate

- **Immediately:** P0 incidents
- **After 30 minutes:** P1 incidents unresolved
- **Architectural:** Requires system design decision
- **Security:** Potential security breach
- **Data Loss:** Risk of data loss

### Contact Information

| Role | Contact | Availability |
|------|---------|--------------|
| On-Call Engineer | PagerDuty | 24/7 |
| Tech Lead | tech-lead@barq.com | Business hours + on-call |
| CTO | cto@barq.com | Escalations only |
| DevOps Team | devops@barq.com | Business hours |
| Security Team | security@barq.com | 24/7 for security issues |

---

## Runbooks

### Runbook: Database Backup & Restore

**Create Manual Backup:**
```bash
# Create backup
gcloud sql backups create --instance=barq-production-db

# Verify backup
gcloud sql backups list --instance=barq-production-db
```

**Restore from Backup:**
```bash
# List available backups
gcloud sql backups list --instance=barq-production-db

# Restore (creates new instance)
gcloud sql backups restore [BACKUP_ID] \
  --backup-instance=barq-production-db \
  --backup-id=[BACKUP_ID]
```

### Runbook: Scale Services

**Manual Scaling:**
```bash
# Scale up
gcloud run services update barq-api \
  --min-instances=2 \
  --max-instances=20

# Scale down
gcloud run services update barq-api \
  --min-instances=1 \
  --max-instances=10
```

### Runbook: Clear Redis Cache

```bash
# Connect to Redis
gcloud redis instances describe barq-redis --region=us-central1

# Flush all keys (CAUTION)
redis-cli -h [REDIS_IP] -p 6379 FLUSHALL

# Flush specific pattern
redis-cli -h [REDIS_IP] -p 6379 --scan --pattern "couriers:*" | xargs redis-cli DEL
```

---

## Tools & Resources

### Essential Tools

1. **Cloud Console:** https://console.cloud.google.com
2. **PagerDuty:** https://barq.pagerduty.com
3. **Status Page:** https://status.barq.com
4. **Monitoring Dashboard:** Cloud Monitoring
5. **Log Viewer:** Cloud Logging

### Useful Commands

```bash
# Quick health check
curl https://api.barq.com/health

# Stream logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50 --format=json

# Check service status
gcloud run services describe barq-api --region=us-central1

# List recent builds
gcloud builds list --limit=10

# Connect to database
gcloud sql connect barq-production-db --user=postgres

# Redis CLI
redis-cli -h [REDIS_IP] -p 6379
```

### Documentation Links

- [Deployment Runbook](DEPLOYMENT_RUNBOOK.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Security Documentation](SECURITY.md)

---

**Document Owner:** DevOps Team
**Review Cycle:** Monthly
**Last Updated:** November 23, 2025
