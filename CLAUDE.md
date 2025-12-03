
## PHASE 0 – Preparation & Safety Net (½ day)

**Goals:** Know what you’re touching, and be able to roll back fast.

1. **Create a short-lived branch**

   * `feature/security-hardening-and-cleanup`

2. **Snapshot & inventory**

   * Run tests: `pytest` (or your test runner) and capture baseline.
   * Export OpenAPI / docs if available.
   * List all legacy routers imported in `app/api/api.py` (non-`v1`).

3. **Add minimal monitoring**

   * Ensure logs include:

     * `user_id`, `org_id`, endpoint path, status code for dashboard & auth.
   * Confirm error tracking is active (Sentry or similar, if you use it).

4. **Rollback strategy**

   * Confirm:

     * DB migrations are reversible.
     * You can deploy previous Docker image / revision quickly.

---

## PHASE 1 – Critical Security Baseline (Week 1, Days 1–3)

### 1.1 SQL Injection Fix in RLS Context (Day 1 – Mandatory)

**Files:**

* `app/core/dependencies.py` (or `backend/app/core/dependencies.py`)
* `app/core/database.py` if it also sets `app.current_org_id`

**Change:**

```python
# BEFORE (vulnerable)
db.execute(text(f"SET app.current_org_id = '{org_id}'"))

# AFTER (safe)
db.execute(text("SET app.current_org_id = :org_id"), {"org_id": str(int(org_id))})
```

Apply anywhere `SET app.current_org_id` is used.

---

### 1.2 Dashboard Authentication & Org Filtering (Day 1–2)

**File:**

* `app/api/v1/dashboard.py`

For each dashboard endpoint (stats, charts, alerts, performance, summary, etc.):

```python
# BEFORE
def endpoint(db: Session = Depends(get_db)):

# AFTER
def endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    org_id = current_org.id
    # Ensure all queries filter by org_id
    query = (
        db.query(Model)
        .filter(Model.organization_id == org_id)
        # ...
    )
```

* Cover all 12 endpoints listed in the plans:

  * `/stats`, `/charts/*`, `/alerts`, `/performance/top-couriers`, `/recent-activity`, `/summary`.

**Goal:**
Dashboard requires auth and always respects tenant isolation.

---

### 1.3 Token Blacklist Check (Day 2)

**File:**

* `app/core/dependencies.py` (in `get_current_user`)

Add:

```python
from app.core.token_blacklist import is_token_blacklisted

# Before jwt.decode:
if is_token_blacklisted(token):
    raise HTTPException(status_code=401, detail="Token has been revoked")
```

Ensure your `token_blacklist` utility exists and is wired to Redis/DB/in-memory as appropriate.

---

### 1.4 Google OAuth Org Context (Day 2)

**File:**

* `app/api/v1/auth.py`

Where OAuth creates the token:

```python
# BEFORE
access_token = create_access_token(data={"sub": str(user.id)})

# AFTER
access_token = create_access_token(data={
    "sub": str(user.id),
    "org_id": organization_id,
    "org_role": organization_role,
})
```

* Make sure this matches what you do in normal login.

---

### 1.5 JWT Expiration & Audience Verification (Day 2–3)

**File:**

* `app/config/settings.py`

Use environment-sensitive default:

```python
default_expire = "15" if self.ENVIRONMENT == "production" else "60"
self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default_expire)
)
```

**Also:**

In `get_current_user` / JWT decode:

```python
# BEFORE
jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_aud": False})

# AFTER
jwt.decode(
    token,
    SECRET_KEY,
    algorithms=[ALGORITHM],
    audience=self.JWT_AUDIENCE,  # ensure configured
    options={"verify_aud": True},
)
```

---

### 1.6 Org ID Validation (Day 3)

**File:**

* `app/core/dependencies.py` where `org_id` is pulled from token or context.

```python
if not isinstance(org_id, int) or org_id < 1:
    raise HTTPException(status_code=401, detail="Invalid organization")
```

---

### 1.7 Health Endpoint Protection (Day 3)

**File:**

* `app/api/v1/health.py`, `/detailed` endpoint.

Option A (recommended): Secure it.

```python
@router.get("/detailed")
def detailed_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    ...
```

Option B: If public, greatly reduce info (no env, no sensitive host details).

---

### 1.8 Admin Password Reset Response Hardening (Day 3)

**File:**

* `app/api/v1/admin/user_enhancements.py`

1. Remove `reset_token` from any response schema.
2. Remove `temporary_password` from admin reset response. Instead, maybe return a simple success indicator and send the temp password via secure channel (email/SMS).

**Also:**

* Update any `PasswordResetResponse` in `app/schemas/admin/` accordingly.

---

#### At the end of Phase 1

* Run full tests.
* Manually test:

  * Dashboard 401 without token.
  * Dashboard per-org isolation.
  * OAuth login → token contains `org_id`.
  * Blacklisted token rejected.
  * Detailed health respects new rules.

---

## PHASE 2 – API & Schema Consistency (Week 1–2)

### 2.1 Standardize HTTP Methods & Pagination (Day 4)

**Files:**

* `app/api/v1/fleet/vehicles.py`

  * `/update-status` → HTTP `PATCH`
* `app/api/v1/fleet/couriers.py`

  * `/update-status` → HTTP `PATCH`

**Pagination limits**
Across v1 API where you have:

```python
limit: int = Query(10, le=1000)
```

Change to:

```python
limit: int = Query(10, le=100)
```

---

### 2.2 Response Models for Statistics Endpoints (Day 4–5)

**Short term (quick win):**

**Files:**

* `app/api/v1/fleet/vehicles.py` (stats endpoints)
* `app/api/v1/fleet/couriers.py` (stats endpoints)

At minimum:

```python
@router.get("/stats", response_model=dict)
def get_stats(...):
    ...
```

*(You’ll replace `dict` with typed schemas in Phase 4.)*

---

### 2.3 Schema Alignment for FMS & Salary (Day 5)

**Files:**

* `app/schemas/fleet/vehicle.py`:

```python
fms_asset_id: Optional[int] = None
fms_tracking_unit_id: Optional[int] = None
fms_last_sync: Optional[datetime] = None  # better than str
```

* `app/schemas/fleet/courier.py`:

```python
fms_asset_id: Optional[int] = None
fms_driver_id: Optional[int] = None
fms_last_sync: Optional[datetime] = None
```

* `app/schemas/hr/salary.py`:

```python
payment_date: Optional[date] = None

# Fix types:
created_at: datetime
updated_at: Optional[datetime] = None
```

* `app/schemas/operations/cod.py`:
* `app/schemas/operations/delivery.py`:

```python
created_at: datetime
```

Make sure these match the SQLAlchemy models.

---

### 2.4 Delivery Model Customer Fields (Day 5)

**File:**

* `app/models/operations/delivery.py`

```python
customer_name = Column(String(200), nullable=True)
customer_phone = Column(String(20), nullable=True)
```

Add an Alembic migration for these fields.

---

## PHASE 3 – Secure Password Reset Model (Week 2)

This is the **nice part from Plan B** that goes beyond “don’t leak the token”.

### 3.1 Password Reset Token Model & Migration (Day 6–7)

**New file:**

* `app/models/password_reset_token.py`

Example:

```python
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(256), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
```

**New migration:**

* `alembic/versions/xxxx_add_password_reset_tokens.py` (create table).

Update reset flow to:

* Generate a random token, store **hash** in DB.
* Send raw token via email/SMS.
* On reset confirmation, compare hash, mark `used`, enforce expiration.

This gives you a **properly secure reset system**, instead of just “no token in response”.

---

## PHASE 4 – Legacy API Deprecation → Removal (Week 2–3)

You want them **gone**, but we can borrow Plan B’s 410 strategy as a short transitional step.

### 4.1 Dependency Scan (Day 8)

Search for usage of legacy routers:

* Imports / includes of:

  * `app/api/fleet/*.py`
  * `app/api/operations/*.py`
  * `app/api/hr/*.py`
  * `app/api/accommodation/*.py`
  * `app/api/analytics/*.py`
  * `app/api/workflow/*.py`
  * `app/api/tenant/*.py`
  * `app/api/fms/*.py`
  * `app/api/finance/*.py`

If no external consumers → you can skip the deprecation step and go straight to removal.

---

### 4.2 Optional Short Deprecation Layer (2–3 days max)

**File (example):**

* `app/api/fleet/__init__.py`

```python
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def deprecated_route(path: str):
    raise HTTPException(
        status_code=410,
        detail={
            "message": "This API version is deprecated",
            "new_endpoint": f"/api/v1/fleet/{path}",
        },
    )
```

Use only if you suspect some lingering consumers.

---

### 4.3 Remove from Main API Router (Day 9–10)

**File:**

* `app/api/api.py`

Remove **all non-v1 includes** for the legacy routers above.

---

### 4.4 Delete Legacy Directories (Day 10–11)

Once you’re comfortable:

Delete:

* `app/api/fleet/`
* `app/api/operations/`
* `app/api/hr/`
* `app/api/accommodation/`
* `app/api/analytics/`
* `app/api/workflow/`
* `app/api/tenant/`
* `app/api/fms/`
* `app/api/finance/`

Run tests & smoke test key flows.

---

## PHASE 5 – Architecture Improvements (Week 3–4, Optional but Recommended)

This is where Plan B’s longer-term improvements live. Do this **only after** the app is stable with Phases 1–4.

### 5.1 Service Exceptions (Days 11–12)

**New file:**

* `app/core/service_exceptions.py`

```python
class ServiceException(Exception):
    pass

class EntityNotFoundException(ServiceException):
    pass

class DuplicateEntityException(ServiceException):
    pass

class BusinessRuleViolationException(ServiceException):
    pass
```

Integrate gradually into service layer methods.

---

### 5.2 Transaction Context Manager (Days 12–13)

**New file:**

* `app/core/transaction.py`

```python
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

@contextmanager
def transactional(db: Session, auto_commit: bool = True):
    try:
        yield db
        if auto_commit:
            db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
```

Use in complex operations:

```python
with transactional(db):
    service.safe_create(...)
    service.safe_update(...)
```

---

### 5.3 Typed Statistics & Analytics Schemas (Days 14–16)

**New files:**

* `app/schemas/analytics/dashboard.py`
* `app/schemas/analytics/kpi.py`
* `app/schemas/analytics/metric_snapshot.py`
* `app/schemas/analytics/report.py`
* `app/schemas/common/statistics.py`

Example:

```python
class VehicleStatisticsResponse(BaseModel):
    total_vehicles: int
    active_vehicles: int
    inactive_vehicles: int
    maintenance_due: int

class CourierStatisticsResponse(BaseModel):
    total_couriers: int
    active_couriers: int
    on_shift: int
    off_shift: int
```

Then update relevant endpoints (dashboard/fleet stats) to return these instead of `dict`.

---

## PHASE 6 – Testing, Validation & Hardening (Ongoing, with a final pass)

After each main phase:

1. **Automated tests**

   * Run test suite, fix regressions.
2. **Manual checks**

   * Login flows (password, OAuth).
   * Dashboard & stats.
   * Multi-tenant isolation.
   * Password reset end-to-end.
3. **Security verifications**

   * Confirm:

     * No `reset_token` / `temporary_password` in responses.
     * Token blacklist works.
     * Health endpoint is safe.
     * Legacy endpoints return 404/410 or are removed.

---

## TL;DR

* **Now / Week 1:**
  Phases **1–2** → fix security, JWT, auth, tenant isolation, and schema mismatches.

* **Next / Week 2:**
  Phase **3–4** → secure password reset model + deprecate and then delete legacy APIs.

* **Later / Week 3–4 (if you have bandwidth):**
  Phase **5** → bring in Plan B’s architecture upgrades (service exceptions, transactions, typed stats/analytics schemas).
