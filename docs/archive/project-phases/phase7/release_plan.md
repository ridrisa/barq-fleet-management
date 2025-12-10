# BARQ Fleet Management - Release Plan

**Created:** December 6, 2025
**Phase:** 7 - Handoff & Implementation Roadmap
**Version:** 1.0

---

## Release Strategy Overview

### Release Philosophy

```
┌─────────────────────────────────────────────────────────────┐
│                    RELEASE STRATEGY                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frequency:     Bi-weekly releases (every 2 weeks)           │
│  Approach:      Continuous delivery with feature flags       │
│  Environments:  Dev → Staging → Canary → Production          │
│  Rollback:      < 5 minutes via container image revert       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Version Numbering

**Semantic Versioning:** MAJOR.MINOR.PATCH

- **MAJOR:** Breaking API changes
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes, security patches

**Current Version:** 1.0.0
**Next Planned:** 1.1.0 (Q1 2026)

---

## Release Calendar

### Q1 2026

| Release | Date | Version | Focus |
|---------|------|---------|-------|
| R1 | Jan 13, 2026 | 1.1.0 | Security Hardening |
| R2 | Jan 27, 2026 | 1.2.0 | Dashboard Auth & API Consistency |
| R3 | Feb 10, 2026 | 1.3.0 | Legacy API Deprecation |
| R4 | Feb 24, 2026 | 1.4.0 | Accessibility Part 1 |
| R5 | Mar 10, 2026 | 1.5.0 | Accessibility Part 2 |
| R6 | Mar 24, 2026 | 1.6.0 | Mobile Responsiveness Part 1 |

### Q2 2026

| Release | Date | Version | Focus |
|---------|------|---------|-------|
| R7 | Apr 7, 2026 | 1.7.0 | Mobile Responsiveness Part 2 |
| R8 | Apr 21, 2026 | 1.8.0 | Performance Backend |
| R9 | May 5, 2026 | 1.9.0 | Performance Frontend |
| R10 | May 19, 2026 | 1.10.0 | Design System |
| R11 | Jun 2, 2026 | 2.0.0 | Major Release - Full Enhancement |
| R12 | Jun 16, 2026 | 2.0.1 | Stabilization & Polish |

---

## Release R1: Security Hardening

**Version:** 1.1.0
**Target Date:** January 13, 2026
**Sprint:** Sprint 1

### Scope

| Category | Items |
|----------|-------|
| Security | SQL injection fix, Token blacklist, JWT config |
| Auth | OAuth org context, Password reset hardening |
| Infrastructure | Health endpoint protection |

### Release Checklist

- [ ] All Sprint 1 stories completed
- [ ] Security scan passed (OWASP ZAP)
- [ ] Penetration test completed
- [ ] All tests green (unit, integration, E2E)
- [ ] Staging deployment verified
- [ ] Canary deployment (5% traffic)
- [ ] 24-hour canary observation
- [ ] Full production rollout
- [ ] Post-deployment monitoring

### Rollback Criteria

- Error rate > 1%
- P95 latency > 500ms
- Authentication failures spike
- Any security vulnerability detected

### Communication

| Audience | Channel | Timing |
|----------|---------|--------|
| Engineering | Slack #releases | Day of |
| Support | Email + Training | 1 day before |
| Customers | In-app notification | Day of |

---

## Release R2: Dashboard & API

**Version:** 1.2.0
**Target Date:** January 27, 2026
**Sprint:** Sprint 2 + Sprint 3

### Scope

| Category | Items |
|----------|-------|
| Dashboard | All 12 endpoints authenticated & org-filtered |
| API | HTTP method standardization, Pagination limits |
| Schemas | Vehicle/Courier stats typed, FMS alignment |
| Security | Security headers, CORS hardening |

### Breaking Changes

| Change | Migration Path |
|--------|---------------|
| Stats endpoints return typed objects | Update frontend type definitions |
| Pagination max 100 | Adjust client page sizes |
| PATCH for status updates | Update frontend API calls |

### Deprecation Notices

```
Warning: The following endpoints are deprecated and will be removed in R3:
- /api/fleet/* (use /api/v1/fleet/*)
- /api/operations/* (use /api/v1/operations/*)
- /api/hr/* (use /api/v1/hr/*)
```

---

## Release R3: Legacy API Removal

**Version:** 1.3.0
**Target Date:** February 10, 2026
**Sprint:** Sprint 4

### Scope

| Category | Items |
|----------|-------|
| Deprecation | Remove all legacy (non-v1) API endpoints |
| Cleanup | Delete legacy directories |
| Documentation | Update API docs to v1 only |

### Breaking Changes

| Change | Impact | Migration |
|--------|--------|-----------|
| Legacy endpoints removed | External integrations | Must use /api/v1/* |
| 410 Gone responses | Legacy consumers | Follow redirect in response |

### Pre-Release Validation

- [ ] Usage audit shows zero legacy traffic
- [ ] All known integrations migrated
- [ ] Support team trained on migration
- [ ] Customer notification sent 2 weeks prior

---

## Release R4-R5: Accessibility

**Version:** 1.4.0, 1.5.0
**Target Dates:** February 24, March 10, 2026
**Sprints:** Sprint 5, Sprint 6

### Scope

| Release | Focus Areas |
|---------|-------------|
| R4 | Skip links, Focus trap, Keyboard nav, ARIA labels |
| R5 | Date picker, Charts, Reduced motion, High contrast |

### Accessibility Certification

- [ ] Axe automated scan: 0 violations
- [ ] Manual keyboard testing: Pass
- [ ] Screen reader testing (NVDA, VoiceOver): Pass
- [ ] Color contrast verification: Pass
- [ ] WCAG 2.1 AA compliance checklist: Complete

---

## Release R6-R7: Mobile Responsiveness

**Version:** 1.6.0, 1.7.0
**Target Dates:** March 24, April 7, 2026
**Sprints:** Sprint 7, Sprint 8

### Scope

| Release | Focus Areas |
|---------|-------------|
| R6 | Table cards, Modal full-screen, Filter sheet, Touch targets |
| R7 | Map view, Forms, Navigation, Calendar |

### Device Testing Matrix

| Device | OS | Browser | Status |
|--------|-----|---------|--------|
| iPhone 12 | iOS 17 | Safari | Required |
| iPhone SE | iOS 17 | Safari | Required |
| Samsung S21 | Android 14 | Chrome | Required |
| iPad Air | iPadOS 17 | Safari | Required |

---

## Release R8-R9: Performance

**Version:** 1.8.0, 1.9.0
**Target Dates:** April 21, May 5, 2026
**Sprints:** Sprint 9, Sprint 10

### Performance Targets

| Metric | Current | Target | Release |
|--------|---------|--------|---------|
| API P95 Latency | 450ms | <200ms | R8 |
| Dashboard Load | 3.2s | <1.5s | R9 |
| Bundle Size | 4.8MB | <2MB | R9 |
| Lighthouse Score | 65 | >85 | R9 |

### Performance Budget

```yaml
# .lighthouserc.js
assert:
  first-contentful-paint: ['warn', {maxNumericValue: 1500}]
  speed-index: ['warn', {maxNumericValue: 3000}]
  largest-contentful-paint: ['error', {maxNumericValue: 2500}]
  total-blocking-time: ['error', {maxNumericValue: 300}]
  cumulative-layout-shift: ['error', {maxNumericValue: 0.1}]
```

---

## Release R10-R11: Design System & Major Release

**Version:** 1.10.0, 2.0.0
**Target Dates:** May 19, June 2, 2026
**Sprints:** Sprint 11, Sprint 12

### Version 2.0.0 Highlights

```
┌─────────────────────────────────────────────────────────────┐
│                    BARQ v2.0.0                               │
│              "The Enhancement Release"                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ Complete Security Hardening                               │
│  ✓ Full API Consistency                                      │
│  ✓ WCAG 2.1 AA Accessibility                                 │
│  ✓ Mobile-First Responsive Design                            │
│  ✓ 3x Performance Improvement                                │
│  ✓ Unified Design System                                     │
│  ✓ 85%+ Test Coverage                                        │
│  ✓ Interactive Onboarding                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Launch Plan

| Day | Activity |
|-----|----------|
| T-14 | Feature freeze |
| T-7 | Staging complete, UAT begins |
| T-3 | UAT sign-off, Release notes finalized |
| T-1 | Marketing materials ready |
| T-0 | Production deployment |
| T+1 | Monitor & respond |
| T+7 | Retrospective |

---

## Deployment Pipeline

### Environment Flow

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│   Dev   │───►│ Staging │───►│ Canary  │───►│  Prod   │
│         │    │         │    │  (5%)   │    │ (100%)  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
  Automated     Manual Gate    Automated      Manual Gate
   Deploy        + Tests         Deploy        (if stable)
```

### Deployment Commands

```bash
# Deploy to staging
gcloud run deploy barq-staging \
  --image gcr.io/barq-fleet/api:${VERSION} \
  --region me-central1

# Canary deployment (5%)
gcloud run services update-traffic barq-prod \
  --to-revisions barq-prod-${REVISION}=5

# Full production (after 24h observation)
gcloud run services update-traffic barq-prod \
  --to-revisions barq-prod-${REVISION}=100
```

### Rollback Procedure

```bash
# Immediate rollback
gcloud run services update-traffic barq-prod \
  --to-revisions barq-prod-${PREVIOUS_REVISION}=100

# Verify rollback
curl -s https://api.barq.sa/api/v1/health | jq .version
```

---

## Feature Flags

### Active Flags

| Flag | Description | Default | Rollout |
|------|-------------|---------|---------|
| `dashboard_v2` | New dashboard layout | false | Gradual |
| `dispatch_drag_drop` | Drag-drop dispatch | false | Beta users |
| `mobile_bottom_nav` | Bottom navigation | false | Mobile only |
| `onboarding_tour` | Interactive tour | false | New users |

### Flag Management

```typescript
// LaunchDarkly integration
const flags = {
  'dashboard_v2': {
    rollout: {
      percentage: 25,
      bucketBy: 'organization_id'
    }
  }
};
```

---

## Monitoring & Alerting

### Release Monitoring Dashboard

| Metric | Warning | Critical |
|--------|---------|----------|
| Error Rate | > 0.5% | > 1% |
| P95 Latency | > 300ms | > 500ms |
| CPU Usage | > 70% | > 85% |
| Memory Usage | > 75% | > 90% |
| Active Users | -10% | -20% |

### Alert Channels

| Severity | Channel | Response Time |
|----------|---------|---------------|
| Critical | PagerDuty + Slack | < 5 min |
| Warning | Slack #alerts | < 30 min |
| Info | Email digest | Next business day |

---

## Communication Plan

### Internal Communication

| Audience | When | What |
|----------|------|------|
| Engineering | T-3 | Release notes draft |
| QA | T-2 | Final test sign-off |
| Support | T-1 | Feature training |
| All Hands | T-0 | Release announcement |

### External Communication

| Audience | When | Channel |
|----------|------|---------|
| Beta Users | T-7 | Email preview |
| All Customers | T-0 | In-app notification |
| Public | T-0 | Blog post |
| Partners | T+1 | Partner newsletter |

### Release Notes Template

```markdown
# BARQ Fleet Management v1.x.0

## What's New

### 🔒 Security
- [Feature description]

### ✨ Features
- [Feature description]

### 🐛 Bug Fixes
- [Fix description]

### ⚡ Performance
- [Improvement description]

## Breaking Changes
- [Change and migration path]

## Deprecations
- [What's deprecated and timeline]

## Known Issues
- [Issue and workaround]
```

---

## Post-Release

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Adoption Rate | > 80% in 7 days | Analytics |
| Error Reports | < 5 critical | Support tickets |
| User Satisfaction | > 4.0/5.0 | In-app survey |
| Performance Maintained | No regression | Monitoring |

### Retrospective

After each major release:
- What went well?
- What could be improved?
- Action items for next release

---

## Appendix: Release Checklist Template

```markdown
## Release v1.x.0 Checklist

### Pre-Release (T-7 to T-1)
- [ ] All sprint stories completed
- [ ] Code freeze
- [ ] All tests passing
- [ ] Security scan clean
- [ ] Staging deployment verified
- [ ] UAT sign-off
- [ ] Release notes written
- [ ] Support team trained
- [ ] Rollback plan documented

### Release Day (T-0)
- [ ] Final staging verification
- [ ] Canary deployment
- [ ] Monitor canary (4h minimum)
- [ ] Production deployment
- [ ] Smoke tests pass
- [ ] Internal announcement
- [ ] Customer notification
- [ ] Monitor dashboards

### Post-Release (T+1 to T+7)
- [ ] 24h stability confirmed
- [ ] Support ticket review
- [ ] Performance comparison
- [ ] User feedback collected
- [ ] Retrospective scheduled
- [ ] Documentation finalized
```

---

*Document created as part of Phase 7 - Handoff & Implementation Roadmap*
