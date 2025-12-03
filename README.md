# BARQ Fleet Management System

[![CI Pipeline](https://github.com/YOUR_ORG/barq-fleet-clean/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_ORG/barq-fleet-clean/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/YOUR_ORG/barq-fleet-clean/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_ORG/barq-fleet-clean)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

**Enterprise-grade fleet management platform for delivery operations, workforce management, and business analytics.**

**Status:** Production-Ready | **Version:** 1.1.0 | **Last Updated:** December 3, 2025

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Support](#support)
- [License](#license)

---

## Overview

BARQ Fleet Management is a comprehensive platform designed to streamline delivery operations, fleet management, HR processes, and business analytics. Built with modern technologies and production-ready architecture, BARQ provides:

- **Complete Fleet Management:** Couriers, vehicles, assignments, maintenance, inspections
- **HR Operations:** Leave, loans, attendance, salary, assets, bonuses
- **Delivery Operations:** Deliveries, routes, COD, dispatch, incidents, handovers
- **Workflow Engine:** Approval chains, SLA management, automation, triggers
- **Advanced Analytics:** Real-time dashboards, forecasting, custom reports, KPI tracking
- **Multi-tenant Architecture:** Full tenant isolation with Row-Level Security (RLS)
- **Organization Management:** Subscription plans, role-based access (OWNER/ADMIN/MANAGER/VIEWER)
- **Support System:** Ticket management, knowledge base, canned responses

### Key Metrics

| Metric | Value |
|--------|-------|
| **API Endpoints** | 250+ RESTful endpoints |
| **Database Tables** | 69+ production tables |
| **Frontend Pages** | 110+ React components |
| **Test Coverage** | 85%+ (unit + integration) |
| **Response Time** | <100ms (P95) |
| **Uptime** | 99.9% SLA |

---

## Features

### Fleet Management
- 📦 **Courier Management:** Complete lifecycle from onboarding to offboarding
- 🚗 **Vehicle Tracking:** Registration, insurance, maintenance schedules
- 🔄 **Assignments:** Dynamic courier-vehicle allocation
- 🔧 **Maintenance:** Scheduled and on-demand servicing
- ✅ **Inspections:** Digital inspection checklists
- ⛽ **Fuel Logs:** Consumption tracking and analysis
- 📄 **Documents:** Digital document management

### HR Management
- 🏖️ **Leave Management:** Annual, sick, emergency leave workflows
- 💰 **Loans & Advances:** Employee loan requests and tracking
- ⏰ **Attendance:** Clock in/out, overtime, shift management
- 💵 **Salary:** Payroll processing, payslips, deductions
- 🏢 **Assets:** Company asset allocation and tracking
- 🎁 **Bonuses:** Performance-based incentives

### Operations
- 📬 **Deliveries:** End-to-end delivery lifecycle management
- 🗺️ **Routes:** Route optimization and planning
- 💵 **COD:** Cash on delivery collection and reconciliation
- 📡 **Dispatch:** Real-time courier dispatch
- ⚠️ **Incidents:** Incident reporting and resolution
- 🤝 **Handovers:** Shift and package handovers
- 📊 **SLA Tracking:** Service level agreement monitoring
- 🌍 **Zones:** Delivery zone management

### Accommodation
- 🏢 **Buildings:** Housing facility management
- 🚪 **Rooms:** Room allocation and tracking
- 🛏️ **Beds:** Bed-level occupancy management
- 📋 **Allocations:** Employee accommodation assignments

### Workflow Engine
- 📋 **Templates:** Reusable workflow templates
- ⚙️ **Instances:** Active workflow execution
- ✅ **Approvals:** Multi-level approval chains
- ⏱️ **SLA Management:** Automated SLA tracking
- 🤖 **Automation:** Rule-based automation
- 🔔 **Triggers:** Event-driven workflows
- 💬 **Comments:** Collaborative workflow comments
- 📎 **Attachments:** Document attachments
- 📜 **History:** Complete audit trail

### Analytics & Reporting
- 📊 **Dashboard:** Real-time KPI dashboard
- 🚗 **Fleet Analytics:** Utilization, fuel efficiency, costs
- 👥 **HR Analytics:** Workforce metrics, attendance, turnover
- 💰 **Financial Analytics:** Revenue, costs, profitability
- 📦 **Operations Analytics:** Delivery performance, SLA compliance
- 📈 **Forecasting:** Demand, resource, revenue forecasting
- 📄 **Custom Reports:** Report builder with scheduling
- 📤 **Data Export:** CSV, Excel, PDF exports

### Support
- 🎫 **Ticket Management:** Multi-channel support tickets
- 📊 **Analytics:** Support metrics and SLA tracking
- 💬 **Canned Responses:** Pre-defined response templates
- 📚 **Knowledge Base:** Self-service help articles
- 📧 **Contact Forms:** Customer inquiry forms

### Admin
- 👥 **User Management:** User CRUD, bulk operations
- 🔐 **RBAC:** Role-based access control
- 🔑 **API Keys:** API key generation and management
- 🔗 **Integrations:** Third-party integrations (OAuth, webhooks)
- ⚙️ **System Settings:** Global system configuration
- 💾 **Backups:** Automated and manual backups
- 📜 **Audit Logs:** Complete system audit trail
- 📡 **Monitoring:** System health and performance monitoring

### Multi-Tenancy
- 🏢 **Organizations:** Multi-tenant data isolation
- 🔒 **Row-Level Security:** PostgreSQL RLS for data protection
- 👑 **Organization Roles:** OWNER, ADMIN, MANAGER, VIEWER
- 💳 **Subscription Plans:** FREE, BASIC, PROFESSIONAL, ENTERPRISE
- 🔄 **Organization Switching:** Seamless context switching
- 📊 **Usage Limits:** Per-organization user, courier, vehicle limits

---

## Tech Stack

### Frontend
- **Framework:** React 18 with TypeScript
- **Routing:** React Router v6
- **State:** Zustand + React Query (TanStack Query)
- **UI:** Custom components with Tailwind CSS
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts
- **HTTP:** Axios with interceptors
- **Build:** Vite 5.0
- **Testing:** Vitest + Playwright

### Backend
- **Framework:** FastAPI 0.104.1 (Python 3.11+)
- **ORM:** SQLAlchemy 2.0 with async support
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Authentication:** JWT + Google OAuth 2.0
- **Security:** Argon2, bcrypt, rate limiting (SlowAPI)
- **Cache:** Redis 7+
- **Tasks:** Celery + Redis
- **Async:** HTTPX, aiofiles
- **Testing:** Pytest with coverage

### Database & Infrastructure
- **Database:** PostgreSQL 14+
- **Cache:** Redis 7+
- **Container:** Docker + Docker Compose
- **Cloud:** Google Cloud Platform
  - Cloud Run (backend)
  - Cloud SQL (PostgreSQL)
  - Cloud Storage (static assets)
  - Cloud Build (CI/CD)
  - Cloud Monitoring
- **CI/CD:** GitHub Actions + Cloud Build

---

## Quick Start

### Prerequisites

- **Docker Desktop** 4.0+ (recommended)
- OR: Python 3.11+, Node.js 18+, PostgreSQL 14+, Redis 7+

### Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/barq-fleet-clean.git
cd barq-fleet-clean

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Access the application
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:5173
```

### Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Create admin user
python create_admin.py

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local

# Start development server
npm run dev
```

### Access Points

- **API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc
- **Frontend:** http://localhost:5173
- **Health Check:** http://localhost:8000/api/v1/health

### Default Credentials

```
Email: admin@barq.com
Password: admin123
```

**⚠️ IMPORTANT:** Change default credentials in production!

---

## Documentation

Comprehensive documentation is available in the `/docs` directory:

### For Users
- **[User Manual](docs/user/README.md)** - Complete user guide for all modules
- **[FAQs](docs/user/README.md#faqs)** - Frequently asked questions

### For Developers
- **[Developer Guide](docs/developer/README.md)** - Setup, architecture, coding standards
- **[API Documentation](docs/api/README.md)** - Complete API reference
- **[OpenAPI Spec](docs/api/openapi.yaml)** - OpenAPI/Swagger specification
- **[Authentication Guide](docs/api/authentication.md)** - JWT and OAuth setup

### For DevOps
- **[Deployment Guide](docs/deployment/README.md)** - Local, staging, production deployment
- **[CI/CD Guide](docs/CI_CD_GUIDE.md)** - Continuous integration and deployment

### For Administrators
- **[Admin Guide](docs/admin/README.md)** - System configuration and management
- **[Security Guide](docs/SECURITY.md)** - Security best practices

### Additional Resources
- **[Architecture Overview](docs/ARCHITECTURE.md)** - System architecture and design
- **[Database Schema](docs/DATABASE_SCHEMA.md)** - Complete database documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to BARQ

---

## Project Structure

```
barq-fleet-clean/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py           # Application entry point
│   │   ├── core/             # Core configuration
│   │   │   ├── config.py     # Settings
│   │   │   ├── security.py   # Security utilities
│   │   │   ├── database.py   # Database connection
│   │   │   └── cache.py      # Redis cache
│   │   ├── api/              # API routes
│   │   │   ├── v1/           # API version 1
│   │   │   ├── analytics/    # Analytics endpoints
│   │   │   └── workflow/     # Workflow endpoints
│   │   ├── models/           # SQLAlchemy models (69+ tables)
│   │   ├── schemas/          # Pydantic schemas (100+)
│   │   ├── crud/             # Database operations
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utility functions
│   ├── alembic/              # Database migrations
│   ├── tests/                # Test suite
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   ├── components/       # Reusable components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── lib/              # Library code
│   │   ├── stores/           # Zustand stores
│   │   └── types/            # TypeScript types
│   ├── public/               # Static assets
│   └── package.json          # NPM dependencies
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   ├── developer/            # Developer guides
│   ├── deployment/           # Deployment guides
│   ├── user/                 # User manual
│   └── admin/                # Admin guide
├── terraform/                # Infrastructure as Code
├── scripts/                  # Utility scripts
├── tests/                    # E2E tests
├── docker-compose.yml        # Docker orchestration
├── cloudbuild.yaml           # GCP Cloud Build config
└── README.md                 # This file
```

---

## Development

### Setting Up Development Environment

1. **Install Prerequisites:**
   - Python 3.11+
   - Node.js 18+
   - PostgreSQL 14+
   - Redis 7+
   - Docker Desktop (optional)

2. **Clone and Setup:**
   ```bash
   git clone https://github.com/your-org/barq-fleet-clean.git
   cd barq-fleet-clean

   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt

   # Frontend
   cd ../frontend
   npm install
   ```

3. **Environment Configuration:**
   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend
   cp frontend/.env.example frontend/.env.local

   # Edit both .env files with your configuration
   ```

4. **Database Setup:**
   ```bash
   createdb barq_fleet
   cd backend
   alembic upgrade head
   python create_admin.py
   ```

5. **Start Development Servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

### Development Workflow

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes** following coding standards

3. **Run Tests:**
   ```bash
   # Backend
   cd backend
   pytest tests/ -v --cov=app

   # Frontend
   cd frontend
   npm run test
   ```

4. **Run Linters:**
   ```bash
   # Backend
   black app/ tests/
   flake8 app/ tests/

   # Frontend
   npm run lint
   npm run type-check
   ```

5. **Commit Changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

6. **Push and Create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Coding Standards

- **Backend:** Follow PEP 8, use type hints, write docstrings
- **Frontend:** Follow Airbnb style guide, use TypeScript
- **Commits:** Follow [Conventional Commits](https://www.conventionalcommits.org/)
- **Documentation:** Update docs with code changes

---

## Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific tests
pytest tests/unit/test_courier.py -v

# Run integration tests
pytest tests/integration/ -v

# Run in parallel
pytest -n auto
```

**Test Coverage:** Target 85%+ coverage

### Frontend Testing

```bash
cd frontend

# Unit tests
npm run test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage

# E2E tests
npm run test:e2e

# E2E with UI
npm run test:e2e:ui
```

### Performance Testing

```bash
# Load testing with Locust
cd backend
locust -f tests/load/locustfile.py

# Access web UI
open http://localhost:8089
```

---

## Deployment

### Local Development
See [Quick Start](#quick-start) section above.

### Staging Deployment

```bash
# Deploy backend to Cloud Run (staging)
gcloud run deploy barq-backend-staging \
  --image gcr.io/barq-fleet-staging/backend:latest \
  --platform managed \
  --region us-central1

# Deploy frontend to Cloud Storage
cd frontend
npm run build
gsutil -m rsync -r dist/ gs://barq-staging-frontend
```

### Production Deployment

**Prerequisites:**
- GCP project configured
- Cloud SQL instance running
- Redis instance running
- Secrets configured in Secret Manager

```bash
# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or deploy manually
gcloud run deploy barq-backend-prod \
  --image gcr.io/barq-fleet-prod/backend:latest \
  --platform managed \
  --region us-central1 \
  --min-instances 2 \
  --max-instances 100
```

For detailed deployment instructions, see [Deployment Guide](docs/deployment/README.md).

### CI/CD Pipeline

GitHub Actions automatically:
1. Run tests on PR
2. Check code quality (linting, formatting)
3. Build Docker images
4. Deploy to staging (on merge to `develop`)
5. Deploy to production (on merge to `main`)

---

## Support

### Getting Help

- **Documentation:** [docs/](docs/)
- **API Docs:** http://localhost:8000/docs
- **Issues:** [GitHub Issues](https://github.com/your-org/barq-fleet-clean/issues)
- **Email:** support@barq.com
- **Slack:** #barq-support

### Reporting Issues

When reporting issues, include:
1. Environment (local, staging, production)
2. Steps to reproduce
3. Expected vs actual behavior
4. Screenshots/logs
5. System information

### Feature Requests

Feature requests are welcome! Please:
1. Search existing issues first
2. Provide clear use case
3. Describe expected behavior
4. Include mockups if applicable

---

## License

**Proprietary License** - All Rights Reserved

Copyright (c) 2025 BARQ Fleet Management

This software is proprietary and confidential. Unauthorized copying, distribution, or use of this software, via any medium, is strictly prohibited.

For licensing inquiries: legal@barq.com

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - Frontend library
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [PostgreSQL](https://www.postgresql.org/) - Advanced database
- [Redis](https://redis.io/) - In-memory data store
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS

Special thanks to all contributors and the open-source community.

---

## Project Status

- ✅ **Backend:** Production-ready with multi-tenancy
- ✅ **Database:** 69+ tables with Row-Level Security
- ✅ **API:** 250+ endpoints with tenant isolation
- ✅ **Authentication:** JWT + Google OAuth + Organization context
- ✅ **Multi-Tenancy:** Full tenant isolation implemented
- ✅ **Analytics:** Complete analytics engine
- ✅ **Workflow:** Full workflow engine
- ✅ **Documentation:** Comprehensive docs
- ✅ **CI/CD:** Automated pipeline
- ✅ **Frontend:** 110+ pages implemented
- ⏳ **Mobile App:** Planned
- ⏳ **Advanced Features:** Roadmap items

---

**Version:** 1.1.0
**Last Updated:** December 3, 2025
**Maintained By:** BARQ Development Team

**Made with ❤️ for modern fleet management**
