# BARQ Fleet Management - Testing Quick Start Guide

## Prerequisites

1. **Python 3.10+** installed
2. **PostgreSQL** database running (or SQLite for tests)
3. **Redis** server running (optional for tests, uses mocks)

## Installation

```bash
# Navigate to backend directory
cd /Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend

# Install dependencies including test requirements
pip install -r requirements.txt

# Verify pytest installation
pytest --version
```

## Quick Test Commands

### Run All Tests
```bash
pytest
```

### Run Tests by Category

**Unit Tests Only** (fastest):
```bash
pytest -m unit
```

**Integration Tests Only**:
```bash
pytest -m integration
```

**E2E Tests Only**:
```bash
pytest -m e2e
```

**Security Tests Only**:
```bash
pytest -m security
```

### Run Tests by Module

```bash
# Fleet Management tests
pytest -m fleet

# HR Management tests
pytest -m hr

# Operations tests
pytest -m operations

# Workflow Engine tests
pytest -m workflow

# Support System tests
pytest -m support

# Analytics tests
pytest -m analytics

# Admin & Auth tests
pytest -m admin
```

### Run with Coverage

**Generate Coverage Report**:
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**View HTML Coverage Report**:
```bash
open tests/coverage/html/index.html
```

### Parallel Execution (Faster)

```bash
# Use all CPU cores
pytest -n auto

# Use specific number of workers
pytest -n 4
```

### Verbose Output

```bash
# Verbose with test names
pytest -v

# Extra verbose with test details
pytest -vv

# Show print statements
pytest -s
```

### Run Specific Test File

```bash
pytest tests/integration/api/test_fleet_couriers_api.py
```

### Run Specific Test Function

```bash
pytest tests/integration/api/test_fleet_couriers_api.py::TestCouriersAPI::test_create_courier_success
```

### Debug Mode

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start
pytest --trace
```

## Test Structure Overview

```
tests/
├── conftest.py                    # Global fixtures & configuration
├── unit/                          # Fast, isolated unit tests
│   ├── models/                    # Model validation tests
│   └── services/                  # Business logic tests
├── integration/                   # API endpoint tests
│   └── api/
│       ├── test_fleet_*.py
│       ├── test_hr_*.py
│       ├── test_operations_*.py
│       └── ...
├── e2e/                          # End-to-end workflow tests
│   ├── test_courier_onboarding_workflow.py
│   ├── test_delivery_lifecycle_workflow.py
│   └── ...
├── security/                     # Security & auth tests
└── utils/                        # Test utilities
    ├── factories.py              # Test data factories
    └── api_helpers.py            # API test helpers
```

## Common Test Patterns

### Using Fixtures

```python
def test_with_fixtures(client, admin_token, courier_factory):
    """Example test using fixtures"""
    courier = courier_factory.create(status="active")

    response = client.get(
        f"/api/v1/fleet/couriers/{courier.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
```

### Using Test Helpers

```python
from tests.utils.api_helpers import (
    make_get_request,
    assert_success_response
)

def test_with_helpers(client, admin_token):
    """Example test using API helpers"""
    response = make_get_request(
        client,
        "/api/v1/fleet/couriers",
        admin_token
    )

    assert_success_response(response)
    data = response.json()
    assert len(data["items"]) > 0
```

### Using Factories

```python
from tests.utils.factories import CourierFactory, VehicleFactory

def test_with_factories(db_session):
    """Example test using factories"""
    courier = CourierFactory.create(
        full_name="Ahmad Hassan",
        status="active"
    )

    vehicle = VehicleFactory.create(
        status="available"
    )

    db_session.commit()

    assert courier.id is not None
    assert vehicle.id is not None
```

## Environment Variables for Testing

```bash
# Set environment to testing
export ENVIRONMENT=testing

# Use in-memory SQLite for faster tests
export DATABASE_URL=sqlite:///:memory:

# Disable external services
export REDIS_ENABLED=false
export EMAIL_ENABLED=false
export SMS_ENABLED=false
```

## Troubleshooting

### Import Errors

If you see import errors:
```bash
# Add app directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or run tests from backend directory
cd backend && pytest
```

### Database Errors

Tests use SQLite in-memory database by default. No PostgreSQL needed for testing.

### Slow Tests

```bash
# Identify slowest tests
pytest --durations=10

# Run fast tests only
pytest -m "not slow"

# Use parallel execution
pytest -n auto
```

### Failed Tests

```bash
# Show detailed failure output
pytest -vv --tb=long

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb
```

## Coverage Targets

| Module | Target | Status |
|--------|--------|--------|
| Fleet Management | 95% | ✅ |
| HR Management | 95% | ✅ |
| Operations | 95% | ✅ |
| Workflow Engine | 90% | ✅ |
| Support System | 90% | ✅ |
| Analytics | 85% | ✅ |
| Admin & Auth | 95% | ✅ |
| **Overall** | **95%** | ✅ |

## Test Counts

- **Unit Tests**: 200+ test cases
- **Integration Tests**: 300+ test cases
- **E2E Tests**: 50+ test cases
- **Security Tests**: 30+ test cases
- **Total**: 580+ test cases

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

## Pre-commit Hook (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running tests before commit..."

# Run fast unit tests
pytest -m unit -x

if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi

echo "Tests passed! Proceeding with commit."
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Useful Pytest Plugins

Already installed:
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities
- `pytest-xdist` - Parallel execution
- `pytest-timeout` - Test timeouts
- `pytest-env` - Environment variables

## Next Steps

1. **Run initial test suite**: `pytest -v`
2. **Check coverage**: `pytest --cov=app --cov-report=html`
3. **Review coverage report**: `open tests/coverage/html/index.html`
4. **Add new tests** as you develop new features
5. **Maintain 95%+ coverage** for all modules

## Additional Resources

- Full Test Suite Summary: `TEST_SUITE_SUMMARY.md`
- Pytest Documentation: https://docs.pytest.org/
- Coverage.py Documentation: https://coverage.readthedocs.io/
- Factory Boy Documentation: https://factoryboy.readthedocs.io/

---

**Last Updated**: 2025-12-02
**Maintainer**: BARQ QA Team
