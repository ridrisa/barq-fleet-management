# BARQ Fleet Management - Test Suite Plan

**Created:** December 6, 2025
**Phase:** 6 - Validation & Testing Plan
**Version:** 1.0

---

## Test Strategy Overview

### Testing Pyramid

```
                    ┌───────────┐
                    │    E2E    │  5%
                    │  (Playwright)
                    ├───────────┤
                    │           │
                  ┌─┴───────────┴─┐  15%
                  │  Integration   │
                  │   (Vitest)     │
                  ├───────────────┤
                  │               │
                ┌─┴───────────────┴─┐  80%
                │      Unit         │
                │  (Vitest/pytest)  │
                └───────────────────┘
```

---

## Backend Test Suite

### Unit Tests

**Location:** `backend/tests/unit/`

**Coverage Target:** 85%

| Module | Files | Coverage Target |
|--------|-------|-----------------|
| Services | 45 | 90% |
| Schemas | 30 | 95% |
| Utils | 15 | 90% |
| Core | 10 | 85% |

**Example Unit Test:**

```python
# tests/unit/services/test_delivery_service.py

import pytest
from unittest.mock import Mock, patch
from app.services.operations.delivery_service import DeliveryService
from app.schemas.operations.delivery import DeliveryCreate

class TestDeliveryService:
    @pytest.fixture
    def service(self, mock_db):
        return DeliveryService(mock_db)

    def test_create_delivery_success(self, service):
        """Test successful delivery creation"""
        delivery_data = DeliveryCreate(
            tracking_number="DEL-001",
            customer_name="Test Customer",
            customer_phone="+966501234567",
            pickup_address="123 Main St",
            delivery_address="456 Oak Ave"
        )

        result = service.create(delivery_data, org_id=1)

        assert result.tracking_number == "DEL-001"
        assert result.status == "created"

    def test_create_delivery_duplicate_tracking(self, service):
        """Test duplicate tracking number rejection"""
        # First creation
        delivery_data = DeliveryCreate(tracking_number="DEL-001", ...)
        service.create(delivery_data, org_id=1)

        # Duplicate should raise
        with pytest.raises(DuplicateEntityException):
            service.create(delivery_data, org_id=1)

    def test_assign_courier_updates_status(self, service):
        """Test that assigning courier updates delivery status"""
        delivery = service.create(...)

        service.assign_courier(delivery.id, courier_id=5)

        assert delivery.status == "assigned"
        assert delivery.courier_id == 5
```

---

### Integration Tests

**Location:** `backend/tests/integration/`

**Coverage Target:** 70%

| Area | Test Count | Priority |
|------|------------|----------|
| API Endpoints | 150+ | High |
| Database | 50 | High |
| External Services | 20 | Medium |
| Authentication | 30 | High |

**Example Integration Test:**

```python
# tests/integration/api/test_fleet_vehicles.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestVehicleAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self, test_user):
        token = create_access_token(test_user)
        return {"Authorization": f"Bearer {token}"}

    def test_list_vehicles_returns_org_vehicles_only(
        self, client, auth_headers, seed_vehicles
    ):
        """Verify multi-tenant isolation"""
        response = client.get(
            "/api/v1/fleet/vehicles/",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Should only see org 1 vehicles
        for vehicle in data["items"]:
            assert vehicle["organization_id"] == 1

    def test_create_vehicle_requires_auth(self, client):
        """Verify auth requirement"""
        response = client.post(
            "/api/v1/fleet/vehicles/",
            json={"plate_number": "ABC123"}
        )

        assert response.status_code == 401

    def test_create_vehicle_validates_plate_format(
        self, client, auth_headers
    ):
        """Verify validation"""
        response = client.post(
            "/api/v1/fleet/vehicles/",
            headers=auth_headers,
            json={"plate_number": "invalid!@#"}
        )

        assert response.status_code == 422
```

---

### Database Tests

```python
# tests/integration/db/test_rls_policies.py

class TestRowLevelSecurity:
    def test_rls_prevents_cross_org_access(self, db_session):
        """Verify RLS policies work correctly"""
        # Set org context to org 1
        db_session.execute(
            text("SET app.current_org_id = :org_id"),
            {"org_id": 1}
        )

        # Query vehicles
        vehicles = db_session.query(Vehicle).all()

        # All vehicles should be from org 1
        for v in vehicles:
            assert v.organization_id == 1

    def test_rls_context_injection_prevented(self, db_session):
        """Verify SQL injection protection"""
        malicious_org_id = "1; DROP TABLE vehicles; --"

        with pytest.raises(Exception):
            db_session.execute(
                text("SET app.current_org_id = :org_id"),
                {"org_id": malicious_org_id}
            )
```

---

## Frontend Test Suite

### Unit Tests

**Location:** `frontend/src/**/*.test.ts(x)`

**Coverage Target:** 80%

| Area | Files | Coverage |
|------|-------|----------|
| Components | 150 | 85% |
| Hooks | 30 | 90% |
| Utils | 25 | 95% |
| Stores | 15 | 85% |

**Example Component Test:**

```typescript
// src/components/ui/Button.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    fireEvent.click(screen.getByText('Click'));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when loading', () => {
    render(<Button loading>Submit</Button>);

    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  it('applies variant styles correctly', () => {
    const { rerender } = render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-amber-500');

    rerender(<Button variant="secondary">Secondary</Button>);
    expect(screen.getByRole('button')).toHaveClass('border-gray-300');
  });

  it('supports different sizes', () => {
    render(<Button size="lg">Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('h-12');
  });
});
```

**Example Hook Test:**

```typescript
// src/hooks/useAuth.test.ts

import { renderHook, act } from '@testing-library/react';
import { useAuth } from './useAuth';

describe('useAuth', () => {
  it('provides current user when authenticated', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.user).toEqual({
      id: 1,
      email: 'test@example.com',
      role: 'admin'
    });
  });

  it('logout clears user and redirects', async () => {
    const { result } = renderHook(() => useAuth());

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(window.location.pathname).toBe('/login');
  });
});
```

---

### Integration Tests

**Location:** `frontend/src/**/*.integration.test.ts(x)`

```typescript
// src/pages/fleet/VehicleList.integration.test.tsx

import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { VehicleList } from './VehicleList';
import { server } from '@/mocks/server';
import { rest } from 'msw';

describe('VehicleList Integration', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } }
  });

  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  it('fetches and displays vehicles', async () => {
    render(<VehicleList />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('VH-001')).toBeInTheDocument();
      expect(screen.getByText('VH-002')).toBeInTheDocument();
    });
  });

  it('handles loading state', () => {
    render(<VehicleList />, { wrapper });

    expect(screen.getByTestId('skeleton-loader')).toBeInTheDocument();
  });

  it('handles error state', async () => {
    server.use(
      rest.get('/api/v1/fleet/vehicles', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    render(<VehicleList />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Failed to load vehicles')).toBeInTheDocument();
    });
  });

  it('filters vehicles by search', async () => {
    render(<VehicleList />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('VH-001')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText('Search...'), {
      target: { value: 'VH-001' }
    });

    await waitFor(() => {
      expect(screen.getByText('VH-001')).toBeInTheDocument();
      expect(screen.queryByText('VH-002')).not.toBeInTheDocument();
    });
  });
});
```

---

## E2E Test Suite

**Framework:** Playwright
**Location:** `frontend/e2e/`

### Critical User Journeys

| Journey | Priority | Duration |
|---------|----------|----------|
| Login & Dashboard | P0 | 30s |
| Vehicle CRUD | P0 | 45s |
| Delivery Dispatch | P0 | 60s |
| Leave Request | P1 | 45s |
| User Management | P1 | 45s |

**Example E2E Test:**

```typescript
// e2e/fleet/vehicle-management.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Vehicle Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('[data-testid="email"]', 'admin@barq.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('/dashboard');
  });

  test('create new vehicle', async ({ page }) => {
    await page.click('[data-testid="nav-fleet"]');
    await page.click('[data-testid="nav-vehicles"]');

    await page.click('[data-testid="add-vehicle-btn"]');

    await page.fill('[data-testid="plate-number"]', 'ABC-1234');
    await page.fill('[data-testid="make"]', 'Toyota');
    await page.fill('[data-testid="model"]', 'Hilux');
    await page.selectOption('[data-testid="type"]', 'truck');

    await page.click('[data-testid="submit-btn"]');

    await expect(page.locator('[data-testid="success-toast"]'))
      .toBeVisible();
    await expect(page.locator('text=ABC-1234')).toBeVisible();
  });

  test('edit vehicle', async ({ page }) => {
    await page.goto('/fleet/vehicles');

    await page.click('[data-testid="vehicle-row-1"] [data-testid="edit-btn"]');

    await page.fill('[data-testid="make"]', 'Nissan');
    await page.click('[data-testid="submit-btn"]');

    await expect(page.locator('text=Nissan')).toBeVisible();
  });

  test('delete vehicle with confirmation', async ({ page }) => {
    await page.goto('/fleet/vehicles');

    await page.click('[data-testid="vehicle-row-1"] [data-testid="delete-btn"]');

    // Confirmation modal
    await expect(page.locator('[data-testid="confirm-modal"]')).toBeVisible();
    await page.click('[data-testid="confirm-delete"]');

    await expect(page.locator('[data-testid="success-toast"]'))
      .toContainText('deleted');
  });
});
```

---

## Accessibility Testing

### Automated A11y Tests

```typescript
// e2e/accessibility.spec.ts

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const pages = [
  { name: 'Login', path: '/login' },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Vehicles', path: '/fleet/vehicles' },
  { name: 'Deliveries', path: '/operations/deliveries' },
];

test.describe('Accessibility', () => {
  for (const page of pages) {
    test(`${page.name} has no a11y violations`, async ({ page: pwPage }) => {
      await pwPage.goto(page.path);

      const results = await new AxeBuilder({ page: pwPage })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();

      expect(results.violations).toEqual([]);
    });
  }
});
```

### Keyboard Navigation Tests

```typescript
// e2e/keyboard-navigation.spec.ts

test('can navigate dashboard with keyboard only', async ({ page }) => {
  await page.goto('/dashboard');

  // Tab through navigation
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'skip-link');

  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'nav-dashboard');

  // Enter activates
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL('/dashboard');
});
```

---

## Performance Testing

### Load Testing (k6)

**Location:** `tests/load/`

```javascript
// tests/load/api-load.js

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up
    { duration: '5m', target: 50 },   // Sustain
    { duration: '2m', target: 100 },  // Peak
    { duration: '5m', target: 100 },  // Sustain peak
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% under 500ms
    http_req_failed: ['rate<0.01'],    // Error rate under 1%
  },
};

export default function () {
  const authRes = http.post(`${BASE_URL}/api/v1/auth/login`, {
    email: 'test@barq.com',
    password: 'password',
  });

  check(authRes, {
    'login successful': (r) => r.status === 200,
  });

  const token = authRes.json('access_token');
  const headers = { Authorization: `Bearer ${token}` };

  // Dashboard
  const dashRes = http.get(`${BASE_URL}/api/v1/dashboard/stats`, { headers });
  check(dashRes, {
    'dashboard loads': (r) => r.status === 200,
    'dashboard fast': (r) => r.timings.duration < 300,
  });

  // Vehicles list
  const vehiclesRes = http.get(`${BASE_URL}/api/v1/fleet/vehicles/`, { headers });
  check(vehiclesRes, {
    'vehicles loads': (r) => r.status === 200,
  });

  sleep(1);
}
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml

name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest tests/unit -v --cov=app --cov-report=xml
      - name: Run integration tests
        run: pytest tests/integration -v
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - name: Run unit tests
        run: npm run test:unit -- --coverage
      - name: Run integration tests
        run: npm run test:integration
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx playwright install --with-deps
      - name: Run E2E tests
        run: npm run test:e2e
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Coverage Requirements

| Area | Current | Target | Timeline |
|------|---------|--------|----------|
| Backend Unit | 65% | 85% | 4 weeks |
| Backend Integration | 50% | 70% | 6 weeks |
| Frontend Unit | 45% | 80% | 6 weeks |
| Frontend Integration | 30% | 60% | 8 weeks |
| E2E Critical Paths | 40% | 90% | 4 weeks |

---

## Test Data Management

### Fixtures

```python
# conftest.py

@pytest.fixture
def sample_organization():
    return Organization(id=1, name="Test Org", status="active")

@pytest.fixture
def sample_vehicle(sample_organization):
    return Vehicle(
        id=1,
        organization_id=sample_organization.id,
        plate_number="ABC-123",
        make="Toyota",
        model="Hilux",
        status="available"
    )

@pytest.fixture
def sample_courier(sample_organization):
    return Courier(
        id=1,
        organization_id=sample_organization.id,
        first_name="Ahmed",
        last_name="Hassan",
        phone="+966501234567",
        status="active"
    )
```

### Database Seeding

```python
# scripts/seed_test_data.py

def seed_test_database():
    """Seed test database with consistent test data"""

    # Organizations
    orgs = [
        Organization(id=1, name="Org Alpha"),
        Organization(id=2, name="Org Beta"),
    ]

    # Users
    users = [
        User(id=1, org_id=1, email="admin@alpha.com", role="admin"),
        User(id=2, org_id=1, email="manager@alpha.com", role="manager"),
        User(id=3, org_id=2, email="admin@beta.com", role="admin"),
    ]

    # Vehicles, Couriers, Deliveries...
```

---

*Document created as part of Phase 6 - Validation & Testing Plan*
