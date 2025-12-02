# BARQ Fleet Management - API Documentation

## Overview

Complete API documentation for the BARQ Fleet Management System. The API is built with FastAPI and provides RESTful endpoints for all fleet management operations.

**Base URL (Production):** `https://api.barq.com`
**Base URL (Staging):** `https://staging-api.barq.com`
**Base URL (Local):** `http://localhost:8000`

**API Version:** v1
**OpenAPI Specification:** Available at `/openapi.json`
**Interactive Documentation:** `/docs` (Swagger UI) or `/redoc` (ReDoc)

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Modules](#api-modules)
4. [Rate Limiting](#rate-limiting)
5. [Error Handling](#error-handling)
6. [Pagination](#pagination)
7. [Filtering & Sorting](#filtering--sorting)
8. [Webhooks](#webhooks)
9. [SDKs & Libraries](#sdks--libraries)

---

## Getting Started

### Quick Start

```bash
# Login and get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@barq.com", "password": "your_password"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}

# Use the token in subsequent requests
curl -X GET http://localhost:8000/api/v1/fleet/couriers \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Interactive API Documentation

Access interactive documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide:
- Try-it-out functionality
- Request/response schemas
- Authentication testing
- Code generation

---

## Authentication

BARQ API uses JWT (JSON Web Tokens) for authentication.

### Authentication Methods

1. **Email/Password Login**
2. **Google OAuth 2.0**
3. **API Keys** (for integrations)

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | Email/password authentication |
| POST | `/api/v1/auth/google` | Google OAuth login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user info |
| POST | `/api/v1/auth/logout` | Invalidate token |

### Email/Password Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "manager"
  }
}
```

### Using JWT Tokens

Include the access token in the Authorization header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Token Refresh

When the access token expires, use the refresh token:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## API Modules

BARQ API is organized into the following modules:

### 1. Fleet Management
**Base Path:** `/api/v1/fleet`

- Couriers management
- Vehicles management
- Assignments (courier-vehicle)
- Maintenance tracking
- Inspections
- Fuel logs
- Documents

[View Fleet API Documentation](./fleet.md)

### 2. HR Management
**Base Path:** `/api/v1/hr`

- Leave management
- Loans and advances
- Attendance tracking
- Salary management
- Asset management
- Bonuses and incentives

[View HR API Documentation](./hr.md)

### 3. Operations
**Base Path:** `/api/v1/operations`

- Deliveries
- Routes
- COD management
- Dispatch
- Incidents
- Handovers
- SLA tracking
- Zones

[View Operations API Documentation](./operations.md)

### 4. Accommodation
**Base Path:** `/api/v1/accommodation`

- Buildings
- Rooms
- Beds
- Allocations

[View Accommodation API Documentation](./accommodation.md)

### 5. Workflow Engine
**Base Path:** `/api/v1/workflow`

- Workflow templates
- Workflow instances
- Approval chains
- SLA management
- Automation rules
- Triggers

[View Workflow API Documentation](./workflow.md)

### 6. Analytics & Reporting
**Base Path:** `/api/v1/analytics`

- Dashboard overview
- Fleet analytics
- HR analytics
- Financial analytics
- Operations analytics
- Custom reports
- KPI tracking
- Forecasting

[View Analytics API Documentation](./analytics.md)

### 7. Support
**Base Path:** `/api/v1/support`

- Ticket management
- Analytics
- Canned responses
- Templates
- Contact forms

[View Support API Documentation](./support.md)

### 8. Admin
**Base Path:** `/api/v1/admin`

- User management
- Role management
- Permissions
- API keys
- Integrations
- System settings
- Backups
- Audit logs
- Monitoring

[View Admin API Documentation](./admin.md)

---

## Rate Limiting

To ensure fair usage and system stability, API requests are rate-limited:

### Rate Limits

| Endpoint Type | Rate Limit | Time Window |
|--------------|------------|-------------|
| Authentication | 5 requests | 1 minute |
| Standard API | 100 requests | 1 minute |
| Analytics/Reports | 30 requests | 1 minute |
| Export/Streaming | 10 requests | 1 minute |

### Rate Limit Headers

Response headers indicate your current rate limit status:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638360000
```

### Rate Limit Exceeded

When you exceed the rate limit, you'll receive:

```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds.",
  "status_code": 429,
  "retry_after": 45
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded, no content returned |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (duplicate) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Human-readable error message",
  "status_code": 400,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ],
  "request_id": "req_abc123",
  "timestamp": "2025-12-02T10:30:00Z"
}
```

### Validation Errors

Validation errors (422) provide detailed field-level errors:

```json
{
  "detail": "Validation error",
  "status_code": 422,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "type": "value_error.email"
    },
    {
      "field": "phone",
      "message": "Phone number is required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Pagination

List endpoints support pagination using cursor-based or offset-based pagination.

### Offset-Based Pagination

```http
GET /api/v1/fleet/couriers?skip=0&limit=20
```

**Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 50, max: 100)

**Response:**
```json
{
  "data": [...],
  "total": 250,
  "skip": 0,
  "limit": 20,
  "has_next": true,
  "has_prev": false
}
```

### Cursor-Based Pagination

For large datasets, use cursor-based pagination:

```http
GET /api/v1/analytics/deliveries?cursor=eyJpZCI6MTAwfQ==&limit=50
```

**Response:**
```json
{
  "data": [...],
  "next_cursor": "eyJpZCI6MTUwfQ==",
  "prev_cursor": "eyJpZCI6NTB9",
  "has_next": true,
  "has_prev": true
}
```

---

## Filtering & Sorting

### Filtering

Use query parameters to filter results:

```http
GET /api/v1/fleet/couriers?status=active&city=riyadh
GET /api/v1/operations/deliveries?status=completed&start_date=2025-12-01&end_date=2025-12-31
```

### Sorting

Sort results using `sort_by` and `sort_desc`:

```http
GET /api/v1/fleet/vehicles?sort_by=created_at&sort_desc=true
```

### Search

Full-text search on supported endpoints:

```http
GET /api/v1/fleet/couriers?search=ahmed
```

---

## Webhooks

BARQ supports webhooks to notify your application of events in real-time.

### Available Events

- `delivery.created`
- `delivery.status_changed`
- `delivery.completed`
- `courier.assigned`
- `maintenance.scheduled`
- `workflow.approved`
- `workflow.rejected`

### Webhook Configuration

Configure webhooks via Admin panel or API:

```http
POST /api/v1/admin/webhooks
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/barq",
  "events": ["delivery.created", "delivery.status_changed"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload

```json
{
  "event": "delivery.created",
  "timestamp": "2025-12-02T10:30:00Z",
  "data": {
    "id": 12345,
    "tracking_number": "BARQ-2025-12345",
    "status": "pending"
  },
  "signature": "sha256=..."
}
```

---

## SDKs & Libraries

### Official SDKs

- **Python SDK:** `pip install barq-fleet-sdk`
- **JavaScript/TypeScript SDK:** `npm install @barq/fleet-sdk`
- **PHP SDK:** `composer require barq/fleet-sdk`

### Python Example

```python
from barq_fleet import BarqClient

client = BarqClient(
    api_key="your_api_key",
    base_url="https://api.barq.com"
)

# Get couriers
couriers = client.fleet.couriers.list(status="active")

# Create delivery
delivery = client.operations.deliveries.create({
    "tracking_number": "BARQ-001",
    "courier_id": 123,
    "destination": {
        "address": "123 Main St",
        "city": "Riyadh"
    }
})
```

### JavaScript Example

```javascript
import { BarqClient } from '@barq/fleet-sdk';

const client = new BarqClient({
  apiKey: 'your_api_key',
  baseUrl: 'https://api.barq.com'
});

// Get couriers
const couriers = await client.fleet.couriers.list({ status: 'active' });

// Create delivery
const delivery = await client.operations.deliveries.create({
  trackingNumber: 'BARQ-001',
  courierId: 123,
  destination: {
    address: '123 Main St',
    city: 'Riyadh'
  }
});
```

---

## Best Practices

### 1. Use HTTPS
Always use HTTPS in production to encrypt data in transit.

### 2. Store Tokens Securely
Never expose API keys or tokens in client-side code or version control.

### 3. Handle Rate Limits
Implement exponential backoff when rate limits are hit.

### 4. Use Pagination
Always paginate large result sets to improve performance.

### 5. Validate Input
Validate all input data before sending to the API.

### 6. Monitor Webhooks
Set up monitoring and alerting for webhook failures.

### 7. Cache Responses
Cache frequently accessed data to reduce API calls.

---

## Support

- **Email:** api-support@barq.com
- **Documentation:** https://docs.barq.com
- **Status Page:** https://status.barq.com
- **Slack Community:** https://barq-community.slack.com

---

**Version:** 1.0.0
**Last Updated:** December 2, 2025
