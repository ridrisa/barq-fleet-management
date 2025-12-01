# BARQ Fleet Management API Reference

**Version:** 1.0.0
**Base URL:** `https://api.barq.com/api/v1` (Production)
**Base URL (Staging):** `https://staging-api.barq.com/api/v1`
**Base URL (Local):** `http://localhost:8000/api/v1`

**Last Updated:** November 23, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [Fleet Management](#fleet-management)
3. [HR & Finance](#hr--finance)
4. [Operations](#operations)
5. [Accommodation](#accommodation)
6. [Workflow Engine](#workflow-engine)
7. [Support](#support)
8. [Administration](#administration)
9. [Dashboard & Analytics](#dashboard--analytics)
10. [Tenant Management](#tenant-management)
11. [Error Codes](#error-codes)
12. [Rate Limits](#rate-limits)

---

## Authentication

All API endpoints (except `/health` and `/auth/login`) require authentication via JWT tokens.

### Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Endpoints

#### POST `/api/v1/auth/login`

Login with email and password.

**Request:**
```json
{
  "email": "admin@barq.com",
  "password": "secure_password"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@barq.com",
    "full_name": "Admin User",
    "role": "admin",
    "is_active": true
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account inactive
- `422 Unprocessable Entity`: Validation error

#### POST `/api/v1/auth/google`

Login with Google OAuth 2.0.

**Request:**
```json
{
  "token": "google_oauth_token"
}
```

**Response (200):**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@gmail.com",
    "full_name": "John Doe",
    "role": "user",
    "is_active": true
  }
}
```

#### GET `/api/v1/auth/me`

Get current authenticated user information.

**Response (200):**
```json
{
  "id": "uuid",
  "email": "admin@barq.com",
  "full_name": "Admin User",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z",
  "last_login": "2025-11-23T14:30:00Z"
}
```

#### POST `/api/v1/auth/refresh`

Refresh JWT token.

**Request:**
```json
{
  "refresh_token": "refresh_token_string"
}
```

**Response (200):**
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer"
}
```

---

## Fleet Management

Manage couriers, vehicles, and assignments.

### Couriers

#### GET `/api/v1/fleet/couriers`

List all couriers with pagination.

**Query Parameters:**
- `skip` (int, optional): Records to skip (default: 0)
- `limit` (int, optional): Records per page (default: 20, max: 100)
- `status` (string, optional): Filter by status (`active`, `inactive`, `suspended`)
- `search` (string, optional): Search by name, email, or phone

**Response (200):**
```json
{
  "total": 150,
  "items": [
    {
      "id": "uuid",
      "name": "Ahmed Ali",
      "email": "ahmed@example.com",
      "phone": "+966501234567",
      "national_id": "1234567890",
      "status": "active",
      "hire_date": "2024-01-15",
      "vehicle_id": "vehicle_uuid",
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### GET `/api/v1/fleet/couriers/{courier_id}`

Get courier details by ID.

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Ahmed Ali",
  "email": "ahmed@example.com",
  "phone": "+966501234567",
  "national_id": "1234567890",
  "license_number": "LIC123456",
  "license_expiry": "2026-12-31",
  "status": "active",
  "hire_date": "2024-01-15",
  "vehicle": {
    "id": "vehicle_uuid",
    "plate_number": "ABC-1234",
    "model": "Honda CRV 2023"
  },
  "bank_details": {
    "bank_name": "Al Rajhi Bank",
    "iban": "SA0380000000608010167519",
    "account_number": "1234567890"
  },
  "emergency_contact": {
    "name": "Mohammed Ali",
    "phone": "+966507654321",
    "relationship": "Brother"
  }
}
```

#### POST `/api/v1/fleet/couriers`

Create a new courier.

**Request:**
```json
{
  "name": "Ahmed Ali",
  "email": "ahmed@example.com",
  "phone": "+966501234567",
  "national_id": "1234567890",
  "license_number": "LIC123456",
  "license_expiry": "2026-12-31",
  "hire_date": "2024-01-15",
  "bank_name": "Al Rajhi Bank",
  "iban": "SA0380000000608010167519",
  "emergency_contact_name": "Mohammed Ali",
  "emergency_contact_phone": "+966507654321",
  "emergency_contact_relationship": "Brother"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "name": "Ahmed Ali",
  "email": "ahmed@example.com",
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid data
- `409 Conflict`: Email or national_id already exists
- `422 Unprocessable Entity`: Validation error

#### PUT `/api/v1/fleet/couriers/{courier_id}`

Update courier information.

**Request:**
```json
{
  "name": "Ahmed Ali Updated",
  "phone": "+966501234568",
  "status": "active"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "name": "Ahmed Ali Updated",
  "phone": "+966501234568",
  "updated_at": "2025-11-23T14:30:00Z"
}
```

#### DELETE `/api/v1/fleet/couriers/{courier_id}`

Soft delete a courier.

**Response (204):** No content

### Vehicles

#### GET `/api/v1/fleet/vehicles`

List all vehicles with pagination.

**Query Parameters:**
- `skip` (int): Records to skip
- `limit` (int): Records per page
- `status` (string): Filter by status (`available`, `assigned`, `maintenance`, `retired`)
- `type` (string): Filter by type (`motorcycle`, `car`, `van`)

**Response (200):**
```json
{
  "total": 200,
  "items": [
    {
      "id": "uuid",
      "plate_number": "ABC-1234",
      "model": "Honda CRV 2023",
      "type": "car",
      "status": "assigned",
      "purchase_date": "2023-06-15",
      "mileage": 45000,
      "last_maintenance": "2025-10-15",
      "assigned_to": {
        "id": "courier_uuid",
        "name": "Ahmed Ali"
      }
    }
  ]
}
```

#### GET `/api/v1/fleet/vehicles/{vehicle_id}`

Get vehicle details by ID.

**Response (200):**
```json
{
  "id": "uuid",
  "plate_number": "ABC-1234",
  "model": "Honda CRV 2023",
  "type": "car",
  "status": "assigned",
  "purchase_date": "2023-06-15",
  "purchase_price": 85000.00,
  "mileage": 45000,
  "last_maintenance": "2025-10-15",
  "next_maintenance_due": "2026-01-15",
  "insurance_expiry": "2026-06-15",
  "registration_expiry": "2026-06-15",
  "assigned_to": {
    "id": "courier_uuid",
    "name": "Ahmed Ali",
    "phone": "+966501234567"
  },
  "maintenance_history": [
    {
      "date": "2025-10-15",
      "type": "scheduled",
      "description": "Oil change and tire rotation",
      "cost": 500.00
    }
  ]
}
```

#### POST `/api/v1/fleet/vehicles`

Add a new vehicle to fleet.

**Request:**
```json
{
  "plate_number": "ABC-1234",
  "model": "Honda CRV 2023",
  "type": "car",
  "purchase_date": "2023-06-15",
  "purchase_price": 85000.00,
  "insurance_expiry": "2026-06-15",
  "registration_expiry": "2026-06-15"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "plate_number": "ABC-1234",
  "status": "available",
  "created_at": "2025-11-23T14:30:00Z"
}
```

#### PUT `/api/v1/fleet/vehicles/{vehicle_id}`

Update vehicle information.

#### DELETE `/api/v1/fleet/vehicles/{vehicle_id}`

Retire a vehicle.

### Assignments

#### GET `/api/v1/fleet/assignments`

List courier-vehicle assignments.

#### POST `/api/v1/fleet/assignments`

Assign vehicle to courier.

**Request:**
```json
{
  "courier_id": "courier_uuid",
  "vehicle_id": "vehicle_uuid",
  "start_date": "2025-11-23",
  "notes": "Initial assignment"
}
```

#### PUT `/api/v1/fleet/assignments/{assignment_id}/end`

End an assignment.

---

## HR & Finance

Manage payroll, loans, attendance, and leave requests.

### Attendance

#### GET `/api/v1/hr/attendance`

Get attendance records.

**Query Parameters:**
- `courier_id` (uuid, optional): Filter by courier
- `date_from` (date, optional): Start date
- `date_to` (date, optional): End date
- `status` (string, optional): `present`, `absent`, `late`, `leave`

**Response (200):**
```json
{
  "total": 500,
  "items": [
    {
      "id": "uuid",
      "courier_id": "courier_uuid",
      "courier_name": "Ahmed Ali",
      "date": "2025-11-23",
      "check_in": "08:00:00",
      "check_out": "17:00:00",
      "status": "present",
      "hours_worked": 9.0
    }
  ]
}
```

#### POST `/api/v1/hr/attendance`

Mark attendance for a courier.

**Request:**
```json
{
  "courier_id": "courier_uuid",
  "date": "2025-11-23",
  "check_in": "08:00:00",
  "check_out": "17:00:00",
  "status": "present"
}
```

### Payroll

#### GET `/api/v1/hr/payroll`

Get payroll records.

**Query Parameters:**
- `month` (int): Month (1-12)
- `year` (int): Year
- `courier_id` (uuid, optional): Filter by courier

**Response (200):**
```json
{
  "total": 150,
  "items": [
    {
      "id": "uuid",
      "courier_id": "courier_uuid",
      "courier_name": "Ahmed Ali",
      "month": 11,
      "year": 2025,
      "basic_salary": 5000.00,
      "allowances": 500.00,
      "deductions": 200.00,
      "net_salary": 5300.00,
      "status": "paid",
      "paid_date": "2025-11-30"
    }
  ]
}
```

#### POST `/api/v1/hr/payroll/generate`

Generate payroll for a month.

**Request:**
```json
{
  "month": 11,
  "year": 2025
}
```

### Loans

#### GET `/api/v1/hr/loans`

List all loans.

**Query Parameters:**
- `courier_id` (uuid, optional)
- `status` (string, optional): `pending`, `approved`, `rejected`, `active`, `completed`

**Response (200):**
```json
{
  "total": 50,
  "items": [
    {
      "id": "uuid",
      "courier_id": "courier_uuid",
      "courier_name": "Ahmed Ali",
      "amount": 10000.00,
      "installments": 10,
      "installment_amount": 1000.00,
      "remaining_amount": 5000.00,
      "status": "active",
      "request_date": "2025-01-15",
      "approval_date": "2025-01-20"
    }
  ]
}
```

#### POST `/api/v1/hr/loans`

Request a loan.

**Request:**
```json
{
  "courier_id": "courier_uuid",
  "amount": 10000.00,
  "installments": 10,
  "reason": "Medical emergency"
}
```

#### PUT `/api/v1/hr/loans/{loan_id}/approve`

Approve a loan request.

#### PUT `/api/v1/hr/loans/{loan_id}/reject`

Reject a loan request.

### Leave Requests

#### GET `/api/v1/hr/leaves`

List leave requests.

**Response (200):**
```json
{
  "total": 100,
  "items": [
    {
      "id": "uuid",
      "courier_id": "courier_uuid",
      "courier_name": "Ahmed Ali",
      "leave_type": "annual",
      "start_date": "2025-12-01",
      "end_date": "2025-12-07",
      "days": 7,
      "status": "approved",
      "reason": "Family vacation"
    }
  ]
}
```

#### POST `/api/v1/hr/leaves`

Request leave.

**Request:**
```json
{
  "courier_id": "courier_uuid",
  "leave_type": "annual",
  "start_date": "2025-12-01",
  "end_date": "2025-12-07",
  "reason": "Family vacation"
}
```

---

## Operations

Manage deliveries, incidents, and vehicle logs.

### Deliveries

#### GET `/api/v1/operations/deliveries`

List deliveries.

**Query Parameters:**
- `courier_id` (uuid, optional)
- `status` (string, optional): `pending`, `in_progress`, `completed`, `failed`
- `date_from` (date, optional)
- `date_to` (date, optional)

**Response (200):**
```json
{
  "total": 1000,
  "items": [
    {
      "id": "uuid",
      "courier_id": "courier_uuid",
      "courier_name": "Ahmed Ali",
      "order_number": "ORD-12345",
      "status": "completed",
      "pickup_address": "Riyadh, Saudi Arabia",
      "delivery_address": "Jeddah, Saudi Arabia",
      "scheduled_time": "2025-11-23T10:00:00Z",
      "completed_time": "2025-11-23T14:30:00Z",
      "cod_amount": 500.00
    }
  ]
}
```

#### POST `/api/v1/operations/deliveries`

Create new delivery task.

#### PUT `/api/v1/operations/deliveries/{delivery_id}/status`

Update delivery status.

### Incidents

#### GET `/api/v1/operations/incidents`

List incident reports.

**Response (200):**
```json
{
  "total": 25,
  "items": [
    {
      "id": "uuid",
      "courier_id": "courier_uuid",
      "courier_name": "Ahmed Ali",
      "vehicle_id": "vehicle_uuid",
      "incident_type": "accident",
      "date": "2025-11-20",
      "description": "Minor collision at intersection",
      "severity": "low",
      "status": "resolved",
      "cost": 2000.00
    }
  ]
}
```

#### POST `/api/v1/operations/incidents`

Report an incident.

### Vehicle Logs

#### GET `/api/v1/operations/vehicle-logs`

Get vehicle maintenance logs.

#### POST `/api/v1/operations/vehicle-logs`

Log vehicle maintenance.

---

## Accommodation

Manage courier housing and accommodations.

### Buildings

#### GET `/api/v1/accommodation/buildings`

List all buildings.

#### POST `/api/v1/accommodation/buildings`

Add new building.

### Rooms

#### GET `/api/v1/accommodation/rooms`

List all rooms.

#### GET `/api/v1/accommodation/rooms/{room_id}/occupants`

Get room occupants.

#### POST `/api/v1/accommodation/rooms/{room_id}/assign`

Assign courier to room.

---

## Workflow Engine

Manage approval workflows.

### Workflow Instances

#### GET `/api/v1/workflow/instances`

List workflow instances.

**Query Parameters:**
- `type` (string, optional): `leave_request`, `loan_request`, `vehicle_assignment`
- `status` (string, optional): `pending`, `approved`, `rejected`

**Response (200):**
```json
{
  "total": 50,
  "items": [
    {
      "id": "uuid",
      "workflow_type": "leave_request",
      "entity_id": "leave_request_uuid",
      "status": "pending",
      "current_step": "manager_approval",
      "initiated_by": "courier_uuid",
      "initiated_at": "2025-11-23T10:00:00Z"
    }
  ]
}
```

#### GET `/api/v1/workflow/instances/{instance_id}`

Get workflow instance details.

#### POST `/api/v1/workflow/instances/{instance_id}/approve`

Approve workflow step.

#### POST `/api/v1/workflow/instances/{instance_id}/reject`

Reject workflow step.

---

## Support

Manage support tickets.

### Tickets

#### GET `/api/v1/support/tickets`

List support tickets.

**Response (200):**
```json
{
  "total": 75,
  "items": [
    {
      "id": "uuid",
      "ticket_number": "TKT-12345",
      "subject": "Vehicle maintenance issue",
      "description": "Vehicle making strange noise",
      "status": "open",
      "priority": "high",
      "category": "vehicle",
      "created_by": "courier_uuid",
      "assigned_to": "support_agent_uuid",
      "created_at": "2025-11-23T10:00:00Z"
    }
  ]
}
```

#### POST `/api/v1/support/tickets`

Create support ticket.

#### PUT `/api/v1/support/tickets/{ticket_id}`

Update ticket.

---

## Administration

Admin-only endpoints.

### Users

#### GET `/api/v1/admin/users`

List all users.

#### POST `/api/v1/admin/users`

Create new user.

#### PUT `/api/v1/admin/users/{user_id}/role`

Update user role.

### Roles & Permissions

#### GET `/api/v1/admin/roles`

List all roles.

#### POST `/api/v1/admin/roles`

Create new role.

#### GET `/api/v1/admin/permissions`

List all permissions.

---

## Dashboard & Analytics

### Dashboard

#### GET `/api/v1/dashboard/stats`

Get dashboard statistics.

**Response (200):**
```json
{
  "total_couriers": 150,
  "active_couriers": 140,
  "total_vehicles": 200,
  "available_vehicles": 60,
  "today_deliveries": 500,
  "completed_deliveries": 450,
  "pending_approvals": 15,
  "total_revenue": 150000.00
}
```

#### GET `/api/v1/dashboard/courier-performance`

Get courier performance metrics.

---

## Tenant Management

Multi-tenancy support.

#### GET `/api/v1/tenant/info`

Get current tenant information.

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `AUTH_001` | 401 | Invalid credentials |
| `AUTH_002` | 401 | Token expired |
| `AUTH_003` | 403 | Insufficient permissions |
| `VAL_001` | 422 | Validation error |
| `RES_001` | 404 | Resource not found |
| `DUP_001` | 409 | Duplicate entry |
| `SRV_001` | 500 | Internal server error |

**Example Error Response:**
```json
{
  "detail": "Invalid credentials provided",
  "code": "AUTH_001"
}
```

---

## Rate Limits

- **Anonymous requests:** 100 requests per hour
- **Authenticated requests:** 1000 requests per hour
- **Admin requests:** 5000 requests per hour

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1700000000
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 20, max: 100)

**Response Format:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 20,
  "items": [...]
}
```

---

## Filtering & Sorting

Many endpoints support filtering and sorting:

**Query Parameters:**
- `sort_by`: Field to sort by (e.g., `created_at`, `name`)
- `sort_order`: `asc` or `desc` (default: `desc`)
- `status`: Filter by status
- `date_from`: Filter by start date
- `date_to`: Filter by end date

**Example:**
```
GET /api/v1/fleet/couriers?status=active&sort_by=name&sort_order=asc
```

---

## Webhooks

BARQ supports webhooks for real-time notifications.

**Supported Events:**
- `courier.created`
- `courier.updated`
- `delivery.completed`
- `loan.approved`
- `leave.approved`

**Webhook Payload:**
```json
{
  "event": "delivery.completed",
  "timestamp": "2025-11-23T14:30:00Z",
  "data": {
    "id": "uuid",
    "order_number": "ORD-12345",
    "status": "completed"
  }
}
```

---

## SDKs & Client Libraries

Official SDKs coming soon:
- JavaScript/TypeScript
- Python
- PHP

**Current Options:**
- Use Swagger UI to generate client code
- Download OpenAPI JSON: `/api/v1/openapi.json`

---

**For interactive API documentation, visit:**
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc

**Support:** support@barq.com
