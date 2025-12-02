# BARQ Fleet Management - Deployment Guide

## Overview

Complete deployment guide for BARQ Fleet Management System covering local development, staging, and production environments.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Staging Deployment](#staging-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Migrations](#database-migrations)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Docker Desktop 4.0+
- Docker Compose 2.0+
- OR: Python 3.11+, Node.js 18+, PostgreSQL 14+, Redis 7+

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/barq-fleet-clean.git
cd barq-fleet-clean

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Manual Setup

**1. Backend Setup:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Start PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
# Windows: Start PostgreSQL service

# Create database
createdb barq_fleet

# Run migrations
alembic upgrade head

# Create admin user
python create_admin.py

# Start Redis
# macOS: brew services start redis
# Linux: sudo systemctl start redis
# Windows: Start Redis service

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**2. Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local

# Start development server
npm run dev
```

**3. Verify Installation:**
```bash
# Backend health check
curl http://localhost:8000/api/v1/health

# Frontend
open http://localhost:5173

# API docs
open http://localhost:8000/docs
```

### Local Development URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Database:** localhost:5432
- **Redis:** localhost:6379

---

## Staging Deployment

### Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and configured
- GitHub repository with GitHub Actions enabled

### Infrastructure Setup

**1. Google Cloud Setup:**
```bash
# Login to GCP
gcloud auth login

# Set project
gcloud config set project barq-fleet-staging

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  redis.googleapis.com
```

**2. Create Cloud SQL Instance:**
```bash
# Create PostgreSQL instance
gcloud sql instances create barq-staging-db \
  --database-version=POSTGRES_14 \
  --tier=db-g1-small \
  --region=us-central1 \
  --storage-size=10GB \
  --storage-type=SSD \
  --backup-start-time=03:00

# Create database
gcloud sql databases create barq_fleet \
  --instance=barq-staging-db

# Create user
gcloud sql users create barq_user \
  --instance=barq-staging-db \
  --password=SECURE_PASSWORD_HERE
```

**3. Create Redis Instance:**
```bash
gcloud redis instances create barq-staging-redis \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

**4. Setup Secrets:**
```bash
# Create secrets in Secret Manager
echo -n "your-secret-key" | gcloud secrets create SECRET_KEY --data-file=-
echo -n "your-database-url" | gcloud secrets create DATABASE_URL --data-file=-
echo -n "your-google-client-id" | gcloud secrets create GOOGLE_CLIENT_ID --data-file=-
echo -n "your-google-client-secret" | gcloud secrets create GOOGLE_CLIENT_SECRET --data-file=-
```

### Backend Deployment

**1. Build Docker Image:**
```bash
cd backend

# Build image
docker build -t gcr.io/barq-fleet-staging/backend:latest .

# Push to Google Container Registry
docker push gcr.io/barq-fleet-staging/backend:latest
```

**2. Deploy to Cloud Run:**
```bash
gcloud run deploy barq-backend-staging \
  --image gcr.io/barq-fleet-staging/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=staging" \
  --set-secrets "DATABASE_URL=DATABASE_URL:latest,SECRET_KEY=SECRET_KEY:latest" \
  --add-cloudsql-instances barq-staging-db \
  --min-instances 1 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

**3. Run Migrations:**
```bash
# Connect to Cloud SQL
gcloud sql connect barq-staging-db --user=barq_user

# Run migrations (from local)
DATABASE_URL="postgresql://..." alembic upgrade head
```

### Frontend Deployment

**1. Build Production Bundle:**
```bash
cd frontend

# Build
npm run build:prod

# The build output is in dist/
```

**2. Deploy to Cloud Storage + Cloud CDN:**
```bash
# Create bucket
gsutil mb gs://barq-staging-frontend

# Upload build files
gsutil -m rsync -r -d dist/ gs://barq-staging-frontend

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://barq-staging-frontend

# Enable web hosting
gsutil web set -m index.html -e 404.html gs://barq-staging-frontend
```

**3. Setup Cloud CDN (Optional):**
```bash
# Create load balancer
gcloud compute backend-buckets create barq-frontend-staging \
  --gcs-bucket-name=barq-staging-frontend \
  --enable-cdn

# Create URL map
gcloud compute url-maps create barq-staging-frontend-map \
  --default-backend-bucket=barq-frontend-staging

# Create HTTP proxy
gcloud compute target-http-proxies create barq-staging-frontend-proxy \
  --url-map=barq-staging-frontend-map

# Create forwarding rule
gcloud compute forwarding-rules create barq-staging-frontend-rule \
  --global \
  --target-http-proxy=barq-staging-frontend-proxy \
  --ports=80
```

### CI/CD Setup (GitHub Actions)

**.github/workflows/deploy-staging.yml:**
```yaml
name: Deploy to Staging

on:
  push:
    branches:
      - develop

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: barq-fleet-staging

      - name: Build and Push Docker Image
        run: |
          cd backend
          docker build -t gcr.io/barq-fleet-staging/backend:${{ github.sha }} .
          docker push gcr.io/barq-fleet-staging/backend:${{ github.sha }}

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy barq-backend-staging \
            --image gcr.io/barq-fleet-staging/backend:${{ github.sha }} \
            --region us-central1

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Build Frontend
        run: |
          cd frontend
          npm ci
          npm run build:prod

      - name: Deploy to Cloud Storage
        uses: google-github-actions/upload-cloud-storage@v1
        with:
          path: frontend/dist
          destination: barq-staging-frontend
          parent: false
```

---

## Production Deployment

### Prerequisites

- Production GCP project
- Domain name configured
- SSL certificate
- Monitoring and alerting setup

### Infrastructure Setup

**1. Production Cloud SQL:**
```bash
# High-availability instance
gcloud sql instances create barq-prod-db \
  --database-version=POSTGRES_14 \
  --tier=db-custom-4-16384 \
  --region=us-central1 \
  --storage-size=100GB \
  --storage-type=SSD \
  --storage-auto-increase \
  --availability-type=REGIONAL \
  --backup-start-time=03:00 \
  --enable-point-in-time-recovery \
  --retained-backups-count=30
```

**2. Production Redis:**
```bash
gcloud redis instances create barq-prod-redis \
  --size=5 \
  --region=us-central1 \
  --tier=standard \
  --redis-version=redis_7_0 \
  --replica-count=1
```

**3. Cloud Armor (DDoS Protection):**
```bash
gcloud compute security-policies create barq-prod-security-policy \
  --description="Security policy for BARQ production"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy=barq-prod-security-policy \
  --expression="true" \
  --action="rate-based-ban" \
  --rate-limit-threshold-count=100 \
  --rate-limit-threshold-interval-sec=60 \
  --ban-duration-sec=600
```

### Backend Deployment (Production)

```bash
# Deploy with production configuration
gcloud run deploy barq-backend-prod \
  --image gcr.io/barq-fleet-prod/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "ENVIRONMENT=production" \
  --set-secrets "DATABASE_URL=DATABASE_URL:latest,SECRET_KEY=SECRET_KEY:latest" \
  --add-cloudsql-instances barq-prod-db \
  --min-instances 2 \
  --max-instances 100 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --concurrency 80 \
  --max-surge-upgrade 1 \
  --max-unavailable-upgrade 0
```

### Custom Domain Setup

**1. Map Custom Domain:**
```bash
# Map domain to Cloud Run
gcloud run domain-mappings create \
  --service=barq-backend-prod \
  --domain=api.barq.com \
  --region=us-central1

# Map frontend domain
gcloud compute backend-services update barq-frontend-prod \
  --global \
  --custom-domain=app.barq.com
```

**2. SSL Certificate:**
```bash
# Create managed SSL certificate
gcloud compute ssl-certificates create barq-prod-cert \
  --domains=api.barq.com,app.barq.com \
  --global
```

### Database Migrations (Production)

**IMPORTANT:** Always test migrations in staging first!

```bash
# 1. Backup database
gcloud sql backups create \
  --instance=barq-prod-db \
  --description="Pre-migration backup"

# 2. Run migrations
DATABASE_URL="postgresql://..." alembic upgrade head

# 3. Verify
DATABASE_URL="postgresql://..." alembic current

# 4. Rollback if needed
DATABASE_URL="postgresql://..." alembic downgrade -1
```

### Deployment Checklist

- [ ] All tests passing
- [ ] Staging deployment successful
- [ ] Database backup created
- [ ] Migration plan reviewed
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Team notified of deployment
- [ ] Maintenance window scheduled (if needed)

---

## Environment Configuration

### Backend Environment Variables

**Development:**
```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/barq_fleet
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=True
```

**Staging:**
```bash
DATABASE_URL=postgresql://user:pass@/cloudsql/project:region:instance/dbname
REDIS_URL=redis://10.0.0.3:6379/0
SECRET_KEY=<secret-from-secret-manager>
ENVIRONMENT=staging
DEBUG=False
CORS_ORIGINS=["https://staging.barq.com"]
```

**Production:**
```bash
DATABASE_URL=postgresql://user:pass@/cloudsql/project:region:instance/dbname
REDIS_URL=redis://10.0.0.5:6379/0
SECRET_KEY=<secret-from-secret-manager>
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=["https://app.barq.com"]
SENTRY_DSN=https://...
```

### Frontend Environment Variables

**Development:**
```bash
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

**Staging:**
```bash
VITE_API_URL=https://staging-api.barq.com
VITE_ENVIRONMENT=staging
VITE_SENTRY_DSN=https://...
```

**Production:**
```bash
VITE_API_URL=https://api.barq.com
VITE_ENVIRONMENT=production
VITE_SENTRY_DSN=https://...
```

---

## Monitoring & Logging

### Cloud Monitoring Setup

```bash
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create uptime check
gcloud monitoring uptime-check-configs create \
  --display-name="BARQ API Health Check" \
  --http-check-path="/api/v1/health" \
  --port=443 \
  --timeout=10s \
  --checked-resource-type=uptime-url \
  --checked-resource-url=https://api.barq.com
```

### Logging

View logs:
```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=barq-backend-prod" \
  --limit 100 \
  --format json

# Error logs only
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit 50
```

### Alerting

Create alert policies:
```bash
# High error rate alert
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 1%" \
  --condition-threshold-value=0.01 \
  --aggregation-alignment-period=60s
```

---

## Backup & Recovery

### Automated Backups

Cloud SQL automatically creates daily backups. Configure retention:

```bash
gcloud sql instances patch barq-prod-db \
  --retained-backups-count=30 \
  --retained-transaction-log-days=7
```

### Manual Backup

```bash
# Create on-demand backup
gcloud sql backups create \
  --instance=barq-prod-db \
  --description="Manual backup before major update"

# List backups
gcloud sql backups list --instance=barq-prod-db
```

### Point-in-Time Recovery

```bash
# Clone instance to specific time
gcloud sql instances clone barq-prod-db barq-recovery-instance \
  --point-in-time=2025-12-01T10:30:00Z
```

### Export Database

```bash
# Export to Cloud Storage
gcloud sql export sql barq-prod-db \
  gs://barq-backups/backup-2025-12-02.sql \
  --database=barq_fleet
```

### Restore from Backup

```bash
# Restore specific backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=barq-prod-db \
  --backup-id=BACKUP_ID
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check Cloud SQL instance status
gcloud sql instances describe barq-prod-db

# Check connection
gcloud sql connect barq-prod-db --user=barq_user

# View logs
gcloud sql operations list --instance=barq-prod-db
```

**2. Cloud Run Deployment Fails**
```bash
# Check deployment status
gcloud run services describe barq-backend-prod --region=us-central1

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit=100

# Rollback to previous revision
gcloud run services update-traffic barq-backend-prod \
  --to-revisions=PREVIOUS_REVISION=100
```

**3. High Memory Usage**
```bash
# Increase memory
gcloud run services update barq-backend-prod \
  --memory 4Gi \
  --region=us-central1
```

**4. Slow Response Times**
```bash
# Check metrics
gcloud monitoring dashboards list

# Increase concurrency
gcloud run services update barq-backend-prod \
  --concurrency=100

# Add more instances
gcloud run services update barq-backend-prod \
  --min-instances=5
```

### Rollback Procedure

**1. Identify Last Good Revision:**
```bash
gcloud run revisions list \
  --service=barq-backend-prod \
  --region=us-central1
```

**2. Route Traffic to Previous Revision:**
```bash
gcloud run services update-traffic barq-backend-prod \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1
```

**3. Database Rollback (if needed):**
```bash
# Use Alembic to downgrade
alembic downgrade -1
```

### Health Checks

```bash
# Backend health
curl https://api.barq.com/api/v1/health

# Expected response:
# {"status":"healthy","version":"1.0.0","database":"connected"}

# Frontend health
curl https://app.barq.com

# Database health
gcloud sql instances describe barq-prod-db \
  --format="get(state)"
```

---

## Support

For deployment issues:
- **Email:** devops@barq.com
- **Slack:** #barq-devops
- **On-Call:** Use PagerDuty

---

**Last Updated:** December 2, 2025
**Maintained By:** BARQ DevOps Team
