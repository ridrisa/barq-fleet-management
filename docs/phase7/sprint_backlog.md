# BARQ Fleet Management - Sprint Backlog

**Created:** December 6, 2025
**Phase:** 7 - Handoff & Implementation Roadmap
**Version:** 1.0

---

## Epic Overview

| Epic ID | Epic Name | Priority | Sprints | Story Points |
|---------|-----------|----------|---------|--------------|
| E1 | Security Hardening | P0 | 2 | 55 |
| E2 | API & Schema Consistency | P0 | 2 | 40 |
| E3 | Dashboard Authentication | P0 | 1 | 21 |
| E4 | Legacy API Deprecation | P1 | 2 | 34 |
| E5 | Accessibility Remediation | P1 | 2 | 42 |
| E6 | Mobile Responsiveness | P1 | 2 | 38 |
| E7 | Performance Optimization | P2 | 3 | 55 |
| E8 | Design System Implementation | P2 | 3 | 65 |
| E9 | Testing Infrastructure | P2 | 2 | 34 |
| E10 | Documentation & Onboarding | P3 | 2 | 28 |

**Total Story Points:** 412
**Sprint Velocity (estimated):** 35-40 points/sprint
**Sprints Required:** 11-12 (approx. 6 months)

---

## Sprint 1: Security Critical Fixes

**Duration:** 2 weeks
**Focus:** Address critical security vulnerabilities
**Total Points:** 34

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S1.1 | SQL Injection Fix in RLS Context | 8 | Backend | To Do |
| S1.2 | Token Blacklist Integration | 5 | Backend | To Do |
| S1.3 | JWT Expiration Configuration | 5 | Backend | To Do |
| S1.4 | Org ID Validation | 3 | Backend | To Do |
| S1.5 | Google OAuth Org Context | 5 | Backend | To Do |
| S1.6 | Password Reset Response Hardening | 5 | Backend | To Do |
| S1.7 | Health Endpoint Protection | 3 | Backend | To Do |

### Acceptance Criteria

**S1.1 - SQL Injection Fix**
- [ ] All `SET app.current_org_id` uses parameterized queries
- [ ] Unit tests verify SQL injection is prevented
- [ ] Security scan passes

**S1.2 - Token Blacklist**
- [ ] Logout invalidates token immediately
- [ ] Blacklisted tokens return 401
- [ ] Blacklist expires with token expiry

**S1.3 - JWT Expiration**
- [ ] Production tokens expire in 15 minutes
- [ ] Refresh token mechanism works
- [ ] Environment-aware configuration

---

## Sprint 2: Dashboard & Auth Completion

**Duration:** 2 weeks
**Focus:** Complete dashboard authentication and security
**Total Points:** 38

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S2.1 | Dashboard Stats Auth | 5 | Backend | To Do |
| S2.2 | Dashboard Charts Auth | 5 | Backend | To Do |
| S2.3 | Dashboard Alerts Auth | 3 | Backend | To Do |
| S2.4 | Dashboard Performance Auth | 5 | Backend | To Do |
| S2.5 | Dashboard Activity Auth | 3 | Backend | To Do |
| S2.6 | Dashboard Summary Auth | 3 | Backend | To Do |
| S2.7 | Org Filtering for All Endpoints | 8 | Backend | To Do |
| S2.8 | Security Headers Middleware | 3 | Backend | To Do |
| S2.9 | CORS Configuration Hardening | 3 | Backend | To Do |

### Acceptance Criteria

**S2.1-S2.6 - Dashboard Auth**
- [ ] All 12 dashboard endpoints require authentication
- [ ] Each endpoint filters by organization_id
- [ ] 401 returned for unauthenticated requests
- [ ] Integration tests cover all endpoints

**S2.7 - Org Filtering**
- [ ] Every query includes organization_id filter
- [ ] Cross-tenant data access impossible
- [ ] RLS policies verified

---

## Sprint 3: API Consistency

**Duration:** 2 weeks
**Focus:** Standardize API patterns and schemas
**Total Points:** 35

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S3.1 | HTTP Method Standardization | 5 | Backend | To Do |
| S3.2 | Pagination Limit Enforcement | 3 | Backend | To Do |
| S3.3 | Vehicle Stats Response Schema | 5 | Backend | To Do |
| S3.4 | Courier Stats Response Schema | 5 | Backend | To Do |
| S3.5 | FMS Schema Alignment | 5 | Backend | To Do |
| S3.6 | Salary Schema Fixes | 3 | Backend | To Do |
| S3.7 | Delivery Model Customer Fields | 5 | Backend | To Do |
| S3.8 | OpenAPI Documentation Update | 4 | Backend | To Do |

### Acceptance Criteria

**S3.1 - HTTP Methods**
- [ ] `/update-status` endpoints use PATCH
- [ ] All endpoints follow RESTful conventions
- [ ] Frontend updated for method changes

**S3.3-S3.4 - Stats Schemas**
- [ ] Typed Pydantic models for all stats
- [ ] Consistent field naming
- [ ] Full OpenAPI documentation

---

## Sprint 4: Legacy API Deprecation

**Duration:** 2 weeks
**Focus:** Remove legacy APIs safely
**Total Points:** 34

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S4.1 | Legacy API Usage Audit | 5 | Backend | To Do |
| S4.2 | 410 Gone Response Layer | 5 | Backend | To Do |
| S4.3 | Remove Legacy Fleet API | 3 | Backend | To Do |
| S4.4 | Remove Legacy Operations API | 3 | Backend | To Do |
| S4.5 | Remove Legacy HR API | 3 | Backend | To Do |
| S4.6 | Remove Legacy Accommodation API | 3 | Backend | To Do |
| S4.7 | Remove Legacy Analytics API | 3 | Backend | To Do |
| S4.8 | Remove Legacy Workflow/Tenant/FMS/Finance | 5 | Backend | To Do |
| S4.9 | Update API Router | 4 | Backend | To Do |

### Acceptance Criteria

**S4.1 - Usage Audit**
- [ ] All legacy endpoint usage documented
- [ ] Migration path for each consumer
- [ ] No external dependencies on legacy

**S4.3-S4.8 - API Removal**
- [ ] Directory deleted
- [ ] No import errors
- [ ] All tests pass
- [ ] OpenAPI docs updated

---

## Sprint 5: Accessibility Remediation (Part 1)

**Duration:** 2 weeks
**Focus:** Critical accessibility fixes
**Total Points:** 36

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S5.1 | Skip Navigation Links | 3 | Frontend | To Do |
| S5.2 | Modal Focus Trap | 5 | Frontend | To Do |
| S5.3 | Keyboard Navigation Sidebar | 5 | Frontend | To Do |
| S5.4 | Color Contrast Fixes | 5 | Frontend | To Do |
| S5.5 | ARIA Labels for Icons | 5 | Frontend | To Do |
| S5.6 | Form Error Announcements | 5 | Frontend | To Do |
| S5.7 | Table Screen Reader Support | 5 | Frontend | To Do |
| S5.8 | Focus Visible Styles | 3 | Frontend | To Do |

### Acceptance Criteria

**S5.2 - Modal Focus Trap**
- [ ] Focus moves to modal on open
- [ ] Tab cycles within modal
- [ ] Escape closes modal
- [ ] Focus returns to trigger

**S5.4 - Color Contrast**
- [ ] All text meets 4.5:1 ratio
- [ ] Interactive elements meet 3:1
- [ ] Tested with contrast checker

---

## Sprint 6: Accessibility Remediation (Part 2)

**Duration:** 2 weeks
**Focus:** Complete accessibility compliance
**Total Points:** 32

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S6.1 | Date Picker Accessibility | 5 | Frontend | To Do |
| S6.2 | Dropdown Menu Accessibility | 5 | Frontend | To Do |
| S6.3 | Toast Notification A11y | 3 | Frontend | To Do |
| S6.4 | Chart Accessibility | 5 | Frontend | To Do |
| S6.5 | Reduced Motion Support | 3 | Frontend | To Do |
| S6.6 | High Contrast Mode | 5 | Frontend | To Do |
| S6.7 | A11y Automated Testing | 3 | Frontend | To Do |
| S6.8 | Screen Reader Testing | 3 | QA | To Do |

---

## Sprint 7: Mobile Responsiveness (Part 1)

**Duration:** 2 weeks
**Focus:** Critical mobile fixes
**Total Points:** 36

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S7.1 | Table Mobile Card View | 8 | Frontend | To Do |
| S7.2 | Modal Full-Screen Mobile | 5 | Frontend | To Do |
| S7.3 | Filter Mobile Sheet | 5 | Frontend | To Do |
| S7.4 | Touch Target Sizes | 5 | Frontend | To Do |
| S7.5 | Dashboard Mobile Priority | 5 | Frontend | To Do |
| S7.6 | Sidebar Mobile Drawer | 5 | Frontend | To Do |
| S7.7 | Date Picker Mobile Sheet | 3 | Frontend | To Do |

---

## Sprint 8: Mobile Responsiveness (Part 2)

**Duration:** 2 weeks
**Focus:** Complete mobile experience
**Total Points:** 32

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S8.1 | Map Full-Screen Mobile | 5 | Frontend | To Do |
| S8.2 | Form Responsive Layout | 5 | Frontend | To Do |
| S8.3 | Navigation Mobile Bottom Bar | 5 | Frontend | To Do |
| S8.4 | Breadcrumb Mobile | 3 | Frontend | To Do |
| S8.5 | Timeline Mobile View | 5 | Frontend | To Do |
| S8.6 | Calendar Mobile View | 5 | Frontend | To Do |
| S8.7 | Mobile Device Testing | 4 | QA | To Do |

---

## Sprint 9: Performance Optimization (Part 1)

**Duration:** 2 weeks
**Focus:** Backend performance
**Total Points:** 35

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S9.1 | Redis Caching Layer | 8 | Backend | To Do |
| S9.2 | Query Optimization (N+1) | 8 | Backend | To Do |
| S9.3 | Database Index Review | 5 | Backend | To Do |
| S9.4 | Response Compression | 3 | Backend | To Do |
| S9.5 | Connection Pool Tuning | 3 | Backend | To Do |
| S9.6 | API Response Time Monitoring | 5 | Backend | To Do |
| S9.7 | Load Testing Setup | 3 | Backend | To Do |

---

## Sprint 10: Performance Optimization (Part 2)

**Duration:** 2 weeks
**Focus:** Frontend performance
**Total Points:** 38

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S10.1 | Bundle Splitting | 8 | Frontend | To Do |
| S10.2 | Lazy Loading Routes | 5 | Frontend | To Do |
| S10.3 | Image Optimization | 5 | Frontend | To Do |
| S10.4 | Virtual Scrolling Tables | 8 | Frontend | To Do |
| S10.5 | API Response Caching | 5 | Frontend | To Do |
| S10.6 | Service Worker | 4 | Frontend | To Do |
| S10.7 | Lighthouse CI | 3 | Frontend | To Do |

---

## Sprint 11: Design System Implementation

**Duration:** 2 weeks
**Focus:** Component library
**Total Points:** 35

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S11.1 | CSS Custom Properties | 5 | Frontend | To Do |
| S11.2 | Button Component Variants | 5 | Frontend | To Do |
| S11.3 | Input Component States | 5 | Frontend | To Do |
| S11.4 | Card Component | 3 | Frontend | To Do |
| S11.5 | Table Component | 8 | Frontend | To Do |
| S11.6 | Modal Component | 5 | Frontend | To Do |
| S11.7 | Storybook Setup | 4 | Frontend | To Do |

---

## Sprint 12: Testing & Documentation

**Duration:** 2 weeks
**Focus:** Quality assurance and docs
**Total Points:** 36

### Stories

| ID | Story | Points | Assignee | Status |
|----|-------|--------|----------|--------|
| S12.1 | Unit Test Coverage 85% | 8 | Full Stack | To Do |
| S12.2 | Integration Test Suite | 8 | Full Stack | To Do |
| S12.3 | E2E Critical Paths | 5 | QA | To Do |
| S12.4 | API Documentation Update | 5 | Backend | To Do |
| S12.5 | User Guide Creation | 5 | Tech Writer | To Do |
| S12.6 | Onboarding Tour | 5 | Frontend | To Do |

---

## Dependency Map

```
Sprint 1 (Security) ────┬──► Sprint 2 (Dashboard)
                        │
                        └──► Sprint 3 (API) ───► Sprint 4 (Legacy)

Sprint 5 (A11y Part 1) ───► Sprint 6 (A11y Part 2)

Sprint 7 (Mobile Part 1) ───► Sprint 8 (Mobile Part 2)

Sprint 9 (Perf Backend) ┬──► Sprint 10 (Perf Frontend)
                        │
                        └──► Sprint 12 (Testing)

Sprint 11 (Design System) ──────────────────────►
```

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Security fixes break existing features | High | Medium | Comprehensive test coverage before changes |
| Legacy API removal affects unknown consumers | High | Low | Extended deprecation period with logging |
| Performance changes cause regressions | Medium | Medium | A/B testing, gradual rollout |
| Accessibility changes affect UX | Low | Low | User testing with assistive tech users |

---

## Definition of Done

- [ ] Code reviewed and approved
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] E2E tests passing (if applicable)
- [ ] Accessibility audit passed
- [ ] Performance baseline maintained
- [ ] Documentation updated
- [ ] Deployed to staging
- [ ] QA approved
- [ ] Product owner accepted

---

*Document created as part of Phase 7 - Handoff & Implementation Roadmap*
