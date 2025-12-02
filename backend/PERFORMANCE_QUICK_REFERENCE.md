# Performance Quick Reference Card

**BARQ Fleet Management - Performance Optimization Cheat Sheet**

---

## 🚀 Quick Start

```bash
# Development
cp .env.development.example .env
docker-compose up -d postgres redis
uvicorn app.main:app --reload

# Production
docker-compose -f docker-compose.performance.yml up -d
```

---

## 📊 Performance Targets

| Metric | Target | Command |
|--------|--------|---------|
| API Response (p95) | < 200ms | `curl /api/v1/performance/metrics` |
| DB Query (avg) | < 50ms | `GET /api/v1/performance/slow-queries` |
| Cache Hit Rate | > 80% | `GET /api/v1/performance/cache/stats` |

---

## 🔧 Common Tasks

### Caching

```python
# Use cache decorator
from app.core.cache import cached

@cached(namespace="users", ttl=600)
def get_user(user_id: str):
    return db.query(User).filter(User.id == user_id).first()

# Manual caching
from app.core.cache import cache_manager
cache_manager.set("user", user_id, data, ttl=600)

# Invalidate cache
from app.core.cache import invalidate_cache
invalidate_cache("users", "*")
```

### Database

```python
# Use read replica for queries
from app.core.database import get_read_db

@app.get("/users")
def get_users(db: Session = Depends(get_read_db)):
    return db.query(User).all()

# Batch operations
from app.utils.batch import bulk_insert
bulk_insert(session, User, records, chunk_size=1000)
```

### Background Jobs

```python
# Queue task
from app.workers.tasks import send_email_task
send_email_task.delay(recipient="user@example.com", subject="Hi", body="...")

# Check status
result = send_email_task.delay(...)
print(result.state)  # PENDING, SUCCESS, FAILURE
```

### Query Optimization

```python
# Detect N+1 queries
from app.utils.query_optimizer import track_queries

with track_queries(session):
    users = session.query(User).all()
    for user in users:
        print(user.organization.name)  # Warns if N+1

# Fix with eager loading
from sqlalchemy.orm import joinedload
users = session.query(User).options(joinedload(User.organization)).all()
```

---

## 🔍 Monitoring

### API Endpoints

```bash
# Health check
curl http://localhost:8000/api/v1/performance/health | jq

# Metrics
curl http://localhost:8000/api/v1/performance/metrics | jq

# Slow queries
curl http://localhost:8000/api/v1/performance/slow-queries?limit=10 | jq

# Cache stats
curl http://localhost:8000/api/v1/performance/cache/stats | jq

# N+1 detection
curl http://localhost:8000/api/v1/performance/n1-queries | jq

# Configuration
curl http://localhost:8000/api/v1/performance/configuration | jq
```

### Celery Monitoring

```bash
# Flower dashboard
open http://localhost:5555

# Celery CLI
celery -A app.workers.celery_app inspect active
celery -A app.workers.celery_app inspect stats
```

---

## ⚙️ Configuration

### Environment Variables (Production)

```bash
# Database
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_READ_REPLICAS_ENABLED=true

# Cache
REDIS_URL=redis://prod-redis:6379/0
REDIS_MAX_CONNECTIONS=50
CACHE_DEFAULT_TTL=300

# Celery
CELERY_BROKER_URL=redis://prod-redis:6379/1
CELERY_WORKER_CONCURRENCY=8

# Monitoring
PROFILING_ENABLED=false
SLOW_QUERY_THRESHOLD=0.1
```

### Common Tuning

| Issue | Solution | Variable |
|-------|----------|----------|
| Slow queries | Increase pool | `DB_POOL_SIZE=40` |
| Low cache hit | Increase TTL | `CACHE_DEFAULT_TTL=600` |
| High memory | Reduce concurrency | `CELERY_WORKER_CONCURRENCY=4` |
| Slow responses | Enable compression | `COMPRESSION_ENABLED=true` |

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose -f docker-compose.performance.yml up -d

# Scale workers
docker-compose up -d --scale celery_worker=4

# View logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Check health
docker-compose ps

# Stop all
docker-compose down
```

---

## 🧪 Testing

```bash
# Performance tests
python scripts/performance_test.py --mode all

# Load test
python scripts/performance_test.py --mode load --duration 60 --users 20

# Expected: Score > 90/100
```

---

## 🚨 Troubleshooting

### High Memory

```bash
# Reduce pool size
DB_POOL_SIZE=10

# Reduce Celery concurrency
CELERY_WORKER_CONCURRENCY=4

# Limit cache
MEMORY_CACHE_SIZE=500
```

### Slow API

```bash
# Check N+1
curl /api/v1/performance/n1-queries

# Enable caching
CACHE_DEFAULT_TTL=600

# Use read replicas
DB_READ_REPLICAS_ENABLED=true
```

### Low Cache Hit

```bash
# Increase TTL
CACHE_DEFAULT_TTL=600

# Enable warming
CACHE_WARMING_ENABLED=true

# Check Redis
redis-cli ping
```

### Tasks Stuck

```bash
# Check Flower
open http://localhost:5555

# Restart workers
docker-compose restart celery_worker

# Check logs
docker-compose logs celery_worker
```

---

## 📁 File Locations

```
backend/
├── app/
│   ├── core/
│   │   ├── performance_config.py    # Performance settings
│   │   ├── cache.py                 # Caching layer
│   │   └── database.py              # Database config
│   ├── workers/
│   │   ├── celery_app.py            # Celery config
│   │   └── tasks.py                 # Background tasks
│   ├── middleware/
│   │   └── performance.py           # Performance middleware
│   ├── utils/
│   │   ├── batch.py                 # Batch operations
│   │   └── query_optimizer.py      # Query optimization
│   └── api/v1/
│       └── performance.py           # Monitoring API
├── scripts/
│   └── performance_test.py          # Test suite
├── .env.production.example
├── .env.development.example
└── docker-compose.performance.yml
```

---

## 📚 Documentation

- **Complete Guide**: `PERFORMANCE_OPTIMIZATION_SUMMARY.md`
- **Configuration**: `PERFORMANCE_CONFIGURATION_GUIDE.md`
- **Implementation**: `PERFORMANCE_IMPLEMENTATION_COMPLETE.md`
- **This Card**: `PERFORMANCE_QUICK_REFERENCE.md`

---

## ✅ Checklist

**Development**:
- [ ] Copy `.env.development.example` to `.env`
- [ ] Start PostgreSQL and Redis
- [ ] Run migrations: `alembic upgrade head`
- [ ] Start API: `uvicorn app.main:app --reload`
- [ ] Test: `curl http://localhost:8000/api/v1/performance/health`

**Production**:
- [ ] Copy `.env.production.example` to `.env.production`
- [ ] Update production values (DB, Redis, secrets)
- [ ] Start services: `docker-compose -f docker-compose.performance.yml up -d`
- [ ] Verify health: `curl /api/v1/performance/health`
- [ ] Check metrics: `curl /api/v1/performance/metrics`
- [ ] Monitor Flower: `open http://localhost:5555`
- [ ] Run load test: `python scripts/performance_test.py --mode load`

---

**Last Updated**: December 2, 2025
**Status**: ✅ Production-Ready
**Version**: 1.0.0
