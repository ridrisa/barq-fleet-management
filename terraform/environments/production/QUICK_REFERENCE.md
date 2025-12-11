# Production Quick Reference Guide
**BARQ Fleet Management - Production Operations**

> Quick commands and troubleshooting for production environment

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Navigate to production environment
cd terraform/environments/production

# 2. Copy configuration template
cp terraform.tfvars.example terraform.tfvars

# 3. Edit configuration
nano terraform.tfvars

# 4. Validate configuration
./validate.sh

# 5. Initialize Terraform
terraform init

# 6. Deploy infrastructure
terraform plan
terraform apply
```

## 📋 Common Commands

### Terraform Operations

```bash
# Initialize (first time or after changing backend)
terraform init

# Validate syntax
terraform validate

# Format code
terraform fmt

# Plan changes
terraform plan

# Apply changes
terraform apply

# Apply specific resource
terraform apply -target=google_cloud_run_service.barq_api_production

# View outputs
terraform output
terraform output api_service_url
terraform output -json

# Refresh state
terraform refresh

# Show current state
terraform show

# List resources
terraform state list

# Destroy (CAREFUL!)
terraform destroy
```

### Service Management

```bash
# API Service
gcloud run services describe barq-api-production --region=me-central1
gcloud run services list --region=me-central1
gcloud run services logs read barq-api-production --region=me-central1 --limit=50

# Web Service
gcloud run services describe barq-web-production --region=me-central1
gcloud run services logs read barq-web-production --region=me-central1 --limit=50

# Update service (manual)
gcloud run services update barq-api-production \
  --region=me-central1 \
  --image=me-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api:v1.0.0

# Scale service
gcloud run services update barq-api-production \
  --region=me-central1 \
  --min-instances=5 \
  --max-instances=100

# Update environment variable
gcloud run services update barq-api-production \
  --region=me-central1 \
  --set-env-vars="LOG_LEVEL=DEBUG"
```

### Database Operations

```bash
# Connect to database
gcloud sql connect barq-production-db --user=barq_app_user --database=barq_production

# List instances
gcloud sql instances list

# Describe instance
gcloud sql instances describe barq-production-db

# List backups
gcloud sql backups list --instance=barq-production-db

# Create backup
gcloud sql backups create --instance=barq-production-db

# Restore backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=barq-production-db \
  --backup-id=BACKUP_ID

# Scale database
gcloud sql instances patch barq-production-db \
  --tier=db-custom-8-30720

# View operations
gcloud sql operations list --instance=barq-production-db

# Export database
gcloud sql export sql barq-production-db \
  gs://barq-backups/dump-$(date +%Y%m%d-%H%M%S).sql \
  --database=barq_production

# Import database
gcloud sql import sql barq-production-db \
  gs://barq-backups/dump.sql \
  --database=barq_production
```

### Secret Management

```bash
# List secrets
gcloud secrets list

# View secret metadata
gcloud secrets describe barq-database-url-prod

# Add new secret version
echo -n "new-secret-value" | \
  gcloud secrets versions add barq-database-url-prod --data-file=-

# Access secret value
gcloud secrets versions access latest --secret=barq-database-url-prod

# Delete old version
gcloud secrets versions destroy VERSION_NUMBER --secret=barq-database-url-prod

# List versions
gcloud secrets versions list barq-database-url-prod
```

### Monitoring & Logs

```bash
# View recent logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=100 \
  --format=json

# Filter logs
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=50

# Stream logs (real-time)
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=10 \
  --format="value(textPayload)" \
  --freshness=1m

# List alert policies
gcloud alpha monitoring policies list

# Describe alert policy
gcloud alpha monitoring policies describe POLICY_ID

# View uptime checks
gcloud monitoring uptime list
```

## 🔧 Troubleshooting

### Issue: Service Returns 503

```bash
# Check service status
gcloud run services describe barq-api-production --region=me-central1 \
  --format="value(status.conditions[0].message)"

# Check logs for errors
gcloud run services logs read barq-api-production --region=me-central1 --limit=100 | grep ERROR

# Check instance count
gcloud run services describe barq-api-production --region=me-central1 \
  --format="value(spec.template.metadata.annotations.autoscaling\.knative\.dev/minScale)"

# Increase min instances
gcloud run services update barq-api-production \
  --region=me-central1 \
  --min-instances=5
```

### Issue: Database Connection Timeout

```bash
# Check Cloud SQL status
gcloud sql instances describe barq-production-db \
  --format="value(state)"

# Check VPC connector
gcloud compute networks vpc-access connectors describe barq-production-connector \
  --region=me-central1

# Test database connection
gcloud sql connect barq-production-db --user=barq_app_user

# Check active connections
gcloud sql operations list --instance=barq-production-db --filter="status=RUNNING"
```

### Issue: High Latency

```bash
# Check Cloud Run metrics
gcloud monitoring timeseries list \
  --filter='metric.type="run.googleapis.com/request_latencies"' \
  --interval-start=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --interval-end=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Check database performance
gcloud sql instances describe barq-production-db \
  --format="value(settings.insightsConfig)"

# View slow queries (in database)
gcloud sql connect barq-production-db --user=barq_app_user
# Then run:
# SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
```

### Issue: High Costs

```bash
# View current billing
gcloud billing accounts list

# Check budget status
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID

# Analyze Cloud Run costs
gcloud run services describe barq-api-production --region=me-central1 \
  --format="value(spec.template.spec.containers[0].resources.limits)"

# Check database costs (scale down if needed)
gcloud sql instances describe barq-production-db \
  --format="value(settings.tier,settings.diskSize)"

# Review VPC connector throughput
gcloud compute networks vpc-access connectors describe barq-production-connector \
  --region=me-central1 \
  --format="value(minThroughput,maxThroughput)"
```

### Issue: Secret Access Denied

```bash
# Check service account permissions
gcloud secrets get-iam-policy barq-database-url-prod

# Grant access
gcloud secrets add-iam-policy-binding barq-database-url-prod \
  --member="serviceAccount:barq-api-production@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Verify
gcloud secrets get-iam-policy barq-database-url-prod
```

## 🔄 Deployment & Rollback

### Deploy New Version

```bash
# Tag release
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1

# Build and deploy (via Cloud Build)
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=production,_IMAGE_TAG=v1.0.1

# Manual deployment
gcloud run deploy barq-api-production \
  --image=me-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api:v1.0.1 \
  --region=me-central1
```

### Rollback to Previous Version

```bash
# List revisions
gcloud run revisions list --service=barq-api-production --region=me-central1

# Rollback to specific revision
gcloud run services update-traffic barq-api-production \
  --to-revisions=barq-api-production-00042-abc=100 \
  --region=me-central1

# Or deploy previous image
gcloud run deploy barq-api-production \
  --image=me-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api:v1.0.0 \
  --region=me-central1
```

### Canary Deployment (Gradual Rollout)

```bash
# Deploy new version with 0% traffic
gcloud run deploy barq-api-production \
  --image=me-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api:v1.0.1 \
  --region=me-central1 \
  --no-traffic

# Route 10% traffic to new version
gcloud run services update-traffic barq-api-production \
  --to-revisions=barq-api-production-00043-new=10,barq-api-production-00042-old=90 \
  --region=me-central1

# Monitor metrics, then increase to 50%
gcloud run services update-traffic barq-api-production \
  --to-revisions=barq-api-production-00043-new=50,barq-api-production-00042-old=50 \
  --region=me-central1

# Finally, 100% to new version
gcloud run services update-traffic barq-api-production \
  --to-revisions=barq-api-production-00043-new=100 \
  --region=me-central1
```

## 📊 Health Checks

### API Health
```bash
# Liveness check
curl https://barq-api-production-HASH.run.app/health/live

# Readiness check
curl https://barq-api-production-HASH.run.app/health/ready

# Database connectivity
curl https://barq-api-production-HASH.run.app/health/db
```

### Database Health
```bash
# Check database status
gcloud sql instances describe barq-production-db \
  --format="value(state,databaseVersion)"

# Check replication (if HA)
gcloud sql instances describe barq-production-db \
  --format="value(replicaConfiguration)"
```

### Service Health
```bash
# Check all services
gcloud run services list --region=me-central1 \
  --format="table(SERVICE,LAST_DEPLOYED,URL)"

# Check VPC connector
gcloud compute networks vpc-access connectors describe barq-production-connector \
  --region=me-central1 \
  --format="value(state)"
```

## 🔐 Security Operations

### Rotate Secrets

```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -hex 32)

# 2. Add new version
echo -n "$NEW_SECRET" | \
  gcloud secrets versions add barq-secret-key-prod --data-file=-

# 3. Cloud Run will pick up new version on next deployment
gcloud run services update barq-api-production --region=me-central1

# 4. Disable old version after verification
gcloud secrets versions disable VERSION_NUMBER --secret=barq-secret-key-prod
```

### Review IAM Permissions

```bash
# List service accounts
gcloud iam service-accounts list

# View service account permissions
gcloud projects get-iam-policy barq-fleet \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:barq-api-production@"

# View secret access
gcloud secrets get-iam-policy barq-database-url-prod
```

### Check Cloud Armor

```bash
# View security policy
gcloud compute security-policies describe barq-api-production-policy

# View rules
gcloud compute security-policies rules list barq-api-production-policy

# Update rate limit
gcloud compute security-policies rules update 1000 \
  --security-policy=barq-api-production-policy \
  --rate-limit-threshold-count=2000
```

## 💾 Backup & Restore

### Manual Backup

```bash
# Database backup
gcloud sql backups create --instance=barq-production-db

# Wait for completion
gcloud sql operations wait OPERATION_ID

# Verify backup
gcloud sql backups list --instance=barq-production-db --limit=1
```

### Restore from Backup

```bash
# List available backups
gcloud sql backups list --instance=barq-production-db

# Restore (CAREFUL - this is destructive!)
gcloud sql backups restore BACKUP_ID \
  --backup-instance=barq-production-db

# Or restore to point-in-time
gcloud sql instances clone barq-production-db barq-production-db-clone \
  --point-in-time='2025-12-11T10:00:00.000Z'
```

### Export for Disaster Recovery

```bash
# Export database to Cloud Storage
gcloud sql export sql barq-production-db \
  gs://barq-backups/production/$(date +%Y%m%d-%H%M%S).sql \
  --database=barq_production

# Export Terraform state
gsutil cp gs://barq-fleet-terraform-state/production/default.tfstate \
  ./terraform-state-backup-$(date +%Y%m%d).tfstate
```

## 📈 Scaling Operations

### Scale Cloud Run

```bash
# Increase capacity
gcloud run services update barq-api-production \
  --region=me-central1 \
  --min-instances=5 \
  --max-instances=100

# Decrease capacity (off-peak)
gcloud run services update barq-api-production \
  --region=me-central1 \
  --min-instances=2 \
  --max-instances=50
```

### Scale Database

```bash
# Scale up
gcloud sql instances patch barq-production-db \
  --tier=db-custom-8-30720

# Scale down
gcloud sql instances patch barq-production-db \
  --tier=db-custom-4-15360

# Increase disk
gcloud sql instances patch barq-production-db \
  --disk-size=100GB
```

## 🎯 Performance Optimization

### Database Query Optimization

```bash
# Connect to database
gcloud sql connect barq-production-db --user=barq_app_user

# Enable pg_stat_statements (in PostgreSQL)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

# Find slow queries
SELECT
  calls,
  total_exec_time,
  mean_exec_time,
  query
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

# Find missing indexes
SELECT
  schemaname,
  tablename,
  attname,
  n_distinct,
  correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY correlation;
```

### Cache Analysis

```bash
# View Cloud Run metrics
gcloud monitoring timeseries list \
  --filter='metric.type="run.googleapis.com/request_count"' \
  --interval-start=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ)

# If using Redis/Memorystore, check hit ratio
# (Connect to Redis and run INFO stats)
```

## 📞 Emergency Contacts

| Issue | Contact | Method |
|-------|---------|--------|
| Infrastructure Down | On-Call Engineer | +966-XXX-XXXX |
| Database Emergency | DBA Team | dba@barq-fleet.com |
| Security Incident | Security Team | security@barq-fleet.com |
| GCP Support | Google Cloud | https://cloud.google.com/support |

## 📝 Environment Variables Reference

| Variable | Location | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | Secret Manager | Database connection string |
| `SECRET_KEY` | Secret Manager | JWT signing key |
| `GOOGLE_CLIENT_ID` | Secret Manager | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Secret Manager | OAuth client secret |
| `SENTRY_DSN` | Secret Manager | Error tracking |
| `REDIS_AUTH` | Secret Manager | Redis authentication |
| `BACKEND_CORS_ORIGINS` | Cloud Run env | Allowed CORS origins |
| `LOG_LEVEL` | Cloud Run env | Logging verbosity |

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| **GCP Console** | https://console.cloud.google.com |
| **Cloud Run Services** | https://console.cloud.google.com/run?project=barq-fleet |
| **Cloud SQL** | https://console.cloud.google.com/sql?project=barq-fleet |
| **Secret Manager** | https://console.cloud.google.com/security/secret-manager?project=barq-fleet |
| **Monitoring** | https://console.cloud.google.com/monitoring?project=barq-fleet |
| **Logs Explorer** | https://console.cloud.google.com/logs?project=barq-fleet |
| **Billing** | https://console.cloud.google.com/billing |
| **IAM** | https://console.cloud.google.com/iam-admin?project=barq-fleet |

---

**Pro Tips**:
- Always test changes in staging first
- Use `terraform plan` before `apply`
- Monitor logs after every deployment
- Keep backups before major changes
- Document all manual changes
- Use version tags for all releases

**Last Updated**: December 11, 2025
**Version**: 1.0
