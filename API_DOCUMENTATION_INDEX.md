# BARQ Fleet Management - API Documentation Index

Welcome! This directory contains comprehensive documentation for all API endpoints in the BARQ Fleet Management system.

## Documentation Files

### 1. **API_ENDPOINTS_SUMMARY.md** (Quick Reference)
- **Size:** ~10 KB
- **Best for:** Quick overview and statistics
- **Contains:**
  - Module statistics and endpoint counts
  - Authentication information
  - HTTP methods summary
  - Common patterns and standards
  - Integration points
  - Deployment notes
  
**Start here if you want:** A bird's-eye view of the API

---

### 2. **API_ENDPOINTS_DOCUMENTATION.md** (Comprehensive Reference)
- **Size:** ~47 KB
- **Best for:** Detailed endpoint information
- **Contains:**
  - Complete endpoint listing organized by module
  - HTTP method for each endpoint
  - Full endpoint path with prefixes
  - Authentication requirements
  - Query parameters with types and defaults
  - Request body specifications
  - Response format descriptions
  - Error handling information

**Start here if you want:** Detailed specifications for specific endpoints

---

### 3. **API_DOCUMENTATION_INDEX.md** (This File)
Navigation guide for all API documentation

---

## Quick Navigation

### By Use Case

#### I want to understand the overall API structure
→ Read: **API_ENDPOINTS_SUMMARY.md**

#### I need to find a specific endpoint
→ Search in: **API_ENDPOINTS_DOCUMENTATION.md**

#### I'm integrating with the API
→ Read: **API_ENDPOINTS_DOCUMENTATION.md** (appropriate section)

#### I'm setting up authentication
→ See: **API_ENDPOINTS_DOCUMENTATION.md** → Authentication section

#### I'm building a client application
→ Start with: **API_ENDPOINTS_SUMMARY.md** → Move to **API_ENDPOINTS_DOCUMENTATION.md** as needed

---

## API Organization

### Core Modules (220+ endpoints total)

1. **Authentication (3 endpoints)**
   - Email/password login
   - Google OAuth2
   - Public registration

2. **Fleet Management (57 endpoints)**
   - Vehicles (15)
   - Couriers (14)
   - Assignments (5)
   - Maintenance (7)
   - Inspections (7)
   - Accident Logs (7)
   - Vehicle Logs (6)

3. **HR Management (42 endpoints)**
   - Attendance (8)
   - Leave (8)
   - Salary (8)
   - Loans (7)
   - Assets (9)

4. **Operations Management (45 endpoints)**
   - Deliveries (9)
   - Routes (10)
   - COD Transactions (13)
   - Incidents (13)

5. **Admin Management (29 endpoints)**
   - Roles (8)
   - Permissions (6)
   - Audit Logs (6)
   - Users (9)

6. **Workflow Management (23 endpoints)**
   - Templates (8)
   - Instances (15)

---

## Base URL and Versions

**Base URL:** `/api/v1`

**Live Documentation:**
- Swagger UI: `{BASE_URL}/docs`
- ReDoc: `{BASE_URL}/redoc`
- OpenAPI JSON: `{BASE_URL}/openapi.json`

---

## Authentication

All endpoints except the following require JWT Bearer token:
- `GET /` - API root
- `GET /health` - Health check
- `POST /auth/login` - Email/password login
- `POST /auth/google` - Google OAuth
- `POST /auth/register` - Registration

**Token expiration:** 7 days

---

## Common Patterns

### Pagination
```
GET /api/v1/fleet/vehicles?skip=0&limit=100
```

### Filtering
```
GET /api/v1/fleet/vehicles?status=active&vehicle_type=van
```

### Searching
```
GET /api/v1/fleet/couriers?search=john
```

### Date Range Filtering
```
GET /api/v1/operations/deliveries?start_date=2025-01-01&end_date=2025-01-31
```

### Statistics
```
GET /api/v1/fleet/vehicles/statistics
GET /api/v1/hr/attendance/statistics
```

---

## Response Format

### Success Response (200 OK)
```json
{
  "id": 1,
  "name": "Example",
  "status": "active",
  "created_at": "2025-11-13T10:00:00Z"
}
```

### List Response with Pagination
```json
[
  {
    "id": 1,
    "name": "Item 1"
  },
  {
    "id": 2,
    "name": "Item 2"
  }
]
```

### Error Response (4xx/5xx)
```json
{
  "detail": "Error description",
  "code": "ERROR_CODE"
}
```

### Resource Created (201 Created)
```json
{
  "id": 1,
  "name": "New Resource",
  "status": "created"
}
```

### No Content (204 No Content)
Empty response body

---

## HTTP Status Codes Used

| Code | Meaning | Common Scenarios |
|------|---------|------------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST creating resource |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input, validation errors |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions (non-superuser) |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Unexpected server error |

---

## Rate Limiting & Pagination

### Standard Limits
- **Default page size:** 100 records
- **Maximum page size:** 1000 (varies by endpoint)
- **Admin endpoints:** Limited to 100 max

### Pagination Query
```
skip=0&limit=100
```

---

## Authentication Headers

### Bearer Token Format
```
Authorization: Bearer {jwt_token}
```

### Example Request
```bash
curl -X GET \
  "http://localhost:8000/api/v1/fleet/vehicles" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Common Filters

### By Status
```
?status=active
?status=inactive
```

### By Date Range
```
?start_date=2025-01-01&end_date=2025-01-31
```

### By User/Entity ID
```
?courier_id=123
?vehicle_id=456
?user_id=789
```

### By Role
```
?role_id=1
```

### By Search Term
```
?search=keyword
```

---

## Special Features

### Bulk Operations
- Update multiple vehicles at once
- Update multiple couriers at once
- Bulk COD deposits

### Statistics Endpoints
Most modules provide `/statistics` endpoints with:
- Total counts
- Status breakdowns
- Time-based aggregations
- Top performers/entities

### Workflow System
- Template-based workflows
- Multi-step process execution
- Approval workflows
- State management

### Audit Trail
- Comprehensive activity logging
- Resource change tracking
- User action tracking
- IP address logging

---

## Using the Documentation

### For API Integration
1. Refer to **API_ENDPOINTS_DOCUMENTATION.md** for your module
2. Check the Authentication section for token requirements
3. Review Query Parameters for filtering options
4. Check Request Body format for POST/PUT/PATCH
5. Review Response format

### For Development
1. Start with **API_ENDPOINTS_SUMMARY.md** to understand modules
2. Review Code Organization section
3. Check Integration Points
4. Review Error Handling patterns

### For Testing
1. Use Swagger UI at `/api/v1/docs` to test endpoints
2. Refer to documentation for test scenarios
3. Check validation rules in endpoint descriptions

---

## Support Resources

### Online Documentation
- **Swagger UI:** `/api/v1/docs`
- **ReDoc:** `/api/v1/redoc`
- **OpenAPI Schema:** `/api/v1/openapi.json`

### Project Files
- Source code: `backend/app/api/v1/`
- Models: `backend/app/models/`
- Schemas: `backend/app/schemas/`
- Services: `backend/app/services/`

---

## Document Version

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-13 | Initial comprehensive documentation |

---

## Quick Reference Tables

### Module Endpoint Count by Category

| Category | Endpoints | Key Resources |
|----------|-----------|---|
| Authentication | 3 | Login, OAuth, Register |
| Health | 3 | Health, Dashboard |
| Admin | 29 | Users, Roles, Permissions, Audit |
| Fleet | 57 | Vehicles, Couriers, Maintenance, Inspections |
| HR | 42 | Attendance, Leave, Salary, Loans, Assets |
| Operations | 45 | Deliveries, Routes, COD, Incidents |
| Workflow | 23 | Templates, Instances |
| **TOTAL** | **~220** | |

### HTTP Methods Distribution

| Method | Count | Use Case |
|--------|-------|----------|
| GET | ~120 | Retrieve data |
| POST | ~60 | Create/Action |
| PUT | ~20 | Full update |
| PATCH | ~15 | Partial update |
| DELETE | ~20 | Delete |

---

## Next Steps

1. **Start Reading:**
   - Begin with **API_ENDPOINTS_SUMMARY.md** for overview
   - Then dive into **API_ENDPOINTS_DOCUMENTATION.md** for details

2. **Interactive Testing:**
   - Visit `/api/v1/docs` in your browser
   - Try endpoints directly with Swagger UI
   - Check response formats

3. **Integration:**
   - Pick your module of interest
   - Review all endpoints in that section
   - Check authentication and parameters
   - Start building!

---

**Documentation generated:** 2025-11-13  
**API Version:** 1.0.0  
**Framework:** FastAPI  
**Language:** Python 3.8+  
**Database:** PostgreSQL

---

For questions or clarifications, refer to the relevant section in **API_ENDPOINTS_DOCUMENTATION.md** or use the interactive API documentation at `/api/v1/docs`.
