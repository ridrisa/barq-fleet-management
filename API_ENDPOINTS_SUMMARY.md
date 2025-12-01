# BARQ Fleet Management API - Comprehensive Endpoints Summary

## Overview
This document provides a complete inventory of all API endpoints in the BARQ Fleet Management backend application built with FastAPI and Python.

**Total Endpoints:** 200+
**Base URL:** `/api/v1`
**Documentation Location:** `/api/v1/docs` (Swagger UI)
**Alternative Docs:** `/api/v1/redoc` (ReDoc)

---

## Quick Statistics

### By Module
| Module | Count | Description |
|--------|-------|-------------|
| Authentication | 3 | Login, Google OAuth, Registration |
| Health & Dashboard | 3 | Health checks and dashboard stats |
| Admin - Roles | 8 | Role CRUD and permission assignment |
| Admin - Permissions | 6 | Permission CRUD and filtering |
| Admin - Audit Logs | 6 | Audit trail and activity logging |
| Admin - Users | 9 | User management and role assignment |
| Fleet - Vehicles | 15 | Vehicle management and maintenance |
| Fleet - Couriers | 14 | Courier management |
| Fleet - Assignments | 5 | Vehicle-Courier assignments |
| Fleet - Maintenance | 7 | Maintenance scheduling and tracking |
| Fleet - Inspections | 7 | Vehicle inspections |
| Fleet - Accident Logs | 7 | Accident incident tracking |
| Fleet - Vehicle Logs | 6 | Vehicle activity logging |
| HR - Attendance | 8 | Check-in/out and attendance tracking |
| HR - Leave Management | 8 | Leave requests and approvals |
| HR - Salary | 8 | Salary calculations and payments |
| HR - Loans | 7 | Employee loan management |
| HR - Assets | 9 | Asset allocation and tracking |
| Operations - Deliveries | 9 | Delivery management and tracking |
| Operations - Routes | 10 | Route planning and optimization |
| Operations - COD | 13 | Cash on delivery transactions |
| Operations - Incidents | 13 | Incident reporting and resolution |
| Workflow - Templates | 8 | Workflow template management |
| Workflow - Instances | 15 | Workflow execution and state management |

**TOTAL: ~220 endpoints**

---

## Authentication
- **Type:** JWT Bearer Token
- **Expiration:** 7 days
- **Supported Methods:**
  - Email/Password (OAuth2)
  - Google OAuth2
  - Public Registration (first user becomes admin)

### Public Endpoints (No Auth Required)
- `GET /` - API root
- `GET /health` - Health check
- `POST /auth/login` - Login
- `POST /auth/google` - Google auth
- `POST /auth/register` - Registration

---

## Authentication-Required Endpoints
All other endpoints require JWT Bearer token authentication.

### Superuser-Only Endpoints
All `/admin/*` routes require superuser privileges.

---

## Pagination Standards
Most list endpoints support:
- `skip` (int, default: 0): Offset for pagination
- `limit` (int, default: 100): Records per page (max varies by endpoint)

Common max limits:
- Fleet/HR/Operations: 1000
- Admin endpoints: 100

---

## HTTP Methods Summary
| Method | Count | Purpose |
|--------|-------|---------|
| GET | ~120 | Retrieve data (list, get by ID, statistics, etc.) |
| POST | ~60 | Create new records and trigger actions |
| PUT | ~20 | Full updates of resources |
| PATCH | ~15 | Partial updates and state changes |
| DELETE | ~20 | Delete records |

---

## Response Status Codes
- **200 OK** - Successful GET/PUT/PATCH
- **201 Created** - Successful POST resource creation
- **204 No Content** - Successful DELETE
- **400 Bad Request** - Invalid input or validation errors
- **401 Unauthorized** - Missing or invalid authentication
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **500 Internal Server Error** - Server error

---

## Common Query Parameters

### Pagination
```
skip=0&limit=100
```

### Filtering
- `search` - Full-text search
- `status` - Status filtering (varies by resource)
- `date_from` / `date_to` - Date range filtering
- `courier_id`, `vehicle_id` - Foreign key filtering
- `is_active` - Active status filtering

### Sorting
Implemented via order_by in services (not query params)

---

## Module Deep Dives

### 1. Fleet Management (57 endpoints)
Manages vehicles, couriers, and their operations.

**Key Features:**
- Vehicle tracking and maintenance scheduling
- Courier management with document tracking
- Vehicle-Courier assignments
- Maintenance history and inspections
- Accident logging and tracking
- Activity logs for auditing

### 2. HR Management (42 endpoints)
Manages employee data, attendance, and compensation.

**Key Features:**
- Check-in/check-out system
- Leave request workflows
- Salary calculation and payment tracking
- Employee loan management
- Asset allocation tracking

### 3. Operations Management (45 endpoints)
Manages deliveries, routes, and financial transactions.

**Key Features:**
- Delivery tracking with status updates
- Route optimization and waypoint management
- COD collection and settlement
- Incident reporting and resolution

### 4. Admin Management (29 endpoints)
System administration and security features.

**Key Features:**
- Role-Based Access Control (RBAC)
- Permission management
- Comprehensive audit logging
- User account management

### 5. Workflow Management (23 endpoints)
Generic workflow execution engine.

**Key Features:**
- Template-based workflows
- Workflow instance lifecycle management
- Step-by-step progression
- Approval workflows

---

## Database Models Covered

The API covers the following main entities:
- User, Role, Permission (Auth & RBAC)
- Vehicle, Courier, Assignment (Fleet)
- Maintenance, Inspection, AccidentLog (Fleet Operations)
- Attendance, Leave, Salary, Loan, Asset (HR)
- Delivery, Route, COD, Incident (Operations)
- WorkflowTemplate, WorkflowInstance (Workflows)
- AuditLog (System Tracking)

---

## Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error description",
  "code": "ERROR_CODE"
}
```

### Common Validations
- Email uniqueness
- BARQ ID uniqueness
- Date range validation
- Status transition validation
- Foreign key constraint checking
- Superuser-only operation checks
- Prevent self-deactivation
- Prevent last superuser deactivation

---

## Special Features

### 1. Bulk Operations
- `POST /fleet/vehicles/bulk-update` - Update multiple vehicles
- `POST /fleet/couriers/bulk-update` - Update multiple couriers
- `POST /operations/cod/bulk-deposit` - Bulk COD deposits

### 2. Advanced Filtering
- Multi-field search capabilities
- Date range filtering
- Status-based filtering
- Foreign key relationships

### 3. Statistics Endpoints
Most modules have `/statistics` endpoints providing:
- Aggregate counts
- Breakdown by categories
- Trends and summaries
- Performance metrics

### 4. Workflow Management
- Template-based approach
- Multiple status states
- Approval workflows
- Step tracking

### 5. Audit Trail
- Comprehensive audit logging
- Resource change tracking
- User activity logs
- IP address logging
- Timestamp tracking

---

## Integration Points

### External Services
- **Google OAuth2** - User authentication
- **PostgreSQL** - Data persistence
- **JWT** - Token-based authentication

### Internal Services
- CRUD services (data access layer)
- Business logic services
- Audit logging service
- Database session management

---

## Code Organization

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py (3 endpoints)
│   │   │   ├── health.py (1 endpoint)
│   │   │   ├── dashboard.py (1 endpoint)
│   │   │   ├── admin/ (29 endpoints)
│   │   │   ├── fleet/ (57 endpoints)
│   │   │   ├── hr/ (42 endpoints)
│   │   │   ├── operations/ (45 endpoints)
│   │   │   └── workflow/ (23 endpoints)
│   ├── services/ (Business logic)
│   ├── models/ (ORM models)
│   ├── schemas/ (Pydantic schemas)
│   └── crud/ (Data access)
```

---

## Testing Considerations

### Test Coverage Areas
1. **Authentication** - Login flows, token validation
2. **Authorization** - Role-based access control
3. **CRUD Operations** - Create, read, update, delete
4. **Business Logic** - Workflows, calculations
5. **Data Validation** - Input constraints
6. **Error Handling** - Edge cases
7. **Pagination** - Large datasets
8. **Filtering** - Multiple filter combinations

### Performance Considerations
- Implement pagination on large datasets
- Use database indexes for filtered queries
- Consider caching for frequently accessed data
- Monitor query performance on complex filters

---

## Documentation

### Where to Find
1. **Interactive Docs:** `/api/v1/docs` (Swagger UI)
2. **Alternative Docs:** `/api/v1/redoc` (ReDoc)
3. **Complete Reference:** `API_ENDPOINTS_DOCUMENTATION.md` (in project root)

### What Each Contains
- Full endpoint descriptions
- Request/response schemas
- Query parameters
- Authentication requirements
- Example requests/responses

---

## Deployment Notes

### Required Environment Variables
- `SECRET_KEY` - JWT secret
- `ALGORITHM` - JWT algorithm (default: HS256)
- `GOOGLE_CLIENT_ID` - For OAuth (optional)
- `DATABASE_URL` - PostgreSQL connection string
- `BACKEND_CORS_ORIGINS` - CORS allowed origins

### CORS Configuration
Default allowed origins:
- `http://localhost:3000` (React dev)
- `http://localhost:5173` (Vite dev)

---

## Maintenance Guidelines

### Adding New Endpoints
1. Create route in appropriate module
2. Define request/response schemas
3. Implement business logic in services
4. Add proper error handling
5. Document with docstrings
6. Update this documentation

### Code Standards
- All routes use dependency injection
- Database sessions managed via FastAPI dependencies
- Consistent error response format
- Comprehensive docstrings
- Type hints on all functions

---

## Version History

**Current Version:** 1.0.0
**API Version String:** `/api/v1`

---

## Support & Questions

For API-related questions, refer to:
1. Interactive API documentation at `/api/v1/docs`
2. Complete endpoint documentation in `API_ENDPOINTS_DOCUMENTATION.md`
3. Source code route files in `app/api/`

---

**Generated:** 2025-11-13
**Framework:** FastAPI
**Python Version:** 3.8+
**Database:** PostgreSQL

