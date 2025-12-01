# Admin Module Implementation Checklist

## Pre-Deployment Checklist

Use this checklist to ensure the Admin Module is properly configured and ready for production.

---

## 1. Database Setup ⚠️ REQUIRED

### Create Database Migrations

```bash
cd /Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend

# Generate migrations for new models
alembic revision --autogenerate -m "Add admin module models (ApiKey, Integration, SystemSetting, Backup)"

# Review the generated migration file
# Location: alembic/versions/xxxxx_add_admin_module_models.py

# Apply migrations
alembic upgrade head

# Verify tables created
psutil
# Connect to database and run:
# \dt  (to list all tables)
# You should see: api_keys, integrations, system_settings, backups
```

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 2. Dependencies Installation

### Check Required Packages

```bash
# psutil is required for system monitoring
pip install psutil

# Verify all dependencies
pip install -r requirements.txt

# Check imports work
python -c "import psutil; print('psutil OK')"
```

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 3. Environment Configuration

### Verify Environment Variables

Edit `.env` file and ensure:

```bash
# Core
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development  # or production

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=barq_fleet

# API
API_V1_STR=/api/v1
PROJECT_NAME=BARQ Fleet Management
VERSION=1.0.0

# CORS (update for production)
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Email (for password reset - optional for now)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# Backup Storage (optional - configure later)
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_S3_BUCKET=

# Security
# JWT_EXPIRATION_MINUTES=60
```

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 4. Initial Data Setup

### Create Superuser (if not exists)

```bash
python create_admin.py
```

### Create Default Roles (SQL or via API)

```sql
-- Run in database or create via API
INSERT INTO roles (name, display_name, description, is_system_role, is_active, created_at, updated_at)
VALUES
('admin', 'Administrator', 'Full system access', true, true, NOW(), NOW()),
('manager', 'Manager', 'Management access', true, true, NOW(), NOW()),
('operator', 'Operator', 'Operational access', true, true, NOW(), NOW()),
('viewer', 'Viewer', 'Read-only access', true, true, NOW(), NOW());
```

### Create Default Permissions

```python
# Via Python script or API
default_permissions = [
    # Users
    ("user:create", "user", "create", "Create users"),
    ("user:read", "user", "read", "View users"),
    ("user:update", "user", "update", "Update users"),
    ("user:delete", "user", "delete", "Delete users"),

    # Roles
    ("role:create", "role", "create", "Create roles"),
    ("role:read", "role", "read", "View roles"),
    ("role:update", "role", "update", "Update roles"),
    ("role:delete", "role", "delete", "Delete roles"),

    # Audit
    ("audit_log:read", "audit_log", "read", "View audit logs"),

    # System
    ("system:manage", "system", "manage", "Manage system settings"),
    ("backup:manage", "backup", "manage", "Manage backups"),
    ("integration:manage", "integration", "manage", "Manage integrations"),
    ("api_key:manage", "api_key", "manage", "Manage API keys"),

    # Fleet
    ("courier:create", "courier", "create", "Create couriers"),
    ("courier:read", "courier", "read", "View couriers"),
    ("courier:update", "courier", "update", "Update couriers"),
    ("courier:delete", "courier", "delete", "Delete couriers"),

    ("vehicle:create", "vehicle", "create", "Create vehicles"),
    ("vehicle:read", "vehicle", "read", "View vehicles"),
    ("vehicle:update", "vehicle", "update", "Update vehicles"),
    ("vehicle:delete", "vehicle", "delete", "Delete vehicles"),

    # Add more as needed...
]

# Create via API: POST /api/v1/admin/permissions (for each)
```

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 5. Testing

### Start the Application

```bash
cd /Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend
uvicorn app.main:app --reload --port 8000
```

### Access API Documentation

```
http://localhost:8000/api/v1/docs
```

### Test Core Endpoints

#### 5.1 Authentication
```bash
# Login as superuser
POST http://localhost:8000/api/v1/auth/login
{
  "username": "admin@barq.com",
  "password": "your-password"
}

# Save the access_token for subsequent requests
```

#### 5.2 User Management
```bash
# List users
GET http://localhost:8000/api/v1/admin/users
Authorization: Bearer <your-token>

# Create user
POST http://localhost:8000/api/v1/admin/users
# (if endpoint exists in main users.py)
```

#### 5.3 System Monitoring
```bash
# System health
GET http://localhost:8000/api/v1/admin/monitoring/health
Authorization: Bearer <your-token>

# Database stats
GET http://localhost:8000/api/v1/admin/monitoring/database/stats
Authorization: Bearer <your-token>

# API metrics
GET http://localhost:8000/api/v1/admin/monitoring/api/metrics
Authorization: Bearer <your-token>

# Resource usage
GET http://localhost:8000/api/v1/admin/monitoring/resources
Authorization: Bearer <your-token>
```

#### 5.4 Audit Logs
```bash
# List audit logs
GET http://localhost:8000/api/v1/admin/audit-logs
Authorization: Bearer <your-token>

# Get summary
GET http://localhost:8000/api/v1/admin/audit-logs/summary
Authorization: Bearer <your-token>
```

#### 5.5 API Keys
```bash
# Create API key
POST http://localhost:8000/api/v1/admin/api-keys
Authorization: Bearer <your-token>
{
  "name": "Test API Key",
  "description": "Testing API key functionality",
  "scopes": ["courier:read", "vehicle:read"],
  "rate_limit_per_minute": 60
}

# IMPORTANT: Save the secret_key from response!

# List API keys
GET http://localhost:8000/api/v1/admin/api-keys
Authorization: Bearer <your-token>
```

#### 5.6 Backups
```bash
# Create backup
POST http://localhost:8000/api/v1/admin/backups
Authorization: Bearer <your-token>
{
  "name": "Test Backup",
  "backup_type": "full",
  "storage_type": "local"
}

# List backups
GET http://localhost:8000/api/v1/admin/backups
Authorization: Bearer <your-token>

# Get stats
GET http://localhost:8000/api/v1/admin/backups/stats
Authorization: Bearer <your-token>
```

#### 5.7 Integrations
```bash
# Create integration
POST http://localhost:8000/api/v1/admin/integrations
Authorization: Bearer <your-token>
{
  "name": "test_sms",
  "display_name": "Test SMS Provider",
  "integration_type": "sms_provider",
  "is_enabled": true
}

# List integrations
GET http://localhost:8000/api/v1/admin/integrations
Authorization: Bearer <your-token>
```

**Testing Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 6. Security Verification

### Check Security Configuration

- [ ] SECRET_KEY changed from default
- [ ] Database credentials secure
- [ ] CORS origins properly configured (no wildcards in production)
- [ ] Debug mode disabled in production
- [ ] HTTPS enabled (in production)
- [ ] Firewall configured to restrict admin endpoints
- [ ] Rate limiting tested and working
- [ ] API key hashing verified
- [ ] Audit logging working for all actions

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 7. Monitoring Setup

### Configure System Monitoring

- [ ] Set up health check alerts
- [ ] Configure error rate monitoring
- [ ] Set up backup success/failure alerts
- [ ] Configure disk space monitoring
- [ ] Set up database connection monitoring
- [ ] Configure API response time alerts

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 8. Documentation Review

### Verify Documentation

- [ ] Read ADMIN_MODULE_DOCUMENTATION.md
- [ ] Read ADMIN_SECURITY_SUMMARY.md
- [ ] Review ADMIN_MODULE_SUMMARY.md
- [ ] Understand all endpoints
- [ ] Review security best practices

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 9. Production Readiness

### Pre-Production Checklist

#### Critical
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Superuser created
- [ ] Default roles created
- [ ] Default permissions created
- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] All endpoints tested
- [ ] Security audit completed
- [ ] Backup tested and verified

#### High Priority
- [ ] Monitoring alerts configured
- [ ] Error tracking set up
- [ ] Backup schedule configured
- [ ] Log aggregation set up
- [ ] Documentation reviewed
- [ ] Admin training completed

#### Medium Priority
- [ ] Email service configured (for password reset)
- [ ] Cloud storage configured (for backups)
- [ ] Integration credentials configured
- [ ] Rate limiting tuned
- [ ] Performance testing completed

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Completed

---

## 10. Known Issues / Future Enhancements

### To Be Implemented

- [ ] Field-level encryption for sensitive data
- [ ] Multi-factor authentication (MFA)
- [ ] Email notifications for password reset
- [ ] Background task queue for backups
- [ ] Real-time monitoring dashboard
- [ ] Automated security scanning
- [ ] OAuth 2.0 integration
- [ ] Webhook notifications

### Notes
_Add any issues or notes encountered during implementation_

---

---

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'psutil'
pip install psutil

# Error: Cannot import admin models
# Check models/__init__.py includes new admin models
```

#### 2. Database Errors
```bash
# Error: relation "api_keys" does not exist
# Run migrations:
alembic upgrade head

# Error: permission denied for table api_keys
# Check database user permissions
```

#### 3. Authentication Errors
```bash
# Error: 403 Forbidden on admin endpoints
# Verify user has is_superuser=True

# Error: 401 Unauthorized
# Check JWT token is valid and not expired
```

#### 4. Monitoring Errors
```bash
# Error: psutil not found
pip install psutil

# Error: Cannot get system metrics
# Check permissions for psutil operations
```

---

## Support

### Resources
- Documentation: `/backend/ADMIN_MODULE_DOCUMENTATION.md`
- Security: `/backend/ADMIN_SECURITY_SUMMARY.md`
- Summary: `/backend/ADMIN_MODULE_SUMMARY.md`
- API Docs: `http://localhost:8000/api/v1/docs`

### Getting Help
1. Check this checklist
2. Review documentation
3. Check API documentation
4. Review audit logs for errors
5. Check application logs

---

## Sign-Off

### Implementation Team

- **Developer**: _________________
- **Date Completed**: _________________
- **Reviewed By**: _________________
- **Approved By**: _________________

### Deployment

- **Deployed to Staging**: _________________
- **Staging Tests Passed**: _________________
- **Deployed to Production**: _________________
- **Production Verified**: _________________

---

**Checklist Version**: 1.0
**Last Updated**: November 16, 2025
**Next Review**: Before Production Deployment
