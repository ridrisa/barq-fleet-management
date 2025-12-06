# Quick Query Optimization Guide

**For Developers**: Fast reference for writing optimized database queries

---

## 1. Preventing N+1 Queries

### ❌ BAD - N+1 Query Pattern

```python
# Loads couriers without vehicles - causes N+1
couriers = db.query(Courier).all()

for courier in couriers:
    # Each iteration makes a new query to get the vehicle!
    if courier.current_vehicle:
        print(courier.current_vehicle.plate_number)

# Result: 1 + N database queries (very slow!)
```

### ✅ GOOD - Eager Loading

```python
from sqlalchemy.orm import joinedload

# Load couriers WITH vehicles in ONE query
couriers = (
    db.query(Courier)
    .options(joinedload(Courier.current_vehicle))
    .all()
)

for courier in couriers:
    # No additional query - vehicle already loaded!
    if courier.current_vehicle:
        print(courier.current_vehicle.plate_number)

# Result: 1 database query (fast!)
```

### When to Use Which Strategy

**joinedload** - Use for one-to-one or many-to-one:
```python
# Courier -> Vehicle (many-to-one)
query.options(joinedload(Courier.current_vehicle))

# Delivery -> Courier (many-to-one)
query.options(joinedload(Delivery.courier))
```

**selectinload** - Use for one-to-many:
```python
# Courier -> Assignments (one-to-many)
query.options(selectinload(Courier.vehicle_assignments))

# Vehicle -> Maintenance Records (one-to-many)
query.options(selectinload(Vehicle.maintenance_records))
```

---

## 2. Optimizing Statistics Queries

### ❌ TERRIBLE - Loading Everything Into Memory

```python
# DON'T DO THIS! Loads ALL deliveries into memory
deliveries = db.query(Delivery).all()  # Could be 100,000 records!

# Then loops in Python
pending = sum(1 for d in deliveries if d.status == 'pending')
delivered = sum(1 for d in deliveries if d.status == 'delivered')
total_cod = sum(d.cod_amount or 0 for d in deliveries)

# Problems:
# - Uses 100+ MB of memory
# - Takes 5+ seconds
# - Loads unnecessary data
```

### ✅ EXCELLENT - SQL Aggregations

```python
from sqlalchemy import func

# Count by status using SQL GROUP BY
status_counts = (
    db.query(
        Delivery.status,
        func.count(Delivery.id).label('count')
    )
    .group_by(Delivery.status)
    .all()
)

# Convert to dictionary
stats = {status: count for status, count in status_counts}

# Total COD using SQL SUM
total_cod = db.query(
    func.coalesce(func.sum(Delivery.cod_amount), 0)
).scalar()

# Benefits:
# - Uses <1 MB memory
# - Takes 50-100ms
# - Runs on database server (optimized)
```

### Common Aggregation Patterns

```python
# COUNT
total = db.query(func.count(Courier.id)).scalar()

# COUNT with filter
active_count = db.query(func.count(Courier.id)).filter(
    Courier.status == 'ACTIVE'
).scalar()

# SUM
total_amount = db.query(func.sum(COD.amount)).scalar()

# AVG
avg_salary = db.query(func.avg(Salary.net_salary)).scalar()

# MIN / MAX
min_date = db.query(func.min(Delivery.created_at)).scalar()
max_date = db.query(func.max(Delivery.created_at)).scalar()

# GROUP BY with multiple aggregations
stats = db.query(
    Courier.city,
    func.count(Courier.id).label('count'),
    func.avg(Courier.performance_score).label('avg_score')
).group_by(Courier.city).all()
```

---

## 3. Efficient Filtering

### Use Indexed Columns

```python
# GOOD - Uses index on status
couriers = db.query(Courier).filter(
    Courier.status == CourierStatus.ACTIVE
)

# GOOD - Uses composite index
couriers = db.query(Courier).filter(
    Courier.organization_id == org_id,
    Courier.status == CourierStatus.ACTIVE
)

# GOOD - Uses index on date
deliveries = db.query(Delivery).filter(
    Delivery.created_at >= start_date,
    Delivery.created_at <= end_date
)
```

### Avoid Expensive Operations

```python
# BAD - Can't use index efficiently
couriers = db.query(Courier).filter(
    Courier.full_name.like('%smith%')  # Leading wildcard = slow
)

# BETTER - Can use index
couriers = db.query(Courier).filter(
    Courier.full_name.like('Smith%')  # No leading wildcard
)

# BEST - Use full-text search for complex text queries
# (Implement with ts_vector for production)
```

---

## 4. Pagination Best Practices

### ❌ BAD - Inefficient Pagination

```python
# Loads ALL records then slices in Python
all_couriers = db.query(Courier).all()
page_couriers = all_couriers[skip:skip+limit]
```

### ✅ GOOD - Database Pagination

```python
# Let database handle pagination
couriers = (
    db.query(Courier)
    .offset(skip)
    .limit(limit)
    .all()
)

# Get total count separately (if needed)
total = db.query(func.count(Courier.id)).scalar()
```

### ✅ BEST - Use Query Optimizer

```python
from app.core.query_optimizer import QueryOptimizer

query = db.query(Courier).filter(Courier.status == 'ACTIVE')

result = QueryOptimizer.paginate_with_count(
    query,
    page=1,
    page_size=50
)

# Returns:
# {
#     'items': [...],
#     'total': 1000,
#     'page': 1,
#     'page_size': 50,
#     'total_pages': 20,
#     'has_next': True,
#     'has_prev': False
# }
```

---

## 5. Efficient EXISTS Checks

### ❌ BAD - Count All Records

```python
# Counts ALL matching records (slow for large tables)
has_couriers = db.query(Courier).count() > 0
```

### ✅ GOOD - LIMIT 1

```python
# Stops after finding first match
has_couriers = db.query(Courier).limit(1).first() is not None
```

### ✅ BEST - Use Optimizer

```python
from app.core.query_optimizer import QueryOptimizer

has_active_couriers = QueryOptimizer.exists(
    db.query(Courier).filter(Courier.status == 'ACTIVE')
)
```

---

## 6. Batch Operations

### ❌ BAD - Loop with Individual Queries

```python
# Makes N queries (very slow)
for courier_id in courier_ids:
    courier = db.query(Courier).filter(Courier.id == courier_id).first()
    # Do something with courier
```

### ✅ GOOD - Single Query with IN

```python
# Single query for all IDs
couriers = db.query(Courier).filter(
    Courier.id.in_(courier_ids)
).all()

# Create ID -> Courier mapping
courier_map = {c.id: c for c in couriers}

# Use mapping for fast lookups
for courier_id in courier_ids:
    courier = courier_map.get(courier_id)
```

### ✅ BEST - Use Batch Loader

```python
from app.core.query_optimizer import QueryOptimizer

couriers = QueryOptimizer.batch_load_by_ids(
    db,
    Courier,
    ids=courier_ids,
    batch_size=100,
    relationships=['current_vehicle']  # Eager load
)
```

---

## 7. Service Layer Pattern

### Create Optimized Service

```python
from app.core.query_optimizer import EagerLoadMixin, QueryOptimizer
from app.services.base import CRUDBase

class CourierService(CRUDBase[Courier, CourierCreate, CourierUpdate], EagerLoadMixin):
    # Define default relationships to load
    default_eager_load = ['current_vehicle', 'organization']

    def get_active_with_vehicles(
        self,
        db: Session,
        organization_id: int,
        skip: int = 0,
        limit: int = 100
    ):
        """Get active couriers with vehicles (optimized)"""
        query = db.query(Courier).filter(
            Courier.organization_id == organization_id,
            Courier.status == CourierStatus.ACTIVE
        )

        # Eager load relationships
        query = QueryOptimizer.eager_load_relationships(
            query,
            self.default_eager_load,
            strategy='joinedload'
        )

        return query.offset(skip).limit(limit).all()

    def get_statistics(
        self,
        db: Session,
        organization_id: int
    ):
        """Get courier statistics (uses SQL aggregations)"""
        # Group by status
        status_counts = (
            db.query(
                Courier.status,
                func.count(Courier.id)
            )
            .filter(Courier.organization_id == organization_id)
            .group_by(Courier.status)
            .all()
        )

        return {status: count for status, count in status_counts}
```

---

## 8. Common Mistakes

### Mistake 1: Accessing Relationships in Loops

```python
# ❌ BAD
deliveries = db.query(Delivery).all()
for delivery in deliveries:
    print(delivery.courier.name)  # N+1 query!

# ✅ GOOD
deliveries = (
    db.query(Delivery)
    .options(joinedload(Delivery.courier))
    .all()
)
for delivery in deliveries:
    print(delivery.courier.name)  # Already loaded
```

### Mistake 2: Multiple COUNT Queries

```python
# ❌ BAD
total = db.query(Courier).count()
active = db.query(Courier).filter(Courier.status == 'ACTIVE').count()
inactive = db.query(Courier).filter(Courier.status == 'INACTIVE').count()
# 3 separate queries!

# ✅ GOOD
counts = (
    db.query(
        Courier.status,
        func.count(Courier.id)
    )
    .group_by(Courier.status)
    .all()
)
# 1 query!
```

### Mistake 3: Loading Unnecessary Data

```python
# ❌ BAD - Loads all columns
couriers = db.query(Courier).all()
courier_ids = [c.id for c in couriers]

# ✅ GOOD - Only load needed column
courier_ids = db.query(Courier.id).all()
courier_ids = [id for (id,) in courier_ids]

# ✅ BEST - Use scalar
courier_ids = [
    id for id in db.query(Courier.id).scalars()
]
```

---

## 9. Testing Query Performance

### Check EXPLAIN Plan

```python
from sqlalchemy import text

# Build your query
query = db.query(Courier).filter(
    Courier.organization_id == 1,
    Courier.status == 'ACTIVE'
)

# Get EXPLAIN
explain = db.execute(
    text(f"EXPLAIN ANALYZE {query.statement.compile(db.bind)}")
).fetchall()

for row in explain:
    print(row[0])
```

### Look For:

✅ **Good Signs**:
- "Index Scan" or "Bitmap Index Scan"
- Low "actual time" values
- "cost=0.42..123.45" (low cost)

❌ **Bad Signs**:
- "Seq Scan" on large tables
- High "actual time" values
- "Rows Removed by Filter" (inefficient filtering)

---

## 10. Quick Checklist

Before committing code, check:

- [ ] No relationship access in loops without eager loading
- [ ] Statistics use SQL aggregations (GROUP BY, SUM, etc.)
- [ ] Pagination uses OFFSET/LIMIT, not Python slicing
- [ ] Complex text search uses proper indexes
- [ ] Batch operations use IN clause or batch loader
- [ ] EXISTS checks use LIMIT 1
- [ ] Only necessary columns loaded
- [ ] Indexes exist on filtered columns
- [ ] EXPLAIN shows index usage

---

## Resources

- **Query Optimizer**: `/backend/app/core/query_optimizer.py`
- **Optimization Report**: `/backend/docs/database/DATABASE_OPTIMIZATION_REPORT.md`
- **RLS Guide**: `/backend/docs/database/RLS_POLICY_OPTIMIZATION.md`
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

---

**Remember**: Premature optimization is bad, but N+1 queries are worse!
