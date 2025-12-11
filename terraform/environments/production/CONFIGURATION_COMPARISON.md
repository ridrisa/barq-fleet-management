# Staging vs Production Configuration Comparison

This document outlines the key differences between staging and production environments to ensure proper configuration and understanding of resource allocation.

## Infrastructure Comparison

| Component | Staging | Production | Rationale |
|-----------|---------|------------|-----------|
| **Environment** | staging | production | Logical separation |
| **Region** | us-central1 | me-central1 | Production closer to Saudi Arabia |
| **CIDR Range** | 10.10.0.0/16 | 10.20.0.0/16 | Network isolation |

## Cloud Run - Backend API

| Configuration | Staging | Production | Change Reason |
|---------------|---------|------------|---------------|
| **Service Name** | barq-api-staging | barq-api-production | Environment separation |
| **Min Instances** | 1 | 2 | High availability, zero-downtime |
| **Max Instances** | 10 | 50 | Handle production load (1000+ users) |
| **CPU** | 2000m (2 vCPU) | 4000m (4 vCPU) | Better performance, faster response |
| **Memory** | 2Gi | 4Gi | Handle larger datasets, more connections |
| **Concurrency** | 80 | 100 | Optimize for production throughput |
| **CPU Throttling** | Default (yes) | Disabled (false) | Always-on performance |
| **Container Image** | barq-api:staging | barq-api:production | Environment-specific builds |

**Impact**:
- Production handles 5x more traffic
- 50% faster response times with more CPU
- Zero downtime with 2+ instances always running
- No CPU throttling ensures consistent performance

## Cloud Run - Frontend Web

| Configuration | Staging | Production | Change Reason |
|---------------|---------|------------|---------------|
| **Service Name** | barq-web-staging | barq-web-production | Environment separation |
| **Min Instances** | 1 | 2 | High availability |
| **Max Instances** | 10 | 20 | Production user load |
| **CPU** | 1000m (1 vCPU) | 2000m (2 vCPU) | Better static serving |
| **Memory** | 512Mi | 1Gi | Larger cache, better performance |
| **Concurrency** | 100 | 200 | More simultaneous connections |
| **Container Image** | barq-web:staging | barq-web:production | Environment-specific builds |

**Impact**:
- 2x capacity for frontend
- Faster initial page loads
- Better handling of peak traffic

## Cloud SQL Database

| Configuration | Staging | Production | Change Reason |
|---------------|---------|------------|---------------|
| **Instance Name** | barq-staging-db | barq-production-db | Environment separation |
| **Database Name** | barq_staging | barq_production | Environment separation |
| **Version** | PostgreSQL 16 | PostgreSQL 16 | Same version |
| **Tier** | db-f1-micro | db-custom-4-15360 | 4 vCPU, 15GB RAM for production |
| **Availability** | ZONAL | REGIONAL | Automatic failover, 99.95% SLA |
| **Disk Size** | 10 GB | 50 GB | More data capacity |
| **Disk Type** | PD_SSD | PD_SSD | Same performance tier |
| **Auto-resize** | No | Yes (up to 500GB) | Automatic growth |
| **Max Connections** | 100 | 500 | Support 1000+ concurrent users |
| **Backup Retention** | 7 days | 30 days | Longer compliance window |
| **PITR Logs** | 3 days | 7 days | Point-in-time recovery |
| **Deletion Protection** | Disabled | Enabled | Prevent accidental deletion |
| **Logging** | Basic | Enhanced (connections, locks, checkpoints) | Better troubleshooting |
| **Insights** | Disabled | Enabled | Query performance monitoring |
| **Maintenance Window** | Random | Sunday 3 AM | Controlled downtime |

**Impact**:
- 99.95% availability with automatic failover
- 5x more connections
- 5x more storage
- Enhanced monitoring and logging
- Protected from accidental deletion

## VPC & Networking

| Configuration | Staging | Production | Change Reason |
|---------------|---------|------------|---------------|
| **VPC Connector** | barq-staging-connector | barq-production-connector | Environment separation |
| **Min Throughput** | 200 Mbps | 300 Mbps | Higher baseline |
| **Max Throughput** | 300 Mbps | 1000 Mbps | Handle peak traffic |
| **CIDR Range** | 10.10.0.0/16 | 10.20.0.0/16 | Network isolation |
| **Service Account (API)** | barq-api-staging | barq-api-production | Environment separation |
| **Service Account (Web)** | N/A (staging has one SA) | barq-web-production | Separate permissions |

**Impact**:
- 3x more network capacity
- Isolated networks prevent cross-environment access
- Dedicated service accounts per service

## Secret Manager

| Secret | Staging | Production | Difference |
|--------|---------|------------|------------|
| **Database URL** | staging-database-url | barq-database-url-prod | Naming convention |
| **Secret Key** | staging-secret-key | barq-secret-key-prod | Naming convention |
| **Google Client ID** | N/A | barq-google-client-id | Production-specific |
| **Google Client Secret** | N/A | barq-google-client-secret | Production-specific |
| **Sentry DSN** | N/A | barq-sentry-dsn-prod | Production-specific |
| **Redis AUTH** | N/A | barq-redis-auth-prod | Production-specific |

**Impact**:
- Completely separate credentials
- More secrets in production for integrations
- Better secret organization

## Monitoring & Alerting

| Configuration | Staging | Production | Difference |
|---------------|---------|------------|------------|
| **Environment Tag** | staging | production | Metric filtering |
| **Slack Channel** | #staging-alerts | #production-alerts | Team notification |
| **Alert Thresholds** | Relaxed | Strict | Production SLA |
| **Uptime Checks** | Basic | Comprehensive | Multi-region checks |
| **Log Retention** | 30 days | 90 days | Compliance requirements |
| **Dashboard** | Basic | Detailed | More metrics tracked |

**Impact**:
- Stricter monitoring in production
- Separate alert channels
- Longer log retention for compliance

## Security & Access Control

| Feature | Staging | Production | Difference |
|---------|---------|------------|------------|
| **Public Access** | Enabled (allUsers) | Enabled (allUsers) | Same (application handles auth) |
| **Cloud Armor** | Not configured | Configured (rate limiting) | DDoS protection |
| **Rate Limiting** | None | 1000 req/min per IP | Abuse prevention |
| **Ban Duration** | N/A | 300 seconds (5 min) | Temporary IP blocks |
| **Deletion Protection** | Disabled | Enabled | Prevent data loss |
| **Audit Logging** | Basic | Enhanced | Compliance tracking |
| **SSL/TLS** | Required | Required | Same security |

**Impact**:
- Cloud Armor protects production from attacks
- Rate limiting prevents abuse
- Deletion protection prevents accidents

## Cost Comparison

### Monthly Costs (Estimated)

| Resource | Staging Cost | Production Cost | Multiplier |
|----------|--------------|-----------------|------------|
| Cloud Run API | $20-50 | $150-800 | 7.5x-16x |
| Cloud Run Web | $10-20 | $50-200 | 5x-10x |
| Cloud SQL | $25-35 | $400-500 | 14x-16x |
| VPC Connector | $15-20 | $30-100 | 2x-5x |
| Secret Manager | $1-2 | $1-5 | Same-2.5x |
| Monitoring | $5-10 | $10-20 | 2x |
| Cloud Armor | $0 | $5 | N/A |
| **Total** | **$75-140** | **$650-1,630** | **8.6x-11.6x** |

**Why the difference?**
- Production has 10x more capacity
- High availability (REGIONAL database, min 2 instances)
- More network throughput
- Enhanced monitoring and logging
- Additional security features

## Environment Variables Comparison

### Backend API Environment Variables

| Variable | Staging | Production | Notes |
|----------|---------|------------|-------|
| `ENVIRONMENT` | staging | production | Environment identifier |
| `PORT` | 8000 | 8000 | Same port |
| `PYTHON_ENV` | production | production | Both use production mode |
| `LOG_LEVEL` | DEBUG (typically) | INFO | Less verbose in production |
| `DATABASE_URL` | From staging secret | From production secret | Separate databases |
| `SECRET_KEY` | From staging secret | From production secret | Separate keys |
| `DB_CONNECTION_NAME` | barq-staging-db | barq-production-db | Different instances |
| `GOOGLE_CLIENT_ID` | Not set | From secret | OAuth only in production |
| `GOOGLE_CLIENT_SECRET` | Not set | From secret | OAuth only in production |
| `SENTRY_DSN` | Not set or staging DSN | From secret | Separate Sentry projects |
| `BACKEND_CORS_ORIGINS` | Staging URLs | Production domains | Different allowed origins |

### Frontend Web Environment Variables

| Variable | Staging | Production | Notes |
|----------|---------|------------|-------|
| `VITE_API_URL` | Staging Cloud Run URL | Production Cloud Run URL or custom domain | Points to different backends |
| `VITE_ENVIRONMENT` | staging | production | Environment identifier |
| `VITE_GOOGLE_CLIENT_ID` | Not set | From variable | OAuth in production |

## Deployment Process Differences

| Step | Staging | Production | Difference |
|------|---------|------------|------------|
| **Trigger** | Push to `develop` branch | Tag with version (e.g., v1.0.0) | Manual production releases |
| **Approval** | Automatic | Manual approval required | Production requires sign-off |
| **Testing** | Basic smoke tests | Full test suite + manual QA | More thorough testing |
| **Deployment Strategy** | Replace all at once | Canary/Blue-Green | Gradual rollout |
| **Rollback** | Simple redeploy | Multi-step process | More careful in production |
| **Monitoring** | 1 hour post-deploy | 24 hours post-deploy | Extended monitoring |

## State Management

| Configuration | Staging | Production | Notes |
|---------------|---------|------------|-------|
| **Backend Type** | GCS | GCS | Both use Cloud Storage |
| **Bucket** | barq-fleet-terraform-state | barq-fleet-terraform-state | Same bucket |
| **Prefix** | staging | production | Different state files |
| **Locking** | Enabled | Enabled | Prevent concurrent changes |
| **Versioning** | Enabled | Enabled | State history |
| **Encryption** | Enabled (default) | Enabled (default) | At-rest encryption |

## Disaster Recovery

| Aspect | Staging | Production | Difference |
|--------|---------|------------|------------|
| **RTO (Recovery Time)** | 4 hours | 1 hour | Faster production recovery |
| **RPO (Recovery Point)** | 24 hours | 5 minutes | Less data loss in production |
| **Backup Frequency** | Daily | Continuous (PITR) | Production has point-in-time recovery |
| **Backup Retention** | 7 days | 30 days | Longer retention |
| **Failover** | Manual | Automatic | Cloud SQL HA failover |
| **DR Testing** | Monthly | Weekly | More frequent production testing |

## Migration Path: Staging → Production

When promoting changes from staging to production:

### 1. Code Changes
```bash
# Tested in staging
git checkout develop
git push origin develop
# Automatic deployment to staging

# After verification, merge to main
git checkout main
git merge develop
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0
# Manual deployment to production
```

### 2. Infrastructure Changes
```bash
# Test in staging first
cd terraform/environments/staging
terraform plan
terraform apply

# After verification, apply to production
cd ../production
terraform plan  # Review carefully!
terraform apply  # Requires approval
```

### 3. Database Migrations
```bash
# Run in staging
gcloud sql connect barq-staging-db --user=barq_app_user
# Run migrations

# After verification, run in production
gcloud sql connect barq-production-db --user=barq_app_user
# Run same migrations

# OR use automated migration on deployment
# (migrations run automatically on container startup)
```

## Configuration Files Summary

### Staging Files
```
terraform/environments/staging/
├── main.tf                    # Infrastructure definition
├── variables.tf               # Variable definitions
└── outputs.tf                 # Output values
```

### Production Files
```
terraform/environments/production/
├── main.tf                    # Infrastructure definition
├── variables.tf               # Variable definitions
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example configuration
├── README.md                  # Production documentation
├── DEPLOYMENT_GUIDE.md        # Step-by-step deployment
├── CONFIGURATION_COMPARISON.md # This file
└── validate.sh                # Pre-deployment validation
```

## Key Takeaways

### High Availability
- **Staging**: Single-zone, can tolerate brief downtime
- **Production**: Multi-zone, automatic failover, 99.95% SLA

### Performance
- **Staging**: Adequate for testing, may be slower
- **Production**: Optimized for speed, 2-4x more resources

### Cost
- **Staging**: ~$100/month, cost-optimized
- **Production**: ~$1,200/month, performance-optimized

### Security
- **Staging**: Basic security, relaxed policies
- **Production**: Enhanced security, strict policies, Cloud Armor

### Monitoring
- **Staging**: Basic monitoring, relaxed alerts
- **Production**: Comprehensive monitoring, strict SLA alerts

### Data Protection
- **Staging**: Weekly backups, can tolerate data loss
- **Production**: Continuous backups, minimal data loss tolerance

## Recommendations

### Before Going to Production
1. ✅ Test all features thoroughly in staging
2. ✅ Verify disaster recovery procedures
3. ✅ Load test with expected production traffic
4. ✅ Security audit and penetration testing
5. ✅ Document all processes and runbooks
6. ✅ Train team on production procedures
7. ✅ Set up proper alerting and on-call rotation
8. ✅ Configure budget alerts
9. ✅ Review and optimize costs
10. ✅ Obtain sign-off from stakeholders

### After Production Deployment
1. ✅ Monitor closely for first 24 hours
2. ✅ Verify all integrations working
3. ✅ Test disaster recovery in production
4. ✅ Review and adjust auto-scaling
5. ✅ Optimize database queries
6. ✅ Set up regular maintenance windows
7. ✅ Document lessons learned
8. ✅ Update team documentation

---

**Last Updated**: December 11, 2025
**Version**: 1.0
**Maintained By**: Infrastructure Team
