# Admin API Documentation

The Admin API provides endpoints for user management, role-based access control, permissions, audit logs, and system configuration.

## Base URL

```
/api/v1/admin
```

## Authentication

All endpoints require a valid JWT token with `admin` or `super_admin` role.

---

## Users

### List Users

```http
GET /users
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `limit` | integer | Items per page |
| `role` | string | Filter by role |
| `status` | string | Filter by status: `active`, `inactive`, `suspended` |
| `search` | string | Search by name or email |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "email": "admin@barq.com",
      "full_name": "System Admin",
      "role": "super_admin",
      "roles": ["super_admin", "admin"],
      "is_active": true,
      "last_login": "2024-12-10T08:00:00Z",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "page": 1
}
```

### Get User

```http
GET /users/{id}
```

**Response:**

```json
{
  "id": 1,
  "email": "admin@barq.com",
  "full_name": "System Admin",
  "role": "super_admin",
  "roles": ["super_admin", "admin"],
  "permissions": [
    "users:read", "users:write", "users:delete",
    "settings:read", "settings:write"
  ],
  "is_active": true,
  "is_superuser": true,
  "phone": "+966501234567",
  "avatar_url": "https://storage.barq.com/avatars/1.jpg",
  "last_login": "2024-12-10T08:00:00Z",
  "login_count": 256,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-12-10T08:00:00Z"
}
```

### Create User

```http
POST /users
```

**Request Body:**

```json
{
  "email": "newuser@barq.com",
  "full_name": "New User",
  "password": "SecureP@ss123",
  "role": "fleet_manager",
  "is_active": true
}
```

### Update User

```http
PUT /users/{id}
```

**Request Body:**

```json
{
  "full_name": "Updated Name",
  "role": "hr_manager",
  "is_active": true
}
```

### Delete User

```http
DELETE /users/{id}
```

### Reset User Password

```http
POST /users/{id}/reset-password
```

**Request Body:**

```json
{
  "new_password": "NewSecureP@ss123",
  "send_email": true
}
```

### Suspend User

```http
POST /users/{id}/suspend
```

**Request Body:**

```json
{
  "reason": "Security policy violation",
  "duration_days": 7
}
```

### Reactivate User

```http
POST /users/{id}/reactivate
```

---

## Roles

### List Roles

```http
GET /roles
```

**Response:**

```json
{
  "roles": [
    {
      "id": "super_admin",
      "name": "Super Admin",
      "description": "Full system access",
      "is_system": true,
      "user_count": 2,
      "permissions_count": 50
    },
    {
      "id": "admin",
      "name": "Administrator",
      "description": "Administrative access",
      "is_system": true,
      "user_count": 5,
      "permissions_count": 40
    },
    {
      "id": "hr_manager",
      "name": "HR Manager",
      "description": "Human resources management",
      "is_system": true,
      "user_count": 3,
      "permissions_count": 25
    },
    {
      "id": "fleet_manager",
      "name": "Fleet Manager",
      "description": "Fleet and courier management",
      "is_system": true,
      "user_count": 10,
      "permissions_count": 20
    },
    {
      "id": "viewer",
      "name": "Viewer",
      "description": "Read-only access",
      "is_system": true,
      "user_count": 15,
      "permissions_count": 10
    }
  ]
}
```

### Get Role

```http
GET /roles/{id}
```

**Response:**

```json
{
  "id": "fleet_manager",
  "name": "Fleet Manager",
  "description": "Fleet and courier management",
  "is_system": true,
  "permissions": [
    {
      "id": "couriers:read",
      "name": "View Couriers",
      "category": "fleet"
    },
    {
      "id": "couriers:write",
      "name": "Manage Couriers",
      "category": "fleet"
    },
    {
      "id": "vehicles:read",
      "name": "View Vehicles",
      "category": "fleet"
    },
    {
      "id": "vehicles:write",
      "name": "Manage Vehicles",
      "category": "fleet"
    }
  ],
  "users": [
    {
      "id": 10,
      "email": "manager@barq.com",
      "full_name": "Fleet Manager Ali"
    }
  ]
}
```

### Create Custom Role

```http
POST /roles
```

**Request Body:**

```json
{
  "id": "regional_manager",
  "name": "Regional Manager",
  "description": "Regional operations manager",
  "permissions": [
    "couriers:read",
    "vehicles:read",
    "deliveries:read",
    "analytics:read"
  ]
}
```

### Update Role Permissions

```http
PUT /roles/{id}/permissions
```

**Request Body:**

```json
{
  "permissions": [
    "couriers:read",
    "couriers:write",
    "vehicles:read"
  ]
}
```

### Delete Custom Role

```http
DELETE /roles/{id}
```

---

## Permissions

### List Permissions

```http
GET /permissions
```

**Response:**

```json
{
  "permissions": [
    {
      "id": "couriers:read",
      "name": "View Couriers",
      "description": "View courier list and details",
      "category": "fleet"
    },
    {
      "id": "couriers:write",
      "name": "Manage Couriers",
      "description": "Create, update, delete couriers",
      "category": "fleet"
    }
  ],
  "categories": [
    {"id": "fleet", "name": "Fleet Management"},
    {"id": "hr", "name": "Human Resources"},
    {"id": "operations", "name": "Operations"},
    {"id": "finance", "name": "Finance"},
    {"id": "admin", "name": "Administration"}
  ]
}
```

### Check Permission

```http
GET /permissions/check
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | integer | User ID |
| `permission` | string | Permission to check |

**Response:**

```json
{
  "user_id": 10,
  "permission": "couriers:write",
  "has_permission": true,
  "granted_via": "role:fleet_manager"
}
```

---

## Audit Logs

### List Audit Logs

```http
GET /audit-logs
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `limit` | integer | Items per page |
| `user_id` | integer | Filter by user |
| `action` | string | Filter by action type |
| `resource_type` | string | Filter by resource type |
| `start_date` | string | Start date |
| `end_date` | string | End date |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "timestamp": "2024-12-10T10:30:00Z",
      "user_id": 10,
      "user_email": "manager@barq.com",
      "action": "update",
      "resource_type": "courier",
      "resource_id": 5,
      "resource_name": "Ahmed Al-Rashid",
      "changes": {
        "status": {
          "old": "active",
          "new": "on_leave"
        }
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "total": 15000,
  "page": 1
}
```

### Get Audit Log

```http
GET /audit-logs/{id}
```

### Export Audit Logs

```http
POST /audit-logs/export
```

**Request Body:**

```json
{
  "start_date": "2024-12-01",
  "end_date": "2024-12-10",
  "format": "csv"
}
```

---

## System Settings

### Get Settings

```http
GET /settings
```

**Response:**

```json
{
  "general": {
    "company_name": "BARQ Delivery",
    "timezone": "Asia/Riyadh",
    "currency": "SAR",
    "language": "ar"
  },
  "operations": {
    "max_dispatch_radius_km": 7,
    "max_pickup_eta_minutes": 15,
    "sla_hours": 4,
    "target_orders_per_day": 15
  },
  "notifications": {
    "email_enabled": true,
    "sms_enabled": true,
    "push_enabled": true
  },
  "security": {
    "password_min_length": 8,
    "password_require_special": true,
    "session_timeout_minutes": 30,
    "max_login_attempts": 5
  }
}
```

### Update Settings

```http
PUT /settings
```

**Request Body:**

```json
{
  "operations": {
    "max_dispatch_radius_km": 10,
    "sla_hours": 6
  }
}
```

### Get Setting by Key

```http
GET /settings/{key}
```

### Update Setting by Key

```http
PUT /settings/{key}
```

**Request Body:**

```json
{
  "value": 10
}
```

---

## API Keys

### List API Keys

```http
GET /api-keys
```

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "E-Commerce Integration",
      "key_prefix": "brq_live_abc...",
      "permissions": ["deliveries:create", "deliveries:read"],
      "last_used": "2024-12-10T10:00:00Z",
      "created_at": "2024-06-01T00:00:00Z",
      "expires_at": null
    }
  ]
}
```

### Create API Key

```http
POST /api-keys
```

**Request Body:**

```json
{
  "name": "New Integration",
  "permissions": ["deliveries:create", "deliveries:read", "tracking:read"],
  "expires_at": "2025-12-31"
}
```

**Response:**

```json
{
  "id": 2,
  "name": "New Integration",
  "key": "brq_live_xyz123456789abcdef",
  "key_prefix": "brq_live_xyz...",
  "permissions": ["deliveries:create", "deliveries:read", "tracking:read"],
  "created_at": "2024-12-10T11:00:00Z",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

**Note:** The full API key is only returned once on creation. Store it securely.

### Revoke API Key

```http
DELETE /api-keys/{id}
```

---

## Webhooks

### List Webhooks

```http
GET /webhooks
```

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "url": "https://example.com/webhook",
      "events": ["delivery.created", "delivery.completed"],
      "is_active": true,
      "secret": "whsec_abc...",
      "last_triggered": "2024-12-10T10:00:00Z",
      "success_rate": 99.5
    }
  ]
}
```

### Create Webhook

```http
POST /webhooks
```

**Request Body:**

```json
{
  "url": "https://example.com/webhook",
  "events": ["delivery.created", "delivery.completed", "delivery.failed"],
  "secret": "your_webhook_secret"
}
```

### Update Webhook

```http
PUT /webhooks/{id}
```

### Delete Webhook

```http
DELETE /webhooks/{id}
```

### Test Webhook

```http
POST /webhooks/{id}/test
```

### Get Webhook Events

```http
GET /webhooks/events
```

**Response:**

```json
{
  "events": [
    {"id": "delivery.created", "description": "Delivery created"},
    {"id": "delivery.assigned", "description": "Delivery assigned to courier"},
    {"id": "delivery.picked_up", "description": "Delivery picked up"},
    {"id": "delivery.completed", "description": "Delivery completed"},
    {"id": "delivery.failed", "description": "Delivery failed"},
    {"id": "courier.created", "description": "Courier created"},
    {"id": "courier.updated", "description": "Courier updated"}
  ]
}
```

---

## System Health

### Get System Status

```http
GET /system/status
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 864000,
  "services": {
    "database": {"status": "healthy", "latency_ms": 5},
    "redis": {"status": "healthy", "latency_ms": 2},
    "storage": {"status": "healthy"},
    "email": {"status": "healthy"}
  },
  "metrics": {
    "cpu_usage_percent": 45.2,
    "memory_usage_percent": 62.5,
    "disk_usage_percent": 35.8,
    "active_connections": 125
  }
}
```

### Get System Metrics

```http
GET /system/metrics
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | string | Time period: `hour`, `day`, `week` |

**Response:**

```json
{
  "period": "day",
  "api": {
    "total_requests": 125000,
    "average_latency_ms": 45,
    "error_rate": 0.5,
    "requests_per_minute": 87
  },
  "database": {
    "queries_per_second": 250,
    "slow_queries": 12,
    "connections_active": 45
  }
}
```
