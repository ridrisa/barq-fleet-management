# BARQ Fleet Management - Master Task List

**Created:** December 6, 2025
**Source:** Phase 1-7 Enhancement Audit
**Total Tasks:** 187
**Estimated Duration:** 6 months (12 sprints)

---

## Task Priority Legend

| Priority | Meaning | Timeline |
|----------|---------|----------|
| 🔴 P0 | Critical - Security/Breaking | Sprint 1-2 |
| 🟠 P1 | High - Core functionality | Sprint 3-6 |
| 🟡 P2 | Medium - Enhancement | Sprint 7-10 |
| 🟢 P3 | Low - Polish/Nice-to-have | Sprint 11-12 |

---

## Category 1: Security Hardening (32 tasks)

### 1.1 Critical Security Fixes 🔴 P0

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 1 | Fix SQL injection in RLS context - use parameterized queries | `app/core/dependencies.py` | 4h |
| 2 | Fix SQL injection in database.py SET statement | `app/core/database.py` | 2h |
| 3 | Implement token blacklist check in get_current_user | `app/core/dependencies.py` | 4h |
| 4 | Create token_blacklist utility module | `app/core/token_blacklist.py` | 3h |
| 5 | Add org_id to Google OAuth token creation | `app/api/v1/auth.py` | 2h |
| 6 | Add org_role to Google OAuth token creation | `app/api/v1/auth.py` | 1h |
| 7 | Configure environment-aware JWT expiration (15m prod, 60m dev) | `app/config/settings.py` | 2h |
| 8 | Enable JWT audience verification | `app/core/dependencies.py` | 2h |
| 9 | Add org_id validation (must be positive integer) | `app/core/dependencies.py` | 2h |
| 10 | Remove reset_token from password reset response | `app/schemas/admin/` | 1h |
| 11 | Remove temporary_password from admin reset response | `app/api/v1/admin/user_enhancements.py` | 2h |

### 1.2 Health Endpoint Protection 🔴 P0

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 12 | Secure /health/detailed endpoint with auth | `app/api/v1/health.py` | 2h |
| 13 | Remove sensitive info from public health endpoint | `app/api/v1/health.py` | 1h |

### 1.3 Security Headers & CORS 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 14 | Add SecurityHeadersMiddleware | `app/core/middleware.py` | 4h |
| 15 | Configure X-Content-Type-Options header | `app/core/middleware.py` | 0.5h |
| 16 | Configure X-Frame-Options header | `app/core/middleware.py` | 0.5h |
| 17 | Configure X-XSS-Protection header | `app/core/middleware.py` | 0.5h |
| 18 | Configure Strict-Transport-Security header | `app/core/middleware.py` | 0.5h |
| 19 | Configure Content-Security-Policy header | `app/core/middleware.py` | 2h |
| 20 | Restrict CORS to specific origins (not *) | `app/main.py` | 2h |
| 21 | Configure CORS credentials handling | `app/main.py` | 1h |

### 1.4 Secure Password Reset 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 22 | Create PasswordResetToken model | `app/models/password_reset_token.py` | 3h |
| 23 | Create password reset token migration | `alembic/versions/` | 1h |
| 24 | Implement token hash storage (not plaintext) | `app/services/auth/` | 3h |
| 25 | Add token expiration enforcement | `app/services/auth/` | 2h |
| 26 | Add token used flag to prevent reuse | `app/services/auth/` | 1h |
| 27 | Send reset token via email only | `app/services/notification/` | 2h |

### 1.5 Rate Limiting & Protection 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 28 | Implement rate limiting for login endpoint | `app/api/v1/auth.py` | 4h |
| 29 | Implement rate limiting for password reset | `app/api/v1/auth.py` | 2h |
| 30 | Add brute force protection | `app/core/security.py` | 4h |
| 31 | Implement account lockout after failed attempts | `app/services/auth/` | 3h |
| 32 | Add audit logging for security events | `app/core/audit.py` | 4h |

---

## Category 2: Dashboard Authentication (14 tasks)

### 2.1 Dashboard Endpoint Auth 🔴 P0

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 33 | Add auth dependency to /dashboard/stats | `app/api/v1/dashboard.py` | 1h |
| 34 | Add auth dependency to /dashboard/charts/deliveries | `app/api/v1/dashboard.py` | 1h |
| 35 | Add auth dependency to /dashboard/charts/revenue | `app/api/v1/dashboard.py` | 1h |
| 36 | Add auth dependency to /dashboard/charts/fleet | `app/api/v1/dashboard.py` | 1h |
| 37 | Add auth dependency to /dashboard/charts/couriers | `app/api/v1/dashboard.py` | 1h |
| 38 | Add auth dependency to /dashboard/alerts | `app/api/v1/dashboard.py` | 1h |
| 39 | Add auth dependency to /dashboard/performance/top-couriers | `app/api/v1/dashboard.py` | 1h |
| 40 | Add auth dependency to /dashboard/recent-activity | `app/api/v1/dashboard.py` | 1h |
| 41 | Add auth dependency to /dashboard/summary | `app/api/v1/dashboard.py` | 1h |

### 2.2 Dashboard Org Filtering 🔴 P0

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 42 | Add organization_id filter to stats queries | `app/api/v1/dashboard.py` | 2h |
| 43 | Add organization_id filter to chart queries | `app/api/v1/dashboard.py` | 2h |
| 44 | Add organization_id filter to alerts query | `app/api/v1/dashboard.py` | 1h |
| 45 | Add organization_id filter to performance queries | `app/api/v1/dashboard.py` | 1h |
| 46 | Write integration tests for dashboard auth | `tests/integration/api/` | 4h |

---

## Category 3: API Consistency (22 tasks)

### 3.1 HTTP Method Standardization 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 47 | Change vehicle /update-status to PATCH method | `app/api/v1/fleet/vehicles.py` | 2h |
| 48 | Change courier /update-status to PATCH method | `app/api/v1/fleet/couriers.py` | 2h |
| 49 | Update frontend API calls for PATCH methods | `frontend/src/lib/api.ts` | 2h |
| 50 | Update OpenAPI documentation for method changes | `app/api/v1/` | 1h |

### 3.2 Pagination Limits 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 51 | Change all pagination limits from le=1000 to le=100 | `app/api/v1/**/*.py` | 3h |
| 52 | Update frontend default page sizes | `frontend/src/lib/api.ts` | 1h |
| 53 | Add pagination metadata to all list responses | `app/schemas/common/` | 2h |

### 3.3 Response Schema Typing 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 54 | Create VehicleStatisticsResponse schema | `app/schemas/fleet/vehicle.py` | 2h |
| 55 | Create CourierStatisticsResponse schema | `app/schemas/fleet/courier.py` | 2h |
| 56 | Create DashboardStatsResponse schema | `app/schemas/analytics/dashboard.py` | 3h |
| 57 | Create DeliveryMetricsResponse schema | `app/schemas/operations/` | 2h |
| 58 | Update stats endpoints to use typed schemas | `app/api/v1/**/*.py` | 4h |

### 3.4 Schema Alignment 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 59 | Add fms_asset_id, fms_tracking_unit_id to vehicle schema | `app/schemas/fleet/vehicle.py` | 1h |
| 60 | Add fms_asset_id, fms_driver_id to courier schema | `app/schemas/fleet/courier.py` | 1h |
| 61 | Fix fms_last_sync type to datetime | `app/schemas/fleet/*.py` | 1h |
| 62 | Fix payment_date type in salary schema | `app/schemas/hr/salary.py` | 1h |
| 63 | Add customer_name, customer_phone to delivery model | `app/models/operations/delivery.py` | 2h |
| 64 | Create migration for delivery customer fields | `alembic/versions/` | 1h |
| 65 | Fix created_at types in COD and delivery schemas | `app/schemas/operations/` | 1h |
| 66 | Ensure all datetime fields use consistent formatting | `app/schemas/**/*.py` | 3h |
| 67 | Validate all schemas match SQLAlchemy models | All schema files | 4h |
| 68 | Update OpenAPI docs with correct types | `app/api/v1/` | 2h |

---

## Category 4: Legacy API Removal (12 tasks)

### 4.1 Legacy API Audit 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 69 | Audit legacy /api/fleet usage in codebase | All files | 2h |
| 70 | Audit legacy /api/operations usage | All files | 2h |
| 71 | Audit legacy /api/hr usage | All files | 2h |
| 72 | Audit external integrations using legacy APIs | Documentation | 4h |
| 73 | Create migration guide for legacy consumers | `docs/` | 4h |

### 4.2 Deprecation Layer 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 74 | Create 410 Gone response handler for legacy routes | `app/api/` | 3h |
| 75 | Add deprecation headers to legacy endpoints | `app/api/` | 2h |
| 76 | Log legacy endpoint usage for monitoring | `app/core/logging.py` | 2h |

### 4.3 Legacy Removal 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 77 | Remove app/api/fleet directory | `app/api/fleet/` | 1h |
| 78 | Remove app/api/operations directory | `app/api/operations/` | 1h |
| 79 | Remove app/api/hr directory | `app/api/hr/` | 1h |
| 80 | Remove remaining legacy directories (accommodation, analytics, workflow, tenant, fms, finance) | `app/api/` | 2h |

---

## Category 5: Accessibility (42 tasks)

### 5.1 Critical A11y Fixes 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 81 | Add skip navigation link to main layout | `frontend/src/layouts/MainLayout.tsx` | 2h |
| 82 | Implement focus trap for all modals | `frontend/src/components/ui/Modal.tsx` | 4h |
| 83 | Add keyboard close (Escape) to all modals | `frontend/src/components/ui/Modal.tsx` | 2h |
| 84 | Return focus to trigger after modal close | `frontend/src/components/ui/Modal.tsx` | 2h |
| 85 | Add keyboard navigation to sidebar | `frontend/src/components/layout/Sidebar.tsx` | 4h |
| 86 | Implement arrow key navigation in dropdowns | `frontend/src/components/ui/Dropdown.tsx` | 4h |

### 5.2 Color & Contrast 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 87 | Update primary amber to meet 4.5:1 contrast | `frontend/src/styles/` | 2h |
| 88 | Add accessible dark alternative for amber | `frontend/src/styles/` | 1h |
| 89 | Fix placeholder text contrast ratio | `frontend/src/components/ui/Input.tsx` | 1h |
| 90 | Fix disabled state contrast ratios | `frontend/src/components/ui/*.tsx` | 2h |
| 91 | Add color-blind safe alternatives for status colors | `frontend/src/styles/` | 3h |

### 5.3 ARIA Labels & Roles 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 92 | Add aria-label to all icon-only buttons | `frontend/src/components/**/*.tsx` | 4h |
| 93 | Add aria-describedby for form errors | `frontend/src/components/ui/Input.tsx` | 2h |
| 94 | Add role="alert" to error messages | `frontend/src/components/ui/Alert.tsx` | 1h |
| 95 | Add aria-live regions for dynamic content | `frontend/src/components/` | 3h |
| 96 | Add proper roles to navigation elements | `frontend/src/components/layout/` | 2h |
| 97 | Add aria-expanded to accordions/dropdowns | `frontend/src/components/ui/` | 2h |

### 5.4 Form Accessibility 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 98 | Associate all labels with form inputs (htmlFor) | `frontend/src/components/ui/Input.tsx` | 2h |
| 99 | Add required indicator to required fields | `frontend/src/components/ui/Input.tsx` | 1h |
| 100 | Add aria-required to required inputs | `frontend/src/components/ui/Input.tsx` | 1h |
| 101 | Announce form errors to screen readers | `frontend/src/hooks/useForm.ts` | 3h |
| 102 | Add inline validation error messages | `frontend/src/components/ui/Input.tsx` | 2h |

### 5.5 Table Accessibility 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 103 | Add proper table headers with scope | `frontend/src/components/ui/Table.tsx` | 2h |
| 104 | Add caption to all data tables | `frontend/src/components/ui/Table.tsx` | 1h |
| 105 | Make sortable columns keyboard accessible | `frontend/src/components/ui/Table.tsx` | 3h |
| 106 | Add aria-sort to sorted columns | `frontend/src/components/ui/Table.tsx` | 1h |
| 107 | Make row selection keyboard accessible | `frontend/src/components/ui/Table.tsx` | 2h |

### 5.6 Component A11y 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 108 | Make date picker fully keyboard accessible | `frontend/src/components/ui/DatePicker.tsx` | 4h |
| 109 | Add screen reader support to charts | `frontend/src/components/charts/` | 4h |
| 110 | Make toast notifications accessible | `frontend/src/components/ui/Toast.tsx` | 2h |
| 111 | Add progress indicator announcements | `frontend/src/components/ui/Progress.tsx` | 2h |
| 112 | Make tabs keyboard navigable (arrow keys) | `frontend/src/components/ui/Tabs.tsx` | 3h |

### 5.7 Motion & Preferences 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 113 | Add prefers-reduced-motion support | `frontend/src/styles/animations.css` | 2h |
| 114 | Implement high contrast mode | `frontend/src/styles/` | 4h |
| 115 | Add dark mode support | `frontend/src/styles/` | 8h |

### 5.8 Testing & Validation 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 116 | Set up Axe automated a11y testing | `frontend/e2e/` | 3h |
| 117 | Create a11y test suite for all pages | `frontend/e2e/accessibility/` | 4h |
| 118 | Test with NVDA screen reader | Manual testing | 4h |
| 119 | Test with VoiceOver | Manual testing | 4h |
| 120 | Create a11y testing checklist | `docs/` | 2h |
| 121 | Document keyboard shortcuts | `docs/` | 2h |
| 122 | Fix all Axe violations to 0 | All components | 8h |

---

## Category 6: Mobile Responsiveness (24 tasks)

### 6.1 Critical Mobile Fixes 🟠 P1

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 123 | Implement card view for tables on mobile | `frontend/src/components/ui/Table.tsx` | 8h |
| 124 | Make modals full-screen on mobile | `frontend/src/components/ui/Modal.tsx` | 3h |
| 125 | Create filter bottom sheet for mobile | `frontend/src/components/ui/FilterSheet.tsx` | 6h |
| 126 | Increase touch targets to 44x44px minimum | `frontend/src/components/ui/*.tsx` | 4h |
| 127 | Fix sidebar as mobile drawer | `frontend/src/components/layout/Sidebar.tsx` | 4h |

### 6.2 Component Responsiveness 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 128 | Create bottom sheet date picker for mobile | `frontend/src/components/ui/DatePicker.tsx` | 4h |
| 129 | Implement full-screen map on mobile | `frontend/src/components/map/` | 4h |
| 130 | Make forms 1-column on mobile | `frontend/src/components/forms/` | 4h |
| 131 | Add mobile breadcrumb navigation | `frontend/src/components/layout/Breadcrumb.tsx` | 2h |
| 132 | Create mobile timeline view | `frontend/src/components/ui/Timeline.tsx` | 4h |
| 133 | Make calendar mobile-friendly | `frontend/src/components/ui/Calendar.tsx` | 4h |

### 6.3 Dashboard Mobile 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 134 | Implement priority widget view on mobile | `frontend/src/pages/dashboard/` | 4h |
| 135 | Add expandable sections for widgets | `frontend/src/pages/dashboard/` | 3h |
| 136 | Optimize charts for mobile viewport | `frontend/src/components/charts/` | 4h |

### 6.4 Navigation Mobile 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 137 | Implement bottom navigation bar | `frontend/src/components/layout/BottomNav.tsx` | 6h |
| 138 | Add hamburger menu functionality | `frontend/src/components/layout/Header.tsx` | 2h |
| 139 | Optimize header for mobile | `frontend/src/components/layout/Header.tsx` | 2h |

### 6.5 Testing 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 140 | Test on iPhone 12 Safari | Manual testing | 4h |
| 141 | Test on iPhone SE Safari | Manual testing | 4h |
| 142 | Test on Samsung S21 Chrome | Manual testing | 4h |
| 143 | Test on iPad Air Safari | Manual testing | 4h |
| 144 | Add responsive E2E tests | `frontend/e2e/` | 4h |
| 145 | Test portrait and landscape orientations | Manual testing | 2h |
| 146 | Test on slow 3G connection | Manual testing | 2h |

---

## Category 7: Performance Optimization (28 tasks)

### 7.1 Backend Performance 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 147 | Implement Redis caching layer | `app/core/cache.py` | 8h |
| 148 | Cache dashboard stats (5 min TTL) | `app/api/v1/dashboard.py` | 4h |
| 149 | Cache vehicle/courier lists | `app/api/v1/fleet/` | 4h |
| 150 | Fix N+1 queries with eager loading | `app/services/**/*.py` | 8h |
| 151 | Add database query logging for profiling | `app/core/database.py` | 2h |
| 152 | Review and add missing database indexes | `alembic/versions/` | 4h |
| 153 | Implement response compression | `app/main.py` | 2h |
| 154 | Tune database connection pool | `app/core/database.py` | 2h |
| 155 | Add query result pagination | `app/services/**/*.py` | 4h |

### 7.2 Frontend Performance 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 156 | Split monolithic api.ts into modules | `frontend/src/lib/api/` | 8h |
| 157 | Implement code splitting per route | `frontend/src/router/` | 4h |
| 158 | Add lazy loading for routes | `frontend/src/router/` | 3h |
| 159 | Implement virtual scrolling for large tables | `frontend/src/components/ui/Table.tsx` | 8h |
| 160 | Optimize image loading (lazy, srcset) | `frontend/src/components/` | 4h |
| 161 | Add TanStack Query caching configuration | `frontend/src/lib/queryClient.ts` | 3h |
| 162 | Implement service worker for offline | `frontend/public/sw.js` | 6h |
| 163 | Tree shake unused dependencies | `frontend/vite.config.ts` | 2h |
| 164 | Analyze and reduce bundle size | `frontend/` | 4h |

### 7.3 Monitoring 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 165 | Set up API response time monitoring | `app/core/middleware.py` | 4h |
| 166 | Implement Lighthouse CI | `.github/workflows/` | 3h |
| 167 | Add performance budgets | `frontend/` | 2h |
| 168 | Set up k6 load testing | `tests/load/` | 4h |
| 169 | Create performance dashboard | Grafana/similar | 4h |

### 7.4 Targets 🟡 P2

| # | Task | Target | Current |
|---|------|--------|---------|
| 170 | Achieve P95 latency < 200ms | 200ms | 450ms |
| 171 | Achieve dashboard load < 1.5s | 1.5s | 3.2s |
| 172 | Reduce bundle size to < 2MB | 2MB | 4.8MB |
| 173 | Achieve Lighthouse score > 85 | 85 | 65 |
| 174 | Achieve Core Web Vitals pass | Pass | Fail |

---

## Category 8: Design System (18 tasks)

### 8.1 Foundation 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 175 | Create CSS custom properties file | `frontend/src/styles/variables.css` | 4h |
| 176 | Implement color tokens | `frontend/src/styles/colors.css` | 2h |
| 177 | Implement typography scale | `frontend/src/styles/typography.css` | 2h |
| 178 | Implement spacing scale | `frontend/src/styles/spacing.css` | 2h |
| 179 | Implement shadow tokens | `frontend/src/styles/shadows.css` | 1h |
| 180 | Implement border radius tokens | `frontend/src/styles/borders.css` | 1h |

### 8.2 Components 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 181 | Standardize Button component variants | `frontend/src/components/ui/Button.tsx` | 4h |
| 182 | Standardize Input component states | `frontend/src/components/ui/Input.tsx` | 4h |
| 183 | Create Card component with header/body/footer | `frontend/src/components/ui/Card.tsx` | 3h |
| 184 | Create consistent Table component | `frontend/src/components/ui/Table.tsx` | 6h |
| 185 | Create Modal component with standard layout | `frontend/src/components/ui/Modal.tsx` | 4h |
| 186 | Create Badge component variants | `frontend/src/components/ui/Badge.tsx` | 2h |

### 8.3 Documentation 🟢 P3

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 187 | Set up Storybook | `frontend/.storybook/` | 4h |
| 188 | Document all components in Storybook | `frontend/src/components/**/*.stories.tsx` | 8h |
| 189 | Create design system documentation | `docs/design-system/` | 4h |

---

## Category 9: Testing Infrastructure (16 tasks)

### 9.1 Backend Testing 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 190 | Achieve 85% unit test coverage | `backend/tests/unit/` | 16h |
| 191 | Add integration tests for all API endpoints | `backend/tests/integration/` | 16h |
| 192 | Add RLS policy tests | `backend/tests/integration/db/` | 4h |
| 193 | Add security-focused tests | `backend/tests/security/` | 8h |
| 194 | Set up test fixtures and factories | `backend/tests/conftest.py` | 4h |

### 9.2 Frontend Testing 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 195 | Achieve 80% unit test coverage | `frontend/src/**/*.test.tsx` | 16h |
| 196 | Add component integration tests | `frontend/src/**/*.integration.test.tsx` | 8h |
| 197 | Set up MSW for API mocking | `frontend/src/mocks/` | 4h |

### 9.3 E2E Testing 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 198 | Create critical path E2E tests | `frontend/e2e/` | 8h |
| 199 | Add E2E tests for auth flows | `frontend/e2e/auth/` | 4h |
| 200 | Add E2E tests for CRUD operations | `frontend/e2e/crud/` | 6h |
| 201 | Set up Playwright visual regression | `frontend/e2e/visual/` | 4h |

### 9.4 CI/CD 🟡 P2

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 202 | Configure test coverage reporting | `.github/workflows/` | 2h |
| 203 | Add test failure notifications | `.github/workflows/` | 1h |
| 204 | Set up parallel test execution | `.github/workflows/` | 2h |
| 205 | Add required test gates for PR merge | `.github/` | 1h |

---

## Category 10: Documentation & Onboarding (12 tasks)

### 10.1 API Documentation 🟢 P3

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 206 | Update OpenAPI specification | `app/api/` | 4h |
| 207 | Add request/response examples | `app/api/` | 4h |
| 208 | Document error codes and handling | `docs/api/` | 2h |
| 209 | Create API changelog | `docs/api/CHANGELOG.md` | 2h |

### 10.2 User Documentation 🟢 P3

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 210 | Create user guide | `docs/user-guide/` | 8h |
| 211 | Create admin guide | `docs/admin-guide/` | 6h |
| 212 | Add contextual help tooltips | `frontend/src/components/` | 4h |
| 213 | Create FAQ section | `frontend/src/pages/help/` | 3h |

### 10.3 Onboarding 🟢 P3

| # | Task | File/Location | Effort |
|---|------|---------------|--------|
| 214 | Implement interactive onboarding tour | `frontend/src/components/Onboarding.tsx` | 8h |
| 215 | Create role-based onboarding paths | `frontend/src/components/Onboarding.tsx` | 4h |
| 216 | Add feature discovery tooltips | `frontend/src/components/` | 4h |
| 217 | Create video tutorials | External | 16h |

---

## Summary by Priority

| Priority | Tasks | Effort (hours) | Sprints |
|----------|-------|----------------|---------|
| 🔴 P0 Critical | 46 | ~120h | 1-2 |
| 🟠 P1 High | 68 | ~200h | 3-6 |
| 🟡 P2 Medium | 85 | ~280h | 7-10 |
| 🟢 P3 Low | 18 | ~80h | 11-12 |
| **Total** | **217** | **~680h** | **12** |

---

## Sprint Assignment

| Sprint | Focus | Tasks | Story Points |
|--------|-------|-------|--------------|
| 1 | Security Critical | 1-13, 33-41 | 34 |
| 2 | Dashboard & Auth | 14-27, 42-46 | 38 |
| 3 | API Consistency | 47-68 | 35 |
| 4 | Legacy Removal | 69-80 | 34 |
| 5 | Accessibility P1 | 81-102 | 36 |
| 6 | Accessibility P2 | 103-122 | 32 |
| 7 | Mobile P1 | 123-139 | 36 |
| 8 | Mobile P2 | 140-146 | 32 |
| 9 | Performance Backend | 147-155 | 35 |
| 10 | Performance Frontend | 156-174 | 38 |
| 11 | Design System | 175-189 | 35 |
| 12 | Testing & Docs | 190-217 | 36 |

---

*This master task list consolidates all findings from Phases 1-7 of the BARQ Fleet Management Enhancement Audit.*
