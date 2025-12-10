# Fleet API Documentation

The Fleet API provides endpoints for managing couriers, vehicles, assignments, and fleet operations.

## Base URL

```
/api/v1/fleet
```

## Authentication

All endpoints require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

---

## Couriers

### List Couriers

```http
GET /couriers
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page (default: 20, max: 100) |
| `status` | string | Filter by status: `active`, `on_leave`, `terminated` |
| `city` | string | Filter by assigned city |
| `search` | string | Search by name, employee_id, or phone |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "employee_id": "EMP-001",
      "name": "Ahmed Al-Rashid",
      "phone": "+966501234567",
      "email": "ahmed@barq.com",
      "status": "active",
      "city": "Riyadh",
      "joining_date": "2024-01-15",
      "license_expiry": "2025-06-30",
      "assigned_vehicle_id": 5,
      "performance_score": 4.8,
      "total_deliveries": 1250
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

### Get Courier

```http
GET /couriers/{id}
```

**Response:**

```json
{
  "id": 1,
  "employee_id": "EMP-001",
  "name": "Ahmed Al-Rashid",
  "phone": "+966501234567",
  "email": "ahmed@barq.com",
  "status": "active",
  "city": "Riyadh",
  "joining_date": "2024-01-15",
  "license_number": "DL-123456",
  "license_expiry": "2025-06-30",
  "national_id": "1234567890",
  "address": "King Fahd Road, Riyadh",
  "emergency_contact": "+966509876543",
  "bank_name": "Al Rajhi Bank",
  "bank_account_number": "1234567890123",
  "iban": "SA1234567890123456789012",
  "assigned_vehicle": {
    "id": 5,
    "plate_number": "ABC 1234",
    "type": "motorcycle"
  },
  "current_location": {
    "latitude": 24.7136,
    "longitude": 46.6753,
    "last_updated": "2024-12-10T10:30:00Z"
  },
  "documents": [
    {
      "type": "national_id",
      "expiry_date": "2028-05-20",
      "status": "valid"
    }
  ],
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-12-10T09:00:00Z"
}
```

### Create Courier

```http
POST /couriers
```

**Request Body:**

```json
{
  "employee_id": "EMP-002",
  "name": "Mohammed Al-Saud",
  "phone": "+966502345678",
  "email": "mohammed@barq.com",
  "status": "active",
  "city": "Jeddah",
  "joining_date": "2024-12-01",
  "license_number": "DL-789012",
  "license_expiry": "2026-03-15",
  "national_id": "0987654321",
  "address": "Corniche Road, Jeddah",
  "emergency_contact": "+966508765432"
}
```

**Response:** `201 Created`

### Update Courier

```http
PUT /couriers/{id}
```

**Request Body:** Same as Create (partial updates supported)

**Response:** `200 OK`

### Delete Courier

```http
DELETE /couriers/{id}
```

**Response:** `204 No Content`

---

## Vehicles

### List Vehicles

```http
GET /vehicles
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `limit` | integer | Items per page |
| `type` | string | Filter by type: `sedan`, `van`, `truck`, `motorcycle`, `bicycle` |
| `status` | string | Filter by status: `available`, `in_use`, `maintenance`, `retired` |
| `fuel_type` | string | Filter by fuel type: `gasoline`, `diesel`, `electric`, `hybrid` |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "plate_number": "ABC 1234",
      "type": "motorcycle",
      "make": "Honda",
      "model": "PCX 150",
      "year": 2023,
      "fuel_type": "gasoline",
      "status": "in_use",
      "mileage": 15000,
      "assigned_courier_id": 1,
      "assigned_courier_name": "Ahmed Al-Rashid"
    }
  ],
  "total": 75,
  "page": 1,
  "pages": 4
}
```

### Get Vehicle

```http
GET /vehicles/{id}
```

### Create Vehicle

```http
POST /vehicles
```

**Request Body:**

```json
{
  "plate_number": "XYZ 5678",
  "type": "van",
  "make": "Toyota",
  "model": "Hiace",
  "year": 2024,
  "color": "White",
  "fuel_type": "diesel",
  "ownership": "owned",
  "status": "available",
  "vin": "JTFSK22P000123456",
  "purchase_date": "2024-06-01",
  "registration_expiry": "2025-06-01",
  "insurance_expiry": "2025-06-01"
}
```

### Update Vehicle

```http
PUT /vehicles/{id}
```

### Delete Vehicle

```http
DELETE /vehicles/{id}
```

---

## Vehicle Assignments

### List Assignments

```http
GET /assignments
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Filter by courier |
| `vehicle_id` | integer | Filter by vehicle |
| `active` | boolean | Filter active assignments only |

### Create Assignment

```http
POST /assignments
```

**Request Body:**

```json
{
  "courier_id": 1,
  "vehicle_id": 5,
  "start_date": "2024-12-10",
  "end_date": null,
  "notes": "Primary delivery vehicle"
}
```

### End Assignment

```http
POST /assignments/{id}/end
```

**Request Body:**

```json
{
  "end_date": "2024-12-31",
  "reason": "Vehicle scheduled for maintenance"
}
```

---

## Courier Documents

### List Documents

```http
GET /couriers/{courier_id}/documents
```

### Upload Document

```http
POST /couriers/{courier_id}/documents
```

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | Document file (PDF, JPG, PNG) |
| `document_type` | string | Yes | Type of document |
| `expiry_date` | string | No | Document expiry date |
| `notes` | string | No | Additional notes |

**Document Types:**
- `national_id`
- `driving_license`
- `passport`
- `employment_contract`
- `medical_certificate`
- `other`

### Delete Document

```http
DELETE /couriers/{courier_id}/documents/{document_id}
```

---

## Performance

### Get Courier Performance

```http
GET /couriers/{id}/performance
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start of period (ISO 8601) |
| `end_date` | string | End of period (ISO 8601) |

**Response:**

```json
{
  "courier_id": 1,
  "period": {
    "start": "2024-12-01",
    "end": "2024-12-10"
  },
  "metrics": {
    "total_deliveries": 125,
    "successful_deliveries": 120,
    "failed_deliveries": 3,
    "cancelled_deliveries": 2,
    "success_rate": 96.0,
    "average_delivery_time_minutes": 28.5,
    "on_time_percentage": 94.2,
    "customer_rating": 4.8,
    "total_distance_km": 450.5,
    "fuel_consumption_liters": 45.2
  }
}
```

### Get Fleet Analytics

```http
GET /analytics/fleet
```

**Response:**

```json
{
  "total_couriers": 150,
  "active_couriers": 135,
  "on_leave_couriers": 10,
  "total_vehicles": 75,
  "vehicles_in_use": 60,
  "vehicles_in_maintenance": 8,
  "average_deliveries_per_courier": 15.5,
  "fleet_utilization_percentage": 80.0
}
```

---

## Error Responses

All endpoints may return the following errors:

| Status Code | Description |
|-------------|-------------|
| `400` | Bad Request - Invalid parameters |
| `401` | Unauthorized - Invalid or missing token |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found - Resource not found |
| `409` | Conflict - Resource already exists |
| `422` | Unprocessable Entity - Validation error |
| `500` | Internal Server Error |

**Error Response Format:**

```json
{
  "detail": "Error message description",
  "code": "ERROR_CODE",
  "field": "field_name"
}
```
