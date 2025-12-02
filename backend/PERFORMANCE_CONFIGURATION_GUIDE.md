# Performance Configuration Guide

Complete guide for configuring and optimizing BARQ Fleet Management performance.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Configuration](#environment-configuration)
3. [Database Tuning](#database-tuning)
4. [Cache Configuration](#cache-configuration)
5. [Background Jobs](#background-jobs)
6. [Monitoring](#monitoring)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Development Setup

```bash
# 1. Copy environment file
cp .env.development.example .env

# 2. Start services
docker-compose up -d postgres redis

# 3. Run migrations
alembic upgrade head

# 4. Start API server
uvicorn app.main:app --reload

# 5. Start Celery worker (optional)
celery -A app.workers.celery_app worker --loglevel=info
```

### Production Setup

```bash
# 1. Copy environment file
cp .env.production.example .env.production

# 2. Update with production values
nano .env.production

# 3. Start all services
docker-compose -f docker-compose.performance.yml up -d

# 4. Verify health
curl http://localhost:8000/api/v1/performance/health
```

---

## Environment Configuration

### Key Variables

#### Database

```bash
# Connection pooling
DB_POOL_SIZE=20              # Base pool size (production: 20-40)
DB_MAX_OVERFLOW=40           # Additional connections (production: 40-80)
DB_POOL_TIMEOUT=30           # Connection timeout seconds
DB_POOL_RECYCLE=3600         # Recycle connections after 1 hour

# Read replicas (optional)
DB_READ_REPLICAS_ENABLED=true
DB_READ_REPLICA_URLS=postgresql://replica1,postgresql://replica2
```

**Recommendations**:
- Development: `DB_POOL_SIZE=5`, `DB_MAX_OVERFLOW=10`
- Production (< 100 users): `DB_POOL_SIZE=20`, `DB_MAX_OVERFLOW=40`
- Production (> 100 users): `DB_POOL_SIZE=40`, `DB_MAX_OVERFLOW=80`

#### Cache

```bash
# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50     # Max Redis connections

# TTL (Time To Live)
CACHE_DEFAULT_TTL=300        # 5 minutes
CACHE_USER_TTL=600           # 10 minutes
CACHE_ORG_TTL=1800           # 30 minutes
CACHE_STATIC_TTL=3600        # 1 hour

# Memory cache
MEMORY_CACHE_SIZE=1000       # Max items in memory
MEMORY_CACHE_TTL=60          # 1 minute
```

**Recommendations**:
- Development: Lower TTLs for faster iteration
- Production: Higher TTLs for better performance
- High-traffic: Increase `REDIS_MAX_CONNECTIONS` to 100+

#### Background Jobs (Celery)

```bash
# Broker & Backend
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Worker settings
CELERY_WORKER_CONCURRENCY=8  # Concurrent tasks per worker
CELERY_PREFETCH_MULTIPLIER=4 # Tasks to prefetch

# Task limits
CELERY_SOFT_TIME_LIMIT=300   # Soft limit (5 min)
CELERY_TIME_LIMIT=600        # Hard limit (10 min)
CELERY_MAX_RETRIES=3         # Max retry attempts
```

**Recommendations**:
- CPU-bound tasks: `CELERY_WORKER_CONCURRENCY=CPU_COUNT`
- I/O-bound tasks: `CELERY_WORKER_CONCURRENCY=CPU_COUNT * 2`
- Memory-constrained: Lower concurrency, increase workers

#### API

```bash
# Compression
COMPRESSION_ENABLED=true
COMPRESSION_LEVEL=6          # 1-9 (higher = more compression)
MIN_COMPRESSION_SIZE=1024    # Minimum bytes to compress

# Rate limiting
RATE_LIMIT_REQUESTS=100      # Requests per window
RATE_LIMIT_WINDOW=60         # Window in seconds

# Deduplication
REQUEST_DEDUPLICATION_ENABLED=true
DEDUPLICATION_WINDOW=5       # Seconds
```

#### Monitoring

```bash
# Profiling (disable in production)
PROFILING_ENABLED=false

# Query logging
LOG_QUERIES=false            # Log all queries
LOG_SLOW_QUERIES_ONLY=true   # Only log slow queries
SLOW_QUERY_THRESHOLD=0.1     # 100ms threshold

# Memory profiling
MEMORY_PROFILING_ENABLED=false
```

---

## Database Tuning

### PostgreSQL Configuration

**Recommended postgresql.conf settings**:

```ini
# Connection settings
max_connections = 200

# Memory settings
shared_buffers = 256MB                  # 25% of RAM
effective_cache_size = 1GB              # 50-75% of RAM
maintenance_work_mem = 64MB
work_mem = 2621kB                       # RAM / max_connections / 16

# WAL settings
wal_buffers = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
checkpoint_completion_target = 0.9

# Query planner
default_statistics_target = 100
random_page_cost = 1.1                  # For SSD
effective_io_concurrency = 200          # For SSD

# Parallelism
max_worker_processes = 4
max_parallel_workers_per_gather = 2
max_parallel_workers = 4
max_parallel_maintenance_workers = 2
```

### Index Optimization

**Critical indexes** (already implemented):

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization_id ON users(organization_id);

-- Deliveries
CREATE INDEX idx_deliveries_status ON deliveries(status);
CREATE INDEX idx_deliveries_courier_id ON deliveries(courier_id);
CREATE INDEX idx_deliveries_delivered_at ON deliveries(delivered_at);

-- Tickets
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_sla_due_at ON tickets(sla_due_at);
```

**Verify index usage**:

```sql
-- Find missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
  AND correlation < 0.5
ORDER BY n_distinct DESC;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;
```

### Query Optimization

**Use EXPLAIN ANALYZE**:

```python
from app.utils.query_optimizer import QueryAnalyzer

query = session.query(User).filter(User.email == "user@example.com")
explain = QueryAnalyzer.explain_query(session, query)
print(explain["explain"])
```

**Avoid N+1 queries**:

```python
# BAD: N+1 query
users = session.query(User).all()
for user in users:
    print(user.organization.name)  # Separate query for each user!

# GOOD: Eager loading
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.organization)).all()
for user in users:
    print(user.organization.name)  # No additional queries!
```

---

## Cache Configuration

### Cache Strategy

**Multi-level caching**:
1. **L1 (Memory)**: Fast, limited capacity (1000 items, 60s TTL)
2. **L2 (Redis)**: Distributed, persistent (300s default TTL)

**Cache namespaces**:
- `user`: User data (600s TTL)
- `organization`: Organization data (1800s TTL)
- `static`: Static reference data (3600s TTL)

### Usage Patterns

**Decorator-based caching**:

```python
from app.core.cache import cached

@cached(namespace="users", ttl=600)
def get_user(user_id: str):
    return db.query(User).filter(User.id == user_id).first()
```

**Manual caching**:

```python
from app.core.cache import cache_manager

# Get from cache
user = cache_manager.get("user", user_id)
if not user:
    # Cache miss - fetch from database
    user = db.query(User).filter(User.id == user_id).first()
    cache_manager.set("user", user_id, user.to_dict(), ttl=600)
```

**Cache invalidation**:

```python
from app.core.cache import invalidate_cache

# Invalidate specific key
invalidate_cache("user", user_id)

# Invalidate all users
invalidate_cache("users", "*")
```

### Redis Tuning

**redis.conf**:

```ini
# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lru  # Evict least recently used

# Persistence
appendonly yes
appendfsync everysec

# Performance
save 900 1       # Save after 900s if 1 key changed
save 300 10      # Save after 300s if 10 keys changed
save 60 10000    # Save after 60s if 10000 keys changed
```

---

## Background Jobs

### Celery Configuration

**Worker deployment**:

```bash
# High priority queue (4 workers)
celery -A app.workers.celery_app worker \
  --concurrency=4 \
  --queues=high_priority \
  --loglevel=info

# Default queue (8 workers)
celery -A app.workers.celery_app worker \
  --concurrency=8 \
  --queues=default \
  --loglevel=info

# Low priority queue (4 workers)
celery -A app.workers.celery_app worker \
  --concurrency=4 \
  --queues=low_priority \
  --loglevel=info

# Beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info
```

### Task Routing

**Queue priority**:
- `high_priority`: Emails, notifications (< 1s)
- `default`: Reports, data processing (< 1min)
- `low_priority`: Cleanup, aggregation (< 5min)

**Task configuration**:

```python
from app.workers.celery_app import celery_app

@celery_app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    queue="high_priority"
)
def critical_task(self, data):
    # Task implementation
    pass
```

### Monitoring with Flower

```bash
# Start Flower
celery -A app.workers.celery_app flower --port=5555

# Access dashboard
open http://localhost:5555
```

---

## Monitoring

### Performance Metrics API

**Get metrics**:

```bash
curl http://localhost:8000/api/v1/performance/metrics | jq
```

**Response**:

```json
{
  "api": {
    "requests": {
      "total_requests": 10000,
      "avg_response_time": 0.085,
      "slow_requests": 50
    }
  },
  "cache": {
    "hit_rate": 0.85,
    "total_hits": 8500
  },
  "database": {
    "total_queries": 5000,
    "avg_time": 0.045
  },
  "system": {
    "cpu_percent": 45.2,
    "memory": {
      "percent": 62.5
    }
  }
}
```

### Health Checks

```bash
# Health check
curl http://localhost:8000/api/v1/performance/health

# Slow queries
curl http://localhost:8000/api/v1/performance/slow-queries

# Cache stats
curl http://localhost:8000/api/v1/performance/cache/stats
```

### Application Monitoring

**Prometheus metrics** (optional):

```python
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
```

**Sentry integration** (errors):

```bash
SENTRY_DSN=https://your-sentry-dsn
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

---

## Production Deployment

### Pre-deployment Checklist

- [ ] Database connection pooling configured
- [ ] Redis cluster setup (master-slave)
- [ ] Read replicas configured (optional)
- [ ] Celery workers running (3+ queues)
- [ ] Celery Beat scheduled
- [ ] Cache warming enabled
- [ ] Monitoring configured (Sentry, etc.)
- [ ] Health checks setup
- [ ] Load balancer configured
- [ ] CDN for static assets (optional)
- [ ] Profiling disabled
- [ ] Query logging disabled (or slow queries only)

### Scaling Guidelines

**Vertical Scaling** (single server):
- 2 CPU, 4GB RAM: ~50 concurrent users
- 4 CPU, 8GB RAM: ~100 concurrent users
- 8 CPU, 16GB RAM: ~200 concurrent users

**Horizontal Scaling** (multiple servers):
- API servers: 2+ behind load balancer
- Celery workers: 3+ per queue
- Database: 1 primary + 2 read replicas
- Redis: Master-slave replication

### Performance Targets

| Metric | Development | Production |
|--------|-------------|------------|
| Page Load (p95) | < 5s | < 2s |
| API Response (p95) | < 500ms | < 200ms |
| Database Query (avg) | < 100ms | < 50ms |
| Cache Hit Rate | > 50% | > 80% |
| Throughput | > 100 rps | > 1000 rps |
| Error Rate | < 10% | < 1% |

---

## Troubleshooting

### High Database CPU

**Symptoms**: Slow queries, high CPU usage

**Solutions**:
1. Check slow query log: `GET /api/v1/performance/slow-queries`
2. Verify indexes: `EXPLAIN ANALYZE` problematic queries
3. Increase connection pool: `DB_POOL_SIZE=40`
4. Enable read replicas: `DB_READ_REPLICAS_ENABLED=true`

### Low Cache Hit Rate

**Symptoms**: Cache hit rate < 70%

**Solutions**:
1. Check cache stats: `GET /api/v1/performance/cache/stats`
2. Increase TTL: `CACHE_DEFAULT_TTL=600`
3. Enable cache warming: `CACHE_WARMING_ENABLED=true`
4. Verify Redis connection
5. Increase memory cache size: `MEMORY_CACHE_SIZE=2000`

### High Memory Usage

**Symptoms**: Memory > 80%, OOM errors

**Solutions**:
1. Reduce connection pool: `DB_POOL_SIZE=10`
2. Reduce Celery concurrency: `CELERY_WORKER_CONCURRENCY=4`
3. Enable garbage collection tuning
4. Limit cache size: `MEMORY_CACHE_SIZE=500`
5. Restart workers periodically: `--max-tasks-per-child=1000`

### Slow API Responses

**Symptoms**: Response time > 200ms (p95)

**Solutions**:
1. Check N+1 queries: `GET /api/v1/performance/n1-queries`
2. Enable request compression: `COMPRESSION_ENABLED=true`
3. Enable response caching
4. Implement pagination for large datasets
5. Use background tasks for heavy operations

### Celery Tasks Stuck

**Symptoms**: Tasks in PENDING state, not processing

**Solutions**:
1. Check Flower dashboard: `http://localhost:5555`
2. Verify Redis connection: `redis-cli ping`
3. Restart Celery workers
4. Check task time limits: `CELERY_TIME_LIMIT=600`
5. Monitor worker logs: `celery -A app.workers.celery_app worker --loglevel=debug`

---

## Performance Testing

### Run Performance Tests

```bash
# Unit tests
python scripts/performance_test.py --mode unit

# Load tests
python scripts/performance_test.py --mode load --duration 60 --users 20

# All tests
python scripts/performance_test.py --mode all
```

### Benchmark Results

**Expected performance** (4 CPU, 8GB RAM):

```
Cache Performance:
  ✓ Write 1000 keys: 0.15s
  ✓ Read 1000 keys: 0.08s
  ✓ Hit rate: 95%
  ✓ Operations/sec: 4500

Database Performance:
  ✓ 100 simple queries: 0.12s
  ✓ Average query time: 1.2ms
  ✓ Queries/sec: 833

API Performance:
  ✓ Average response time: 85ms
  ✓ Min response time: 45ms
  ✓ Max response time: 180ms
```

---

## Additional Resources

- [Performance Optimization Summary](./PERFORMANCE_OPTIMIZATION_SUMMARY.md)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/optimizing.html)
- [FastAPI Performance](https://fastapi.tiangolo.com/deployment/concepts/)

---

**Last Updated**: December 2, 2025
**Version**: 1.0.0
