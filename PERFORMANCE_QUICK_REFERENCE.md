# Performance Optimization Quick Reference

## 🚀 Quick Wins (< 1 Day Each)

### 1. Lazy Load Export Libraries (4 hours)

```typescript
// ❌ Before
import jsPDF from 'jspdf'
export function exportPDF() {
  const doc = new jsPDF()
  // ...
}

// ✅ After
export async function exportPDF() {
  const { default: jsPDF } = await import('jspdf')
  const doc = new jsPDF()
  // ...
}
```

### 2. Add Composite Indexes (2 hours)

```sql
-- Migration: Add these indexes
CREATE INDEX idx_couriers_org_status ON couriers(organization_id, status);
CREATE INDEX idx_couriers_org_city ON couriers(organization_id, city);
CREATE INDEX idx_vehicles_org_status ON vehicles(organization_id, status);
```

### 3. Fix Dashboard N+1 Queries (4 hours)

```python
# ❌ Before: 6 queries
active = db.query(Courier).filter_by(status='ACTIVE').count()
inactive = db.query(Courier).filter_by(status='INACTIVE').count()
# ... 4 more

# ✅ After: 1 query
stats = db.query(Courier.status, func.count()).group_by(Courier.status).all()
stats_dict = {status: count for status, count in stats}
```

---

## 🔴 Critical Issues

### Issue 1: No Caching Layer
**Impact:** 50-70% slower responses
**Fix:** Implement Redis caching

```python
# Setup (app/core/cache.py)
import redis
redis_client = redis.Redis(host='localhost', port=6379)

# Usage
@cache_result("dashboard:stats", ttl=300)
def get_dashboard_stats(org_id):
    # Expensive query
    return stats
```

### Issue 2: Monolithic api.ts (2,035 lines)
**Impact:** Poor tree-shaking, large bundle
**Fix:** Split into modules

```
lib/api/
├── auth.ts
├── fleet.ts
├── hr.ts
├── operations.ts
└── index.ts
```

### Issue 3: Missing Eager Loading
**Impact:** N+1 queries on lists
**Fix:** Use joinedload

```python
# ❌ Before
couriers = db.query(Courier).all()

# ✅ After
from sqlalchemy.orm import joinedload
couriers = db.query(Courier).options(
    joinedload(Courier.current_vehicle)
).all()
```

---

## 📊 Performance Targets

| Metric | Current | Target |
|--------|---------|--------|
| Dashboard API | ~800ms | < 200ms |
| List Endpoints | ~400ms | < 100ms |
| Initial Bundle | ~980KB | < 500KB |
| DB Queries/Page | 10+ | 2-3 |

---

## 🛠️ Essential Tools

### Setup Redis (Docker)
```bash
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

### Setup Jaeger (APM)
```bash
docker run -d -p 16686:16686 -p 6831:6831/udp --name jaeger jaegertracing/all-in-one
```

### Analyze Bundle
```bash
npm run build:analyze
open dist/stats.html
```

---

## 📝 Code Patterns

### Pattern 1: Caching Decorator
```python
def cache_result(key_prefix: str, ttl: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{key_prefix}:{args}"
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            result = func(*args, **kwargs)
            redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Pattern 2: Eager Loading Helper
```python
def with_relationships(query, *relationships):
    for rel in relationships:
        query = query.options(joinedload(rel))
    return query

# Usage
couriers = with_relationships(
    db.query(Courier),
    Courier.current_vehicle,
    Courier.vehicle_assignments
).all()
```

### Pattern 3: Dynamic Import
```typescript
async function loadHeavyModule() {
  const module = await import('./heavy-module')
  return module.default
}
```

---

## 🧪 Testing Performance

### Database Query Count
```python
from sqlalchemy import event

query_count = 0

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    global query_count
    query_count += 1

# Run test
query_count = 0
response = client.get("/api/v1/dashboard/stats")
print(f"Queries executed: {query_count}")
```

### Bundle Size
```bash
# Build and check sizes
npm run build
ls -lh dist/assets/*.js | awk '{print $5, $9}'
```

### API Response Time
```bash
# Using httpie
http GET localhost:8000/api/v1/dashboard/stats --print=h | grep -i "x-response-time"
```

---

## 📋 Pre-Deployment Checklist

- [ ] Redis caching configured
- [ ] Composite indexes added
- [ ] N+1 queries fixed
- [ ] api.ts split into modules
- [ ] Heavy libraries lazy-loaded
- [ ] APM/monitoring set up
- [ ] Bundle size < 500KB
- [ ] API responses < 200ms (p95)
- [ ] Cache hit rate > 70%
- [ ] Load testing passed (100 users)

---

## 🔗 Resources

- **Full Report:** `PERFORMANCE_BASELINE_REPORT.md`
- **Detailed Data:** `performance_baseline.json`
- **Bundle Analyzer:** `npm run build:analyze`
- **Jaeger UI:** http://localhost:16686
- **Redis CLI:** `docker exec -it redis redis-cli`

---

**Last Updated:** December 6, 2025
