# Rollback Procedures

## Table of Contents
- [Overview](#overview)
- [Automated Rollback](#automated-rollback)
- [Manual Rollback](#manual-rollback)
- [Rollback Checklist](#rollback-checklist)
- [Post-Rollback Actions](#post-rollback-actions)
- [Incident Response](#incident-response)

## Overview

This document describes the rollback procedures for the BARQ Fleet Management system. Rollbacks should be executed when:

- Error rate exceeds 1% during canary deployment
- Critical bugs are discovered in production
- Performance degradation is detected
- Data integrity issues are identified
- Security vulnerabilities are found

**Target Rollback Time**: < 5 minutes from decision to completion

## Automated Rollback

### During Canary Deployment

The CD pipeline automatically monitors error rates during canary deployments:

1. **10% Canary Phase** (5 minutes)
   - Monitors error rate
   - Automatically rolls back if errors > 5 in 5 minutes
   - Restores 100% traffic to previous revision

2. **50% Canary Phase** (5 minutes)
   - Monitors error rate
   - Automatically rolls back if errors > 10 in 5 minutes
   - Restores 100% traffic to previous revision

### Monitoring Triggers

Automated rollback is triggered by:

```yaml
Error Conditions:
  - HTTP 5xx errors > threshold
  - Application crashes
  - Health check failures
  - Database connection failures

Thresholds:
  - 10% canary: 5 errors in 5 minutes
  - 50% canary: 10 errors in 5 minutes
  - Production: 1% error rate sustained for 2 minutes
```

## Manual Rollback

### Emergency Rollback Script

Use the emergency rollback script for immediate rollback:

```bash
cd scripts/deployment
./rollback-production.sh
```

This will:
1. Show available revisions
2. Automatically select the previous stable revision
3. Require confirmation
4. Execute rollback (100% traffic shift)
5. Verify health checks
6. Report rollback time

**Expected Time**: 1-2 minutes

### Rollback to Specific Revision

```bash
# List available revisions
gcloud run revisions list \
  --service barq-api-production \
  --region us-central1

# Rollback to specific revision
./rollback-production.sh <revision-name>
```

### Manual GCloud Commands

If scripts are unavailable:

```bash
# 1. Set project
gcloud config set project barq-fleet

# 2. Get current revisions
gcloud run revisions list \
  --service barq-api-production \
  --region us-central1 \
  --limit 10

# 3. Rollback to previous revision
gcloud run services update-traffic barq-api-production \
  --to-revisions <previous-revision-name>=100 \
  --region us-central1

# 4. Verify rollback
curl -f https://api.barq-fleet.com/health
```

## Rollback Checklist

### Pre-Rollback

- [ ] **Identify Issue**: Document the problem requiring rollback
- [ ] **Notify Team**: Alert on-call team and stakeholders
- [ ] **Confirm Decision**: Get approval from tech lead (if time permits)
- [ ] **Note Current State**: Record current revision and traffic distribution

### During Rollback

- [ ] **Execute Rollback**: Run rollback script or manual commands
- [ ] **Monitor Progress**: Watch traffic shift in real-time
- [ ] **Health Checks**: Verify all health endpoints return 200 OK
- [ ] **Error Monitoring**: Check Cloud Logging for new errors

### Post-Rollback

- [ ] **Verify Services**: Run verification script
- [ ] **Check Metrics**: Review error rates, latency, and throughput
- [ ] **Update Status**: Update incident status page
- [ ] **Document Incident**: Create incident report
- [ ] **Schedule Postmortem**: Plan blameless postmortem meeting

## Post-Rollback Actions

### 1. Immediate Verification (< 5 minutes)

```bash
# Run verification script
./scripts/deployment/verify-deployment.sh production

# Check key metrics
gcloud monitoring metrics-descriptors list \
  --filter="metric.type:run.googleapis.com"
```

### 2. Monitor for 30 Minutes

Watch for:
- Error rate stabilization
- Response time normalization
- User-reported issues
- Database connection pool status

### 3. Create Incident Report

Document:
- **Time of issue detection**
- **Symptoms observed**
- **Decision timeline**
- **Rollback execution time**
- **Impact assessment** (users affected, duration)
- **Root cause** (preliminary)

Template:

```markdown
# Incident Report: [Date] - [Brief Description]

## Timeline
- [Time]: Issue detected
- [Time]: Rollback decision made
- [Time]: Rollback executed
- [Time]: Service restored

## Impact
- Duration: X minutes
- Users affected: ~Y users
- Requests failed: Z requests

## Root Cause
[Preliminary analysis]

## Actions Taken
1. [Action 1]
2. [Action 2]

## Follow-up Items
- [ ] Fix root cause
- [ ] Add monitoring for early detection
- [ ] Update tests to prevent recurrence
```

### 4. Schedule Postmortem

Conduct blameless postmortem within 48 hours:

**Agenda**:
1. Timeline review
2. Root cause analysis
3. What went well
4. What could be improved
5. Action items

## Incident Response

### Severity Levels

**P0 - Critical** (Rollback immediately)
- Complete service outage
- Data loss or corruption
- Security breach
- Rollback Time Target: < 5 minutes

**P1 - High** (Rollback if no quick fix)
- Partial service degradation
- Critical feature broken
- Error rate > 5%
- Rollback Time Target: < 10 minutes

**P2 - Medium** (Monitor, consider rollback)
- Non-critical feature broken
- Performance degradation
- Error rate 1-5%
- Decision Time: 15 minutes

**P3 - Low** (No rollback needed)
- Minor issues
- Error rate < 1%
- Can be fixed forward

### Communication Protocol

**Internal**:
1. Alert on-call engineer (PagerDuty/Slack)
2. Create incident channel (#incident-YYYY-MM-DD)
3. Update incident commander
4. Post status updates every 15 minutes

**External** (if customer-facing):
1. Update status page
2. Send email notification (if > 100 users affected)
3. Post resolution update

### On-Call Escalation

```
Level 1: On-call DevOps Engineer (0-5 min)
    ↓ (if not resolved)
Level 2: Tech Lead (5-15 min)
    ↓ (if critical)
Level 3: CTO/VP Engineering (15-30 min)
```

## Rollback Time Targets

| Environment | Target Time | Maximum Time |
|------------|-------------|--------------|
| Staging | < 2 minutes | 5 minutes |
| Production | < 5 minutes | 10 minutes |

### Time Breakdown

**Automated Rollback** (during canary):
- Detection: 0-5 minutes (monitoring interval)
- Execution: 30 seconds (traffic shift)
- Verification: 30 seconds (health checks)
- **Total**: 1-6 minutes

**Manual Rollback**:
- Detection: 0-2 minutes
- Decision: 0-3 minutes
- Execution: 1 minute (script)
- Verification: 1 minute
- **Total**: 2-7 minutes

## Testing Rollback Procedures

Test rollback procedures monthly:

```bash
# 1. Deploy to staging
./scripts/deployment/deploy-staging.sh

# 2. Wait for deployment
sleep 60

# 3. Practice rollback
./scripts/deployment/rollback-production.sh

# 4. Verify
./scripts/deployment/verify-deployment.sh staging
```

## Cloud Run Revision Management

### Keep Revisions

Maintain at least 3 previous revisions:
- Current production revision
- Previous stable revision (N-1)
- Last known good revision (N-2)

### Auto-Cleanup

Cloud Run automatically keeps:
- Last 10 revisions by default
- All revisions with active traffic
- Manually tagged revisions

### Manual Cleanup

```bash
# List old revisions
gcloud run revisions list \
  --service barq-api-production \
  --region us-central1 \
  --filter="status.conditions[0].status=False" \
  --limit 50

# Delete old revisions (keep last 10)
gcloud run revisions delete <revision-name> \
  --region us-central1 \
  --quiet
```

## Monitoring During Rollback

### Key Metrics to Watch

```bash
# Error rate
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 50 \
  --format "table(timestamp,severity,textPayload)" \
  --freshness=10m

# Request latency
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_latencies"'

# Active instances
gcloud run services describe barq-api-production \
  --region us-central1 \
  --format 'value(status.traffic)'
```

### Health Check Endpoints

Monitor continuously:
- `/health/live` - Liveness (every 10s)
- `/health/ready` - Readiness (every 10s)
- `/health/detailed` - Full status (every 60s)

## Database Rollback Considerations

**IMPORTANT**: Code rollback does NOT rollback database changes.

### Before Deploying Database Changes

1. **Backward Compatible Migrations**
   - New columns should be nullable or have defaults
   - Don't drop columns in same release as code changes
   - Use feature flags for schema changes

2. **Rollback Plan**
   ```sql
   -- Document reverse migrations
   -- Test reverse migrations in staging
   -- Keep migration history
   ```

3. **Data Validation**
   - Backup before migration
   - Verify data integrity after migration
   - Test rollback on backup copy

### If Database Rollback Needed

This requires manual intervention:

1. Stop application traffic
2. Restore from backup (if available)
3. Apply reverse migrations
4. Verify data integrity
5. Resume traffic

**Time Estimate**: 15-60 minutes (depending on database size)

## Contact Information

### Emergency Contacts

- **On-Call DevOps**: [PagerDuty] or [Phone]
- **Tech Lead**: [Contact]
- **CTO**: [Contact]

### Tools

- **Cloud Console**: https://console.cloud.google.com
- **Cloud Run**: https://console.cloud.google.com/run
- **Monitoring**: https://console.cloud.google.com/monitoring
- **Logs**: https://console.cloud.google.com/logs

---

**Last Updated**: [Current Date]
**Document Owner**: DevOps Team
**Review Frequency**: Monthly
