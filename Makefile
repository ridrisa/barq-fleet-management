.PHONY: help install dev test clean migrate seed docker-up docker-down

help:
	@echo "BARQ Fleet Management - Available Commands"
	@echo ""
	@echo "  make install      - Install all dependencies"
	@echo "  make dev          - Start development servers"
	@echo "  make test         - Run all tests"
	@echo "  make migrate      - Run database migrations"
	@echo "  make seed         - Seed database with sample data"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"
	@echo "  make clean        - Clean generated files"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt -r requirements-dev.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev:
	@echo "Starting development environment..."
	docker-compose up -d postgres
	@echo "Waiting for database..."
	sleep 5
	@echo "Starting backend..."
	cd backend && uvicorn app.main:app --reload &
	@echo "Starting frontend..."
	cd frontend && npm run dev

test:
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

seed:
	@echo "Seeding database..."
	cd backend && python scripts/seed_data.py

docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	cd frontend && rm -rf node_modules dist build 2>/dev/null || true
	@echo "Clean complete"
