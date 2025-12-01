# BARQ Fleet Management - Backend

Python FastAPI backend with PostgreSQL database.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Environment Variables

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Database Setup

```bash
# Start PostgreSQL (or use Docker)
docker-compose up -d postgres

# Run migrations
alembic upgrade head

# (Optional) Seed data
python scripts/seed_data.py
```

### 5. Run Development Server

```bash
uvicorn app.main:app --reload
```

API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/            # API routes
│   ├── config/         # Configuration
│   ├── core/           # Core utilities
│   ├── crud/           # CRUD operations
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── tests/          # Tests
├── alembic/            # Database migrations
└── scripts/            # Utility scripts
```

## Development

### Run Tests

```bash
pytest
# With coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/

# Type check
mypy app/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show history
alembic history
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Couriers
- `GET /api/v1/couriers/` - List couriers
- `POST /api/v1/couriers/` - Create courier
- `GET /api/v1/couriers/{id}` - Get courier
- `PUT /api/v1/couriers/{id}` - Update courier
- `DELETE /api/v1/couriers/{id}` - Delete courier

### Vehicles
- `GET /api/v1/vehicles/` - List vehicles
- `POST /api/v1/vehicles/` - Create vehicle
- `GET /api/v1/vehicles/{id}` - Get vehicle
- `PUT /api/v1/vehicles/{id}` - Update vehicle
- `DELETE /api/v1/vehicles/{id}` - Delete vehicle

Full API documentation available at `/docs` when running the server.

## Environment Variables

See `.env.example` for all available configuration options.

## Deployment

See [../docs/deployment](../docs/deployment) for deployment guides.
