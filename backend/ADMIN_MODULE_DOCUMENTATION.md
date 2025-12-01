# BARQ Fleet Management - Admin Module Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Security Considerations](#security-considerations)
4. [API Endpoints](#api-endpoints)
5. [Models](#models)
6. [Usage Examples](#usage-examples)
7. [Best Practices](#best-practices)
8. [Deployment Checklist](#deployment-checklist)

---

## Overview

The Admin Module provides comprehensive system administration capabilities for the BARQ Fleet Management system. It includes:

- **User Management**: Extended CRUD operations, bulk actions, password reset
- **Role & Permission Management**: RBAC (Role-Based Access Control)
- **Audit Logging**: Complete audit trail of all system actions
- **System Monitoring**: Health checks, database stats, API metrics, resource usage
- **Backup Management**: Database backups, verification, restoration
- **Integration Management**: Third-party service integrations
- **API Key Management**: Programmatic API access control

---

## Architecture

### Directory Structure

```
app/
├── api/v1/admin/
│   ├── __init__.py              # Admin router registration
│   ├── users.py                 # User management
│   ├── user_enhancements.py     # Bulk operations, password reset
│   ├── roles.py                 # Role management
│   ├── permissions.py           # Permission management
│   ├── audit_logs.py            # Audit log queries
│   ├── monitoring.py            # System monitoring
│   ├── backups.py               # Backup management
│   ├── integrations.py          # Integration management
│   └── api_keys.py              # API key management
├── models/admin/
│   ├── __init__.py
│   ├── api_key.py               # API Key model
│   ├── integration.py           # Integration model
│   ├── system_setting.py        # System settings model
│   └── backup.py                # Backup model
├── schemas/admin/
│   ├── __init__.py
│   ├── api_key.py               # API Key schemas
│   ├── integration.py           # Integration schemas
│   ├── system_setting.py        # System settings schemas
│   ├── backup.py                # Backup schemas
│   └── monitoring.py            # Monitoring schemas
└── utils/
    └── audit.py                 # Centralized audit logging
```

### Data Flow

```
Client Request
    ↓
API Endpoint (FastAPI)
    ↓
Authentication & Authorization (JWT + RBAC)
    ↓
Business Logic
    ↓
Audit Logging (AuditLogger)
    ↓
Database Operations (SQLAlchemy)
    ↓
Response
```

---

## Security Considerations

### Authentication & Authorization

1. **Superuser Requirement**: All admin endpoints require superuser privileges
   - Enforced via `get_current_superuser()` dependency
   - Prevents unauthorized access to admin functions

2. **Role-Based Access Control (RBAC)**:
   - Granular permissions (resource:action format)
   - Role hierarchy support
   - User can have multiple roles
   - Permissions are checked at runtime

3. **API Key Security**:
   - Keys are hashed (SHA-256) before storage
   - Only key prefix stored in plain text for identification
   - Full key shown only once upon creation
   - Support for IP whitelisting
   - Rate limiting per key

### Data Protection

1. **Sensitive Data**:
   - API keys hashed with SHA-256
   - OAuth credentials marked for encryption
   - System settings can be marked as sensitive
   - Audit logs capture data changes without exposing passwords

2. **Password Security**:
   - Passwords hashed with bcrypt
   - Password reset tokens time-limited (24 hours)
   - Temporary passwords generated securely
   - Force password change on reset

3. **Audit Trail**:
   - All admin actions logged
   - IP addresses and user agents tracked
   - Old and new values captured for updates
   - Immutable audit log records

### Attack Prevention

1. **Rate Limiting**:
   - API keys have configurable rate limits
   - Per minute, hour, and day limits
   - Prevents abuse of API access

2. **Input Validation**:
   - Pydantic schemas validate all inputs
   - SQL injection prevented by SQLAlchemy ORM
   - XSS prevention through proper output encoding

3. **Security Headers**:
   - CORS properly configured
   - HTTPS recommended for production
   - Secure cookie flags

---

## API Endpoints

### User Management (`/api/v1/admin/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all users (paginated, filterable) |
| GET | `/{user_id}` | Get specific user details |
| PATCH | `/{user_id}` | Update user information |
| POST | `/{user_id}/activate` | Activate user account |
| POST | `/{user_id}/deactivate` | Deactivate user account |
| GET | `/{user_id}/roles` | Get user's assigned roles |
| POST | `/{user_id}/roles` | Assign roles to user |
| DELETE | `/{user_id}/roles/{role_id}` | Remove role from user |
| GET | `/{user_id}/activity` | Get user's activity logs |
| POST | `/bulk/activate` | Bulk activate users |
| POST | `/bulk/deactivate` | Bulk deactivate users |
| POST | `/bulk/assign-roles` | Bulk assign roles |
| POST | `/{user_id}/password-reset` | Admin reset user password |
| DELETE | `/bulk/delete` | Bulk delete users |

### Role Management (`/api/v1/admin/roles`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all roles |
| POST | `/` | Create new role |
| GET | `/{role_id}` | Get role details |
| PATCH | `/{role_id}` | Update role |
| DELETE | `/{role_id}` | Delete role |
| GET | `/{role_id}/permissions` | Get role permissions |
| POST | `/{role_id}/permissions` | Assign permissions to role |

### Permission Management (`/api/v1/admin/permissions`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all permissions |
| POST | `/` | Create new permission |
| GET | `/{permission_id}` | Get permission details |
| PATCH | `/{permission_id}` | Update permission |
| DELETE | `/{permission_id}` | Delete permission |
| GET | `/resources/list` | List all resource types |
| GET | `/actions/list` | List all action types |

### Audit Logs (`/api/v1/admin/audit-logs`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List audit logs (filterable) |
| GET | `/summary` | Get audit log statistics |
| GET | `/{audit_log_id}` | Get specific audit log |
| GET | `/resource/{type}/{id}` | Get audit trail for resource |
| GET | `/actions/types` | List action types |
| GET | `/resources/types` | List resource types |

### System Monitoring (`/api/v1/admin/monitoring`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Overall system health |
| GET | `/database/stats` | Database statistics |
| GET | `/api/metrics` | API request metrics |
| GET | `/resources` | System resource usage |

### Backup Management (`/api/v1/admin/backups`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all backups |
| POST | `/` | Create new backup |
| GET | `/stats` | Backup statistics |
| GET | `/{backup_id}` | Get backup details |
| PATCH | `/{backup_id}` | Update backup metadata |
| DELETE | `/{backup_id}` | Delete backup |
| POST | `/{backup_id}/verify` | Verify backup integrity |
| POST | `/{backup_id}/restore` | Restore from backup |
| DELETE | `/cleanup/expired` | Delete expired backups |

### Integration Management (`/api/v1/admin/integrations`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all integrations |
| POST | `/` | Create new integration |
| GET | `/{integration_id}` | Get integration details |
| PATCH | `/{integration_id}` | Update integration |
| DELETE | `/{integration_id}` | Delete integration |
| POST | `/{integration_id}/enable` | Enable integration |
| POST | `/{integration_id}/disable` | Disable integration |
| POST | `/{integration_id}/test` | Test integration |
| POST | `/{integration_id}/health-check` | Health check integration |
| GET | `/types/list` | List integration types |

### API Key Management (`/api/v1/admin/api-keys`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all API keys |
| POST | `/` | Create new API key |
| GET | `/{api_key_id}` | Get API key details |
| PATCH | `/{api_key_id}` | Update API key |
| DELETE | `/{api_key_id}` | Delete API key |
| POST | `/{api_key_id}/revoke` | Revoke API key |
| POST | `/{api_key_id}/rotate` | Rotate API key |
| GET | `/{api_key_id}/usage` | Get API key usage stats |
| GET | `/user/{user_id}/keys` | List user's API keys |

---

## Models

### ApiKey

Manages programmatic API access.

**Key Fields**:
- `key_prefix`: First 8 characters (visible)
- `key_hash`: SHA-256 hash of full key
- `scopes`: List of allowed permissions
- `ip_whitelist`: Allowed IP addresses
- `rate_limit_*`: Rate limiting settings
- `expires_at`: Optional expiration date

**Methods**:
- `generate_key()`: Generate secure random key
- `is_active()`: Check if key is currently valid
- `has_scope(scope)`: Check permission
- `is_ip_allowed(ip)`: Check IP whitelist

### Integration

Manages third-party service integrations.

**Key Fields**:
- `integration_type`: Type (payment, SMS, email, etc.)
- `config`: Integration-specific configuration
- `credentials`: Encrypted API credentials
- `oauth_*`: OAuth-specific fields
- `status`: Current status (active, error, etc.)

**Methods**:
- `is_healthy()`: Check integration health
- `record_success()`: Log successful API call
- `record_error(message)`: Log failed API call
- `needs_oauth_refresh()`: Check token expiration

### SystemSetting

Stores system-wide configuration.

**Key Fields**:
- `key`: Unique setting identifier
- `category`: Setting category
- `setting_type`: Data type (string, integer, boolean, JSON)
- `value`: Setting value
- `is_sensitive`: Encryption flag
- `validation_regex`: Value validation

**Methods**:
- `get_value()`: Get typed value
- `set_value(value)`: Set value with type conversion
- `validate_value(value)`: Validate against constraints

### Backup

Manages database backups.

**Key Fields**:
- `backup_type`: Full, incremental, or differential
- `status`: Pending, completed, failed, verified
- `storage_type`: Local, S3, GCS, Azure
- `size_bytes`: Backup size
- `checksum`: SHA-256 checksum
- `is_pinned`: Prevent auto-deletion

**Methods**:
- `mark_started()`: Start backup
- `mark_completed(size)`: Complete backup
- `mark_failed(error)`: Mark as failed
- `mark_verified(checksum)`: Verify integrity
- `is_expired()`: Check expiration

---

## Usage Examples

### Creating an API Key

```python
from app.api.deps import get_db, get_current_superuser
from app.schemas.admin.api_key import ApiKeyCreate

# Create API key
api_key_data = ApiKeyCreate(
    name="Mobile App API Key",
    description="API key for iOS mobile application",
    scopes=["courier:read", "delivery:read", "delivery:update"],
    ip_whitelist=["203.0.113.0/24"],  # Optional
    rate_limit_per_minute=60,
    rate_limit_per_hour=1000,
    expires_at=datetime(2025, 12, 31)
)

# POST /api/v1/admin/api-keys
# Response includes full key - SAVE IT!
{
    "id": 1,
    "name": "Mobile App API Key",
    "key_prefix": "barq_abc",
    "secret_key": "barq_abc123def456...",  # Full key
    ...
}
```

### Bulk User Operations

```python
# Bulk activate users
POST /api/v1/admin/users/bulk/activate
{
    "user_ids": [1, 2, 3, 4, 5]
}

# Bulk assign roles
POST /api/v1/admin/users/bulk/assign-roles
{
    "user_ids": [10, 11, 12],
    "role_ids": [2, 3]  # Assign Fleet Manager and HR Manager roles
}
```

### Creating a Backup

```python
# Create backup
POST /api/v1/admin/backups
{
    "name": "Daily Backup 2025-11-16",
    "description": "Automated daily backup",
    "backup_type": "full",
    "storage_type": "s3",
    "storage_bucket": "barq-backups",
    "is_compressed": true,
    "is_encrypted": true,
    "expires_at": "2025-12-16T00:00:00"
}
```

### System Health Check

```python
# Get system health
GET /api/v1/admin/monitoring/health

# Response
{
    "status": "healthy",
    "timestamp": "2025-11-16T10:30:00",
    "uptime_seconds": 86400,
    "version": "1.0.0",
    "environment": "production",
    "database": {
        "healthy": true,
        "latency_ms": 5,
        "status": "connected"
    },
    "cpu_usage_percent": 25.5,
    "memory_usage_percent": 68.2,
    "active_users": 42
}
```

### Using Audit Logger

```python
from app.utils.audit import AuditLogger
from app.models.audit_log import AuditAction

# Log user creation
AuditLogger.log_create(
    db=db,
    resource_type="user",
    resource_id=new_user.id,
    user=current_user,
    description=f"Created new user: {new_user.email}",
    new_values={"email": new_user.email, "role": "courier"}
)

# Log permission change
AuditLogger.log_permission_change(
    db=db,
    user=current_user,
    target_user_id=user_id,
    old_permissions=["courier:read"],
    new_permissions=["courier:read", "courier:update"]
)

# Log system action
AuditLogger.log_system_action(
    db=db,
    action_type="backup",
    description="Database backup completed successfully",
    user=current_user,
    metadata={"backup_id": backup.id, "size_mb": 150.5}
)
```

---

## Best Practices

### Security

1. **Always use HTTPS in production**
2. **Rotate API keys regularly** (every 90 days recommended)
3. **Enable IP whitelisting** for API keys when possible
4. **Review audit logs regularly** for suspicious activity
5. **Implement backup encryption** for sensitive data
6. **Use strong password policies** for admin accounts
7. **Enable MFA** for superuser accounts (future enhancement)

### Performance

1. **Use pagination** for large result sets
2. **Cache frequently accessed settings**
3. **Schedule backups during low-traffic periods**
4. **Index audit logs** by timestamp and user_id
5. **Archive old audit logs** (> 1 year) to separate storage
6. **Monitor database size** and plan scaling accordingly

### Maintenance

1. **Review and clean expired backups** monthly
2. **Test backup restoration** quarterly
3. **Review integration health** weekly
4. **Audit user permissions** quarterly
5. **Update system settings** as needed
6. **Monitor error rates** and respond to spikes
7. **Review API key usage** and revoke unused keys

### Audit Logging

1. **Log all admin actions** without exception
2. **Include old and new values** for updates
3. **Capture IP addresses** for security tracking
4. **Use descriptive messages** for clarity
5. **Avoid logging sensitive data** (passwords, tokens)

---

## Deployment Checklist

### Pre-Deployment

- [ ] Review all environment variables
- [ ] Verify database migrations are up to date
- [ ] Test all endpoints in staging environment
- [ ] Review CORS configuration
- [ ] Ensure SECRET_KEY is properly set
- [ ] Configure backup storage (S3, GCS, etc.)
- [ ] Set up email service for password resets
- [ ] Review rate limiting settings

### Post-Deployment

- [ ] Create initial superuser account
- [ ] Set up default roles and permissions
- [ ] Configure system settings
- [ ] Test backup creation and restoration
- [ ] Set up backup schedule
- [ ] Configure monitoring alerts
- [ ] Test integration connections
- [ ] Review initial audit logs
- [ ] Document admin procedures
- [ ] Train admin staff

### Monitoring

- [ ] Set up uptime monitoring
- [ ] Configure error alerting
- [ ] Monitor disk space for backups
- [ ] Track API response times
- [ ] Monitor failed login attempts
- [ ] Review audit logs daily
- [ ] Check backup completion status
- [ ] Monitor integration health

---

## Security Summary

### Critical Security Features

1. **Authentication & Authorization**:
   - JWT-based authentication
   - Superuser-only access to admin endpoints
   - Role-based access control (RBAC)
   - Granular permissions (resource:action)

2. **Data Protection**:
   - API keys hashed with SHA-256
   - Passwords hashed with bcrypt
   - Sensitive settings marked for encryption
   - OAuth credentials secured

3. **Audit Trail**:
   - Complete action logging
   - IP address tracking
   - User agent capture
   - Old/new value tracking
   - Immutable logs

4. **Access Control**:
   - IP whitelisting for API keys
   - Rate limiting per key
   - Session management
   - Token expiration

5. **Attack Prevention**:
   - Input validation (Pydantic)
   - SQL injection protection (ORM)
   - XSS prevention
   - CSRF protection
   - Rate limiting

### Known Limitations

1. **Encryption**: System settings and integration credentials marked for encryption but not yet implemented
2. **MFA**: Multi-factor authentication not yet implemented
3. **Email**: Password reset emails not yet configured
4. **Background Tasks**: Backup creation/restoration runs synchronously (should be async)
5. **Token Storage**: Password reset tokens not yet persisted to database

### Recommended Enhancements

1. Implement encryption for sensitive fields
2. Add multi-factor authentication (MFA)
3. Integrate email service for notifications
4. Implement background task queue (Celery/RQ)
5. Add webhook support for audit logs
6. Implement database backup to cloud storage
7. Add real-time system monitoring dashboard
8. Implement automated security scanning

---

## Support & Troubleshooting

### Common Issues

**Issue**: Cannot access admin endpoints
- **Solution**: Verify user has `is_superuser=True` flag

**Issue**: API key authentication failing
- **Solution**: Check key hasn't expired and IP is whitelisted

**Issue**: Backup creation fails
- **Solution**: Check disk space and database permissions

**Issue**: Audit logs growing too large
- **Solution**: Implement log archival strategy

### Getting Help

- Review this documentation
- Check API documentation at `/api/v1/docs`
- Review audit logs for error details
- Check application logs for stack traces

---

**Version**: 1.0.0
**Last Updated**: November 16, 2025
**Author**: BARQ Fleet Management Development Team
