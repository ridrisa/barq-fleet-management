# Production Deployment Guide
**BARQ Fleet Management System**

> **CRITICAL**: This guide is for production deployment. Ensure all prerequisites are met before proceeding.

## Pre-Deployment Checklist

### 1. Environment Preparation

- [ ] GCP Project created and billing enabled
- [ ] Project ID: `barq-fleet` (or your custom project ID)
- [ ] Region selected: `me-central1` (Middle East - Doha)
- [ ] Terraform 1.0+ installed
- [ ] Google Cloud SDK installed and authenticated
- [ ] Git repository access configured

### 2. Credentials & Secrets Preparation

Generate all required secrets BEFORE deployment:

```bash
# 1. Database password (32 characters, strong)
DB_PASSWORD=$(openssl rand -base64 32)
echo "Database Password: $DB_PASSWORD"

# 2. Application secret key (64 hex characters)
SECRET_KEY=$(openssl rand -hex 32)
echo "Secret Key: $SECRET_KEY"

# 3. Save these securely in a password manager!
```

### 3. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized JavaScript origins:
     - `https://barq-fleet.com`
     - `https://app.barq-fleet.com`
     - `https://barq-web-production-[hash].run.app`
   - Authorized redirect URIs:
     - `https://barq-fleet.com/auth/callback`
     - `https://app.barq-fleet.com/auth/callback`
     - `https://barq-web-production-[hash].run.app/auth/callback`
3. Save Client ID and Client Secret

### 4. Third-Party Services

- [ ] **Sentry Account**:
  - Create project at https://sentry.io
  - Get DSN from project settings
  - Save DSN for configuration

- [ ] **Slack Webhook** (Optional):
  - Create webhook at https://api.slack.com/messaging/webhooks
  - Choose channel: `#production-alerts`
  - Save webhook URL

### 5. Domain Configuration (If using custom domains)

- [ ] Register domains:
  - Primary: `barq-fleet.com`
  - API: `api.barq-fleet.com`
  - App: `app.barq-fleet.com`
- [ ] Configure DNS provider access
- [ ] Prepare SSL certificates (or use Google-managed)

## Deployment Steps

### Step 1: GCP Project Setup

```bash
# Set project ID
export PROJECT_ID="barq-fleet"

# Set active project
gcloud config set project $PROJECT_ID

# Enable billing (must be done via Console if not already enabled)
# https://console.cloud.google.com/billing

# Verify project
gcloud projects describe $PROJECT_ID
```

### Step 2: Create Terraform State Bucket

```bash
# Create GCS bucket for Terraform state
gsutil mb -p $PROJECT_ID -l me-central1 gs://barq-fleet-terraform-state

# Enable versioning
gsutil versioning set on gs://barq-fleet-terraform-state

# Set lifecycle policy to keep 10 versions
cat > /tmp/lifecycle.json <<EOF
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {
        "numNewerVersions": 10,
        "isLive": false
      }
    }
  ]
}
EOF

gsutil lifecycle set /tmp/lifecycle.json gs://barq-fleet-terraform-state

# Verify bucket
gsutil ls -L -b gs://barq-fleet-terraform-state
```

### Step 3: Configure Terraform Variables

```bash
# Navigate to production environment
cd terraform/environments/production

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit with your actual values
nano terraform.tfvars
```

**Required configurations in `terraform.tfvars`**:

```hcl
project_id = "barq-fleet"
region     = "me-central1"

# Database
db_user     = "barq_app_user"
db_password = "YOUR_GENERATED_DB_PASSWORD"  # From step 2
database_url = "postgresql://barq_app_user:YOUR_GENERATED_DB_PASSWORD@/barq_production?host=/cloudsql/barq-fleet:me-central1:barq-production-db"

# Application
secret_key = "YOUR_GENERATED_SECRET_KEY"  # From step 2

# Google OAuth
google_client_id     = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com"
google_client_secret = "YOUR_GOOGLE_CLIENT_SECRET"

# Monitoring
alert_email       = "alerts@your-company.com"
slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Sentry
sentry_dsn = "https://YOUR_SENTRY_DSN@sentry.io/PROJECT_ID"

# CORS (update with your actual domains)
cors_origins = "https://barq-fleet.com,https://app.barq-fleet.com"

# API URL (update after first deployment or if using custom domain)
api_url = "https://api.barq-fleet.com"
```

### Step 4: Initialize Terraform

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format files
terraform fmt
```

Expected output:
```
Initializing the backend...
Successfully configured the backend "gcs"!
Terraform has been successfully initialized!
```

### Step 5: Review Deployment Plan

```bash
# Generate and review plan
terraform plan -out=tfplan

# Review carefully:
# - ~30-35 resources will be created
# - Verify resource names
# - Check instance configurations
# - Validate security settings
```

**Critical items to verify**:
- ✅ Cloud SQL has `deletion_protection = true`
- ✅ Cloud SQL uses `REGIONAL` availability
- ✅ Cloud SQL has private IP only
- ✅ Secrets are stored in Secret Manager
- ✅ Min instances set to 2 for HA
- ✅ VPC connector configured

### Step 6: Deploy Infrastructure

```bash
# Apply the plan
terraform apply tfplan

# This will take 15-20 minutes
# Cloud SQL creation is the slowest (~10 minutes)
```

Monitor the deployment:
```bash
# In another terminal, watch Cloud SQL creation
gcloud sql operations list --instance=barq-production-db --filter="status=RUNNING"
```

### Step 7: Verify Deployment

```bash
# Get service URLs
API_URL=$(terraform output -raw api_service_url)
WEB_URL=$(terraform output -raw web_service_url)

echo "API URL: $API_URL"
echo "Web URL: $WEB_URL"

# Test API health endpoint
curl $API_URL/health/live

# Expected response:
# {"status":"healthy","timestamp":"2025-12-11T...","version":"1.0.0"}

# View all outputs
terraform output
```

### Step 8: Database Setup

```bash
# Get database connection name
DB_CONN=$(terraform output -raw database_connection_name)

# Connect to database
gcloud sql connect barq-production-db --user=barq_app_user --database=barq_production

# Inside PostgreSQL prompt, verify:
\dt  # List tables (should be empty initially)
\l   # List databases
\q   # Quit
```

### Step 9: Deploy Application Code

```bash
# Build and push Docker images
cd ../../../  # Back to project root

# Build backend
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_ENVIRONMENT=production,_IMAGE_TAG=v1.0.0

# Or use the automated deployment workflow
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

### Step 10: Run Database Migrations

```bash
# Migrations should run automatically on container startup
# Verify by checking logs:
gcloud run services logs read barq-api-production \
  --region=me-central1 \
  --limit=50 \
  | grep -i "migration"

# Expected output:
# Running migrations...
# Applied migration 001_initial_schema
# Applied migration 002_add_tenancy
# ...
# Migrations complete
```

### Step 11: Configure Custom Domains (Optional)

If using custom domains instead of Cloud Run URLs:

```bash
# Map API domain
gcloud run domain-mappings create \
  --service barq-api-production \
  --domain api.barq-fleet.com \
  --region me-central1

# Map Web domain
gcloud run domain-mappings create \
  --service barq-web-production \
  --domain app.barq-fleet.com \
  --region me-central1

# Add DNS records (output will show required records)
# Example:
# TYPE  NAME                VALUE
# A     api.barq-fleet.com  216.239.32.21
# AAAA  api.barq-fleet.com  2001:db8::1
```

Update DNS provider:
1. Go to your DNS provider (e.g., Cloudflare, Route53)
2. Add the A and AAAA records shown in output
3. Wait for DNS propagation (5-60 minutes)
4. Verify: `nslookup api.barq-fleet.com`

### Step 12: Update Frontend Configuration

After deployment, update frontend to use production API:

```bash
# Update terraform.tfvars with actual API URL
api_url = "https://barq-api-production-[hash].run.app"
# or if using custom domain:
api_url = "https://api.barq-fleet.com"

# Redeploy frontend
terraform apply -target=google_cloud_run_service.barq_web_production
```

### Step 13: Verify End-to-End

```bash
# 1. Test API endpoints
curl $API_URL/api/v1/docs  # Swagger documentation
curl $API_URL/health/ready # Readiness check
curl $API_URL/health/live  # Liveness check

# 2. Test authentication
curl -X POST $API_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@barq-fleet.com","password":"admin123"}'

# 3. Open web interface
open $WEB_URL  # macOS
# or
xdg-open $WEB_URL  # Linux

# 4. Test Google OAuth
# - Click "Sign in with Google" button
# - Should redirect to Google login
# - Should return to app after authentication
```

### Step 14: Configure Monitoring Alerts

```bash
# Verify alert policies were created
gcloud alpha monitoring policies list --format="table(displayName,enabled)"

# Test alert notification
# Simulate high error rate by making failed requests
for i in {1..100}; do
  curl $API_URL/api/v1/nonexistent-endpoint
done

# Check if alert email was received (may take 5-10 minutes)
```

### Step 15: Final Security Hardening

```bash
# 1. Verify no public IPs on Cloud SQL
gcloud sql instances describe barq-production-db \
  --format="value(ipAddresses[0].type)"
# Should output: PRIVATE

# 2. Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:barq-api-production@"

# 3. Enable Cloud Armor rate limiting (already configured)
gcloud compute security-policies describe barq-api-production-policy

# 4. Review Secret Manager access
gcloud secrets get-iam-policy barq-database-url-prod

# 5. Enable audit logging
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=10 \
  --format=json
```

## Post-Deployment Checklist

### Immediate (Day 1)

- [ ] Verify all health checks are passing
- [ ] Test user authentication (email + Google OAuth)
- [ ] Create first admin user
- [ ] Verify database connectivity
- [ ] Check monitoring dashboards
- [ ] Confirm alert emails are received
- [ ] Test backup restoration (important!)
- [ ] Document actual service URLs
- [ ] Update DNS records (if using custom domains)
- [ ] Configure SSL certificates

### Week 1

- [ ] Monitor error rates and latency
- [ ] Review logs for any anomalies
- [ ] Load testing (simulate 100+ concurrent users)
- [ ] Database performance tuning
- [ ] Cost analysis and budget alerts
- [ ] Security scan with Cloud Security Command Center
- [ ] Backup verification (restore to test instance)
- [ ] Disaster recovery drill

### Month 1

- [ ] Review and optimize Cloud SQL instance size
- [ ] Analyze auto-scaling patterns
- [ ] Adjust min/max instances based on usage
- [ ] Review and optimize costs
- [ ] Security audit
- [ ] Performance optimization based on metrics
- [ ] User feedback collection
- [ ] Documentation updates

## Rollback Procedures

### If deployment fails during `terraform apply`:

```bash
# Terraform maintains state, so safe to retry
terraform apply

# If specific resource fails, target it:
terraform apply -target=google_sql_database_instance.production

# If completely stuck, destroy and retry:
terraform destroy -target=PROBLEMATIC_RESOURCE
terraform apply
```

### If application has critical bugs after deployment:

```bash
# Rollback to previous Cloud Run revision
gcloud run services update-traffic barq-api-production \
  --to-revisions=barq-api-production-00001-xyz=100 \
  --region=me-central1

# Or deploy known good version
gcloud run deploy barq-api-production \
  --image=me-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api:v0.9.0 \
  --region=me-central1
```

### If database migration fails:

```bash
# Connect to database
gcloud sql connect barq-production-db --user=barq_app_user

# Check migration status
SELECT * FROM alembic_version;

# Rollback to previous version (if using Alembic)
alembic downgrade -1

# Or restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=barq-production-db
```

## Monitoring & Maintenance

### Daily Checks

```bash
# Check service health
curl $API_URL/health/live

# View error logs
gcloud run services logs read barq-api-production \
  --region=me-central1 \
  --limit=100 \
  | grep ERROR

# Check active instances
gcloud run services describe barq-api-production \
  --region=me-central1 \
  --format="value(status.traffic[0].percent)"
```

### Weekly Checks

```bash
# Review database performance
gcloud sql operations list --instance=barq-production-db --limit=20

# Check backup status
gcloud sql backups list --instance=barq-production-db --limit=7

# Review costs
gcloud billing accounts list
gcloud billing budgets list --billing-account=BILLING_ACCOUNT_ID

# Security scan
gcloud scc findings list $PROJECT_ID
```

### Monthly Maintenance

```bash
# Update dependencies
# Rebuild and deploy with latest patches

# Rotate secrets
# Generate new passwords and update Secret Manager

# Review and optimize costs
# Analyze Cloud Monitoring metrics for right-sizing

# Test disaster recovery
# Restore from backup to test instance

# Security audit
# Review IAM permissions, network rules, etc.
```

## Troubleshooting

### Issue: Cloud SQL connection timeouts

**Symptoms**: API logs show "could not connect to database"

**Solution**:
```bash
# Verify VPC connector
gcloud compute networks vpc-access connectors describe barq-production-connector \
  --region=me-central1

# Check private service connection
gcloud services vpc-peerings list --service=servicenetworking.googleapis.com

# Verify Cloud SQL is in same VPC
gcloud sql instances describe barq-production-db \
  --format="value(ipAddresses[0].type)"
```

### Issue: 503 Service Unavailable

**Symptoms**: API returns 503 errors

**Solution**:
```bash
# Check if instances are running
gcloud run services describe barq-api-production --region=me-central1

# View logs for errors
gcloud run services logs read barq-api-production --region=me-central1 --limit=100

# Increase min instances temporarily
gcloud run services update barq-api-production \
  --min-instances=5 \
  --region=me-central1
```

### Issue: High database CPU usage

**Symptoms**: Cloud SQL CPU > 80%

**Solution**:
```bash
# Scale up database instance
# Update in terraform.tfvars:
db_tier = "db-custom-8-30720"  # 8 vCPU, 30GB RAM

# Apply change
terraform apply -target=google_sql_database_instance.production

# Or use gcloud:
gcloud sql instances patch barq-production-db \
  --tier=db-custom-8-30720
```

### Issue: Secret Manager access denied

**Symptoms**: API logs show "failed to access secret"

**Solution**:
```bash
# Grant access to service account
gcloud secrets add-iam-policy-binding barq-database-url-prod \
  --member="serviceAccount:barq-api-production@barq-fleet.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Redeploy to pick up new permissions
gcloud run services update barq-api-production \
  --region=me-central1
```

## Success Criteria

### Technical Metrics

- ✅ API response time p95 < 500ms
- ✅ Error rate < 0.1%
- ✅ Uptime > 99.9%
- ✅ Database connection pool healthy
- ✅ All health checks passing
- ✅ No critical security vulnerabilities

### Business Metrics

- ✅ User authentication working (email + Google)
- ✅ All core features functional
- ✅ Data accuracy verified
- ✅ Reports generating correctly
- ✅ Mobile app connectivity working
- ✅ Real-time updates functioning

### Operational Metrics

- ✅ Monitoring dashboards configured
- ✅ Alerts being received
- ✅ Backups running daily
- ✅ Logs being collected
- ✅ Cost within budget
- ✅ Documentation complete

## Support Contacts

- **Infrastructure Team**: infrastructure@barq-fleet.com
- **On-Call Engineer**: +966-XXX-XXXX-XXX
- **GCP Support**: https://cloud.google.com/support
- **Emergency Runbook**: `/docs/operations/RUNBOOK.md`

## Additional Resources

- **Terraform Documentation**: https://www.terraform.io/docs
- **GCP Best Practices**: https://cloud.google.com/architecture/framework
- **Cloud Run Documentation**: https://cloud.google.com/run/docs
- **Cloud SQL Documentation**: https://cloud.google.com/sql/docs
- **Security Hardening Guide**: `/docs/security/HARDENING.md`
- **Disaster Recovery Plan**: `/docs/operations/DR_PLAN.md`

---

**Deployment Date**: _________________
**Deployed By**: _________________
**Sign-off**: _________________

**Version**: 1.0.0
**Last Updated**: December 11, 2025
