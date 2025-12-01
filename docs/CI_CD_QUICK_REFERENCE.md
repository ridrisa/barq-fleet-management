# CI/CD Quick Reference

## 🚀 Quick Start

### Before Pushing Code

```bash
# Run all CI checks locally
./scripts/run-ci-checks.sh

# Auto-fix formatting issues
./scripts/fix-code-quality.sh
```

---

## 📋 Checklists

### Pre-Push Checklist

- [ ] Code formatted (Black, ESLint)
- [ ] Types checked (MyPy, TypeScript)
- [ ] Tests pass locally
- [ ] No linting errors
- [ ] Build succeeds
- [ ] Commit message follows convention

### Pre-Merge Checklist

- [ ] All CI checks pass ✅
- [ ] Code review approved
- [ ] No merge conflicts
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No security vulnerabilities

---

## 🎯 Common Commands

### Backend

```bash
# Format code
black app/
isort app/

# Lint
flake8 app/ --max-line-length=100

# Type check
mypy app/ --ignore-missing-imports

# Test
pytest app/tests/ -v --cov=app

# Coverage report
pytest app/tests/ --cov=app --cov-report=html
```

### Frontend

```bash
# Type check
npm run type-check

# Lint
npm run lint

# Fix lint issues
npm run lint -- --fix

# Test
npm run test:run

# Coverage
npm run test:coverage

# Build
npm run build
```

### Docker

```bash
# Build backend
docker build -t barq-backend ./backend

# Build frontend
docker build -f frontend/Dockerfile.prod -t barq-frontend ./frontend

# Test locally
docker-compose up -d
```

---

## 🔍 CI Pipeline Status

### Check CI Status

```bash
# GitHub CLI
gh pr checks

# View workflow runs
gh run list

# View specific run
gh run view RUN_ID
```

### Common CI Failures

| Error | Cause | Fix |
|-------|-------|-----|
| Black formatting | Code not formatted | Run `black app/` |
| TypeScript errors | Type issues | Run `npm run type-check` |
| Build failed | Syntax/config error | Check build logs |
| Tests failed | Test failures | Run tests locally |
| Lint errors | Code quality | Run linter locally |

---

## 🚢 Deployment

### Trigger Deployment

```bash
# Push to main (auto-deploy to staging)
git push origin main

# Tag for production
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Manual trigger (GitHub UI)
Actions → Deploy to Production → Run workflow
```

### Check Deployment Status

```bash
# Cloud Build
gcloud builds list --limit=5

# Cloud Run services
gcloud run services list

# Service details
gcloud run services describe barq-api-staging --region=us-central1
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service=barq-api-staging

# Rollback to previous
gcloud run services update-traffic barq-api-staging \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1
```

---

## 🐛 Troubleshooting

### CI Checks Failing

```bash
# 1. Run checks locally
./scripts/run-ci-checks.sh

# 2. Fix formatting
./scripts/fix-code-quality.sh

# 3. Check specific issue
cd backend && black --diff app/  # See what will change
cd frontend && npm run lint      # See lint errors

# 4. View CI logs
gh run view --log-failed
```

### Build Failing

```bash
# 1. Clean build
cd frontend
rm -rf node_modules dist
npm ci
npm run build

# 2. Check Docker build
docker build -t test ./backend
```

### Tests Failing

```bash
# 1. Run tests locally
cd backend && pytest app/tests/ -v

# 2. Run specific test
pytest app/tests/test_file.py::test_function -v

# 3. Debug mode
pytest app/tests/ -v -s --pdb
```

---

## 📊 Quality Metrics

### Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| Backend | 80% | TBD |
| Frontend | 80% | TBD |

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| CI Runtime | < 10 min | ~8 min |
| Build Time | < 5 min | ~3 min |
| Deploy Time | < 5 min | ~4 min |

---

## 🔐 Secrets Management

### Required Secrets

**GitHub Actions:**
- `GCP_PROJECT_ID`
- `GCP_SA_KEY`
- `CODECOV_TOKEN` (optional)

**Cloud Build:**
- `_DATABASE_URL`
- `_SECRET_KEY`

### Update Secrets

```bash
# GitHub (via UI)
Settings → Secrets and variables → Actions → New repository secret

# GCP Secret Manager
gcloud secrets create SECRET_NAME --data-file=./secret.txt

# Update Cloud Build trigger
gcloud builds triggers update TRIGGER_NAME \
  --substitutions=_SECRET_KEY='$(gcloud secrets versions access latest --secret="secret-key")'
```

---

## 📞 Help & Support

### Resources

- **Full Guide:** [CI_CD_GUIDE.md](./CI_CD_GUIDE.md)
- **Project README:** [README.md](../README.md)
- **GitHub Actions Docs:** https://docs.github.com/actions
- **Cloud Build Docs:** https://cloud.google.com/build/docs

### Common Issues

1. **CI failing on format:** Run `./scripts/fix-code-quality.sh`
2. **TypeScript errors:** Run `npm run type-check` locally
3. **Build timeout:** Check Cloud Build logs
4. **Deployment failed:** Check Cloud Run logs

### Get Help

```bash
# View CI logs
gh run view --log-failed

# View Cloud Build logs
gcloud builds log BUILD_ID

# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50
```

---

## 🎨 Code Quality Standards

### Python (Backend)

- **Formatter:** Black (line-length=100)
- **Import sort:** isort
- **Linter:** Flake8
- **Type checker:** MyPy
- **Test framework:** Pytest

### TypeScript (Frontend)

- **Compiler:** TypeScript 5.3+
- **Linter:** ESLint
- **Test framework:** Vitest
- **Build tool:** Vite

---

## 🔄 Workflow Tips

### Fast Feedback Loop

```bash
# 1. Make changes
vim backend/app/main.py

# 2. Quick local check
black app/main.py
pytest app/tests/test_main.py

# 3. Full CI check
./scripts/run-ci-checks.sh

# 4. Commit & push
git add .
git commit -m "feat: add new feature"
git push
```

### Parallel Development

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, commit
git add .
git commit -m "feat: implement feature"

# Push and create PR
git push origin feature/my-feature
gh pr create
```

### Emergency Hotfix

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-fix

# Fix, test, commit
git add .
git commit -m "fix: critical bug"

# Push and create PR (bypass some checks if needed)
git push origin hotfix/critical-fix
gh pr create --label "hotfix"
```

---

**Last Updated:** November 2024
**Quick Access:** Pin this file for easy reference!
