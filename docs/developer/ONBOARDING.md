# BARQ Fleet Management - Developer Onboarding Guide

Welcome to the BARQ Fleet Management development team! This guide will help you get up and running quickly.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Day 1 Setup](#day-1-setup)
3. [Week 1 Goals](#week-1-goals)
4. [Development Environment](#development-environment)
5. [IDE Setup](#ide-setup)
6. [Architecture Overview](#architecture-overview)
7. [Common Tasks](#common-tasks)
8. [Testing](#testing)
9. [Git Workflow](#git-workflow)
10. [Resources](#resources)

---

## Prerequisites

Before starting, ensure you have the following installed:

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | 4.x+ | Container runtime |
| Node.js | 18.x+ | Frontend development |
| Python | 3.11+ | Backend development |
| Git | 2.x+ | Version control |
| VS Code | Latest | Recommended IDE |

**Optional but recommended:**
- PostgreSQL client (`psql`) for database debugging
- Redis CLI for cache inspection
- Postman/Insomnia for API testing

---

## Day 1 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ridrisa/barq-fleet-management.git
cd barq-fleet-management
```

### 2. Set Up Environment Variables

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env.development
```

### 3. Start Development Environment

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check services are running
docker-compose ps
```

### 4. Run Database Migrations

```bash
# Enter backend container
docker-compose exec backend bash

# Inside container, run migrations
alembic upgrade head

# Seed initial data (optional)
python -m scripts.seed_data
```

### 5. Verify Setup

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| Swagger Docs | http://localhost:8000/api/v1/docs | - |
| Database | localhost:5432 | postgres/postgres |

### 6. Run Test Suite

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm run test
```

**Checklist:**
- [ ] Repository cloned
- [ ] Docker Desktop running
- [ ] Environment variables configured
- [ ] Services running (`docker-compose ps`)
- [ ] Database migrations applied
- [ ] Swagger UI accessible
- [ ] Test suite passing

---

## Week 1 Goals

### Day 1-2: Environment & Exploration
- [ ] Complete Day 1 setup
- [ ] Read through ARCHITECTURE.md
- [ ] Explore the codebase structure
- [ ] Review DATABASE_SCHEMA.md
- [ ] Access Swagger UI and test a few endpoints

### Day 3: First Bug Fix
- [ ] Pick a "good first issue" from the issue tracker
- [ ] Create a feature branch
- [ ] Make the fix
- [ ] Write/update tests
- [ ] Submit PR for review

### Day 4: Understanding Auth Flow
- [ ] Read docs/api/authentication.md
- [ ] Trace login flow through code
- [ ] Understand JWT token handling
- [ ] Review RBAC implementation

### Day 5: Code Review & Pairing
- [ ] Pair programming session with team lead
- [ ] Review 2-3 open PRs
- [ ] Ask questions about patterns/decisions

---

## Development Environment

### Project Structure

```
barq-fleet-management/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Core utilities (auth, config)
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── alembic/            # Database migrations
│   └── tests/              # Backend tests
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── stores/         # Zustand state stores
│   │   ├── lib/            # API client, utilities
│   │   └── schemas/        # Zod validation schemas
│   └── e2e/                # Playwright E2E tests
├── docs/                   # Documentation
├── terraform/              # Infrastructure as code
└── docker-compose.yml      # Local development setup
```

### Running Services Individually

```bash
# Backend only (hot reload)
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend only (hot reload)
cd frontend
npm run dev

# Database only
docker-compose up -d postgres

# All services except frontend (for frontend development)
docker-compose up -d postgres backend
```

### Useful Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Rebuild containers
docker-compose up -d --build

# Clean up
docker-compose down -v  # Warning: removes data!
```

---

## IDE Setup

### VS Code

#### Recommended Extensions

```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-azuretools.vscode-docker",
    "mtxr.sqltools",
    "redhat.vscode-yaml"
  ]
}
```

#### Python Settings

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./backend/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.mypyEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

#### Debug Configuration

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env"
    },
    {
      "name": "Backend: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "cwd": "${workspaceFolder}/backend"
    },
    {
      "name": "Frontend: Chrome",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000",
      "webRoot": "${workspaceFolder}/frontend/src"
    }
  ]
}
```

### PyCharm

1. Open `backend/` as a project
2. Configure Python interpreter from `.venv`
3. Enable FastAPI support in Settings → Languages & Frameworks → FastAPI
4. Mark `app/` as Sources Root

### WebStorm

1. Open `frontend/` as a project
2. Run `npm install`
3. Configure ESLint in Settings → Languages & Frameworks → JavaScript → Code Quality Tools

---

## Architecture Overview

### Backend (FastAPI)

```
Request → Router → Dependency Injection → Service → Repository → Database
                         ↓
                   Authentication
                   Authorization
                   Validation
```

**Key Concepts:**
- **Routers**: Handle HTTP endpoints (`app/api/v1/`)
- **Services**: Business logic (`app/services/`)
- **Schemas**: Request/response validation (`app/schemas/`)
- **Models**: Database models (`app/models/`)
- **Dependencies**: Auth, DB session injection (`app/core/dependencies.py`)

### Frontend (React + TypeScript)

```
Component → Hooks (React Query) → API Client → Backend
              ↓
         State (Zustand)
              ↓
         UI Components (shadcn/ui)
```

**Key Concepts:**
- **Pages**: Route-level components (`src/pages/`)
- **Components**: Reusable UI (`src/components/`)
- **Stores**: Global state with Zustand (`src/stores/`)
- **API**: API client functions (`src/lib/api.ts`)
- **Schemas**: Zod validation (`src/schemas/`)

### Authentication Flow

1. User submits credentials to `/auth/login`
2. Backend validates and returns JWT token
3. Frontend stores token in memory (Zustand) and localStorage
4. All subsequent requests include `Authorization: Bearer <token>`
5. Backend middleware validates token on protected routes
6. Token expiry triggers refresh or logout

---

## Common Tasks

### Adding a New API Endpoint

1. **Create/Update Schema** (`backend/app/schemas/`)
```python
from pydantic import BaseModel

class NewFeatureCreate(BaseModel):
    name: str
    value: int
```

2. **Create/Update Service** (`backend/app/services/`)
```python
class NewFeatureService:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, data: NewFeatureCreate):
        # Business logic here
        pass
```

3. **Create Router** (`backend/app/api/v1/`)
```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/new-feature", tags=["New Feature"])

@router.post("/")
async def create_new_feature(
    data: NewFeatureCreate,
    service: NewFeatureService = Depends()
):
    return await service.create(data)
```

4. **Register Router** (`backend/app/api/v1/__init__.py`)
```python
from .new_feature import router as new_feature_router
api_router.include_router(new_feature_router)
```

### Adding a New Frontend Page

1. **Create Page Component** (`frontend/src/pages/`)
```tsx
export default function NewFeaturePage() {
  return <div>New Feature</div>
}
```

2. **Add Route** (`frontend/src/router/index.tsx`)
```tsx
{
  path: '/new-feature',
  element: <NewFeaturePage />,
}
```

3. **Add Navigation** (if needed)

### Database Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Add new_feature table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/services/test_user_service.py

# Run specific test
pytest tests/unit/services/test_user_service.py::TestUserService::test_create_user
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run with watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

---

## Git Workflow

### Branch Naming

```
feature/ABC-123-add-new-feature
bugfix/ABC-124-fix-login-error
hotfix/ABC-125-critical-fix
```

### Commit Messages

```
feat: add courier performance dashboard
fix: resolve login redirect issue
docs: update API documentation
test: add unit tests for user service
refactor: simplify delivery assignment logic
```

### PR Process

1. Create feature branch from `main`
2. Make changes with clear commits
3. Push branch and create PR
4. Fill out PR template
5. Request review from team
6. Address feedback
7. Squash and merge when approved

---

## Resources

### Documentation

- [Architecture Guide](./ARCHITECTURE.md)
- [Database Schema](./DATABASE_SCHEMA.md)
- [API Documentation](../api/README.md)
- [Security Guidelines](./SECURITY.md)
- [CI/CD Guide](./CI_CD_GUIDE.md)

### External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Query](https://tanstack.com/query/latest)

### Getting Help

- **Slack**: #dev-barq-fleet
- **Team Lead**: [Name] - for architecture questions
- **Code Reviews**: Tag @dev-team in PRs
- **Issues**: Create GitHub issues for bugs/features

---

## Troubleshooting

### Common Issues

**Docker containers won't start**
```bash
# Check Docker is running
docker info

# Remove old containers and try again
docker-compose down -v
docker-compose up -d
```

**Database connection errors**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U postgres -d barq_fleet
```

**Frontend build errors**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Backend import errors**
```bash
# Ensure you're in backend directory with venv activated
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

**Welcome aboard! Happy coding! 🚀**
