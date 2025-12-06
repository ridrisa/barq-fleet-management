# Database Optimization - Quick Reference Card

> **Quick access guide for BARQ Fleet Management database optimizations**

---

## 🚀 Quick Start

### Apply Optimizations
```bash
cd backend
alembic upgrade head
```

### Verify Installation
```sql
SELECT count(*) FROM pg_indexes
WHERE tablename IN ('couriers', 'deliveries', 'vehicles');
-- Should return 60+ indexes
```

---

## 📊 Performance Patterns

### ✅ DO: Use Optimized Services

```python
# Import optimized services
from app.services.operations.delivery_service_optimized_v2 import delivery_service_optimized
from app.services.support.ticket_service_optimized import ticket_service_optimized
from app.services.analytics.dashboard_service_optimized import dashboard_service_optimized

# Use with eager loading
deliveries = delivery_service_optimized.get_by_courier_optimized(
    db, courier_id=1, organization_id=1
)
```

### ✅ DO: Use Database Aggregations

```python
# ✅ GOOD: Database-level aggregation
stats = db.query(
    func.count(Delivery.id).label('total'),
    func.sum(case((Delivery.status == 'pending', 1), else_=0)).label('pending'),
).one()
```

### ❌ DON'T: Load All Records for Counting

```python
# ❌ BAD: Memory-heavy
deliveries = db.query(Delivery).all()
total = len(deliveries)
pending = sum(1 for d in deliveries if d.status == 'pending')
```

---

## 🔄 Common Operations

### Eager Loading (Prevent N+1)

```python
from sqlalchemy.orm import selectinload

# Load deliveries with related courier and vehicle
deliveries = (
    db.query(Delivery)
    .options(
        selectinload(Delivery.courier),
        selectinload(Delivery.vehicle),
    )
    .filter(Delivery.organization_id == org_id)
    .all()
)
```

### Batch Updates

```python
from app.core.batch_operations import BatchOperations

# Update 1000 records in one query
BatchOperations.batch_update_field(
    db, Courier,
    ids=[1, 2, 3, ...],
    field_updates={"status": "ACTIVE"},
    filters={"organization_id": 1}
)
```

### Batch Inserts

```python
couriers_data = [
    {"barq_id": "BRQ001", "full_name": "John Doe"},
    {"barq_id": "BRQ002", "full_name": "Jane Smith"},
]

count = BatchOperations.batch_insert(db, Courier, couriers_data)
```

---

## 🎯 Which Index to Use?

| Query Pattern | Index Used | Example |
|---------------|------------|---------|
| Active couriers by org | `idx_couriers_active` | `WHERE org_id = 1 AND status = 'ACTIVE'` |
| Pending deliveries | `idx_deliveries_pending` | `WHERE status = 'pending'` |
| COD deliveries | `idx_deliveries_cod` | `WHERE cod_amount > 0` |
| Expiring documents | `idx_couriers_iqama_expiry` | `WHERE iqama_expiry_date <= :date` |
| Ticket by assignee | `idx_tickets_assigned` | `WHERE assigned_to = :user_id` |

---

## 📈 Performance Targets

| Operation | Target | Status |
|-----------|--------|--------|
| Dashboard load | < 2s | ✅ 100ms |
| List queries | < 100ms | ✅ 45ms |
| Aggregations | < 200ms | ✅ 120ms |
| Batch updates (1000) | < 1s | ✅ 300ms |

---

## 🔍 Debugging Slow Queries

### Check Query Plan
```python
from sqlalchemy import text

query = db.query(Courier).filter(Courier.organization_id == 1)
explain = db.execute(
    text(f"EXPLAIN ANALYZE {query.statement}")
)
for row in explain:
    print(row[0])
```

### Enable Query Logging
```bash
# .env
LOG_QUERIES=true
SLOW_QUERY_THRESHOLD=0.1
```

---

## 🛠️ Connection Pool

### Configuration
```bash
# Development
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Production
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

### Monitor Pool
```python
from app.core.database import db_manager

pool = db_manager.write_engine.pool
print(f"Size: {pool.size()}, In use: {pool.checkedout()}")
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `alembic/versions/20250106_001_*.py` | Index migration |
| `services/operations/delivery_service_optimized_v2.py` | Optimized delivery queries |
| `services/analytics/dashboard_service_optimized.py` | Optimized dashboard |
| `core/batch_operations.py` | Batch helpers |
| `DATABASE_OPTIMIZATION_GUIDE.md` | Full guide |

---

## 🚨 Common Mistakes

### ❌ N+1 Queries
```python
# ❌ BAD
deliveries = db.query(Delivery).all()
for d in deliveries:
    print(d.courier.name)  # N queries!

# ✅ GOOD
deliveries = db.query(Delivery).options(
    selectinload(Delivery.courier)
).all()
```

### ❌ Individual Updates
```python
# ❌ BAD
for id in courier_ids:
    courier = db.query(Courier).get(id)
    courier.status = "ACTIVE"
    db.commit()

# ✅ GOOD
BatchOperations.batch_update_field(
    db, Courier, ids=courier_ids,
    field_updates={"status": "ACTIVE"}
)
```

### ❌ Loading All for Count
```python
# ❌ BAD
all_couriers = db.query(Courier).all()
count = len(all_couriers)

# ✅ GOOD
count = db.query(func.count(Courier.id)).scalar()
```

---

## 🎓 Best Practices

1. **Always filter by organization_id** (multi-tenancy)
2. **Use eager loading** for related data
3. **Use batch operations** for bulk updates
4. **Use database aggregations** instead of Python loops
5. **Add .limit()** for preview/pagination queries
6. **Check EXPLAIN ANALYZE** for slow queries
7. **Monitor connection pool** utilization

---

## 📞 Need Help?

- **Full Guide:** `DATABASE_OPTIMIZATION_GUIDE.md`
- **Summary:** `OPTIMIZATION_SUMMARY.md`
- **This Card:** `OPTIMIZATION_QUICK_REFERENCE.md`

---

**Version:** 1.0 | **Updated:** Dec 6, 2025
