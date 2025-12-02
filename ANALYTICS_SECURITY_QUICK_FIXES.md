# Analytics Module - Security Quick Fixes

## 🔴 CRITICAL: Implement Within 24-48 Hours

### 1. Add Role-Based Access Control (RBAC)

**File:** `backend/app/api/deps.py`

Add this new dependency function:

```python
from typing import List
from fastapi import HTTPException, status

def require_role(allowed_roles: List[str]):
    """
    Dependency to require specific roles for endpoint access

    Usage:
        @router.get("/endpoint")
        def endpoint(current_user: User = Depends(require_role(["admin", "finance_manager"]))):
            ...
    """
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not hasattr(current_user, 'role'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User role not configured"
            )

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )

        return current_user

    return role_checker
```

### 2. Protect Financial Endpoints

**File:** `backend/app/api/analytics/financial.py`

Change ALL endpoints from:
```python
def get_revenue_metrics(
    current_user: User = Depends(get_current_user),
):
```

To:
```python
def get_revenue_metrics(
    current_user: User = Depends(require_role(["admin", "finance_manager", "analyst"])),
):
```

**Apply to these endpoints:**
- `/revenue-metrics`
- `/cost-breakdown`
- `/profit-margins`
- `/budget-vs-actual`
- `/cash-flow`
- `/cod-collection-rates`
- `/payment-aging`
- `/revenue-forecast`
- `/profitability-analysis`
- `/financial-ratios`

### 3. Protect Export Endpoints

**File:** `backend/app/api/analytics/export.py`

Add limits and role checks:

```python
from app.api.deps import require_role
from app.core.audit import log_data_export

# Add this constant at top of file
MAX_EXPORT_DAYS = 90
MAX_EXPORT_ROWS = {
    "csv": 100_000,
    "json": 50_000,
    "excel": 100_000,
}

@router.post("/generate")
def generate_export(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "analyst", "manager"])),  # ✅ Add RBAC
):
    """Generate data export in requested format"""
    # ✅ Add date range validation
    if not request.end_date:
        request.end_date = date.today()
    if not request.start_date:
        request.start_date = request.end_date - timedelta(days=30)

    # ✅ Enforce maximum date range
    if (request.end_date - request.start_date).days > MAX_EXPORT_DAYS:
        raise HTTPException(
            status_code=400,
            detail=f"Export date range cannot exceed {MAX_EXPORT_DAYS} days"
        )

    # ... fetch data ...

    # ✅ Enforce row limits
    if len(sample_data) > MAX_EXPORT_ROWS.get(request.format, 100_000):
        raise HTTPException(
            status_code=400,
            detail=f"Export exceeds maximum {MAX_EXPORT_ROWS[request.format]:,} rows. Please narrow your date range."
        )

    # ✅ Add audit logging
    log_data_export(
        user_id=current_user.id,
        user_email=current_user.email,
        data_type=request.data_type,
        date_range=(request.start_date, request.end_date),
        row_count=len(sample_data),
        export_format=request.format,
    )

    # ... rest of code ...
```

### 4. Create Audit Logging Function

**File:** `backend/app/core/audit.py`

```python
"""
Audit Logging Module

Provides comprehensive audit trail for security-sensitive operations.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from app.core.logging import get_logger

audit_logger = get_logger("audit")


def log_data_export(
    user_id: int,
    user_email: str,
    data_type: str,
    date_range: tuple,
    row_count: int,
    export_format: str,
):
    """Log data export event for audit trail"""
    audit_logger.warning(
        "DATA_EXPORT",
        extra={
            "event_type": "data_export",
            "user_id": user_id,
            "user_email": user_email,
            "data_type": data_type,
            "start_date": date_range[0].isoformat() if date_range[0] else None,
            "end_date": date_range[1].isoformat() if date_range[1] else None,
            "row_count": row_count,
            "export_format": export_format,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def log_analytics_access(
    user_id: int,
    user_email: str,
    endpoint: str,
    data_type: str,
    filters: Dict[str, Any],
    row_count: Optional[int] = None,
):
    """Log analytics data access for audit trail"""
    audit_logger.info(
        "ANALYTICS_ACCESS",
        extra={
            "event_type": "analytics_access",
            "user_id": user_id,
            "user_email": user_email,
            "endpoint": endpoint,
            "data_type": data_type,
            "filters": filters,
            "row_count": row_count,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


def log_financial_data_access(
    user_id: int,
    user_email: str,
    endpoint: str,
    date_range: tuple,
):
    """Log financial data access (special audit category)"""
    audit_logger.warning(
        "FINANCIAL_DATA_ACCESS",
        extra={
            "event_type": "financial_data_access",
            "user_id": user_id,
            "user_email": user_email,
            "endpoint": endpoint,
            "start_date": date_range[0].isoformat() if date_range[0] else None,
            "end_date": date_range[1].isoformat() if date_range[1] else None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
```

---

## 🟠 HIGH PRIORITY: Implement Within 7 Days

### 5. Add Rate Limiting

**File:** `backend/app/middleware/rate_limit.py`

Update `CUSTOM_LIMITS` dictionary:

```python
CUSTOM_LIMITS = {
    "/api/v1/auth/login": "5/minute",
    "/api/v1/auth/register": "3/minute",
    "/api/v1/auth/forgot-password": "3/hour",
    "/api/v1/auth/verify-email": "5/hour",
    "/api/v1/users/me": "100/minute",

    # ✅ Add analytics rate limits
    "/api/v1/analytics/overview": "60/minute",
    "/api/v1/analytics/fleet": "30/minute",
    "/api/v1/analytics/financial": "20/minute",  # More restrictive for sensitive data
    "/api/v1/analytics/hr": "20/minute",
    "/api/v1/analytics/operations": "40/minute",
    "/api/v1/analytics/kpi": "40/minute",
    "/api/v1/analytics/forecasting": "10/minute",
    "/api/v1/analytics/export": "5/hour",  # Very restrictive
    "/api/v1/analytics/reports/execute": "10/hour",
}
```

### 6. Add Input Validation

**File:** `backend/app/api/analytics/overview.py`

Update endpoints with validation:

```python
from pydantic import validator

@router.get("/trends/{metric}", response_model=List[TrendDataPoint])
def get_metric_trends(
    metric: str = Path(..., regex="^[a-z_]{1,50}$", description="Metric name"),  # ✅ Add validation
    db: Session = Depends(get_db),
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
    period: PeriodType = Query(PeriodType.DAILY),
    current_user: User = Depends(get_current_user),
):
    """Get trend data for a specific metric over time"""

    # ✅ Add date range validation
    if end_date and start_date:
        if end_date < start_date:
            raise HTTPException(400, "end_date must be after start_date")
        if (end_date - start_date).days > 365:
            raise HTTPException(400, "Date range cannot exceed 365 days")

    # ... rest of code ...
```

**Apply similar validation to:**
- All `metric` path parameters
- All `limit` query parameters (add `ge=1, le=200`)
- All `offset` query parameters (add `ge=0, le=10000`)
- All date range parameters

### 7. Protect HR Analytics

**File:** `backend/app/api/analytics/hr.py`

Add RBAC to all endpoints:

```python
@router.get("/performance-metrics", response_model=dict)
def get_performance_metrics(
    current_user: User = Depends(require_role(["admin", "hr_manager", "manager"])),  # ✅ Add RBAC
):
```

---

## 🟡 MEDIUM PRIORITY: Implement Within 30 Days

### 8. Add Field-Level Permissions

**File:** `backend/app/utils/permissions.py` (new file)

```python
"""
Field-level permission utilities
"""
from typing import Dict, Any, List

def filter_sensitive_financial_fields(data: dict, user_role: str) -> dict:
    """Remove sensitive financial fields based on user role"""

    # Define sensitive fields
    SALARY_FIELDS = ["courier_salaries", "staff_salaries", "salaries"]
    COST_DETAIL_FIELDS = ["cost_categories"]

    if user_role in ["admin", "finance_manager"]:
        # Full access
        return data

    # Remove salary information for non-privileged users
    if "cost_categories" in data:
        for category_name, category_data in data["cost_categories"].items():
            if isinstance(category_data, dict):
                for field in SALARY_FIELDS:
                    category_data.pop(field, None)

    # Remove detailed breakdowns
    if user_role not in ["admin", "finance_manager", "analyst"]:
        data.pop("cost_categories", None)

    return data
```

Apply in financial endpoints:

```python
from app.utils.permissions import filter_sensitive_financial_fields

@router.get("/cost-breakdown", response_model=dict)
def get_cost_breakdown(...):
    result = {
        # ... data ...
    }

    # Filter based on user role
    result = filter_sensitive_financial_fields(result, current_user.role)

    return result
```

### 9. Update CORS for Production

**File:** `backend/app/main.py`

```python
from app.config.settings import settings

# Define allowed origins based on environment
if settings.ENVIRONMENT.lower() == "production":
    ALLOWED_ORIGINS = [
        "https://barq.example.com",
        "https://app.barq.example.com",
        "https://admin.barq.example.com",
    ]
else:
    ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ Environment-specific
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
)
```

---

## Testing Checklist

After implementing fixes, test:

- [ ] Non-admin users cannot access `/analytics/financial/*`
- [ ] Non-admin users cannot access `/analytics/export/*`
- [ ] Export date range limited to 90 days
- [ ] Export row count limited based on format
- [ ] Exports are logged in audit trail
- [ ] Rate limits trigger on repeated requests
- [ ] Invalid inputs return 400 errors with clear messages
- [ ] Date ranges exceeding 365 days are rejected
- [ ] CORS only allows configured origins (production)

---

## Database Migration Required

If `User` model doesn't have a `role` field, add migration:

```python
"""Add role to users table

Revision ID: add_user_roles
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('users', sa.Column('role', sa.String(50), nullable=False, server_default='user'))
    op.create_index('idx_users_role', 'users', ['role'])

def downgrade():
    op.drop_index('idx_users_role', 'users')
    op.drop_column('users', 'role')
```

Then define roles in User model:

```python
# app/models/user.py
class UserRole(str, Enum):
    ADMIN = "admin"
    FINANCE_MANAGER = "finance_manager"
    HR_MANAGER = "hr_manager"
    MANAGER = "manager"
    ANALYST = "analyst"
    COURIER = "courier"
    USER = "user"

class User(Base):
    # ... existing fields ...
    role = Column(String(50), nullable=False, default=UserRole.USER.value, index=True)
```

---

## Deployment Checklist

Before deploying to production:

- [ ] Run security tests
- [ ] Update environment variables (ALLOWED_ORIGINS)
- [ ] Verify audit logs are being written
- [ ] Test RBAC with different user roles
- [ ] Verify rate limits are active
- [ ] Check CORS configuration
- [ ] Review security headers
- [ ] Run penetration tests
- [ ] Document all changes

---

## Priority Summary

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 🔴 Critical | RBAC on financial endpoints | 4 hours | High |
| 🔴 Critical | RBAC on export endpoints | 2 hours | High |
| 🔴 Critical | Export limits & audit | 4 hours | High |
| 🟠 High | Rate limiting | 3 hours | Medium |
| 🟠 High | Input validation | 6 hours | Medium |
| 🟡 Medium | Field-level permissions | 8 hours | Low |
| 🟡 Medium | CORS update | 1 hour | Low |

**Total Estimated Effort:** 28 hours (3.5 days)

---

**Next Steps:**
1. Review this document with team
2. Create tickets for each priority item
3. Assign to developers
4. Set deadlines (24h, 7d, 30d)
5. Schedule security testing session
6. Plan production deployment
