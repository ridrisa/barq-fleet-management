# BARQ Fleet Management - Developer Setup Guide

**Version:** 1.0.0
**Last Updated:** November 23, 2025

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Development Workflow](#development-workflow)
8. [Testing](#testing)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.11+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| PostgreSQL | 16 | https://postgresql.org |
| Redis | 7+ | https://redis.io |
| Git | Latest | https://git-scm.com |
| Docker | Latest | https://docker.com |
| Docker Compose | Latest | Included with Docker Desktop |

### Optional Tools

- **VS Code** - Recommended IDE
- **Postman** - API testing
- **pgAdmin** - PostgreSQL GUI
- **Redis Commander** - Redis GUI

### System Requirements

- **OS:** macOS, Linux, or Windows (WSL2)
- **RAM:** Minimum 8GB, recommended 16GB
- **Disk:** Minimum 10GB free space
- **Network:** Internet connection for package installation

---

## Environment Setup

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/barq/fleet-management.git
cd fleet-management

# Check current branch
git branch
# Should show: main or develop
```

### 2. Install System Dependencies

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 node postgresql@16 redis
brew install --cask docker

# Start services
brew services start postgresql@16
brew services start redis
```

#### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL 16
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-16

# Install Redis
sudo apt install -y redis-server

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### Windows (WSL2)

```bash
# Install WSL2 (PowerShell as Administrator)
wsl --install

# Follow Linux instructions above inside WSL2
```

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify Python version
python --version
# Should show: Python 3.11.x
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
pip list
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/barq_fleet
DATABASE_TEST_URL=postgresql://postgres:postgres@localhost:5432/barq_fleet_test

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth (get from Google Cloud Console)
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-google-client-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@barq.com

# Application
PROJECT_NAME=BARQ Fleet Management
VERSION=1.0.0
DEBUG=true
API_V1_STR=/api/v1

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 5. Verify Backend Installation

```bash
# Test Python imports
python -c "import fastapi; import sqlalchemy; import redis; print('All imports successful')"

# Check installed packages
pip list | grep -E "fastapi|sqlalchemy|redis|alembic"
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd ../frontend
```

### 2. Install Node.js Dependencies

```bash
# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env.local

# Edit .env.local
nano .env.local
```

**Frontend Environment Variables:**

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_V1_PATH=/api/v1

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id

# Application
VITE_APP_NAME=BARQ Fleet Management
VITE_APP_VERSION=1.0.0
```

### 4. Verify Frontend Installation

```bash
# Check Node and npm versions
node --version  # Should be v18.x or higher
npm --version   # Should be v9.x or higher

# Test build
npm run build

# Should complete without errors
```

---

## Database Setup

### Option 1: Using Docker (Recommended)

```bash
# From project root
docker-compose up -d postgres redis

# Verify containers are running
docker-compose ps

# Check logs
docker-compose logs postgres
docker-compose logs redis
```

### Option 2: Local Installation

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE barq_fleet;
CREATE DATABASE barq_fleet_test;

# Create user (optional)
CREATE USER barq_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE barq_fleet TO barq_user;
GRANT ALL PRIVILEGES ON DATABASE barq_fleet_test TO barq_user;

# Exit psql
\q
```

#### Verify Database Connection

```bash
# Test connection
psql -U postgres -d barq_fleet -c "SELECT version();"

# Should display PostgreSQL version
```

### Run Database Migrations

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Check migration status
alembic current

# Run all migrations
alembic upgrade head

# Verify migrations
alembic history
```

### Seed Database (Optional)

```bash
# Run seed script
python scripts/seed_database.py

# This will create:
# - Admin user (admin@barq.com / admin123)
# - Sample couriers
# - Sample vehicles
# - Sample data for testing
```

---

## Running the Application

### Terminal Setup (3 terminals required)

#### Terminal 1: Backend API

```bash
cd backend
source venv/bin/activate

# Start backend with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

#### Terminal 2: Frontend Dev Server

```bash
cd frontend

# Start frontend dev server
npm run dev

# Output:
# VITE v5.0.0  ready in 500 ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: http://192.168.1.100:5173/
```

#### Terminal 3: Background Jobs (Optional)

```bash
cd backend
source venv/bin/activate

# Start Celery worker
celery -A app.celery worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.celery beat --loglevel=info
```

### Access Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/api/v1/docs
- **API Docs (ReDoc):** http://localhost:8000/api/v1/redoc
- **Health Check:** http://localhost:8000/health

### Default Login Credentials

```
Email: admin@barq.com
Password: admin123
```

**IMPORTANT:** Change default password after first login!

---

## Development Workflow

### Branch Strategy

```
main                  → Production-ready code
├── develop           → Integration branch
    ├── feature/xxx   → New features
    ├── bugfix/xxx    → Bug fixes
    └── hotfix/xxx    → Urgent production fixes
```

### Creating a Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/add-courier-profile

# Make changes...

# Commit changes
git add .
git commit -m "feat: add courier profile page"

# Push to remote
git push origin feature/add-courier-profile

# Create pull request on GitHub
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: update dependencies
```

**Examples:**
```bash
git commit -m "feat: add courier search functionality"
git commit -m "fix: resolve vehicle assignment bug"
git commit -m "docs: update API documentation"
git commit -m "test: add unit tests for courier service"
```

---

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_couriers.py

# Run specific test
pytest tests/test_couriers.py::test_create_courier

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- CourierList.test.tsx
```

### E2E Tests

```bash
cd frontend

# Install Playwright (first time only)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run E2E tests in headed mode
npm run test:e2e -- --headed

# Run specific E2E test
npm run test:e2e -- courier.spec.ts
```

### Manual Testing

1. **Start application** (see Running the Application)
2. **Open Swagger UI:** http://localhost:8000/api/v1/docs
3. **Test endpoints** using Swagger UI
4. **Verify in frontend:** http://localhost:5173

---

## Common Tasks

### Database Tasks

```bash
# Create new migration
cd backend
alembic revision -m "add courier profile fields"

# Run migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# Show current version
alembic current

# Generate migration SQL (dry run)
alembic upgrade head --sql

# Reset database (CAUTION: deletes all data)
alembic downgrade base
alembic upgrade head
python scripts/seed_database.py
```

### Code Quality

```bash
# Backend - Format with Black
cd backend
black .

# Backend - Lint with Flake8
flake8 app/

# Backend - Type check with mypy
mypy app/

# Frontend - Lint with ESLint
cd frontend
npm run lint

# Frontend - Format with Prettier
npm run format

# Frontend - Type check
npm run type-check
```

### Dependency Management

```bash
# Backend - Add new dependency
cd backend
pip install package-name
pip freeze > requirements.txt

# Frontend - Add new dependency
cd frontend
npm install package-name

# Update dependencies
# Backend
pip install --upgrade -r requirements.txt

# Frontend
npm update
```

### Docker Tasks

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up -d --build

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d barq_fleet

# Access Redis CLI
docker-compose exec redis redis-cli

# Remove all containers and volumes
docker-compose down -v
```

---

## Troubleshooting

### Issue 1: Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

### Issue 2: Database Connection Error

**Error:** `could not connect to server: Connection refused`

**Solution:**
```bash
# Check PostgreSQL status
# macOS:
brew services list

# Linux:
sudo systemctl status postgresql

# Start PostgreSQL
# macOS:
brew services start postgresql@16

# Linux:
sudo systemctl start postgresql

# Verify connection
psql -U postgres -c "SELECT 1"
```

### Issue 3: Redis Connection Error

**Error:** `Error connecting to Redis`

**Solution:**
```bash
# Check Redis status
# macOS:
brew services list

# Linux:
sudo systemctl status redis

# Start Redis
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis

# Test connection
redis-cli ping
# Should return: PONG
```

### Issue 4: Migration Error

**Error:** `Target database is not up to date`

**Solution:**
```bash
cd backend

# Check current version
alembic current

# Check migration history
alembic history

# Downgrade to base
alembic downgrade base

# Upgrade to head
alembic upgrade head
```

### Issue 5: Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Issue 6: npm Install Errors

**Error:** `npm ERR! code EACCES`

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install

# If permission issues persist
sudo chown -R $USER ~/.npm
```

### Issue 7: Docker Issues

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
```bash
# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker

# Verify Docker is running
docker ps
```

---

## IDE Setup

### VS Code Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "dsznajder.es7-react-js-snippets",
    "ms-azuretools.vscode-docker",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg"
  ]
}
```

### VS Code Settings

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

---

## Useful Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **React Documentation:** https://react.dev
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org
- **Alembic Documentation:** https://alembic.sqlalchemy.org
- **Pydantic Documentation:** https://docs.pydantic.dev
- **TypeScript Documentation:** https://www.typescriptlang.org/docs/

---

## Getting Help

- **Check Documentation:** Start with this guide and other docs in `/docs`
- **API Documentation:** http://localhost:8000/api/v1/docs
- **Team Chat:** #engineering Slack channel
- **Create Issue:** Use GitHub Issues for bugs/features
- **Ask Team:** Don't hesitate to ask questions!

---

**Congratulations!** You should now have a fully functional development environment.

**Next Steps:**
1. Explore the codebase
2. Read ARCHITECTURE.md for system design
3. Check existing issues/features
4. Start coding!

---

**Document Owner:** Engineering Team
**Review Cycle:** Monthly
**Last Updated:** November 23, 2025
