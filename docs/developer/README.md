# BARQ Fleet Management - Developer Guide

## Welcome

Welcome to the BARQ Fleet Management developer documentation. This guide will help you set up your development environment, understand the architecture, and contribute to the project.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture Overview](#architecture-overview)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Contributing](#contributing)
8. [Resources](#resources)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

**Required:**
- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **PostgreSQL** 14+ (database)
- **Redis** 7+ (caching and sessions)
- **Docker** & **Docker Compose** (recommended)
- **Git** 2.30+

**Optional:**
- **VS Code** with recommended extensions
- **Postman** or **Insomnia** (API testing)
- **pgAdmin** or **TablePlus** (database management)

### Quick Setup

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/barq-fleet-clean.git
cd barq-fleet-clean
```

#### 2. Using Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Access API docs
open http://localhost:8000/docs
```

#### 3. Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Create admin user
python create_admin.py

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

**Database:**
```bash
# Create database
createdb barq_fleet

# Or using PostgreSQL CLI
psql -U postgres
CREATE DATABASE barq_fleet;
\q
```

### Environment Configuration

**Backend (.env):**
```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/barq_fleet

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Redis
REDIS_URL=redis://localhost:6379/0

# Environment
ENVIRONMENT=development
DEBUG=True
```

**Frontend (.env.local):**
```bash
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_ENVIRONMENT=development
```

### Verify Installation

```bash
# Backend health check
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"healthy","version":"1.0.0","database":"connected"}

# Frontend
open http://localhost:5173
```

---

## Architecture Overview

BARQ Fleet Management follows a modern, scalable architecture:

### High-Level Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│  Database   │
│  (React)    │      │  (FastAPI)   │      │ (PostgreSQL)│
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Redis     │
                     │  (Cache)     │
                     └──────────────┘
```

### Technology Stack

**Frontend:**
- **Framework:** React 18 with TypeScript
- **Routing:** React Router v6
- **State Management:** Zustand + React Query
- **UI Library:** Custom components with Tailwind CSS
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts
- **HTTP Client:** Axios
- **Build Tool:** Vite

**Backend:**
- **Framework:** FastAPI 0.104.1
- **Language:** Python 3.11+
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Authentication:** JWT + OAuth 2.0
- **Task Queue:** Celery + Redis
- **Async:** HTTPX, aiofiles

**Database:**
- **Primary:** PostgreSQL 14+
- **Cache:** Redis 7+
- **ORM:** SQLAlchemy 2.0 with async support

**Infrastructure:**
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions + Google Cloud Build
- **Cloud:** Google Cloud Platform (Cloud Run, Cloud SQL)
- **Monitoring:** Cloud Logging, Cloud Monitoring

### Architecture Principles

1. **Separation of Concerns:** Frontend, backend, and database are decoupled
2. **API-First:** Backend exposes RESTful APIs consumed by frontend
3. **Security:** JWT authentication, RBAC, input validation
4. **Scalability:** Horizontal scaling with Cloud Run
5. **Performance:** Redis caching, database indexing, query optimization
6. **Maintainability:** Clean code, comprehensive tests, documentation

---

## Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core configuration
│   │   ├── config.py           # Settings and configuration
│   │   ├── security.py         # Security utilities
│   │   ├── database.py         # Database connection
│   │   └── cache.py            # Redis cache
│   ├── api/                    # API routes
│   │   ├── v1/                 # API version 1
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── fleet/          # Fleet management
│   │   │   ├── hr/             # HR management
│   │   │   ├── operations/     # Operations
│   │   │   ├── admin/          # Admin
│   │   │   └── ...
│   │   ├── analytics/          # Analytics endpoints
│   │   └── workflow/           # Workflow engine
│   ├── models/                 # SQLAlchemy models
│   │   ├── base.py             # Base model
│   │   ├── user.py             # User model
│   │   ├── fleet/              # Fleet models
│   │   ├── hr/                 # HR models
│   │   └── ...
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py             # Auth schemas
│   │   ├── fleet/              # Fleet schemas
│   │   └── ...
│   ├── crud/                   # Database operations
│   │   ├── base.py             # Base CRUD
│   │   ├── fleet/              # Fleet CRUD
│   │   └── ...
│   ├── services/               # Business logic
│   │   ├── fleet/              # Fleet services
│   │   ├── analytics/          # Analytics services
│   │   └── ...
│   ├── utils/                  # Utility functions
│   │   ├── email.py            # Email utilities
│   │   ├── export.py           # Export utilities
│   │   └── ...
│   └── middleware/             # Custom middleware
│       ├── auth.py             # Auth middleware
│       └── logging.py          # Logging middleware
├── alembic/                    # Database migrations
│   └── versions/               # Migration files
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── pytest.ini                  # Pytest configuration
└── alembic.ini                 # Alembic configuration
```

### Frontend Structure

```
frontend/
├── src/
│   ├── main.tsx                # Application entry point
│   ├── App.tsx                 # Root component
│   ├── router/                 # Routing configuration
│   │   └── index.tsx           # Route definitions
│   ├── pages/                  # Page components
│   │   ├── Dashboard.tsx       # Dashboard page
│   │   ├── fleet/              # Fleet pages
│   │   ├── hr/                 # HR pages
│   │   └── ...
│   ├── components/             # Reusable components
│   │   ├── ui/                 # UI primitives
│   │   ├── forms/              # Form components
│   │   ├── charts/             # Chart components
│   │   └── layout/             # Layout components
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.ts          # Authentication hook
│   │   ├── useApi.ts           # API hook
│   │   └── ...
│   ├── lib/                    # Library code
│   │   ├── api.ts              # API client
│   │   ├── auth.ts             # Auth utilities
│   │   └── utils.ts            # Utility functions
│   ├── stores/                 # Zustand stores
│   │   ├── authStore.ts        # Auth state
│   │   └── ...
│   ├── types/                  # TypeScript types
│   │   ├── api.ts              # API types
│   │   ├── models.ts           # Model types
│   │   └── ...
│   ├── config/                 # Configuration
│   │   └── constants.ts        # Constants
│   ├── i18n/                   # Internationalization
│   │   ├── en.json             # English translations
│   │   └── ar.json             # Arabic translations
│   └── styles/                 # Global styles
│       └── globals.css         # Global CSS
├── public/                     # Static assets
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # Playwright E2E tests
├── package.json                # NPM dependencies
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
└── tailwind.config.js          # Tailwind CSS configuration
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/add-vehicle-tracking
```

### 2. Make Changes

Follow the coding standards and best practices outlined below.

### 3. Write Tests

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm run test
```

### 4. Run Linters

```bash
# Backend
cd backend
black app/ tests/
flake8 app/ tests/

# Frontend
cd frontend
npm run lint
npm run type-check
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add vehicle tracking feature"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build/config changes

### 6. Push and Create PR

```bash
git push origin feature/add-vehicle-tracking
```

Create a pull request on GitHub with:
- Clear description of changes
- Link to related issues
- Screenshots (if UI changes)
- Test coverage report

### 7. Code Review

- Address reviewer feedback
- Ensure CI/CD checks pass
- Get at least one approval

### 8. Merge

Squash and merge to main branch.

---

## Coding Standards

### Backend (Python)

**Style Guide:** PEP 8

```python
# Use type hints
def get_courier(db: Session, courier_id: int) -> Optional[Courier]:
    """Get courier by ID.

    Args:
        db: Database session
        courier_id: Courier ID

    Returns:
        Courier object or None if not found
    """
    return db.query(Courier).filter(Courier.id == courier_id).first()

# Use Pydantic for validation
class CourierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^[0-9+\-\(\) ]+$")

# Use async when appropriate
async def send_notification(user_id: int, message: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(NOTIFICATION_URL, json={"user_id": user_id, "message": message})
```

**Best Practices:**
- Use `black` for formatting
- Use `flake8` for linting
- Use `mypy` for type checking
- Write docstrings for all functions
- Keep functions small and focused
- Use dependency injection
- Handle exceptions explicitly

### Frontend (TypeScript/React)

**Style Guide:** Airbnb JavaScript Style Guide

```typescript
// Use TypeScript interfaces
interface Courier {
  id: number;
  name: string;
  email: string;
  status: 'active' | 'inactive';
}

// Use functional components with hooks
const CourierList: React.FC = () => {
  const [couriers, setCouriers] = useState<Courier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCouriers();
  }, []);

  const fetchCouriers = async () => {
    try {
      const response = await api.get<Courier[]>('/fleet/couriers');
      setCouriers(response.data);
    } catch (error) {
      console.error('Failed to fetch couriers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="courier-list">
      {couriers.map(courier => (
        <CourierCard key={courier.id} courier={courier} />
      ))}
    </div>
  );
};
```

**Best Practices:**
- Use functional components
- Use TypeScript for type safety
- Use React Query for data fetching
- Keep components small and focused
- Extract reusable logic into hooks
- Use proper error boundaries
- Follow accessibility guidelines (a11y)

### Database

```python
# Use proper indexing
class Courier(Base):
    __tablename__ = "couriers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    status = Column(Enum(CourierStatus), index=True, default=CourierStatus.ACTIVE)

    # Add foreign key indexes
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    # Add composite indexes for common queries
    __table_args__ = (
        Index('idx_courier_status_city', 'status', 'city'),
    )
```

**Best Practices:**
- Index foreign keys
- Index commonly queried columns
- Use composite indexes for multi-column queries
- Add proper constraints (unique, not null)
- Use migrations for schema changes
- Never run migrations directly on production

---

## Testing

### Backend Testing

```python
# Unit test example
import pytest
from app.services.fleet.courier_service import CourierService

def test_create_courier(db_session):
    courier_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+966501234567"
    }

    courier = CourierService.create(db_session, courier_data)

    assert courier.id is not None
    assert courier.name == "John Doe"
    assert courier.email == "john@example.com"

# Integration test example
def test_courier_api(client, auth_headers):
    response = client.post(
        "/api/v1/fleet/couriers",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+966501234567"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Doe"
```

**Run Tests:**
```bash
# All tests
pytest

# Specific file
pytest tests/unit/test_courier_service.py

# With coverage
pytest --cov=app --cov-report=html

# Parallel execution
pytest -n auto
```

### Frontend Testing

```typescript
// Component test
import { render, screen, waitFor } from '@testing-library/react';
import { CourierList } from './CourierList';

describe('CourierList', () => {
  it('renders courier list', async () => {
    const mockCouriers = [
      { id: 1, name: 'John Doe', email: 'john@example.com' },
      { id: 2, name: 'Jane Doe', email: 'jane@example.com' }
    ];

    jest.spyOn(api, 'get').mockResolvedValue({ data: mockCouriers });

    render(<CourierList />);

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    });
  });
});
```

**Run Tests:**
```bash
# All tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# E2E tests
npm run test:e2e
```

---

## Contributing

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Write/update tests**
5. **Update documentation**
6. **Submit a pull request**

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No new warnings
```

### Code Review Process

1. **Automated Checks:** CI/CD must pass
2. **Code Quality:** Linters and formatters must pass
3. **Tests:** All tests must pass with adequate coverage
4. **Review:** At least one approval required
5. **Documentation:** Update relevant documentation

---

## Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tools
- [VS Code Extensions](./tools.md#vs-code-extensions)
- [Docker Commands](./tools.md#docker-commands)
- [Database Tools](./tools.md#database-tools)

### Internal Docs
- [API Documentation](../api/README.md)
- [Deployment Guide](../deployment/README.md)
- [Architecture Details](./architecture.md)
- [Database Schema](./database-schema.md)

---

## Support

- **Slack:** #barq-dev
- **Email:** dev-team@barq.com
- **Wiki:** https://wiki.barq.com
- **Issues:** GitHub Issues

---

**Last Updated:** December 2, 2025
**Maintained By:** BARQ Development Team
