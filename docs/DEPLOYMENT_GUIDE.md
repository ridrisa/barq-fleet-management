# BARQ Fleet Management - Deployment Guide

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring & Alerts](#monitoring--alerts)
- [Troubleshooting](#troubleshooting)

## Overview

This guide covers the complete deployment process for BARQ Fleet Management, including:

- Automated CI/CD pipeline
- Staging and production environments
- Canary deployments with auto-rollback
- Zero-downtime deployments
- Comprehensive monitoring and alerting

**Deployment Strategy**: Continuous Deployment with canary releases
**Target Metrics**:
- Deployment frequency: 10+ times per day
- Lead time: < 5 minutes
- MTTR (Mean Time To Recovery): < 5 minutes
- Change failure rate: < 5%

## Prerequisites

### Required Accounts & Access
- [x] Google Cloud Platform account with billing enabled
- [x] GitHub account with repository access
- [x] GCP Project created (`barq-fleet`)
- [x] GitHub Actions enabled
- [x] Terraform installed locally (v1.0+)

### Required GCP APIs
Enable these APIs in your GCP project:

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  cloudtrace.googleapis.com
```

### GCP Service Account
Create a service account for deployments:

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding barq-fleet \
  --member="serviceAccount:github-actions@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding barq-fleet \
  --member="serviceAccount:github-actions@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding barq-fleet \
  --member="serviceAccount:github-actions@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding barq-fleet \
  --member="serviceAccount:github-actions@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"

gcloud projects add-iam-policy-binding barq-fleet \
  --member="serviceAccount:github-actions@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@barq-fleet.iam.gserviceaccount.com
```

## Initial Setup

### 1. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```
GCP_PROJECT_ID: barq-fleet
GCP_SA_KEY: <contents of github-actions-key.json>
```

### 2. Create Artifact Registry Repository

```bash
gcloud artifacts repositories create barq-artifacts \
  --repository-format=docker \
  --location=us-central1 \
  --description="BARQ Fleet Management Docker images"
```

### 3. Set Up Secret Manager

Create secrets for database and application:

```bash
# Staging database URL
echo -n "postgresql://user:password@/cloudsql/barq-fleet:us-central1:barq-staging-db/barq_staging" | \
  gcloud secrets create staging-database-url --data-file=-

# Staging secret key
openssl rand -base64 32 | \
  gcloud secrets create staging-secret-key --data-file=-

# Production database URL
echo -n "postgresql://user:password@/cloudsql/barq-fleet:us-central1:barq-production-db/barq_production" | \
  gcloud secrets create production-database-url --data-file=-

# Production secret key
openssl rand -base64 32 | \
  gcloud secrets create production-secret-key --data-file=-
```

### 4. Initialize Terraform

```bash
cd terraform/environments/staging

# Initialize Terraform
terraform init

# Create a plan
terraform plan

# Apply infrastructure
terraform apply
```

Repeat for production:

```bash
cd ../production
terraform init
terraform plan
terraform apply
```

## Staging Deployment

### Automatic Deployment

Staging is deployed automatically on every push to the `main` branch:

1. **Push to main branch**:
   ```bash
   git push origin main
   ```

2. **GitHub Actions automatically**:
   - Runs CI checks (linting, tests)
   - Builds Docker image
   - Pushes to Artifact Registry
   - Deploys to Cloud Run (staging)
   - Runs smoke tests
   - Shifts 100% traffic to new revision

3. **Monitor deployment**:
   - GitHub Actions: https://github.com/barq-fleet/barq-fleet-clean/actions
   - Cloud Run Console: https://console.cloud.google.com/run

### Manual Deployment

Deploy manually using the script:

```bash
cd scripts/deployment

# Deploy latest image
./deploy-staging.sh

# Deploy specific image tag
./deploy-staging.sh <git-sha>
```

### Verify Staging Deployment

```bash
# Run verification script
./scripts/deployment/verify-deployment.sh staging

# Check health endpoints manually
STAGING_URL=$(gcloud run services describe barq-api-staging \
  --region us-central1 \
  --format 'value(status.url)')

curl $STAGING_URL/health/live
curl $STAGING_URL/health/ready
curl $STAGING_URL/health/detailed | jq
```

## Production Deployment

### Manual Approval Required

Production deployments require manual approval through GitHub Actions:

1. **Trigger deployment workflow**:
   - Go to GitHub Actions
   - Select "Continuous Deployment" workflow
   - Click "Run workflow"
   - Select `environment: production`

2. **Approval process**:
   - GitHub notifies designated approvers
   - Reviewer checks staging deployment
   - Reviewer approves production deployment

3. **Canary deployment (automatic)**:
   - **Phase 1**: 10% traffic (5 minutes)
     - Monitor error rate
     - Auto-rollback if errors > 5
   - **Phase 2**: 50% traffic (5 minutes)
     - Monitor error rate
     - Auto-rollback if errors > 10
   - **Phase 3**: 100% traffic
     - Final health checks
     - Complete deployment

### Manual Production Deployment

For emergency deployments:

```bash
cd scripts/deployment

# Deploy with canary strategy
./deploy-production.sh

# Deploy specific version
./deploy-production.sh <git-sha>
```

The script will:
1. Confirm deployment decision
2. Deploy new revision (0% traffic)
3. Run smoke tests
4. Gradually shift traffic (10% → 50% → 100%)
5. Monitor for errors
6. Auto-rollback if issues detected

### Rollback Production

If issues are detected:

```bash
# Emergency rollback (automatic revision selection)
./scripts/deployment/rollback-production.sh

# Rollback to specific revision
./scripts/deployment/rollback-production.sh <revision-name>
```

**Target rollback time**: < 5 minutes

See [ROLLBACK_PROCEDURES.md](./ROLLBACK_PROCEDURES.md) for detailed procedures.

## Monitoring & Alerts

### Dashboards

**Main Dashboard**:
- Service health status
- Request rate and success rate
- Response latency (p50, p95, p99)
- Error rate
- Container instances
- Database metrics

**Deployment Dashboard**:
- Active revisions
- Traffic distribution
- Error rate by revision
- Deployment history

Access dashboards:
```bash
# Get dashboard URLs from Terraform
cd terraform/environments/production
terraform output
```

Or navigate to:
- https://console.cloud.google.com/monitoring/dashboards

### Alert Policies

Configured alerts:
1. **High Error Rate** (> 1%) - PagerDuty + Slack
2. **High Latency** (p95 > 1s) - Email
3. **Service Unavailable** - PagerDuty + Slack
4. **Database Connection Pool High** (> 80%) - Email
5. **Database CPU High** (> 85%) - Email
6. **High Instance Count** (> 80% of max) - Email
7. **Container Startup Latency** (> 10s) - Email
8. **Application Error Spike** - Email

### Notification Channels

Configure in Terraform:
```hcl
# terraform/environments/production/terraform.tfvars
alert_email       = "devops@barq-fleet.com"
slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Health Check Endpoints

Monitor continuously:

```bash
# Liveness (is the app running?)
curl https://api.barq-fleet.com/health/live

# Readiness (is the app ready to serve traffic?)
curl https://api.barq-fleet.com/health/ready

# Detailed health (full system status)
curl https://api.barq-fleet.com/health/detailed | jq
```

## Deployment Best Practices

### 1. Test in Staging First
- Always deploy to staging before production
- Run integration tests
- Verify all critical user flows

### 2. Deploy During Low-Traffic Hours
- Preferred window: 10 PM - 4 AM (user local time)
- Exception: Critical security fixes (deploy immediately)

### 3. Monitor Deployments
- Watch the first 15 minutes after deployment
- Check error rates and latency
- Review user-reported issues

### 4. Feature Flags
- Use feature flags for large changes
- Roll out gradually
- Easy rollback without code deployment

### 5. Database Migrations
- Always backward compatible
- Test rollback scenario
- Don't drop columns in same release

### 6. Communication
- Announce deployments in team channel
- Update status page for major releases
- Document changes in release notes

## Troubleshooting

### Deployment Failures

**Issue**: Docker build fails
```bash
# Solution: Check Cloud Build logs
gcloud builds list --limit 5
gcloud builds log <build-id>
```

**Issue**: Tests fail in CI
```bash
# Solution: Run tests locally
cd backend
pytest app/tests/ -v

# Fix issues and push again
```

**Issue**: Health checks fail after deployment
```bash
# Solution: Check application logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=barq-api-production" \
  --limit 50 \
  --format json

# Rollback if critical
./scripts/deployment/rollback-production.sh
```

### High Error Rates

**Issue**: Error rate spikes after deployment
```bash
# 1. Check error logs
gcloud logging read \
  "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 20

# 2. Rollback immediately
./scripts/deployment/rollback-production.sh

# 3. Investigate root cause
# 4. Fix and redeploy
```

### Performance Issues

**Issue**: High latency after deployment
```bash
# 1. Check Cloud Monitoring latency metrics
# 2. Review recent code changes
# 3. Check database query performance
# 4. Consider scaling up resources

# Temporary fix: Scale up
gcloud run services update barq-api-production \
  --cpu 8 \
  --memory 8Gi \
  --region us-central1
```

### Database Connection Issues

**Issue**: Connection pool exhausted
```bash
# 1. Check current connections
gcloud sql operations list --instance barq-production-db

# 2. Review connection leaks in code
# 3. Adjust connection pool settings

# Temporary fix: Scale up database
gcloud sql instances patch barq-production-db \
  --tier db-n1-standard-2
```

## CI/CD Pipeline Details

### Workflow Triggers

**CI Pipeline** (`.github/workflows/ci.yml`):
- Trigger: Pull requests, pushes to main/develop
- Actions: Lint, test, build, security scan

**CD Pipeline** (`.github/workflows/cd.yml`):
- Trigger: Push to main, manual workflow dispatch
- Actions: Build, push, deploy, canary rollout

### Pipeline Stages

1. **CI Checks** (parallel):
   - Backend lint & test
   - Frontend lint & test
   - Security scanning
   - Docker build test

2. **Build & Push**:
   - Multi-stage Docker build
   - Push to Artifact Registry
   - Security scan (Trivy)

3. **Deploy Staging** (automatic):
   - Deploy with 0% traffic
   - Run smoke tests
   - Shift to 100% traffic

4. **Deploy Production** (manual approval):
   - Manual approval gate
   - Deploy with 0% traffic
   - Run smoke tests
   - Canary: 10% → 50% → 100%
   - Auto-rollback on errors

5. **Notify**:
   - Slack notification
   - GitHub deployment status
   - Update status page

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Deployment Frequency | 10+/day | - |
| Lead Time | < 5 min | - |
| MTTR | < 5 min | - |
| Change Failure Rate | < 5% | - |
| Deployment Success | > 99% | - |
| Availability | 99.9% | - |

## Security Considerations

### Secrets Management
- All secrets in Secret Manager
- Never commit secrets to Git
- Rotate secrets quarterly

### Image Security
- Scan all images with Trivy
- Use distroless base images
- Update dependencies regularly

### Access Control
- Least privilege principle
- Service accounts for automation
- MFA for production access

### Audit Logging
- All deployments logged
- Access logs retained 90 days
- Regular security audits

## Cost Optimization

### Cloud Run
- Use min instances only for production
- Adjust CPU/memory based on actual usage
- Review billable instance time

### Cloud SQL
- Use appropriate tier (don't over-provision)
- Enable automatic storage increase
- Delete old backups (keep 7 days)

### Artifact Registry
- Clean up old images (keep last 10)
- Use lifecycle policies
- Compress images

## Support & Escalation

### On-Call Rotation
- Primary: DevOps Engineer
- Secondary: Backend Lead
- Escalation: CTO

### Contact Information
- Slack: #devops-alerts
- PagerDuty: https://barq-fleet.pagerduty.com
- Email: devops@barq-fleet.com

### Runbooks
- [Rollback Procedures](./ROLLBACK_PROCEDURES.md)
- [Incident Response](./INCIDENT_RESPONSE.md)
- [Database Operations](./DATABASE_OPS.md)

---

**Last Updated**: 2024-11-23
**Document Owner**: DevOps Team
**Review Frequency**: Monthly
