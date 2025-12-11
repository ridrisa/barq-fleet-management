# BARQ Fleet Management - Production Infrastructure

This directory contains the Terraform configuration for deploying the BARQ Fleet Management system to a production Google Cloud Platform (GCP) environment.

## Architecture Overview

### Infrastructure Components

- **Cloud Run Services**:
  - `barq-api-production` - Backend API (FastAPI)
    - Min instances: 2 (high availability)
    - Max instances: 50 (scales with demand)
    - Resources: 4 vCPU, 4GB RAM per instance
    - Always-on CPU (no throttling)

  - `barq-web-production` - Frontend Web (React/Vite)
    - Min instances: 2 (high availability)
    - Max instances: 20 (scales with demand)
    - Resources: 2 vCPU, 1GB RAM per instance

- **Cloud SQL PostgreSQL**:
  - Version: PostgreSQL 16
  - Tier: db-custom-4-15360 (4 vCPU, 15GB RAM)
  - Availability: REGIONAL (automatic failover)
  - Disk: 50GB SSD (auto-resizes to 500GB)
  - Backups: Daily automated with 30-day retention
  - Point-in-time recovery: 7-day transaction logs
  - Private IP only (no public internet access)

- **VPC Networking**:
  - VPC Access Connector: 300-1000 Mbps throughput
  - Private Service Connection for Cloud SQL
  - Reserved IP range: 10.20.0.0/16

- **Secret Manager**:
  - Database credentials
  - Application secret keys
  - Google OAuth credentials
  - Sentry DSN
  - Redis AUTH string

- **Monitoring & Alerting**:
  - Cloud Monitoring dashboards
  - Uptime checks
  - Email and Slack notifications
  - Custom alert policies

- **Security**:
  - Cloud Armor DDoS protection (rate limiting)
  - SSL/TLS encryption in transit
  - IAM service accounts with least privilege
  - Private networking for database access

## Prerequisites

### Required Tools

```bash
# Install Terraform (>= 1.0)
brew install terraform  # macOS
# or download from: https://www.terraform.io/downloads

# Install Google Cloud SDK
brew install google-cloud-sdk  # macOS
# or download from: https://cloud.google.com/sdk/docs/install

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login
```

### Required GCP Permissions

Your GCP account needs the following roles:

- `roles/owner` or
- Custom role with:
  - `roles/compute.admin`
  - `roles/iam.serviceAccountAdmin`
  - `roles/run.admin`
  - `roles/cloudsql.admin`
  - `roles/secretmanager.admin`
  - `roles/monitoring.admin`

### Required GCP APIs

These APIs will be automatically enabled by Terraform:

- Cloud Run API (`run.googleapis.com`)
- Secret Manager API (`secretmanager.googleapis.com`)
- Cloud SQL Admin API (`sqladmin.googleapis.com`)
- Compute Engine API (`compute.googleapis.com`)
- Serverless VPC Access API (`vpcaccess.googleapis.com`)
- Service Networking API (`servicenetworking.googleapis.com`)
- Cloud Monitoring API (`monitoring.googleapis.com`)
- Cloud Logging API (`logging.googleapis.com`)
- Cloud KMS API (`cloudkms.googleapis.com`)

## Quick Start

### 1. Configure Variables

```bash
# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

**IMPORTANT**: Never commit `terraform.tfvars` to Git! It contains sensitive credentials.

### 2. Initialize Terraform

```bash
cd terraform/environments/production
terraform init
```

This will:
- Download the Google Cloud provider
- Configure the GCS backend for state storage
- Initialize modules

### 3. Review the Plan

```bash
terraform plan
```

This shows what resources will be created. Review carefully!

### 4. Apply Configuration

```bash
terraform apply
```

Type `yes` when prompted. This will create:
- ~30 resources
- Takes approximately 15-20 minutes
- Cloud SQL creation is the slowest step (~10 minutes)

### 5. Verify Deployment

```bash
# Get service URLs
terraform output api_service_url
terraform output web_service_url

# Test API health
curl $(terraform output -raw api_service_url)/health/live

# View all outputs
terraform output
```

## Configuration Guide

### Required Variables

These variables MUST be set in `terraform.tfvars`:

| Variable | Description | Example |
|----------|-------------|---------|
| `project_id` | GCP Project ID | `barq-fleet` |
| `region` | GCP Region | `me-central1` |
| `db_user` | Database username | `barq_app_user` |
| `db_password` | Database password | `[generated-secure-password]` |
| `database_url` | Full DB connection URL | `postgresql://...` |
| `secret_key` | JWT signing key | `[generated-hex-string]` |
| `google_client_id` | Google OAuth Client ID | `xxx.apps.googleusercontent.com` |
| `google_client_secret` | Google OAuth Secret | `[from-google-console]` |
| `alert_email` | Email for alerts | `alerts@barq-fleet.com` |

### Generating Secrets

```bash
# Generate a secure database password (32 characters)
openssl rand -base64 32

# Generate application secret key (64 hex characters)
openssl rand -hex 32

# Generate a random string
openssl rand -base64 16
```

### Database Connection URL

After Cloud SQL is created, construct the database URL:

```bash
# Format
postgresql://{db_user}:{db_password}@/{database_name}?host=/cloudsql/{connection_name}

# Example
postgresql://barq_app_user:SecurePass123@/barq_production?host=/cloudsql/barq-fleet:me-central1:barq-production-db

# Get connection name
terraform output database_connection_name
```

## Post-Deployment Steps

### 1. Run Database Migrations

```bash
# Connect to Cloud SQL using Cloud SQL Proxy
gcloud sql connect barq-production-db --user=barq_app_user --database=barq_production

# Or from your Cloud Run service (automatic)
# Migrations run automatically on container startup
```

### 2. Configure Custom Domain (Optional)

```bash
# Map custom domain to Cloud Run
gcloud run domain-mappings create \
  --service barq-api-production \
  --domain api.barq-fleet.com \
  --region me-central1

# Add DNS records (shown in command output)
# A record: points to Cloud Run IP
# AAAA record: points to Cloud Run IPv6
```

### 3. Set Up Monitoring Alerts

```bash
# Alerts are automatically created by the monitoring module
# Verify in GCP Console:
# https://console.cloud.google.com/monitoring/alerting

# Test alert delivery
gcloud alpha monitoring policies list
```

### 4. Verify Security

```bash
# Check Cloud Armor policy
gcloud compute security-policies describe barq-api-production-policy

# Verify private IP configuration
gcloud sql instances describe barq-production-db \
  --format="value(ipAddresses[0].ipAddress)"

# Check service account permissions
gcloud iam service-accounts get-iam-policy \
  barq-api-production@barq-fleet.iam.gserviceaccount.com
```

## Maintenance

### Viewing Logs

```bash
# Backend API logs
gcloud run services logs read barq-api-production --region=me-central1 --limit=50

# Frontend logs
gcloud run services logs read barq-web-production --region=me-central1 --limit=50

# Database logs
gcloud sql operations list --instance=barq-production-db
```

### Updating Configuration

```bash
# 1. Modify terraform.tfvars or *.tf files
nano variables.tf

# 2. Review changes
terraform plan

# 3. Apply updates
terraform apply
```

### Scaling Configuration

Update in `main.tf`:

```hcl
# Increase API instances
"autoscaling.knative.dev/minScale" = "5"  # from 2
"autoscaling.knative.dev/maxScale" = "100" # from 50

# Increase database resources
db_tier = "db-custom-8-30720" # 8 vCPU, 30GB RAM
```

### Database Backups

```bash
# List automated backups
gcloud sql backups list --instance=barq-production-db

# Create manual backup
gcloud sql backups create --instance=barq-production-db

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=barq-production-db \
  --backup-id=BACKUP_ID
```

### Secret Rotation

```bash
# Update database password
gcloud sql users set-password barq_app_user \
  --instance=barq-production-db \
  --password=NEW_SECURE_PASSWORD

# Update secret in Secret Manager
echo -n "NEW_VALUE" | gcloud secrets versions add barq-secret-key-prod --data-file=-

# Cloud Run will automatically pick up new secret version on next deployment
```

## Disaster Recovery

### Backup Strategy

- **Automated Daily Backups**: 30-day retention
- **Point-in-Time Recovery**: 7-day transaction logs
- **Manual Backups**: Before major updates

### Recovery Time Objective (RTO)

- **Database Failover**: < 30 seconds (automatic)
- **Full Recovery from Backup**: < 1 hour
- **Service Restart**: < 2 minutes

### Recovery Point Objective (RPO)

- **Continuous Replication**: < 5 minutes data loss
- **Point-in-Time Recovery**: Down to the second within 7 days

### Recovery Procedures

#### 1. Database Recovery

```bash
# Restore from latest automated backup
gcloud sql backups restore $(gcloud sql backups list --instance=barq-production-db --limit=1 --format="value(id)") \
  --backup-instance=barq-production-db

# Or restore to specific point in time
gcloud sql instances restore-backup barq-production-db \
  --backup-run=BACKUP_RUN_ID
```

#### 2. Service Recovery

```bash
# Rollback to previous revision
gcloud run services update-traffic barq-api-production \
  --to-revisions=barq-api-production-00002-xyz=100 \
  --region=me-central1

# Or redeploy from known good image
gcloud run deploy barq-api-production \
  --image=me-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api:v1.2.3 \
  --region=me-central1
```

#### 3. Full Environment Recreation

```bash
# If Terraform state is intact
terraform apply

# If state is lost, import existing resources
terraform import google_cloud_run_service.barq_api_production locations/me-central1/services/barq-api-production
```

## Cost Optimization

### Estimated Monthly Costs (Production)

| Resource | Configuration | Monthly Cost (USD) |
|----------|---------------|-------------------|
| Cloud Run API | 2-50 instances, 4vCPU, 4GB | $150-$800 |
| Cloud Run Web | 2-20 instances, 2vCPU, 1GB | $50-$200 |
| Cloud SQL | db-custom-4-15360, HA | $400-$500 |
| VPC Connector | 300-1000 Mbps | $30-$100 |
| Secret Manager | 10 secrets, 1000 accesses | $1-$5 |
| Cloud Monitoring | Standard metrics | $10-$20 |
| Cloud Armor | 1 policy | $5 |
| **Total** | | **$650-$1,630** |

### Cost Saving Tips

1. **Use Committed Use Discounts**:
   ```bash
   # Save up to 57% for 1-year or 3-year commitments
   gcloud compute commitments create
   ```

2. **Adjust Auto-scaling**:
   - Lower `minScale` during off-peak hours
   - Use Cloud Scheduler to scale down at night

3. **Optimize Cloud SQL**:
   - Right-size instance (start smaller, scale up)
   - Use ZONAL instead of REGIONAL for dev/staging

4. **Monitor and Alert**:
   ```bash
   # Set budget alerts
   gcloud billing budgets create \
     --billing-account=BILLING_ACCOUNT_ID \
     --display-name="BARQ Production Budget" \
     --budget-amount=2000 \
     --threshold-rule=percent=50 \
     --threshold-rule=percent=90
   ```

## Security Hardening

### Best Practices Implemented

✅ **Network Security**:
- Private IP for Cloud SQL
- VPC Access Connector for serverless
- No public IP addresses exposed

✅ **Identity & Access**:
- Service accounts with least privilege
- Secret Manager for credentials
- IAM roles scoped to specific resources

✅ **Data Protection**:
- Encryption at rest (automatic)
- Encryption in transit (TLS 1.3)
- SSL required for database connections

✅ **Application Security**:
- Cloud Armor rate limiting (1000 req/min per IP)
- CORS configuration
- Health check probes

✅ **Monitoring & Audit**:
- Cloud Logging enabled
- Audit logs for data access
- Alert policies for anomalies

### Additional Hardening (Recommended)

1. **Enable Binary Authorization**:
   ```bash
   gcloud services enable binaryauthorization.googleapis.com
   ```

2. **Set Up VPC Service Controls**:
   ```bash
   gcloud access-context-manager perimeters create barq-perimeter \
     --resources=projects/PROJECT_NUMBER \
     --restricted-services=storage.googleapis.com
   ```

3. **Configure Cloud KMS for CMEK**:
   ```bash
   gcloud kms keyrings create barq-keyring --location=me-central1
   gcloud kms keys create barq-key --keyring=barq-keyring --location=me-central1 --purpose=encryption
   ```

## Troubleshooting

### Common Issues

#### 1. Cloud SQL Connection Timeouts

```bash
# Check VPC connector status
gcloud compute networks vpc-access connectors describe barq-production-connector --region=me-central1

# Verify private service connection
gcloud services vpc-peerings list --service=servicenetworking.googleapis.com

# Test from Cloud Shell
gcloud sql connect barq-production-db --user=barq_app_user
```

#### 2. Cloud Run 503 Errors

```bash
# Check service logs
gcloud run services logs read barq-api-production --region=me-central1 --limit=100

# Check instance count
gcloud run services describe barq-api-production --region=me-central1 --format="value(status.traffic[0].percent)"

# Increase min instances temporarily
gcloud run services update barq-api-production \
  --min-instances=5 \
  --region=me-central1
```

#### 3. Terraform State Locked

```bash
# Force unlock (CAREFUL!)
terraform force-unlock LOCK_ID

# Or wait for lock to expire (15 minutes)
```

#### 4. Secret Manager Access Denied

```bash
# Grant service account access
gcloud secrets add-iam-policy-binding barq-database-url-prod \
  --member="serviceAccount:barq-api-production@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Monitoring & Observability

### Key Metrics

- **API Response Time**: Target < 500ms (p95)
- **Error Rate**: Target < 0.1%
- **Database Connections**: Monitor for leaks
- **CPU Utilization**: Scale at 70%
- **Memory Utilization**: Scale at 80%

### Dashboards

Access in GCP Console:
- Cloud Monitoring: https://console.cloud.google.com/monitoring
- Cloud Run Metrics: https://console.cloud.google.com/run
- Cloud SQL Insights: https://console.cloud.google.com/sql/instances

### Alerts Configured

1. **High Error Rate**: > 5% errors for 5 minutes
2. **API Latency**: p95 > 1000ms for 5 minutes
3. **Database CPU**: > 80% for 10 minutes
4. **Database Connections**: > 450 for 5 minutes
5. **Service Downtime**: Uptime check fails for 2 minutes

## Compliance & Governance

### Saudi Arabia Specific

- **Data Residency**: Middle East region (`me-central1`)
- **ZATCA E-Invoicing**: Compliance features in application
- **Arabic Language**: RTL support in frontend
- **Prayer Times**: Built into scheduling system

### Audit & Compliance

```bash
# Enable audit logs
gcloud projects add-iam-policy-binding barq-fleet \
  --member="allUsers" \
  --role="roles/logging.viewer"

# Export logs for long-term storage
gcloud logging sinks create barq-audit-sink \
  storage.googleapis.com/barq-audit-logs \
  --log-filter='resource.type="cloud_run_revision"'
```

## CI/CD Integration

### GitHub Actions Deployment

```yaml
# .github/workflows/deploy-production.yml
- name: Deploy to Production
  run: |
    cd terraform/environments/production
    terraform init
    terraform apply -auto-approve
```

### Cloud Build Integration

```bash
# Submit build for production
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=production
```

## Support & Documentation

- **Terraform Registry**: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- **GCP Documentation**: https://cloud.google.com/docs
- **BARQ Project Docs**: `/docs/` directory in repository
- **Runbook**: `/docs/operations/RUNBOOK.md`

## Changelog

### Version 1.0 (2025-12-11)
- Initial production infrastructure
- High availability configuration
- Cloud Armor security
- Comprehensive monitoring
- Secret Manager integration
- Google OAuth support

---

**Last Updated**: December 11, 2025
**Maintained By**: Infrastructure Team
**Contact**: infrastructure@barq-fleet.com
