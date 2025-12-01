# Deployment Scripts

This directory contains automation scripts for deploying BARQ Fleet Management to Google Cloud Run.

## Scripts Overview

### 1. deploy-staging.sh
Deploy to staging environment with automatic traffic shifting.

**Usage**:
```bash
./deploy-staging.sh [IMAGE_TAG]
```

**What it does**:
- Deploys to Cloud Run (staging)
- Runs health checks
- Shifts 100% traffic to new revision
- Verifies deployment success

**Example**:
```bash
# Deploy latest image
./deploy-staging.sh

# Deploy specific Git SHA
./deploy-staging.sh abc1234
```

**Time**: ~2-3 minutes

---

### 2. deploy-production.sh
Deploy to production with canary strategy and auto-rollback.

**Usage**:
```bash
./deploy-production.sh [IMAGE_TAG]
```

**What it does**:
- Requires manual confirmation
- Deploys new revision (0% traffic)
- Runs smoke tests
- **Canary Phase 1**: 10% traffic (5 min monitoring)
- **Canary Phase 2**: 50% traffic (5 min monitoring)
- **Canary Phase 3**: 100% traffic
- Auto-rollback if error threshold exceeded

**Example**:
```bash
# Deploy latest image with canary
./deploy-production.sh

# Deploy specific version
./deploy-production.sh def5678
```

**Time**: ~15-20 minutes (including monitoring periods)

---

### 3. rollback-production.sh
Emergency rollback to previous stable revision.

**Usage**:
```bash
./rollback-production.sh [REVISION_NAME]
```

**What it does**:
- Lists available revisions
- Auto-selects previous revision (if not specified)
- Requires confirmation
- Shifts 100% traffic to target revision
- Verifies rollback success

**Example**:
```bash
# Rollback to previous revision (automatic)
./rollback-production.sh

# Rollback to specific revision
./rollback-production.sh barq-api-production-00042-abc
```

**Time**: ~1-2 minutes
**Target**: < 5 minutes

---

### 4. verify-deployment.sh
Verify deployment health and run comprehensive checks.

**Usage**:
```bash
./verify-deployment.sh [staging|production]
```

**What it does**:
- Tests liveness endpoint
- Tests readiness endpoint
- Tests detailed health check
- Checks API documentation
- Measures response time
- Reviews recent errors
- Displays service configuration
- Shows traffic distribution

**Example**:
```bash
# Verify staging
./verify-deployment.sh staging

# Verify production
./verify-deployment.sh production
```

**Time**: ~30 seconds

---

## Prerequisites

### Environment Variables
Set these before running scripts:

```bash
export GCP_PROJECT_ID="barq-fleet"
export GCP_REGION="us-central1"
```

### Required Tools
- `gcloud` CLI (authenticated)
- `curl`
- `jq`
- `bc` (for response time calculation)

### Authentication
Authenticate with Google Cloud:

```bash
gcloud auth login
gcloud config set project barq-fleet
```

## Common Workflows

### Deploy to Staging
```bash
# 1. Deploy
./deploy-staging.sh

# 2. Verify
./verify-deployment.sh staging

# 3. Test manually
STAGING_URL=$(gcloud run services describe barq-api-staging \
  --region us-central1 --format 'value(status.url)')
curl $STAGING_URL/health/detailed | jq
```

### Deploy to Production
```bash
# 1. Test in staging first
./verify-deployment.sh staging

# 2. Deploy to production (with canary)
./deploy-production.sh

# 3. Monitor deployment
# Script automatically monitors, but you can check manually:
gcloud logging tail \
  "resource.type=cloud_run_revision AND resource.labels.service_name=barq-api-production"

# 4. Verify final deployment
./verify-deployment.sh production
```

### Emergency Rollback
```bash
# 1. Immediate rollback
./rollback-production.sh

# 2. Verify rollback
./verify-deployment.sh production

# 3. Monitor for stability
gcloud logging tail \
  "resource.type=cloud_run_revision AND severity>=ERROR"

# 4. Create incident report (see docs/ROLLBACK_PROCEDURES.md)
```

## Script Exit Codes

All scripts follow standard exit code conventions:

- `0`: Success
- `1`: Failure (deployment failed, health checks failed, etc.)
- `130`: User cancelled (Ctrl+C)

## Error Handling

### Deployment Failures

If deployment fails:
1. Check the error message
2. Review Cloud Run logs
3. Verify image exists in Artifact Registry
4. Check service account permissions

```bash
# Check recent builds
gcloud builds list --limit 5

# Check build logs
gcloud builds log <build-id>

# Check Cloud Run logs
gcloud logging read \
  "resource.type=cloud_run_revision" \
  --limit 20
```

### Health Check Failures

If health checks fail:
1. Check application logs
2. Verify database connectivity
3. Check Secret Manager secrets
4. Review recent code changes

```bash
# Check application errors
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 10

# Test database connection manually
gcloud sql connect barq-production-db --user=postgres
```

### Rollback Failures

If rollback fails:
1. Use GCloud Console (emergency)
2. Manually shift traffic to known-good revision

```bash
# Emergency manual rollback
gcloud run services update-traffic barq-api-production \
  --to-revisions <known-good-revision>=100 \
  --region us-central1
```

## Monitoring During Deployments

### Real-time Logs
```bash
# Watch deployment logs
gcloud logging tail \
  "resource.type=cloud_run_revision" \
  --format json

# Watch errors only
gcloud logging tail \
  "resource.type=cloud_run_revision AND severity>=ERROR"
```

### Metrics
```bash
# Check request count
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count"' \
  --format json

# Check error rate
gcloud monitoring time-series list \
  --filter='metric.type="run.googleapis.com/request_count" AND metric.label.response_code_class="5xx"' \
  --format json
```

### Traffic Distribution
```bash
# Show current traffic split
gcloud run services describe barq-api-production \
  --region us-central1 \
  --format 'table(status.traffic.revisionName,status.traffic.percent)'
```

## Canary Deployment Details

### Traffic Split Strategy

**Phase 1: 10% Traffic** (5 minutes)
- 10% of traffic to new revision
- 90% to previous revision
- Monitor error rate
- Auto-rollback if > 5 errors in 5 minutes

**Phase 2: 50% Traffic** (5 minutes)
- 50% to new revision
- 50% to previous revision
- Monitor error rate
- Auto-rollback if > 10 errors in 5 minutes

**Phase 3: 100% Traffic**
- 100% to new revision
- Previous revision kept for quick rollback
- Final health verification

### Error Thresholds

| Phase | Duration | Error Threshold | Action |
|-------|----------|----------------|---------|
| 10% | 5 min | 5 errors | Rollback |
| 50% | 5 min | 10 errors | Rollback |
| 100% | Ongoing | 1% error rate | Alert |

### Monitoring Canary

The scripts automatically monitor, but you can also:

```bash
# Check errors during canary
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --freshness=5m \
  --format json | jq '. | length'

# Monitor specific revision
NEW_REVISION="barq-api-production-00043-def"
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.revision_name=${NEW_REVISION} AND severity>=ERROR" \
  --freshness=5m
```

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Staging Deployment | < 3 min | - |
| Production Deployment (Full) | < 20 min | - |
| Rollback Time | < 5 min | - |
| Health Check Response | < 100ms | - |

## Security Notes

### Secrets
- Never hardcode credentials
- Use Secret Manager for all secrets
- Rotate secrets quarterly

### Access Control
- Scripts require `run.admin` role
- Use service accounts for automation
- Enable audit logging

### Image Scanning
- All images scanned with Trivy
- Critical/High vulnerabilities block deployment
- Regular dependency updates

## Customization

### Environment Variables
You can customize behavior with environment variables:

```bash
# Change project
export GCP_PROJECT_ID="my-project"

# Change region
export GCP_REGION="us-east1"

# Adjust canary timing (in seconds)
export CANARY_WAIT_TIME=600  # 10 minutes instead of 5

# Adjust error threshold
export ERROR_THRESHOLD=10  # More lenient
```

### Script Modification
Scripts are designed to be readable and modifiable:

- Clear section comments
- Reusable functions
- Configurable variables at top
- Extensive logging

Feel free to adapt for your needs!

## Troubleshooting Guide

### "Service not found" Error
```bash
# Verify service exists
gcloud run services list --region us-central1

# If missing, deploy via GitHub Actions first
```

### "Permission denied" Error
```bash
# Check your permissions
gcloud projects get-iam-policy barq-fleet \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:$(gcloud config get-value account)"

# You need: roles/run.admin, roles/cloudsql.client
```

### "Image not found" Error
```bash
# Check image exists
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api

# Build image if missing (via GitHub Actions or Cloud Build)
```

### "Health check timeout" Error
```bash
# Increase startup time in Cloud Run configuration
# Or optimize application startup time
# Check logs for slow initialization
```

## Best Practices

1. **Always deploy to staging first**
2. **Monitor the first 15 minutes after production deployment**
3. **Keep previous revision for quick rollback**
4. **Document deployment in team channel**
5. **Review error logs before considering deployment successful**
6. **Test rollback procedures monthly**
7. **Update runbooks after incidents**

## Support

For issues with these scripts:
1. Check logs: `gcloud logging read ...`
2. Review documentation: `docs/DEPLOYMENT_GUIDE.md`
3. Contact DevOps team: `#devops` on Slack
4. Create incident: `docs/ROLLBACK_PROCEDURES.md`

---

**Last Updated**: 2024-11-23
**Maintainer**: DevOps Team
