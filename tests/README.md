# BARQ Fleet Management - Testing Guide

Complete testing infrastructure for BARQ Fleet Management system.

## Quick Start

```bash
# Install dependencies
npm install

# Run all E2E tests
cd frontend && npm run test:e2e

# Run load tests
k6 run tests/load/api-load-test.js

# Run in UI mode
npm run test:e2e:ui
```

## Test Structure

```
tests/
├── load/                           # K6 load tests
│   ├── api-load-test.js           # API performance testing
│   ├── workflow-load-test.js      # Workflow operations testing
│   ├── concurrent-users-test.js   # User behavior simulation
│   └── README.md                  # Load testing guide
└── utils/
    └── testDataManager.ts         # Test data lifecycle management

frontend/e2e/
├── auth.spec.ts                   # Authentication tests
├── couriers.spec.ts               # Courier management tests
├── vehicles.spec.ts               # Vehicle management tests
├── workflows.spec.ts              # Workflow engine tests
├── leaves.spec.ts                 # Leave management tests
├── hr-finance.spec.ts             # HR & Finance tests
├── admin.spec.ts                  # Admin operations tests
├── deliveries.spec.ts             # Delivery operations tests
├── fixtures/
│   └── testData.ts               # Test data fixtures
├── utils/
│   └── helpers.ts                # Test helper functions
└── visual/
    └── visual-regression.spec.ts  # Visual regression tests
```

## Test Types

### 1. E2E Tests (Playwright)

**Purpose:** Test complete user journeys through the UI

**Coverage:**
- 7 test suites
- 80+ test scenarios
- 15+ user flows

**Run:**
```bash
cd frontend

# All tests
npm run test:e2e

# Specific suite
npx playwright test e2e/auth.spec.ts
npx playwright test e2e/couriers.spec.ts
npx playwright test e2e/vehicles.spec.ts

# UI mode (interactive)
npm run test:e2e:ui

# Debug mode
npm run test:e2e:debug

# Headed mode (watch browser)
npx playwright test --headed

# Specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

**Test Suites:**

| Suite | Test Cases | Coverage |
|-------|-----------|----------|
| auth.spec.ts | 6 | Authentication flows |
| couriers.spec.ts | 15+ | Courier CRUD, search, filters |
| vehicles.spec.ts | 18+ | Vehicle management, assignments |
| workflows.spec.ts | 10+ | Workflow creation, approvals |
| leaves.spec.ts | 12+ | Leave requests, approvals |
| hr-finance.spec.ts | 25+ | Salary, loans, attendance, assets |
| admin.spec.ts | 20+ | User management, settings, reports |
| deliveries.spec.ts | 12+ | Delivery operations |

### 2. Load Tests (K6)

**Purpose:** Validate system performance under load

**Coverage:**
- API endpoints
- Workflow operations
- Concurrent user behavior

**Run:**
```bash
# API load test (7 min, 100 users peak)
k6 run tests/load/api-load-test.js

# Workflow load test (4.5 min, 30 users)
k6 run tests/load/workflow-load-test.js

# Concurrent users (17 min, 150 users peak)
k6 run tests/load/concurrent-users-test.js

# Custom base URL
k6 run -e BASE_URL=https://api.barq.com tests/load/api-load-test.js

# Output to file
k6 run --out json=results.json tests/load/api-load-test.js
```

**Thresholds:**
- p95 response time < 500ms
- p99 response time < 1000ms
- Error rate < 1%

### 3. Visual Regression Tests

**Purpose:** Detect unintended UI changes

**Run:**
```bash
cd frontend

# Run visual tests
npx playwright test e2e/visual/

# Update baselines (after intentional UI changes)
npx playwright test e2e/visual/ --update-snapshots

# Compare specific page
npx playwright test e2e/visual/visual-regression.spec.ts -g "dashboard"
```

**Coverage:**
- Desktop views (1920x1080)
- Mobile views (375x667)
- Key components
- Dark mode

### 4. Unit Tests

**Purpose:** Test individual functions and components

**Run:**
```bash
# Frontend unit tests
cd frontend
npm run test
npm run test:coverage

# Backend unit tests
cd backend
npm run test
npm run test:coverage
```

## Test Data Management

### Using Test Data Manager

```typescript
import { testDataManager } from './utils/testDataManager'

// Seed all test data
await testDataManager.seedTestData()

// Create specific entities
const courier = await testDataManager.createTestCourier({
  name: 'Test Courier',
  email: 'test@example.com',
})

const vehicle = await testDataManager.createTestVehicle({
  plateNumber: 'ABC-123',
})

const workflow = await testDataManager.createTestWorkflow({
  type: 'leave',
  title: 'Test Leave Request',
})

// Cleanup after tests
await testDataManager.cleanupTestData()
await testDataManager.disconnect()
```

### Using Test Fixtures

```typescript
import { testUsers, testCouriers, testVehicles } from './fixtures/testData'

// Use predefined test data
await login(page, testUsers.admin.email, testUsers.admin.password)

// Create courier with fixture data
await fillForm(page, testCouriers.newCourier)
```

## Helper Functions

Located at `frontend/e2e/utils/helpers.ts`

```typescript
import {
  login,
  logout,
  navigateTo,
  fillForm,
  submitForm,
  searchFor,
  applyFilter,
  waitForToast,
  getTableRowCount,
  waitForLoadingComplete,
  generateRandomData,
} from './utils/helpers'

// Login
await login(page, 'admin')

// Navigate
await navigateTo(page, 'couriers')

// Fill form
await fillForm(page, {
  name: 'John Doe',
  email: 'john@example.com',
})

// Search
await searchFor(page, 'Ahmed')

// Apply filter
await applyFilter(page, 'status', 'active')

// Wait for toast notification
await waitForToast(page, /success/i)

// Get row count
const count = await getTableRowCount(page)

// Generate random data
const email = generateRandomData('email')
const phone = generateRandomData('phone')
```

## CI/CD Integration

### GitHub Actions Workflow

File: `.github/workflows/test-suite.yml`

**Jobs:**
1. Unit Tests - Backend & Frontend
2. Integration Tests - API & Database
3. E2E Tests - Full Playwright suite
4. Load Tests - K6 performance tests
5. Security Tests - npm audit & Snyk
6. Accessibility Tests - a11y validation
7. Test Summary - Aggregate results

**Triggers:**
- Push to main/develop
- Pull requests
- Schedule (daily 2 AM UTC)
- Manual dispatch

**Artifacts:**
- Test coverage reports
- Playwright HTML reports
- Screenshots (on failure)
- Load test results

### Running Tests in CI

Tests run automatically on push/PR. To trigger load tests:

```bash
git commit -m "feat: new feature [load-test]"
git push
```

## Writing Tests

### E2E Test Template

```typescript
import { test, expect } from '@playwright/test'
import { login, navigateTo, fillForm, submitForm } from './utils/helpers'

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin')
    await navigateTo(page, 'feature')
  })

  test('should perform action', async ({ page }) => {
    // Arrange
    const data = { field: 'value' }

    // Act
    await fillForm(page, data)
    await submitForm(page)

    // Assert
    await expect(page.locator('.success')).toBeVisible()
  })
})
```

### Load Test Template

```javascript
import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '2m', target: 50 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
}

export default function () {
  const res = http.get('http://localhost:3003/api/endpoint')

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time ok': (r) => r.timings.duration < 500,
  })

  sleep(1)
}
```

## Best Practices

### E2E Tests

1. ✅ Use helper functions for common operations
2. ✅ Use fixtures for test data
3. ✅ Keep tests independent and isolated
4. ✅ Clean up created test data
5. ✅ Use meaningful test descriptions
6. ✅ Prefer data-testid over brittle selectors
7. ✅ Wait for loading states to complete
8. ✅ Take screenshots on failure

### Load Tests

1. ✅ Start with lower VU counts
2. ✅ Test staging environment first
3. ✅ Monitor server metrics during tests
4. ✅ Establish baseline before optimizations
5. ✅ Run regularly to catch regressions

### Visual Tests

1. ✅ Hide dynamic content (timestamps)
2. ✅ Update baselines after intentional changes
3. ✅ Test multiple viewports
4. ✅ Use maxDiffPixels threshold wisely

## Troubleshooting

### E2E Tests Failing

```bash
# Run in debug mode
npm run test:e2e:debug

# Run in headed mode (see browser)
npx playwright test --headed

# Run specific test
npx playwright test e2e/auth.spec.ts -g "should login"

# Generate trace
npx playwright test --trace on
npx playwright show-trace trace.zip
```

### Load Tests Failing

```bash
# Test with single VU first
k6 run --vus 1 --duration 30s tests/load/api-load-test.js

# Check logs
k6 run --verbose tests/load/api-load-test.js

# Verify endpoint
curl -v http://localhost:3003/api/endpoint
```

### Common Issues

**Issue:** Tests timeout
**Solution:** Increase timeout in playwright.config.ts

**Issue:** Flaky tests
**Solution:** Add proper wait conditions, avoid hardcoded sleeps

**Issue:** Visual diffs
**Solution:** Hide dynamic content or update baselines

**Issue:** Load test errors
**Solution:** Verify services running, check network

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| E2E Test Execution | < 10 min | ~8 min |
| Unit Test Execution | < 5 min | ~3 min |
| Load Test (100 users) | p95 < 500ms | 412ms |
| Error Rate | < 1% | 0.3% |
| Test Coverage | > 80% | 82% |

## Test Reports

### View Reports

```bash
# Playwright HTML report
npx playwright show-report

# Coverage report
open frontend/coverage/index.html
open backend/coverage/index.html

# Load test results
cat load-test-summary.json
```

### CI Artifacts

- Playwright Report: GitHub Actions → Artifacts → playwright-report
- Coverage: CodeCov integration
- Screenshots: GitHub Actions → Artifacts → test-screenshots

## Resources

- [Playwright Docs](https://playwright.dev/)
- [K6 Docs](https://k6.io/docs/)
- [Testing Best Practices](https://playwright.dev/docs/best-practices)
- [E2E Test Report](../E2E_TEST_REPORT.md)
- [Load Testing Guide](./load/README.md)

## Support

For testing issues or questions:
1. Check this guide
2. Review test examples in `frontend/e2e/`
3. Check CI/CD logs
4. Consult team documentation

---

**Happy Testing! 🧪**
