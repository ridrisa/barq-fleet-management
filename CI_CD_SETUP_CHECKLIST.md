# CI/CD Setup Checklist - BARQ Fleet Management

## ✅ Implementation Status

**Status:** All CI/CD components implemented and ready for activation

---

## 📋 Pre-Deployment Checklist

### 1. GitHub Repository Setup

- [ ] **Repository exists on GitHub**
  - Organization/User: `YOUR_ORG`
  - Repository name: `barq-fleet-clean`
  - Visibility: Private (recommended)

- [ ] **Branch protection rules configured**
  ```
  Settings → Branches → Add rule

  Branch name pattern: main
  ☑ Require a pull request before merging
  ☑ Require status checks to pass before merging
    - Select: ci-success
    - Select: backend-lint
    - Select: frontend-lint
    - Select: backend-build
    - Select: frontend-build
  ☑ Require conversation resolution before merging
  ☑ Include administrators
  ```

- [ ] **GitHub Secrets configured**
  ```
  Settings → Secrets and variables → Actions → New repository secret

  Required secrets:
  - GCP_PROJECT_ID: [your-gcp-project-id]
  - GCP_SA_KEY: [service-account-json-key]
  - CODECOV_TOKEN: [codecov-token] (optional)
  ```

### 2. Google Cloud Platform Setup

- [ ] **GCP Project created**
  - Project ID: `barq-fleet-production`
  - Billing account linked
  - Region: `us-central1`

- [ ] **Required APIs enabled**
  ```bash
  gcloud services enable cloudbuild.googleapis.com
  gcloud services enable run.googleapis.com
  gcloud services enable artifactregistry.googleapis.com
  gcloud services enable secretmanager.googleapis.com
  gcloud services enable cloudresourcemanager.googleapis.com
  ```

- [ ] **Artifact Registry repository created**
  ```bash
  gcloud artifacts repositories create barq-fleet \
    --repository-format=docker \
    --location=us-central1 \
    --description="BARQ Fleet container images"
  ```

- [ ] **Service account created and configured**
  ```bash
  # Create service account
  gcloud iam service-accounts create barq-cloudbuild \
    --description="Cloud Build service account for BARQ Fleet" \
    --display-name="BARQ Cloud Build"

  # Grant required roles
  gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:barq-cloudbuild@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

  gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:barq-cloudbuild@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

  gcloud projects add-iam-policy-binding PROJECT_ID \
    --member="serviceAccount:barq-cloudbuild@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

  # Create and download key
  gcloud iam service-accounts keys create key.json \
    --iam-account=barq-cloudbuild@PROJECT_ID.iam.gserviceaccount.com

  # Copy contents to GitHub Secret GCP_SA_KEY
  cat key.json
  ```

- [ ] **Cloud Build trigger created**
  ```bash
  gcloud builds triggers create github \
    --name="barq-fleet-main" \
    --repo-name=barq-fleet-clean \
    --repo-owner=YOUR_ORG \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --substitutions=_REGION=us-central1,_REPOSITORY=barq-fleet
  ```

- [ ] **Secrets stored in Secret Manager**
  ```bash
  # Database URL
  echo -n "postgresql://user:pass@host:5432/dbname" | \
    gcloud secrets create database-url --data-file=-

  # Secret key for JWT
  openssl rand -base64 32 | \
    gcloud secrets create jwt-secret-key --data-file=-

  # Grant access to Cloud Build service account
  gcloud secrets add-iam-policy-binding database-url \
    --member="serviceAccount:barq-cloudbuild@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

  gcloud secrets add-iam-policy-binding jwt-secret-key \
    --member="serviceAccount:barq-cloudbuild@PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
  ```

### 3. Database Setup

- [ ] **Cloud SQL instance created**
  ```bash
  gcloud sql instances create barq-fleet-db \
    --database-version=POSTGRES_16 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=[strong-password] \
    --backup \
    --backup-start-time=03:00
  ```

- [ ] **Database and user created**
  ```bash
  gcloud sql databases create barq_fleet \
    --instance=barq-fleet-db

  gcloud sql users create barq_user \
    --instance=barq-fleet-db \
    --password=[user-password]
  ```

- [ ] **Connection configured**
  - Cloud SQL Proxy configured
  - Or: Public IP with authorized networks
  - Connection string stored in Secret Manager

### 4. Local Development Setup

- [ ] **Dependencies installed**
  ```bash
  # Backend
  cd backend
  pip install -r requirements.txt -r requirements-dev.txt

  # Frontend
  cd frontend
  npm ci
  ```

- [ ] **Scripts are executable**
  ```bash
  chmod +x scripts/run-ci-checks.sh
  chmod +x scripts/fix-code-quality.sh
  chmod +x scripts/verify-ci-setup.sh
  ```

- [ ] **Local CI checks pass**
  ```bash
  ./scripts/run-ci-checks.sh
  ```

- [ ] **Docker Compose works**
  ```bash
  docker-compose up -d
  docker-compose ps
  docker-compose down
  ```

### 5. Testing the Pipeline

- [ ] **Create test branch**
  ```bash
  git checkout -b test/ci-pipeline
  ```

- [ ] **Make a small change**
  ```bash
  echo "# CI Test" >> README.md
  git add README.md
  git commit -m "test: verify CI pipeline"
  ```

- [ ] **Push and create PR**
  ```bash
  git push origin test/ci-pipeline
  gh pr create --title "test: CI pipeline verification" --body "Testing CI/CD setup"
  ```

- [ ] **Verify CI runs**
  - Check GitHub Actions tab
  - All jobs should run
  - All quality gates should execute

- [ ] **Merge to main (after CI passes)**
  ```bash
  gh pr merge --squash
  ```

- [ ] **Verify Cloud Build triggers**
  - Check Cloud Build console
  - Build should start automatically
  - Deployment to staging should complete

- [ ] **Verify Cloud Run deployment**
  ```bash
  gcloud run services list
  gcloud run services describe barq-api-staging --region=us-central1
  ```

- [ ] **Test deployed application**
  ```bash
  # Get URL
  SERVICE_URL=$(gcloud run services describe barq-api-staging \
    --region=us-central1 --format='value(status.url)')

  # Test health endpoint
  curl $SERVICE_URL/api/v1/health
  ```

---

## 🚀 Post-Deployment Checklist

### 1. Monitoring & Alerts

- [ ] **Cloud Monitoring dashboard created**
  - Service health metrics
  - Request latency
  - Error rates
  - Resource usage

- [ ] **Alert policies configured**
  - High error rate (>1%)
  - High latency (p95 >500ms)
  - Failed deployments
  - Resource exhaustion

- [ ] **Notification channels set up**
  - Email notifications
  - Slack integration (optional)
  - PagerDuty integration (optional)

### 2. Documentation

- [ ] **Update README badges with actual URLs**
  ```markdown
  Replace YOUR_ORG with actual organization name
  Replace placeholders with actual links
  ```

- [ ] **Team onboarding completed**
  - All team members have access
  - CI/CD guide reviewed
  - Local setup instructions followed

### 3. Production Readiness

- [ ] **Production environment configured**
  - Separate Cloud Run service
  - Production database
  - Production secrets

- [ ] **Manual approval gate added**
  ```yaml
  # In deploy-production.yml
  environment: production
    # Requires manual approval in GitHub
  ```

- [ ] **Rollback procedure tested**
  - Manual rollback tested
  - Automatic rollback verified
  - Recovery time measured

- [ ] **Disaster recovery plan documented**
  - Backup procedures
  - Restore procedures
  - Contact information

---

## 📊 Verification Commands

### Check All Components

```bash
# Run verification script
./scripts/verify-ci-setup.sh

# Expected output: All checks pass ✅
```

### Check GitHub Actions

```bash
# List workflow runs
gh run list

# View latest run
gh run view --log

# Check PR status
gh pr checks
```

### Check Cloud Build

```bash
# List recent builds
gcloud builds list --limit=10

# View build details
gcloud builds describe BUILD_ID

# View build logs
gcloud builds log BUILD_ID
```

### Check Cloud Run

```bash
# List services
gcloud run services list

# Get service details
gcloud run services describe SERVICE_NAME --region=us-central1

# List revisions
gcloud run revisions list --service=SERVICE_NAME

# Check logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

---

## 🎯 Success Criteria

All items below should be ✅ before considering setup complete:

- ✅ GitHub Actions CI runs on every PR
- ✅ All quality gates execute (lint, type-check, test, build)
- ✅ Security scanning runs (Trivy)
- ✅ Cloud Build triggers on main branch push
- ✅ Deployment to staging completes successfully
- ✅ Health checks pass
- ✅ Canary deployment works
- ✅ Rollback procedure tested
- ✅ Monitoring dashboards created
- ✅ Alert policies configured
- ✅ Team members onboarded
- ✅ Documentation complete

---

## 🆘 Troubleshooting

### GitHub Actions not running

1. Check workflow file syntax: `.github/workflows/ci.yml`
2. Verify branch protection rules
3. Check repository permissions
4. Review workflow run logs

### Cloud Build not triggering

1. Check trigger configuration in GCP Console
2. Verify service account permissions
3. Check Cloud Build API is enabled
4. Review trigger logs

### Deployment failures

1. Check Cloud Build logs
2. Verify secrets are accessible
3. Check Cloud Run quotas
4. Review service account roles

### Tests failing in CI

1. Run tests locally first
2. Check test database setup
3. Review environment variables
4. Check for missing dependencies

---

## 📞 Support Resources

- **CI/CD Guide:** `/docs/CI_CD_GUIDE.md`
- **Quick Reference:** `/docs/CI_CD_QUICK_REFERENCE.md`
- **Implementation Report:** `/CI_CD_IMPLEMENTATION_REPORT.md`
- **GitHub Actions Docs:** https://docs.github.com/actions
- **Cloud Build Docs:** https://cloud.google.com/build/docs
- **Cloud Run Docs:** https://cloud.google.com/run/docs

---

## ✅ Final Verification

Once all items are checked:

```bash
# 1. Verify CI/CD setup
./scripts/verify-ci-setup.sh

# 2. Run local checks
./scripts/run-ci-checks.sh

# 3. Create test PR
git checkout -b test/final-verification
echo "test" >> test.txt
git add test.txt
git commit -m "test: final CI/CD verification"
git push origin test/final-verification
gh pr create --title "test: final verification" --body "Final CI/CD test"

# 4. Watch CI run
gh pr checks --watch

# 5. Merge if all pass
gh pr merge --squash

# 6. Verify Cloud Build
gcloud builds list --limit=1

# 7. Check deployment
gcloud run services list
```

If all steps succeed: **🎉 CI/CD setup is complete and production-ready!**

---

**Checklist Last Updated:** November 2024
**Version:** 1.0
**Status:** Ready for deployment
