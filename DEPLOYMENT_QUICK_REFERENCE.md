# Deployment Quick Reference Card

## 🚀 Quick Commands

### Deploy to Staging (Automatic)
```bash
git push origin main
# ✅ Auto-deploys to staging via GitHub Actions
```

### Deploy to Production (Manual)
```bash
# Option 1: Via GitHub Actions (Recommended)
# 1. Go to: https://github.com/barq-fleet/barq-fleet-clean/actions
# 2. Select "Continuous Deployment"
# 3. Click "Run workflow" → Select "production"
# 4. Approve when prompted

# Option 2: Via Script
cd scripts/deployment
./deploy-production.sh
```

### Emergency Rollback
```bash
cd scripts/deployment
./rollback-production.sh
# Time: 1-2 minutes ⏱️
```

### Verify Deployment
```bash
cd scripts/deployment
./verify-deployment.sh [staging|production]
```

---

## 📊 Health Check Endpoints

```bash
# Liveness (is app running?)
curl https://api.barq-fleet.com/health/live

# Readiness (ready for traffic?)
curl https://api.barq-fleet.com/health/ready

# Detailed (full system status)
curl https://api.barq-fleet.com/health/detailed | jq
```

---

## 🔍 Monitoring

### Dashboards
- **Main**: Cloud Console → Monitoring → Dashboards → "BARQ Fleet Management - Main"
- **Deployments**: "BARQ - Deployments & Revisions"

### Logs
```bash
# Real-time logs
gcloud logging tail "resource.type=cloud_run_revision"

# Errors only
gcloud logging tail "resource.type=cloud_run_revision AND severity>=ERROR"

# Specific service
gcloud logging tail "resource.labels.service_name=barq-api-production"
```

### Traffic Distribution
```bash
gcloud run services describe barq-api-production \
  --region us-central1 \
  --format 'table(status.traffic.revisionName,status.traffic.percent)'
```

---

## ⚠️ Emergency Procedures

### Service Down (P0)
```bash
# 1. Check status
gcloud run services describe barq-api-production --region us-central1

# 2. Check recent deployments
gcloud run revisions list --service barq-api-production --region us-central1 --limit 5

# 3. Rollback immediately
./scripts/deployment/rollback-production.sh

# 4. Notify team
# - Slack: #incident-channel
# - PagerDuty: Alert on-call
```

### High Error Rate (P1)
```bash
# 1. Check error logs
gcloud logging read "severity>=ERROR" --limit 20

# 2. Assess if rollback needed
./scripts/deployment/verify-deployment.sh production

# 3. Rollback if errors persist
./scripts/deployment/rollback-production.sh
```

### Performance Degradation (P2)
```bash
# 1. Check metrics
# Go to Monitoring Dashboard

# 2. Check database
gcloud sql instances describe barq-production-db

# 3. Scale up if needed (temporary)
gcloud run services update barq-api-production \
  --cpu 8 --memory 8Gi --region us-central1
```

---

## 📋 Canary Deployment Timeline

| Time | Phase | Traffic | Action | Rollback If |
|------|-------|---------|--------|-------------|
| 0 min | Deploy | 0% | Deploy new revision | Smoke test fails |
| 2 min | Canary 1 | 10% | Monitor errors | > 5 errors in 5 min |
| 7 min | Canary 2 | 50% | Monitor errors | > 10 errors in 5 min |
| 12 min | Full | 100% | Final verification | Health check fails |

**Total time**: ~15-20 minutes

---

## 🎯 Performance Targets

| Action | Target | Actual |
|--------|--------|--------|
| Staging Deploy | < 3 min | ⏱️ |
| Production Deploy | < 20 min | ⏱️ |
| Rollback | < 5 min | ⏱️ |
| Health Check | < 100ms | ⏱️ |

---

## 🔐 Required Secrets

### GitHub Secrets
```
GCP_PROJECT_ID
GCP_SA_KEY
```

### Secret Manager (GCP)
```
staging-database-url
staging-secret-key
production-database-url
production-secret-key
```

---

## 🛠️ Troubleshooting

### "Permission denied"
```bash
# Re-authenticate
gcloud auth login
gcloud config set project barq-fleet
```

### "Service not found"
```bash
# List services
gcloud run services list --region us-central1

# Check if deployed
gcloud run revisions list --service barq-api-production --region us-central1
```

### "Image not found"
```bash
# Check images
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/barq-fleet/barq-artifacts/barq-api

# Trigger build via GitHub Actions
```

### "Health check failed"
```bash
# Check logs
gcloud logging read "severity>=ERROR" --limit 10

# Check database connection
gcloud sql instances describe barq-production-db
```

---

## 📞 Escalation

| Level | Contact | Response Time |
|-------|---------|---------------|
| L1 | DevOps On-Call | 5 min |
| L2 | Tech Lead | 15 min |
| L3 | CTO | 30 min |

**Slack**: `#devops-alerts`
**PagerDuty**: https://barq-fleet.pagerduty.com

---

## 📚 Documentation

- **Full Guide**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)
- **Rollback**: [docs/ROLLBACK_PROCEDURES.md](docs/ROLLBACK_PROCEDURES.md)
- **Scripts**: [scripts/deployment/README.md](scripts/deployment/README.md)
- **Summary**: [CD_IMPLEMENTATION_SUMMARY.md](CD_IMPLEMENTATION_SUMMARY.md)

---

## ✅ Pre-Deployment Checklist

- [ ] Staging deployment successful
- [ ] All tests passing
- [ ] Health checks green
- [ ] Recent errors reviewed
- [ ] Team notified
- [ ] Backup plan ready
- [ ] On-call engineer available

---

## 🚦 Deployment Status Colors

- 🟢 **Green**: All systems operational
- 🟡 **Yellow**: Minor issues, monitoring
- 🔴 **Red**: Critical issues, rollback needed
- ⚪ **Gray**: Deployment in progress

---

**Quick Start**: Push to `main` → Auto-deploys to staging → Verify → Deploy to production (manual approval)

**Emergency**: `./scripts/deployment/rollback-production.sh` (< 5 min)

**Questions**: Check [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) or ask in `#devops`
