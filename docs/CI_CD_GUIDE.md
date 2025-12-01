# CI/CD Pipeline Guide - BARQ Fleet Management

## Overview

This document describes the complete CI/CD pipeline implementation for BARQ Fleet Management, including automated testing, quality gates, and deployment to Google Cloud Platform.

## Table of Contents

1. [Architecture](#architecture)
2. [GitHub Actions CI Pipeline](#github-actions-ci-pipeline)
3. [Google Cloud Build](#google-cloud-build)
4. [Quality Gates](#quality-gates)
5. [Deployment Strategy](#deployment-strategy)
6. [Local Development](#local-development)
7. [Troubleshooting](#troubleshooting)

---

## Architecture

### CI/CD Flow

```
┌─────────────┐
│  Git Push   │
│  /PR Create │
└──────┬──────┘
       │
       ├──────────────────────────┬────────────────────────┐
       │                          │                        │
       ▼                          ▼                        ▼
┌──────────────┐          ┌──────────────┐        ┌─────────────┐
│  GitHub      │          │  Code        │        │  Security   │
│  Actions CI  │          │  Quality     │        │  Scanning   │
└──────┬───────┘          └──────┬───────┘        └──────┬──────┘
       │                          │                       │
       │ ✅ All Checks Pass       │                       │
       └──────────────┬───────────┴───────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  Cloud Build  │
              │  (on main)    │
              └───────┬───────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌──────────┐
    │ Build   │ │ Test    │ │ Deploy   │
    │ Images  │ │ Images  │ │ Staging  │
    └─────────┘ └─────────┘ └────┬─────┘
                                  │
                            ┌─────┴─────┐
                            │  Canary   │
                            │  25%      │
                            └─────┬─────┘
                                  │
                            ┌─────┴─────┐
                            │  Monitor  │
                            │  5 min    │
                            └─────┬─────┘
                                  │
                            ┌─────┴─────┐
                            │  Deploy   │
                            │  100%     │
                            └───────────┘
```

---

## GitHub Actions CI Pipeline

### Workflows

#### 1. Main CI Pipeline (`.github/workflows/ci.yml`)

**Triggers:**
- Pull requests to `main` or `develop`
- Pushes to `main` or `develop`

**Jobs:**

##### Backend Jobs
- **backend-lint**: Code quality checks
  - Black formatting
  - isort import sorting
  - Flake8 linting
  - MyPy type checking
  - Pylint static analysis

- **backend-test**: Test execution
  - PostgreSQL test database setup
  - Database migrations
  - Pytest with coverage
  - Coverage upload to Codecov

- **backend-build**: Build verification
  - FastAPI app loading
  - Dependency installation

##### Frontend Jobs
- **frontend-lint**: Code quality
  - TypeScript compilation
  - ESLint

- **frontend-test**: Test execution
  - Unit tests (Vitest)
  - Coverage reporting

- **frontend-build**: Production build
  - Vite build
  - Build artifact upload

##### Security & Docker
- **security-scan**: Vulnerability scanning
  - Trivy security scanner
  - SARIF upload to GitHub Security

- **docker-build**: Container verification
  - Docker buildx setup
  - Multi-platform builds
  - Build caching

##### Summary
- **ci-success**: Overall status
  - Checks all job results
  - Reports overall CI status

### Example CI Run Output

```
✅ backend-lint        ✓ Passed in 1m 23s
✅ backend-test        ✓ Passed in 2m 45s
✅ backend-build       ✓ Passed in 1m 12s
✅ frontend-lint       ✓ Passed in 45s
✅ frontend-test       ⚠ Passed in 38s (no tests configured)
✅ frontend-build      ✓ Passed in 1m 56s
✅ security-scan       ✓ Passed in 2m 10s
✅ docker-build        ✓ Passed in 3m 22s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ CI Pipeline Success ✓ All checks passed
```

#### 2. PR Checks (`.github/workflows/pr-checks.yml`)

**Additional PR validation:**
- PR title format (conventional commits)
- Merge conflict detection
- Large file checks (>5MB blocked)
- Code statistics
- Dependency security audit
- Auto-labeling
- PR comment with statistics

#### 3. Production Deployment (`.github/workflows/deploy-production.yml`)

**Triggers:**
- Push to `main` branch
- Git tags (v*.*.*)
- Manual workflow dispatch

**Features:**
- GCP authentication
- Cloud Build trigger
- Deployment verification
- GitHub release creation

---

## Google Cloud Build

### Configuration (`cloudbuild.yaml`)

#### Build Steps

1. **Install Dependencies** (Parallel)
   - Frontend: npm ci
   - Backend: pip install

2. **Code Quality Checks** (Parallel)
   - Frontend: lint, type-check
   - Backend: black, isort, flake8

3. **Run Tests** (Parallel)
   - Frontend: unit tests
   - Backend: pytest with coverage

4. **Build Artifacts**
   - Frontend: Vite production build
   - Backend: Verify FastAPI app

5. **Build Docker Images**
   - Backend: Python 3.11 slim
   - Frontend: Nginx alpine

6. **Security Scanning**
   - Trivy vulnerability scan
   - CRITICAL/HIGH severity check

7. **Push Images**
   - Artifact Registry upload
   - Tag: SHA + latest

8. **Deploy to Cloud Run**
   - Staging deployment
   - No traffic initially
   - Health check ready

9. **Smoke Tests**
   - Backend health endpoint
   - Frontend root endpoint

10. **Canary Deployment**
    - 25% traffic shift
    - Monitor for 5 minutes
    - Error rate check

11. **Full Deployment**
    - 100% traffic shift
    - Deployment summary

### Substitutions

```yaml
_REGION: us-central1
_REPOSITORY: barq-fleet
_SERVICE_BACKEND: barq-api
_SERVICE_FRONTEND: barq-web
_DATABASE_URL: (from Secret Manager)
_SECRET_KEY: (from Secret Manager)
```

### Example Cloud Build Run

```
Step 1: Install Dependencies ━━━━━━━━━━━━━━━ ✓ 45s
Step 2: Code Quality Checks ━━━━━━━━━━━━━━━ ✓ 1m 23s
Step 3: Run Tests ━━━━━━━━━━━━━━━━━━━━━━━━━ ✓ 2m 10s
Step 4: Build Frontend ━━━━━━━━━━━━━━━━━━━━ ✓ 1m 45s
Step 5: Build Backend Image ━━━━━━━━━━━━━━━ ✓ 2m 30s
Step 6: Build Frontend Image ━━━━━━━━━━━━━━ ✓ 1m 20s
Step 7: Security Scan ━━━━━━━━━━━━━━━━━━━━━ ✓ 1m 15s
Step 8: Push Images ━━━━━━━━━━━━━━━━━━━━━━━ ✓ 45s
Step 9: Deploy Staging ━━━━━━━━━━━━━━━━━━━━ ✓ 1m 30s
Step 10: Smoke Tests ━━━━━━━━━━━━━━━━━━━━━━ ✓ 30s
Step 11: Canary 25% ━━━━━━━━━━━━━━━━━━━━━━━ ✓ 10s
Step 12: Monitor ━━━━━━━━━━━━━━━━━━━━━━━━━━ ✓ 5m 00s
Step 13: Full Deploy ━━━━━━━━━━━━━━━━━━━━━━ ✓ 15s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Deployment Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backend:  https://barq-api-staging---us-central1.run.app
Frontend: https://barq-web-staging---us-central1.run.app
Image:    abc1234
Status:   ✅ SUCCESS
Duration: 18m 23s
```

---

## Quality Gates

### Backend Quality Gates

#### 1. Code Formatting
```bash
# Black (100 char line length)
black --check --diff app/

# isort (import sorting)
isort --check-only --diff app/
```

**Enforcement:** CI fails if not formatted

#### 2. Linting
```bash
# Flake8
flake8 app/ --max-line-length=100 \
  --exclude=*/migrations/*,*/venv/* \
  --ignore=E203,W503
```

**Max Warnings:** 0

#### 3. Type Checking
```bash
# MyPy
mypy app/ --ignore-missing-imports
```

**Status:** Advisory (warnings logged)

#### 4. Testing
```bash
# Pytest with coverage
pytest app/tests/ -v \
  --cov=app \
  --cov-report=xml \
  --cov-report=term-missing
```

**Coverage Target:** 80% (goal)
**Current:** TBD (tests in development)

### Frontend Quality Gates

#### 1. TypeScript Compilation
```bash
npm run type-check
```

**Enforcement:** CI fails on type errors

#### 2. Linting
```bash
npm run lint
```

**Max Warnings:** 0

#### 3. Build
```bash
npm run build
```

**Enforcement:** Must succeed

#### 4. Testing
```bash
npm run test:coverage
```

**Coverage Target:** 80%

### Docker Quality Gates

#### 1. Security Scanning
- **Tool:** Trivy
- **Severity:** CRITICAL, HIGH
- **Action:** Block on CRITICAL vulnerabilities

#### 2. Image Size
- **Backend:** < 500MB
- **Frontend:** < 100MB (nginx + static files)

---

## Deployment Strategy

### Environments

| Environment | Branch | Auto-Deploy | URL Pattern |
|-------------|--------|-------------|-------------|
| Development | `develop` | ✓ | `*-dev-*.run.app` |
| Staging | `main` | ✓ | `*-staging-*.run.app` |
| Production | `main` + approval | Manual | `*-prod-*.run.app` |

### Canary Deployment Process

1. **Deploy with no traffic**
   - New revision created
   - Tagged with git SHA
   - No user traffic

2. **Shift 25% traffic**
   - Gradual rollout
   - Monitor metrics

3. **Monitor period (5 minutes)**
   - Error rate check
   - Latency monitoring
   - Log analysis

4. **Rollback or proceed**
   - If errors > threshold: Rollback
   - If healthy: Continue

5. **Full traffic (100%)**
   - Complete deployment
   - Old revision kept for quick rollback

### Rollback Procedure

**Automatic rollback triggers:**
- Error rate > 1% during canary
- Health check failures
- Deployment timeout

**Manual rollback:**
```bash
# Via gcloud CLI
gcloud run services update-traffic barq-api-staging \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1

# Via Console
# Cloud Run > Service > Revisions > Manage Traffic
```

---

## Local Development

### Pre-commit Checks

Run all CI checks locally before pushing:

```bash
./scripts/run-ci-checks.sh
```

**Output:**
```
🔍 Running Local CI Checks
======================================

📦 Backend Checks
==================
1. Black formatting... ✓
2. isort imports... ✓
3. Flake8 linting... ✓
4. MyPy type checking... ⚠
5. Tests... ✓

🎨 Frontend Checks
==================
1. TypeScript compilation... ✓
2. ESLint... ✓
3. Build... ✓
4. Tests... ⚠

======================================
✅ All checks passed!
Safe to push to repository
```

### Auto-fix Issues

Automatically fix formatting issues:

```bash
./scripts/fix-code-quality.sh
```

**Fixes:**
- Backend: Black, isort
- Frontend: ESLint --fix

### Manual Checks

#### Backend
```bash
cd backend

# Format code
black app/
isort app/

# Lint
flake8 app/ --max-line-length=100

# Type check
mypy app/ --ignore-missing-imports

# Test
pytest app/tests/ -v --cov=app
```

#### Frontend
```bash
cd frontend

# Type check
npm run type-check

# Lint
npm run lint

# Fix
npm run lint -- --fix

# Test
npm run test:run

# Coverage
npm run test:coverage

# Build
npm run build
```

---

## Troubleshooting

### Common Issues

#### 1. CI Failing on Formatting

**Error:**
```
would reformat app/main.py
1 file would be reformatted
```

**Fix:**
```bash
./scripts/fix-code-quality.sh
# or manually
cd backend && black app/
```

#### 2. TypeScript Errors

**Error:**
```
error TS2339: Property 'foo' does not exist on type 'Bar'
```

**Fix:**
- Fix type definitions
- Run `npm run type-check` locally first

#### 3. Build Failures

**Error:**
```
npm run build failed
```

**Debug:**
```bash
cd frontend
rm -rf node_modules dist
npm ci
npm run build
```

#### 4. Docker Build Fails

**Error:**
```
failed to solve with frontend dockerfile.v0
```

**Fix:**
- Check Dockerfile syntax
- Verify base image availability
- Check Docker buildx version

#### 5. Cloud Build Timeout

**Error:**
```
build timeout exceeded (1800s)
```

**Fix:**
- Optimize build steps
- Use build caching
- Increase timeout in `cloudbuild.yaml`

#### 6. Deployment Health Check Fails

**Error:**
```
Cloud Run health check failed
```

**Debug:**
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit=50 \
  --format=json

# Test locally
docker run -p 8000:8000 IMAGE_NAME
curl http://localhost:8000/api/v1/health
```

### CI Environment Variables

#### GitHub Actions Secrets

Required secrets:
```
GCP_PROJECT_ID      # Google Cloud project ID
GCP_SA_KEY          # Service account JSON key
CODECOV_TOKEN       # Codecov upload token (optional)
```

#### Cloud Build Substitutions

Configure in Cloud Build trigger:
```
_REGION             # GCP region (us-central1)
_DATABASE_URL       # PostgreSQL connection string
_SECRET_KEY         # JWT secret key
_REPOSITORY         # Artifact Registry repository
```

### Performance Optimization

#### Speed up CI

1. **Use caching:**
   - npm: `cache: 'npm'`
   - pip: `cache: 'pip'`
   - Docker: `cache-from: type=gha`

2. **Parallelize jobs:**
   - Run backend/frontend independently
   - Use `waitFor: ['-']` in Cloud Build

3. **Optimize Docker builds:**
   - Multi-stage builds
   - Layer caching
   - Minimal base images

#### Reduce costs

1. **Use appropriate machine types:**
   - CI: `ubuntu-latest` (default)
   - Cloud Build: `E2_HIGHCPU_8`

2. **Minimize build time:**
   - Skip unnecessary steps
   - Use `paths-ignore` for docs

3. **Clean up artifacts:**
   - Retention: 7 days
   - Auto-delete old images

---

## Monitoring & Alerts

### CI Monitoring

**Metrics tracked:**
- Build success rate
- Average build time
- Test pass rate
- Coverage trends

**Alerts:**
- Build failures (immediate)
- Coverage drop >5%
- Security vulnerabilities

### Deployment Monitoring

**Cloud Run metrics:**
- Request count
- Latency (p50, p95, p99)
- Error rate
- CPU/Memory usage

**Alerting policies:**
- Error rate > 1%
- p95 latency > 500ms
- CPU > 80%
- Memory > 80%

---

## Best Practices

### Commit Messages

Follow conventional commits:
```
feat: add user authentication
fix: resolve database connection timeout
docs: update CI/CD guide
style: format code with black
refactor: simplify error handling
test: add unit tests for auth service
chore: update dependencies
```

### Pull Requests

1. **Keep PRs small:** < 500 lines changed
2. **Run local checks:** `./scripts/run-ci-checks.sh`
3. **Write clear descriptions**
4. **Link to issues:** Closes #123
5. **Wait for CI:** Don't merge on red

### Branching Strategy

```
main        # Production-ready
  ├── develop    # Integration branch
  │   ├── feature/user-auth
  │   ├── fix/database-timeout
  │   └── refactor/api-structure
  └── hotfix/critical-bug
```

### Code Review

**Required checks before merge:**
- ✅ All CI jobs pass
- ✅ Code review approved (1+ reviewer)
- ✅ No merge conflicts
- ✅ Coverage maintained
- ✅ Docs updated (if needed)

---

## Reference

### File Locations

```
.github/
  ├── workflows/
  │   ├── ci.yml                  # Main CI pipeline
  │   ├── pr-checks.yml           # PR validation
  │   └── deploy-production.yml   # Production deployment
  └── labeler.yml                 # Auto-labeling rules

scripts/
  ├── run-ci-checks.sh            # Local CI runner
  └── fix-code-quality.sh         # Auto-fix script

cloudbuild.yaml                    # Cloud Build config

frontend/
  ├── Dockerfile.prod              # Production Dockerfile
  └── nginx.conf                   # Nginx configuration

backend/
  ├── Dockerfile                   # Backend Dockerfile
  ├── pytest.ini                   # Pytest config
  └── pyproject.toml               # Python tools config
```

### Useful Commands

```bash
# GitHub CLI
gh pr checks                      # Check PR status
gh workflow run ci.yml            # Manually trigger workflow

# gcloud
gcloud builds list                # List builds
gcloud builds log BUILD_ID        # View build logs
gcloud run services list          # List Cloud Run services
gcloud run revisions list         # List revisions

# Docker
docker build -t test .            # Build locally
docker run -p 8000:8000 test     # Run locally
```

---

## Support

For CI/CD issues:
1. Check this guide
2. Review CI logs
3. Run local checks
4. Contact DevOps team

**Last Updated:** November 2024
**Version:** 1.0
**Maintained by:** DevOps Team
