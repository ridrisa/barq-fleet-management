# BARQ Fleet Management - System Architecture

**Version:** 1.2.0
**Last Updated:** December 9, 2025

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Technology Stack](#technology-stack)
4. [System Components](#system-components)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Database Design](#database-design)
8. [Infrastructure Architecture](#infrastructure-architecture)
9. [Security Architecture](#security-architecture)
10. [Integration Points](#integration-points)
11. [Scalability & Performance](#scalability--performance)
12. [Disaster Recovery](#disaster-recovery)

---

## System Overview

BARQ Fleet Management is a comprehensive enterprise solution for managing fleet operations, courier workforce, and logistics operations. The system is built on modern cloud-native architecture leveraging Google Cloud Platform.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Web Browser │  │ Mobile App   │  │  Admin Panel │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────┴──────────────────────────────────┐
│                   API Gateway / CDN                          │
│              (Cloud Load Balancer + Cloud CDN)               │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐ ┌──────▼─────────┐ ┌─────▼──────────┐
│   Frontend     │ │   Backend API  │ │   WebSocket    │
│  (React SPA)   │ │  (FastAPI)     │ │   Server       │
│  Cloud Storage │ │  Cloud Run     │ │  Cloud Run     │
└────────────────┘ └────────┬───────┘ └────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐ ┌────────▼────────┐ ┌──────▼────────┐
│   PostgreSQL   │ │     Redis       │ │  Cloud Pub/Sub│
│   Cloud SQL    │ │  Memorystore    │ │               │
└────────────────┘ └─────────────────┘ └───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐ ┌────────▼────────┐ ┌──────▼────────┐
│   BigQuery     │ │  Cloud Storage  │ │ Secret Manager│
│  (Analytics)   │ │  (Files/Backups)│ │               │
└────────────────┘ └─────────────────┘ └───────────────┘
```

### Key Characteristics

- **Deployment Model:** Cloud-native (GCP)
- **Architecture Style:** Microservices-ready monolith
- **API Style:** RESTful + WebSocket
- **Data Storage:** PostgreSQL (primary), Redis (cache)
- **Authentication:** JWT + OAuth 2.0
- **Scalability:** Horizontal (Cloud Run auto-scaling)

---

## Architecture Principles

### 1. Cloud-Native First
- Containerized applications (Docker)
- Serverless compute (Cloud Run)
- Managed services (Cloud SQL, Redis, etc.)
- Auto-scaling and self-healing

### 2. API-First Design
- OpenAPI specification
- Versioned APIs (`/api/v1`)
- RESTful conventions
- Comprehensive documentation

### 3. Security by Design
- Zero-trust architecture
- End-to-end encryption
- Role-based access control (RBAC)
- Secrets management via Google Secret Manager

### 4. Observability
- Structured logging (Cloud Logging)
- Distributed tracing (Cloud Trace)
- Metrics and monitoring (Cloud Monitoring)
- Real-time alerting

### 5. Data Integrity
- ACID transactions
- Database constraints
- Validation at multiple layers
- Audit trails for critical operations

### 6. Scalability
- Horizontal scaling
- Database connection pooling
- Redis caching layer
- CDN for static assets

---

## Technology Stack

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.104.1 | Web framework |
| Language | Python | 3.11+ | Programming language |
| ORM | SQLAlchemy | 2.0 | Database ORM |
| Migration | Alembic | 1.12+ | Database migrations |
| Validation | Pydantic | 2.0+ | Data validation |
| Authentication | JWT | PyJWT 2.8+ | Token-based auth |
| Task Queue | Celery | 5.3+ | Background jobs |
| WSGI Server | Uvicorn | 0.24+ | ASGI server |

### Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18.2+ | UI framework |
| Language | TypeScript | 5.0+ | Type safety |
| Routing | React Router | 6.0+ | Client-side routing |
| State | React Query | 4.0+ | Server state management |
| Styling | Tailwind CSS | 3.0+ | Utility-first CSS |
| Build Tool | Vite | 5.0+ | Fast build tool |
| Icons | Lucide React | Latest | Icon library |

### Database

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Primary DB | PostgreSQL | 16 | Relational database |
| Cache | Redis | 7.0 | Caching layer |
| Analytics | BigQuery | - | Data warehouse |

### Infrastructure (GCP)

| Service | Purpose |
|---------|---------|
| Cloud Run | Container hosting |
| Cloud SQL | Managed PostgreSQL |
| Memorystore | Managed Redis |
| Cloud Storage | Object storage |
| Cloud Load Balancing | Load distribution |
| Cloud CDN | Content delivery |
| Secret Manager | Secrets management |
| Cloud Logging | Log aggregation |
| Cloud Monitoring | Metrics & alerts |
| Cloud Build | CI/CD pipeline |
| Container Registry | Docker image storage |

### DevOps

| Tool | Purpose |
|------|---------|
| Docker | Containerization |
| GitHub Actions | CI/CD |
| Terraform | Infrastructure as Code |
| Pytest | Backend testing |
| Vitest | Frontend testing |
| Black | Python code formatting |
| ESLint | JavaScript linting |
| Prettier | Code formatting |

---

## System Components

### 1. API Gateway Layer

**Purpose:** Entry point for all client requests

**Components:**
- Cloud Load Balancer (HTTPS termination)
- Cloud Armor (DDoS protection)
- Cloud CDN (static asset caching)

**Features:**
- SSL/TLS termination
- Rate limiting
- Request routing
- Static file serving

### 2. Application Layer

**Purpose:** Business logic and API endpoints

**Components:**
- FastAPI application (Cloud Run)
- WebSocket server (Cloud Run)
- Background job workers (Cloud Run Jobs)

**Features:**
- RESTful API endpoints (750+)
- WebSocket connections (real-time)
- Background job processing
- Auto-scaling (0-100 instances)

### 3. Data Layer

**Purpose:** Data persistence and caching

**Components:**
- Cloud SQL (PostgreSQL)
- Memorystore (Redis)
- Cloud Storage (files)
- BigQuery (analytics)

**Features:**
- ACID transactions
- Read replicas
- Automated backups
- Point-in-time recovery

### 4. Integration Layer

**Purpose:** External service integration

**Components:**
- Google OAuth 2.0
- SMTP (email)
- SMS gateway
- Payment gateways

---

## Backend Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────┐
│           API Layer (FastAPI)               │
│  - Route handlers                           │
│  - Request/response serialization           │
│  - OpenAPI documentation                    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Service Layer                      │
│  - Business logic                           │
│  - Data orchestration                       │
│  - Transaction management                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Repository Layer                   │
│  - Database operations                      │
│  - Query building                           │
│  - Data mapping                             │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Data Layer                         │
│  - SQLAlchemy models                        │
│  - Database connections                     │
│  - Migration scripts                        │
└─────────────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py              # Authentication endpoints
│   │       ├── fleet/               # Fleet management
│   │       │   ├── couriers.py
│   │       │   ├── vehicles.py
│   │       │   └── assignments.py
│   │       ├── hr/                  # HR & Finance
│   │       │   ├── attendance.py
│   │       │   ├── payroll.py
│   │       │   └── loans.py
│   │       ├── operations/          # Operations
│   │       ├── accommodation/       # Accommodation
│   │       ├── workflow/            # Workflow engine
│   │       ├── support/             # Support tickets
│   │       └── admin/               # Administration
│   ├── models/                      # SQLAlchemy models
│   │   ├── fleet/
│   │   ├── hr/
│   │   └── ...
│   ├── schemas/                     # Pydantic schemas
│   │   ├── fleet/
│   │   ├── hr/
│   │   └── ...
│   ├── services/                    # Business logic
│   │   ├── fleet_service.py
│   │   ├── hr_service.py
│   │   └── ...
│   ├── core/                        # Core utilities
│   │   ├── security.py              # Auth & security
│   │   ├── config.py                # Configuration
│   │   └── exceptions.py            # Custom exceptions
│   ├── config/                      # Configuration
│   │   ├── settings.py              # App settings
│   │   └── database.py              # DB connection
│   └── main.py                      # Application entry
├── alembic/                         # Database migrations
│   └── versions/
├── tests/                           # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── Dockerfile                       # Container definition
└── requirements.txt                 # Python dependencies
```

### Request Flow

```
1. Client Request
   ↓
2. FastAPI Route Handler
   ↓
3. Authentication Middleware
   ↓
4. Request Validation (Pydantic)
   ↓
5. Service Layer (Business Logic)
   ↓
6. Repository Layer (Database)
   ↓
7. Response Serialization
   ↓
8. Client Response
```

### Key Patterns

#### 1. Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/couriers")
def get_couriers(db: Session = Depends(get_db)):
    return courier_service.get_all(db)
```

#### 2. Service Layer Pattern

```python
class CourierService:
    def __init__(self, db: Session):
        self.db = db

    def create_courier(self, data: CourierCreate):
        # Business logic
        courier = Courier(**data.dict())
        self.db.add(courier)
        self.db.commit()
        return courier
```

#### 3. Repository Pattern

```python
class CourierRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, courier_id: str):
        return self.db.query(Courier).filter(
            Courier.id == courier_id
        ).first()
```

---

## Frontend Architecture

### Component Architecture

```
┌─────────────────────────────────────────────┐
│           Pages Layer                       │
│  - Route components                         │
│  - Page layouts                             │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Feature Components                 │
│  - Domain-specific UI                       │
│  - Business logic components                │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          Shared Components                  │
│  - Reusable UI components                   │
│  - Forms, tables, modals                    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          State Management                   │
│  - React Query (server state)               │
│  - Context API (UI state)                   │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│          API Layer                          │
│  - HTTP client (axios)                      │
│  - API service functions                    │
└─────────────────────────────────────────────┘
```

### Directory Structure

```
frontend/
├── src/
│   ├── pages/                       # Route pages
│   │   ├── fleet/
│   │   │   ├── CouriersPage.tsx
│   │   │   ├── VehiclesPage.tsx
│   │   │   └── AssignmentsPage.tsx
│   │   ├── hr/
│   │   ├── operations/
│   │   └── ...
│   ├── components/                  # Reusable components
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── forms/
│   │   ├── tables/
│   │   └── modals/
│   ├── hooks/                       # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useCouriers.ts
│   │   └── ...
│   ├── services/                    # API services
│   │   ├── api.ts                   # Axios instance
│   │   ├── courierService.ts
│   │   ├── vehicleService.ts
│   │   └── ...
│   ├── types/                       # TypeScript types
│   │   ├── courier.types.ts
│   │   ├── vehicle.types.ts
│   │   └── ...
│   ├── utils/                       # Utilities
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── ...
│   ├── contexts/                    # React contexts
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── App.tsx                      # Root component
│   └── main.tsx                     # Entry point
├── public/                          # Static assets
├── index.html
└── package.json
```

### State Management Strategy

#### 1. Server State (React Query)

```typescript
// Fetching data
const { data, isLoading } = useQuery(
  ['couriers'],
  courierService.getAll
);

// Mutations
const mutation = useMutation(
  courierService.create,
  {
    onSuccess: () => {
      queryClient.invalidateQueries(['couriers']);
    }
  }
);
```

#### 2. UI State (Context API)

```typescript
// AuthContext for authentication state
const { user, login, logout } = useAuth();

// ThemeContext for UI preferences
const { theme, toggleTheme } = useTheme();
```

### Routing Structure

```
/                           → Dashboard
/fleet
  /couriers                 → Couriers list
  /couriers/:id             → Courier details
  /vehicles                 → Vehicles list
  /vehicles/:id             → Vehicle details
  /assignments              → Assignments
/hr
  /attendance               → Attendance
  /payroll                  → Payroll
  /loans                    → Loans
/operations
  /deliveries               → Deliveries
  /incidents                → Incidents
/accommodation
  /buildings                → Buildings
  /rooms                    → Rooms
/admin
  /users                    → User management
  /roles                    → Role management
```

---

## Database Design

### Schema Overview

**Total Tables: 93+** (See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for complete documentation)

```
Core Module (8 tables):
├── users                 (System users with Argon2 hashing)
├── roles                 (User roles with hierarchy)
├── permissions           (Fine-grained access control)
├── audit_logs            (Complete system audit trail)
├── password_reset_tokens (Secure password reset)
├── organizations         (Multi-tenant organizations)
├── organization_users    (Org membership with roles)
└── system_settings       (Global configuration)

Fleet Module (11 tables):
├── couriers              (60+ columns with full profiles)
├── vehicles              (40+ columns with tracking)
├── courier_vehicles      (Assignment history)
├── vehicle_logs          (Daily operations logs)
├── fuel_logs             (Fuel consumption tracking)
├── maintenance_records   (Service history)
├── inspections           (Digital checklists)
├── documents             (Document management)
├── accident_logs         (Incident records)
├── vehicle_assignments   (Active assignments)
└── courier_documents     (Driver documents)

HR & Finance Module (7 tables):
├── salaries              (Payroll with deductions)
├── loans                 (Loan management & tracking)
├── leave_requests        (Leave workflow)
├── attendance            (Clock in/out, shifts)
├── assets                (Asset allocation)
├── bonuses               (Performance incentives)
└── gosi_records          (Saudi insurance)

Operations Module (15 tables):
├── deliveries            (Full delivery lifecycle)
├── routes                (Route planning, 30+ columns)
├── zones                 (Delivery zones)
├── dispatch_assignments  (Real-time dispatch)
├── priority_queue_entries (SLA-based queuing)
├── sla_definitions       (SLA rules)
├── sla_tracking          (SLA monitoring)
├── cod_collections       (Cash on delivery)
├── incidents             (Incident management)
├── feedback              (Customer feedback)
├── handovers             (Shift handovers)
├── quality_checks        (Quality assurance)
├── operation_settings    (Configuration)
├── scheduled_deliveries  (Scheduling)
└── operation_documents   (Procedures/policies)

Workflow Module (20+ tables):
├── workflow_templates    (Reusable templates)
├── workflow_instances    (Active executions)
├── workflow_steps        (Step definitions)
├── approval_chains       (Multi-level approvals)
├── approval_requests     (Approval tracking)
├── workflow_automation   (Rule-based automation)
├── workflow_triggers     (Event triggers)
├── workflow_sla          (SLA management)
├── workflow_notifications (Multi-channel alerts)
├── workflow_history      (Complete audit trail)
└── workflow_analytics    (Performance metrics)

Accommodation Module (4 tables):
├── buildings             (Properties)
├── rooms                 (Room inventory)
├── beds                  (Bed-level tracking)
└── allocations           (Occupancy management)

Support Module (12 tables):
├── tickets               (Multi-channel support)
├── ticket_replies        (Conversation threads)
├── ticket_attachments    (File attachments)
├── ticket_templates      (Response templates)
├── canned_responses      (Quick replies)
├── faq                   (FAQ management)
├── kb_categories         (Knowledge base categories)
├── kb_articles           (Help articles)
├── chat_sessions         (Live chat)
├── chat_messages         (Chat history)
├── feedback              (Support feedback)
└── contact_forms         (Customer inquiries)

Analytics Module (6 tables):
├── dashboards            (Custom dashboards)
├── kpi_definitions       (KPI configuration)
├── metric_snapshots      (Historical metrics)
├── performance_data      (Performance tracking)
├── reports               (Report definitions)
└── scheduled_reports     (Report scheduling)

Admin Module (4 tables):
├── api_keys              (API key management)
├── backups               (Backup records)
├── integrations          (Third-party integrations)
└── system_monitoring     (Health metrics)

Integrations Module (2 tables):
├── syarah_fuel_transactions (Fuel card integration)
└── platform_orders       (External platform orders)
```

### Key Relationships

```
couriers (1) ←→ (1) courier_vehicles ←→ (1) vehicles
couriers (1) ←→ (n) attendance
couriers (1) ←→ (n) payroll
couriers (1) ←→ (n) loans
couriers (1) ←→ (n) deliveries
couriers (1) ←→ (n) room_assignments
vehicles (1) ←→ (n) vehicle_logs
vehicles (1) ←→ (n) incidents
```

### Indexing Strategy

**Primary Indexes:**
- All `id` columns (UUID primary keys)
- Foreign key columns

**Secondary Indexes:**
- `couriers.email` (unique)
- `couriers.national_id` (unique)
- `couriers.status`
- `vehicles.plate_number` (unique)
- `vehicles.status`
- `deliveries.status`
- `attendance.date`

**Composite Indexes:**
- `(courier_id, date)` on attendance
- `(courier_id, month, year)` on payroll
- `(vehicle_id, created_at)` on vehicle_logs

---

## Infrastructure Architecture

### Google Cloud Platform Setup

```
┌─────────────────────────────────────────────────────┐
│                   GCP Project                       │
│                   barq-production                   │
└─────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌───────▼──────┐ ┌──────▼────────┐
│  Compute     │ │   Data       │ │  Networking   │
│              │ │              │ │               │
│ Cloud Run    │ │ Cloud SQL    │ │ Load Balancer │
│ (API)        │ │ (PostgreSQL) │ │ Cloud CDN     │
│              │ │              │ │ Cloud Armor   │
│ Cloud Run    │ │ Memorystore  │ │ VPC           │
│ (WebSocket)  │ │ (Redis)      │ │               │
│              │ │              │ │               │
│ Cloud Run    │ │ Cloud Storage│ │               │
│ Jobs (Celery)│ │ (Files)      │ │               │
│              │ │              │ │               │
│              │ │ BigQuery     │ │               │
└──────────────┘ └──────────────┘ └───────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
┌─────────────────────────▼───────────────────────────┐
│              Management & Security                  │
│                                                     │
│  Secret Manager │ Cloud Logging │ Cloud Monitoring │
│  IAM & Admin    │ Cloud Trace   │ Error Reporting  │
└─────────────────────────────────────────────────────┘
```

### Cloud Run Configuration

```yaml
service: barq-api
region: us-central1
platform: managed

spec:
  containers:
    - image: gcr.io/barq-production/api:latest
      resources:
        limits:
          memory: 1Gi
          cpu: 2

  scaling:
    minInstances: 1
    maxInstances: 100

  autoscaling:
    target:
      concurrency: 80
      cpuUtilization: 70

  timeout: 300s

  environment:
    - DATABASE_URL (from Secret Manager)
    - REDIS_URL (from Secret Manager)
    - JWT_SECRET_KEY (from Secret Manager)
```

### Cloud SQL Configuration

```yaml
instance: barq-production-db
version: POSTGRES_16
tier: db-custom-4-16384  # 4 vCPU, 16 GB RAM

settings:
  backupConfiguration:
    enabled: true
    startTime: "03:00"  # UTC
    pointInTimeRecoveryEnabled: true

  ipConfiguration:
    privateNetwork: projects/barq/global/networks/vpc
    requireSsl: true

  maintenanceWindow:
    day: 7  # Sunday
    hour: 4  # 4 AM UTC

  flags:
    - max_connections: 200
    - shared_buffers: 4GB
    - effective_cache_size: 12GB
```

### Networking

```
Internet
   │
   ▼
Cloud Load Balancer (HTTPS)
   │
   ├─► Cloud CDN (static files)
   │
   ├─► Cloud Armor (DDoS protection)
   │
   ▼
VPC Network (private)
   │
   ├─► Cloud Run (API)
   │   └─► Cloud SQL Proxy
   │       └─► Cloud SQL (private IP)
   │
   └─► Memorystore (Redis, private IP)
```

---

## Security Architecture

### Authentication Flow

```
1. User submits credentials
   ↓
2. API validates credentials
   ↓
3. Generate JWT token (30 min expiry)
   ↓
4. Return token to client
   ↓
5. Client includes token in Authorization header
   ↓
6. API validates token on each request
   ↓
7. Extract user info from token
   ↓
8. Check permissions (RBAC)
   ↓
9. Process request
```

### Role-Based Access Control (RBAC)

```
Roles:
  admin         → Full system access
  manager       → Fleet management, approvals
  hr_manager    → HR & finance access
  operations    → Operations access
  courier       → Limited self-service access
  support       → Support ticket access

Permissions:
  couriers.read
  couriers.create
  couriers.update
  couriers.delete
  vehicles.read
  vehicles.create
  ...
```

### Security Layers

1. **Network Security**
   - Cloud Armor (DDoS protection)
   - VPC with private subnets
   - Cloud SQL private IP
   - SSL/TLS encryption

2. **Application Security**
   - JWT authentication
   - RBAC authorization
   - Input validation (Pydantic)
   - SQL injection prevention (SQLAlchemy)
   - XSS protection
   - CSRF tokens

3. **Data Security**
   - Encrypted at rest (Cloud SQL encryption)
   - Encrypted in transit (TLS)
   - Sensitive data in Secret Manager
   - Password hashing (bcrypt)

4. **API Security**
   - Rate limiting
   - API key validation
   - CORS configuration
   - Request size limits

---

## Integration Points

### External Services

1. **Google OAuth 2.0**
   - User authentication
   - Single sign-on (SSO)

2. **SMTP Email**
   - Transactional emails
   - Notifications

3. **SMS Gateway**
   - SMS notifications
   - OTP verification

4. **Payment Gateway**
   - Payroll processing
   - Loan disbursement

5. **BigQuery**
   - Data warehouse
   - Analytics and reporting

6. **Cloud Storage**
   - Document storage
   - Backup storage

---

## Scalability & Performance

### Horizontal Scaling

- **Cloud Run:** Auto-scales 1-100 instances
- **Database:** Read replicas for read-heavy operations
- **Redis:** Cluster mode for cache distribution

### Performance Optimizations

1. **Database**
   - Connection pooling (max 20 connections)
   - Query optimization
   - Indexes on frequently queried columns
   - Materialized views for complex reports

2. **Caching**
   - Redis for frequently accessed data
   - TTL-based cache invalidation
   - Cache warming for critical data

3. **API**
   - Response compression (gzip)
   - Pagination (limit 100 records/page)
   - Field selection (sparse fieldsets)

4. **Frontend**
   - Code splitting
   - Lazy loading
   - CDN for static assets
   - Image optimization

### Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (P95) | < 500ms |
| Database Query Time (avg) | < 100ms |
| Page Load Time | < 2s |
| Time to Interactive | < 3s |
| Uptime | 99.9% |

---

## Disaster Recovery

### Backup Strategy

1. **Database Backups**
   - Automated daily backups (Cloud SQL)
   - 30-day retention
   - Point-in-time recovery (7 days)

2. **File Backups**
   - Cloud Storage versioning
   - 90-day retention

3. **Application Backups**
   - Container images in Container Registry
   - Indefinite retention

### Recovery Procedures

**RTO (Recovery Time Objective):** 1 hour
**RPO (Recovery Point Objective):** 24 hours

**Disaster Recovery Steps:**
1. Assess incident severity
2. Notify stakeholders
3. Restore database from backup
4. Deploy last known good version
5. Verify system functionality
6. Resume normal operations

---

## Monitoring & Observability

### Metrics

- Request rate (requests/second)
- Error rate (errors/total requests)
- Response time (P50, P95, P99)
- CPU utilization
- Memory utilization
- Database connections

### Logging

- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Centralized logging (Cloud Logging)
- 90-day retention

### Tracing

- Distributed tracing (Cloud Trace)
- Request correlation IDs
- Performance bottleneck identification

### Alerts

- High error rate (>5%)
- High response time (>2s P95)
- Database connection failures
- Memory usage >90%

---

**Document Owner:** Engineering Team
**Review Cycle:** Quarterly
**Last Reviewed:** December 9, 2025
**Next Review:** March 9, 2026
