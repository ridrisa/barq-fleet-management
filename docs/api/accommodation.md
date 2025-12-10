# Accommodation API Documentation

The Accommodation API provides endpoints for managing courier housing including buildings, rooms, beds, and allocations.

## Base URL

```
/api/v1/accommodation
```

## Authentication

All endpoints require a valid JWT token. Most endpoints require `admin` or `hr_manager` role.

---

## Buildings

### List Buildings

```http
GET /buildings
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `limit` | integer | Items per page |
| `city` | string | Filter by city |
| `status` | string | Filter by status: `active`, `inactive`, `maintenance` |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Barq Housing A",
      "address": "Industrial Area, Riyadh",
      "city": "Riyadh",
      "status": "active",
      "total_rooms": 20,
      "total_beds": 80,
      "occupied_beds": 65,
      "occupancy_rate": 81.25,
      "manager_name": "Abdullah",
      "manager_phone": "+966501234567"
    }
  ],
  "total": 5,
  "page": 1
}
```

### Get Building

```http
GET /buildings/{id}
```

**Response:**

```json
{
  "id": 1,
  "name": "Barq Housing A",
  "address": "Industrial Area, Riyadh",
  "city": "Riyadh",
  "status": "active",
  "manager_name": "Abdullah",
  "manager_phone": "+966501234567",
  "facilities": ["wifi", "laundry", "kitchen", "parking"],
  "monthly_cost_per_bed": 500.00,
  "rooms": [
    {
      "id": 1,
      "room_number": "101",
      "floor": 1,
      "type": "quad",
      "beds": 4,
      "occupied": 3
    }
  ],
  "statistics": {
    "total_rooms": 20,
    "total_beds": 80,
    "occupied_beds": 65,
    "available_beds": 15,
    "occupancy_rate": 81.25
  }
}
```

### Create Building

```http
POST /buildings
```

**Request Body:**

```json
{
  "name": "Barq Housing B",
  "address": "Second Industrial Area, Riyadh",
  "city": "Riyadh",
  "manager_name": "Mohammed",
  "manager_phone": "+966509876543",
  "facilities": ["wifi", "laundry", "kitchen"],
  "monthly_cost_per_bed": 450.00
}
```

### Update Building

```http
PUT /buildings/{id}
```

### Delete Building

```http
DELETE /buildings/{id}
```

---

## Rooms

### List Rooms

```http
GET /rooms
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `building_id` | integer | Filter by building |
| `floor` | integer | Filter by floor |
| `type` | string | Filter by room type |
| `available` | boolean | Show only rooms with available beds |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "building_id": 1,
      "building_name": "Barq Housing A",
      "room_number": "101",
      "floor": 1,
      "type": "quad",
      "total_beds": 4,
      "occupied_beds": 3,
      "available_beds": 1,
      "status": "active"
    }
  ]
}
```

### Get Room

```http
GET /rooms/{id}
```

**Response:**

```json
{
  "id": 1,
  "building_id": 1,
  "room_number": "101",
  "floor": 1,
  "type": "quad",
  "status": "active",
  "facilities": ["ac", "bathroom"],
  "beds": [
    {
      "id": 1,
      "bed_number": "A",
      "status": "occupied",
      "occupant": {
        "id": 5,
        "name": "Ahmed Al-Rashid",
        "employee_id": "EMP-001"
      },
      "allocation_date": "2024-06-01"
    },
    {
      "id": 2,
      "bed_number": "B",
      "status": "available"
    }
  ]
}
```

### Create Room

```http
POST /rooms
```

**Request Body:**

```json
{
  "building_id": 1,
  "room_number": "102",
  "floor": 1,
  "type": "quad",
  "facilities": ["ac", "bathroom"],
  "beds_count": 4
}
```

**Room Types:**
- `single` - 1 bed
- `double` - 2 beds
- `triple` - 3 beds
- `quad` - 4 beds
- `dorm` - 6+ beds

### Update Room

```http
PUT /rooms/{id}
```

### Delete Room

```http
DELETE /rooms/{id}
```

---

## Beds

### List Beds

```http
GET /beds
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `room_id` | integer | Filter by room |
| `building_id` | integer | Filter by building |
| `status` | string | Filter by status: `available`, `occupied`, `maintenance`, `reserved` |

### Get Bed

```http
GET /beds/{id}
```

### Create Bed

```http
POST /beds
```

**Request Body:**

```json
{
  "room_id": 1,
  "bed_number": "E",
  "status": "available"
}
```

### Update Bed Status

```http
PUT /beds/{id}
```

**Request Body:**

```json
{
  "status": "maintenance",
  "notes": "Mattress replacement needed"
}
```

---

## Allocations

### List Allocations

```http
GET /allocations
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Filter by courier |
| `building_id` | integer | Filter by building |
| `active` | boolean | Show only active allocations |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "courier_id": 5,
      "courier_name": "Ahmed Al-Rashid",
      "bed_id": 1,
      "bed_number": "A",
      "room_number": "101",
      "building_name": "Barq Housing A",
      "start_date": "2024-06-01",
      "end_date": null,
      "status": "active",
      "monthly_deduction": 500.00
    }
  ]
}
```

### Get Courier Allocation

```http
GET /allocations/courier/{courier_id}
```

**Response:**

```json
{
  "courier_id": 5,
  "has_allocation": true,
  "allocation": {
    "id": 1,
    "bed": {
      "id": 1,
      "bed_number": "A",
      "room_number": "101",
      "floor": 1
    },
    "building": {
      "id": 1,
      "name": "Barq Housing A",
      "address": "Industrial Area, Riyadh"
    },
    "start_date": "2024-06-01",
    "monthly_deduction": 500.00
  }
}
```

### Create Allocation

```http
POST /allocations
```

**Request Body:**

```json
{
  "courier_id": 5,
  "bed_id": 2,
  "start_date": "2024-12-15",
  "monthly_deduction": 500.00,
  "notes": "Transferred from Building B"
}
```

### End Allocation

```http
POST /allocations/{id}/end
```

**Request Body:**

```json
{
  "end_date": "2024-12-31",
  "reason": "Courier terminated"
}
```

### Transfer Allocation

```http
POST /allocations/{id}/transfer
```

**Request Body:**

```json
{
  "new_bed_id": 15,
  "transfer_date": "2024-12-20",
  "reason": "Room maintenance"
}
```

---

## Reports

### Building Occupancy Report

```http
GET /reports/occupancy
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `building_id` | integer | Specific building (optional) |
| `city` | string | Filter by city |

**Response:**

```json
{
  "generated_at": "2024-12-10T10:00:00Z",
  "buildings": [
    {
      "id": 1,
      "name": "Barq Housing A",
      "city": "Riyadh",
      "total_capacity": 80,
      "occupied": 65,
      "available": 15,
      "occupancy_rate": 81.25,
      "monthly_revenue": 32500.00
    }
  ],
  "summary": {
    "total_buildings": 5,
    "total_capacity": 400,
    "total_occupied": 320,
    "total_available": 80,
    "average_occupancy_rate": 80.0,
    "total_monthly_revenue": 160000.00
  }
}
```

### Allocation History Report

```http
GET /reports/allocation-history
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Filter by courier |
| `start_date` | string | Start date |
| `end_date` | string | End date |

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| `400` | Bad Request - Invalid parameters |
| `401` | Unauthorized |
| `403` | Forbidden - Insufficient permissions |
| `404` | Not Found |
| `409` | Conflict - Bed already occupied or courier already has allocation |
| `422` | Validation Error |
