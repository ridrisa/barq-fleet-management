# BARQ Fleet Management - Database Optimization Guide

## Overview

This document provides comprehensive guidance on the database optimizations implemented for BARQ Fleet Management system.

**Performance Targets:**
- Query response time: < 100ms (p95) for OLTP operations
- Dashboard queries: < 2s (using materialized views and aggregations)
- Connection pool: 100-200 concurrent connections
- Support for 1M+ records per table
- 10K+ transactions/second capacity

---

## 1. Index Optimization

### 1.1 Implemented Indexes

The migration `20250106_001_database_optimization.py` adds comprehensive indexes across all major tables:

#### Fleet Module - Couriers
```sql
-- Composite indexes for multi-tenant queries
CREATE INDEX idx_couriers_org_status ON couriers (organization_id, status);
CREATE INDEX idx_couriers_org_city_status ON couriers (organization_id, city, status);

-- Partial index for active couriers (most common query)
CREATE INDEX idx_couriers_active ON couriers (organization_id, joining_date DESC)
WHERE status = 'ACTIVE';

-- Partial index for couriers without vehicles
CREATE INDEX idx_couriers_no_vehicle ON couriers (organization_id, id)
WHERE current_vehicle_id IS NULL AND status = 'ACTIVE';

-- Document expiry indexes
CREATE INDEX idx_couriers_iqama_expiry ON couriers (iqama_expiry_date)
WHERE iqama_expiry_date IS NOT NULL;

CREATE INDEX idx_couriers_license_expiry ON couriers (license_expiry_date)
WHERE license_expiry_date IS NOT NULL;
```

**When to use:**
- `idx_couriers_org_status`: Filtering couriers by organization and status
- `idx_couriers_active`: Dashboard queries for active couriers
- `idx_couriers_no_vehicle`: Finding unassigned couriers
- Expiry indexes: Document expiration alerts and warnings

#### Operations Module - Deliveries
```sql
-- Composite indexes for courier and organization queries
CREATE INDEX idx_deliveries_courier_status ON deliveries (courier_id, status, created_at);
CREATE INDEX idx_deliveries_org_status ON deliveries (organization_id, status, created_at);

-- Partial index for pending deliveries
CREATE INDEX idx_deliveries_pending ON deliveries (organization_id, courier_id, created_at DESC)
WHERE status = 'pending';

-- Partial index for COD deliveries
CREATE INDEX idx_deliveries_cod ON deliveries (courier_id, status, cod_amount)
WHERE cod_amount > 0;

-- Unique index on tracking number with text pattern ops
CREATE UNIQUE INDEX idx_deliveries_tracking ON deliveries (tracking_number)
WITH (text_pattern_ops);
```

**When to use:**
- `idx_deliveries_courier_status`: Courier delivery history
- `idx_deliveries_pending`: Finding pending assignments
- `idx_deliveries_cod`: COD collection reports
- `idx_deliveries_tracking`: Tracking number lookups

#### HR Module - Attendance
```sql
-- BRIN index for time-series data (large tables)
CREATE INDEX idx_attendance_date_brin ON attendance USING BRIN (date, created_at);

-- Composite index for organization queries
CREATE INDEX idx_attendance_org_date ON attendance (organization_id, date, status);

-- Partial index for absent records
CREATE INDEX idx_attendance_absent ON attendance (courier_id, date)
WHERE status = 'absent';
```

**When to use:**
- `idx_attendance_date_brin`: Monthly/yearly attendance reports (very efficient for large datasets)
- `idx_attendance_org_date`: Organization-level attendance analysis
- `idx_attendance_absent`: Finding absent couriers

### 1.2 Index Best Practices

**DO:**
- ✅ Use composite indexes with most selective column first
- ✅ Use partial indexes for frequently queried subsets
- ✅ Use BRIN indexes for time-series data (created_at, date columns)
- ✅ Use `text_pattern_ops` for LIKE queries with prefix patterns

**DON'T:**
- ❌ Create redundant indexes (e.g., (a, b) makes (a) redundant)
- ❌ Index low-cardinality columns alone (e.g., boolean fields)
- ❌ Create indexes on columns that are rarely queried
- ❌ Forget to add indexes on foreign keys

---

## 2. N+1 Query Prevention

### 2.1 Eager Loading with SQLAlchemy

The optimized services use `selectinload` and `joinedload` to prevent N+1 queries:

```python
# ❌ BAD: N+1 Query Problem
deliveries = db.query(Delivery).filter(Delivery.courier_id == courier_id).all()
for delivery in deliveries:
    print(delivery.courier.full_name)  # Causes N additional queries!
    print(delivery.vehicle.plate_number)  # Another N queries!

# ✅ GOOD: Eager Loading
from sqlalchemy.orm import selectinload

deliveries = (
    db.query(Delivery)
    .options(
        selectinload(Delivery.courier),
        selectinload(Delivery.vehicle),
    )
    .filter(Delivery.courier_id == courier_id)
    .all()
)
# All related data loaded in 3 queries total (1 + 1 for couriers + 1 for vehicles)
```

### 2.2 When to Use selectinload vs joinedload

**Use `selectinload`:**
- For one-to-many relationships
- When loading many related items
- Default choice for most cases

**Use `joinedload`:**
- For many-to-one relationships
- When you need immediate access to the related object
- For small, always-loaded relationships

```python
# selectinload: Courier -> many Deliveries
courier = (
    db.query(Courier)
    .options(selectinload(Courier.deliveries))
    .first()
)

# joinedload: Delivery -> one Courier (many-to-one)
delivery = (
    db.query(Delivery)
    .options(joinedload(Delivery.courier))
    .first()
)
```

### 2.3 Optimized Service Files

**Created optimized service modules:**

1. **`delivery_service_optimized_v2.py`**
   - Eager loads courier and vehicle relationships
   - Uses database aggregations for statistics
   - Batch operations for updates

2. **`ticket_service_optimized.py`**
   - Eager loads assigned user, created by user, and courier
   - Optimized statistics with CASE expressions
   - Batch assign and status change operations

3. **`dashboard_service_optimized.py`**
   - Database-level aggregations (no memory loading)
   - Single queries with CASE expressions
   - Efficient GROUP BY for distributions

**Usage:**
```python
from app.services.operations.delivery_service_optimized_v2 import delivery_service_optimized

# Get deliveries with eager loading
deliveries = delivery_service_optimized.get_by_courier_optimized(
    db, courier_id=1, organization_id=1
)

# Get statistics without loading all records
stats = delivery_service_optimized.get_statistics_optimized(
    db, organization_id=1
)
```

---

## 3. Connection Pool Configuration

### 3.1 Current Settings

From `backend/app/core/performance_config.py`:

```python
pool_size: int = 20              # Base pool size
max_overflow: int = 40           # Additional connections when needed
pool_timeout: int = 30           # Seconds to wait for connection
pool_recycle: int = 3600         # Recycle connections after 1 hour
pool_pre_ping: bool = True       # Test connections before use
```

### 3.2 Environment Variables

Configure via environment variables:

```bash
# .env file
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### 3.3 Tuning Guidelines

**For development:**
```bash
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

**For production (moderate load):**
```bash
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

**For production (high load):**
```bash
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100
```

**Formula:**
```
pool_size = (num_workers * expected_concurrent_requests_per_worker) / 2
max_overflow = pool_size * 2
```

---

## 4. Batch Operations

### 4.1 Using BatchOperations Helper

From `backend/app/core/batch_operations.py`:

```python
from app.core.batch_operations import BatchOperations

# ❌ BAD: Individual updates (N queries)
for courier_id in courier_ids:
    courier = db.query(Courier).get(courier_id)
    courier.status = "ACTIVE"
    db.commit()

# ✅ GOOD: Batch update (1 query)
BatchOperations.batch_update_field(
    db, Courier,
    ids=courier_ids,
    field_updates={"status": "ACTIVE"},
    filters={"organization_id": 1}
)
```

### 4.2 Batch Insert

```python
# Insert 1000 couriers efficiently
couriers_data = [
    {"barq_id": f"BRQ{i:05d}", "full_name": f"Courier {i}", ...}
    for i in range(1000)
]

count = BatchOperations.batch_insert(db, Courier, couriers_data)
```

### 4.3 Batch Upsert

```python
# Insert new records or update existing ones
objects = [
    {"barq_id": "BRQ001", "full_name": "John Doe", "status": "ACTIVE"},
    {"barq_id": "BRQ002", "full_name": "Jane Smith", "status": "INACTIVE"},
]

result = BatchOperations.batch_upsert(
    db, Courier, objects,
    unique_fields=["barq_id"],
    update_fields=["full_name", "status"]
)
# Returns: {"inserted": 1, "updated": 1}
```

---

## 5. Query Optimization Patterns

### 5.1 Use Database Aggregations

```python
# ❌ BAD: Load all records into memory
deliveries = db.query(Delivery).all()
total = len(deliveries)
pending = sum(1 for d in deliveries if d.status == 'pending')
delivered = sum(1 for d in deliveries if d.status == 'delivered')

# ✅ GOOD: Database-level aggregation
from sqlalchemy import func, case

result = db.query(
    func.count(Delivery.id).label('total'),
    func.sum(case((Delivery.status == 'pending', 1), else_=0)).label('pending'),
    func.sum(case((Delivery.status == 'delivered', 1), else_=0)).label('delivered'),
).one()
```

### 5.2 Use .only() for Specific Columns

```python
# ❌ BAD: Load all columns
couriers = db.query(Courier).all()

# ✅ GOOD: Load only required columns
from sqlalchemy.orm import load_only

couriers = (
    db.query(Courier)
    .options(load_only(Courier.id, Courier.full_name, Courier.status))
    .all()
)
```

### 5.3 Use Exists Instead of Count

```python
# ❌ BAD: Count all matching records
has_pending = db.query(Delivery).filter(Delivery.status == 'pending').count() > 0

# ✅ GOOD: Check existence (stops at first match)
from sqlalchemy import exists

has_pending = db.query(
    exists().where(Delivery.status == 'pending')
).scalar()
```

### 5.4 Use .limit() for Preview Queries

```python
# ❌ BAD: Load everything for preview
recent_deliveries = db.query(Delivery).order_by(Delivery.created_at.desc()).all()[:10]

# ✅ GOOD: Limit at database level
recent_deliveries = (
    db.query(Delivery)
    .order_by(Delivery.created_at.desc())
    .limit(10)
    .all()
)
```

---

## 6. Monitoring & Profiling

### 6.1 Enable Query Logging (Development Only)

```bash
# .env file
LOG_QUERIES=true
SLOW_QUERY_THRESHOLD=0.1  # 100ms
```

### 6.2 Analyze Slow Queries

```python
# Add to your endpoint temporarily
import time
from sqlalchemy import event

@event.listens_for(db.engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    print(f"Start Query: {statement}")

@event.listens_for(db.engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    print(f"Query Complete in {total:.3f}s")
```

### 6.3 Use EXPLAIN ANALYZE

```python
from sqlalchemy import text

# Get query plan
query = db.query(Courier).filter(Courier.organization_id == 1)
explain_query = f"EXPLAIN ANALYZE {str(query.statement.compile(compile_kwargs={'literal_binds': True}))}"
result = db.execute(text(explain_query))

for row in result:
    print(row[0])
```

---

## 7. Read Replicas (Optional)

### 7.1 Configuration

```bash
# .env file
DB_READ_REPLICAS_ENABLED=true
DB_READ_REPLICA_URLS=postgresql://user:pass@replica1:5432/db,postgresql://user:pass@replica2:5432/db
```

### 7.2 Usage

```python
from app.core.database import get_read_db

# Use read replica for read-only operations
@app.get("/couriers")
def get_couriers(db: Session = Depends(get_read_db)):
    return db.query(Courier).all()
```

---

## 8. Migration Deployment

### 8.1 Apply Optimizations

```bash
# Development
cd backend
alembic upgrade head

# Production (with backup first!)
pg_dump -h localhost -U postgres barq_fleet > backup_before_optimization.sql
alembic upgrade head
```

### 8.2 Verify Indexes

```sql
-- Check indexes on couriers table
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'couriers'
ORDER BY indexname;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE tablename = 'couriers'
ORDER BY idx_scan DESC;
```

---

## 9. Performance Checklist

### Before Deployment

- [ ] Run `alembic upgrade head` to apply optimizations
- [ ] Test key queries with EXPLAIN ANALYZE
- [ ] Verify connection pool settings for expected load
- [ ] Enable slow query logging temporarily
- [ ] Run load tests on staging environment
- [ ] Create database backup

### After Deployment

- [ ] Monitor query performance (p50, p95, p99)
- [ ] Check connection pool utilization
- [ ] Monitor index usage statistics
- [ ] Review slow query logs
- [ ] Adjust pool settings if needed

---

## 10. Common Issues & Solutions

### Issue: Slow Dashboard Load

**Solution:**
- Use `dashboard_service_optimized.py` methods
- These use database aggregations instead of loading all records
- Response time: ~100ms vs ~5000ms for non-optimized

### Issue: N+1 Queries in Delivery List

**Solution:**
```python
# Use optimized service with eager loading
from app.services.operations.delivery_service_optimized_v2 import delivery_service_optimized

deliveries = delivery_service_optimized.get_by_courier_optimized(
    db, courier_id=courier_id, organization_id=org_id
)
```

### Issue: Timeout on Bulk Updates

**Solution:**
```python
# Use batch operations with chunking
from app.core.batch_operations import BatchOperations

# Process in chunks of 100
results = BatchOperations.chunked_operation(
    items=courier_ids,
    chunk_size=100,
    operation_func=lambda ids: BatchOperations.batch_update_field(
        db, Courier, ids, {"status": "ACTIVE"}
    )
)
```

### Issue: Connection Pool Exhausted

**Solution:**
1. Increase pool size: `DB_POOL_SIZE=50`
2. Increase max overflow: `DB_MAX_OVERFLOW=100`
3. Check for connection leaks (always close sessions)
4. Consider using read replicas for read-heavy workloads

---

## 11. References

### Files Created/Modified

1. **Migrations:**
   - `backend/alembic/versions/20250106_001_database_optimization.py`

2. **Optimized Services:**
   - `backend/app/services/operations/delivery_service_optimized_v2.py`
   - `backend/app/services/support/ticket_service_optimized.py`
   - `backend/app/services/analytics/dashboard_service_optimized.py`

3. **Helpers:**
   - `backend/app/core/batch_operations.py`
   - `backend/app/core/database.py` (connection pool configuration)
   - `backend/app/core/performance_config.py` (performance settings)

### Related Documentation

- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)
- [SQLAlchemy ORM Performance](https://docs.sqlalchemy.org/en/20/orm/queryguide/performance.html)
- [Database Indexing Strategies](https://use-the-index-luke.com/)

---

**Last Updated:** December 6, 2025
**Version:** 1.0
**Author:** Database Architect - BARQ Fleet Management
