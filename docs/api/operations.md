# Operations API Documentation

The Operations API provides endpoints for managing deliveries, dispatch, routes, SLA monitoring, zones, incidents, and COD operations.

## Base URL

```
/api/v1/operations
```

## Authentication

All endpoints require a valid JWT token.

---

## Deliveries

### List Deliveries

```http
GET /deliveries
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `limit` | integer | Items per page |
| `status` | string | Filter by status |
| `priority` | string | Filter by priority |
| `courier_id` | integer | Filter by assigned courier |
| `date_from` | string | Filter from date |
| `date_to` | string | Filter to date |
| `city` | string | Filter by city |
| `search` | string | Search tracking number or reference |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "tracking_number": "BRQ-2024121001",
      "status": "in_transit",
      "priority": "normal",
      "sender": {
        "name": "Tech Store",
        "phone": "+966501234567"
      },
      "recipient": {
        "name": "Mohammed Ali",
        "phone": "+966509876543"
      },
      "pickup_address": {
        "city": "Riyadh",
        "district": "Al Olaya"
      },
      "delivery_address": {
        "city": "Riyadh",
        "district": "Al Malaz"
      },
      "courier_id": 5,
      "courier_name": "Ahmed Al-Rashid",
      "created_at": "2024-12-10T08:00:00Z",
      "estimated_delivery": "2024-12-10T14:00:00Z"
    }
  ],
  "total": 500,
  "page": 1,
  "pages": 25
}
```

### Create Delivery

```http
POST /deliveries
```

**Request Body:**

```json
{
  "sender": {
    "name": "Tech Store",
    "phone": "+966501234567",
    "company": "Tech Store LLC"
  },
  "pickup_address": {
    "street": "King Fahd Road",
    "city": "Riyadh",
    "district": "Al Olaya",
    "building": "Tower A",
    "latitude": 24.7136,
    "longitude": 46.6753
  },
  "recipient": {
    "name": "Mohammed Ali",
    "phone": "+966509876543"
  },
  "delivery_address": {
    "street": "Prince Sultan Street",
    "city": "Riyadh",
    "district": "Al Malaz",
    "apartment": "Apt 5B"
  },
  "package": {
    "weight": 2.5,
    "description": "Electronics",
    "fragile": true,
    "cod_amount": 500.00
  },
  "pickup_date": "2024-12-10",
  "priority": "normal",
  "service_type": "standard"
}
```

### Get Delivery

```http
GET /deliveries/{id}
```

### Update Delivery Status

```http
POST /deliveries/{id}/status
```

**Request Body:**

```json
{
  "status": "delivered",
  "notes": "Delivered to recipient",
  "location": {
    "latitude": 24.7140,
    "longitude": 46.6758
  },
  "signature_url": "https://storage.barq.com/signatures/sig123.png",
  "photo_url": "https://storage.barq.com/photos/del123.jpg"
}
```

**Delivery Statuses:**
- `pending` - Awaiting pickup
- `assigned` - Assigned to courier
- `picked_up` - Picked up from sender
- `in_transit` - In transit to recipient
- `delivered` - Successfully delivered
- `failed` - Delivery failed
- `cancelled` - Cancelled
- `returned` - Returned to sender

### Track Delivery

```http
GET /deliveries/{tracking_number}/track
```

**Response:**

```json
{
  "tracking_number": "BRQ-2024121001",
  "status": "in_transit",
  "estimated_delivery": "2024-12-10T14:00:00Z",
  "history": [
    {
      "status": "pending",
      "timestamp": "2024-12-10T08:00:00Z",
      "location": null
    },
    {
      "status": "assigned",
      "timestamp": "2024-12-10T08:30:00Z",
      "notes": "Assigned to courier"
    },
    {
      "status": "picked_up",
      "timestamp": "2024-12-10T09:15:00Z",
      "location": {
        "latitude": 24.7136,
        "longitude": 46.6753
      }
    },
    {
      "status": "in_transit",
      "timestamp": "2024-12-10T09:20:00Z"
    }
  ],
  "courier": {
    "name": "Ahmed",
    "phone": "+966501234567",
    "current_location": {
      "latitude": 24.7138,
      "longitude": 46.6755,
      "last_updated": "2024-12-10T10:30:00Z"
    }
  }
}
```

---

## Dispatch

### Auto-Dispatch

```http
POST /dispatch/auto
```

**Request Body:**

```json
{
  "delivery_ids": [1, 2, 3],
  "optimization_criteria": "distance",
  "max_radius_km": 7,
  "consider_courier_workload": true
}
```

**Response:**

```json
{
  "assignments": [
    {
      "delivery_id": 1,
      "courier_id": 5,
      "courier_name": "Ahmed Al-Rashid",
      "estimated_pickup_time": "2024-12-10T10:30:00Z",
      "distance_km": 2.5
    },
    {
      "delivery_id": 2,
      "courier_id": 5,
      "courier_name": "Ahmed Al-Rashid",
      "estimated_pickup_time": "2024-12-10T11:00:00Z",
      "distance_km": 3.2
    }
  ],
  "unassigned": [
    {
      "delivery_id": 3,
      "reason": "No available courier within radius"
    }
  ]
}
```

### Manual Dispatch

```http
POST /dispatch/manual
```

**Request Body:**

```json
{
  "delivery_id": 1,
  "courier_id": 5,
  "notes": "Priority customer"
}
```

### Bulk Assignment

```http
POST /dispatch/bulk-assign
```

**Request Body:**

```json
{
  "delivery_ids": [1, 2, 3, 4, 5],
  "courier_id": 5,
  "notes": "Morning batch"
}
```

### Get Available Couriers

```http
GET /dispatch/available-couriers
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | number | Pickup location latitude |
| `longitude` | number | Pickup location longitude |
| `radius_km` | number | Search radius (default: 7) |

**Response:**

```json
{
  "couriers": [
    {
      "id": 5,
      "name": "Ahmed Al-Rashid",
      "distance_km": 1.5,
      "current_deliveries": 3,
      "eta_minutes": 8,
      "rating": 4.8
    }
  ]
}
```

---

## Routes

### Optimize Route

```http
POST /routes/optimize
```

**Request Body:**

```json
{
  "courier_id": 5,
  "delivery_ids": [1, 2, 3, 4, 5],
  "start_location": {
    "latitude": 24.7136,
    "longitude": 46.6753
  },
  "optimization_type": "time"
}
```

**Response:**

```json
{
  "optimized_route": {
    "total_distance_km": 25.5,
    "estimated_duration_minutes": 120,
    "stops": [
      {
        "order": 1,
        "delivery_id": 3,
        "type": "pickup",
        "address": "King Fahd Road, Riyadh",
        "eta": "2024-12-10T10:30:00Z"
      },
      {
        "order": 2,
        "delivery_id": 1,
        "type": "pickup",
        "address": "Prince Sultan Street, Riyadh",
        "eta": "2024-12-10T10:45:00Z"
      }
    ]
  }
}
```

### Get Courier Route

```http
GET /routes/courier/{courier_id}
```

---

## SLA Monitoring

### Get SLA Status

```http
GET /sla/status
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `date` | string | Date to check |
| `city` | string | Filter by city |

**Response:**

```json
{
  "date": "2024-12-10",
  "summary": {
    "total_deliveries": 500,
    "on_time": 475,
    "at_risk": 15,
    "breached": 10,
    "sla_compliance_percentage": 95.0
  },
  "at_risk_deliveries": [
    {
      "delivery_id": 123,
      "tracking_number": "BRQ-2024121023",
      "sla_deadline": "2024-12-10T14:00:00Z",
      "minutes_remaining": 30,
      "courier_id": 5
    }
  ]
}
```

### Get SLA Breaches

```http
GET /sla/breaches
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date |
| `end_date` | string | End date |
| `courier_id` | integer | Filter by courier |

### Escalate SLA Breach

```http
POST /sla/escalate
```

**Request Body:**

```json
{
  "delivery_id": 123,
  "escalation_level": 2,
  "reason": "Customer complaint received"
}
```

---

## Zones

### List Zones

```http
GET /zones
```

### Create Zone

```http
POST /zones
```

**Request Body:**

```json
{
  "name": "Riyadh Central",
  "city": "Riyadh",
  "polygon": [
    {"lat": 24.7136, "lng": 46.6753},
    {"lat": 24.7200, "lng": 46.6800},
    {"lat": 24.7100, "lng": 46.6850}
  ],
  "delivery_fee": 15.00,
  "priority": 1
}
```

### Update Zone

```http
PUT /zones/{id}
```

### Delete Zone

```http
DELETE /zones/{id}
```

---

## Incidents

### List Incidents

```http
GET /incidents
```

### Create Incident

```http
POST /incidents
```

**Request Body:**

```json
{
  "delivery_id": 123,
  "courier_id": 5,
  "incident_type": "vehicle_breakdown",
  "description": "Motorcycle engine failure",
  "location": {
    "latitude": 24.7136,
    "longitude": 46.6753
  },
  "severity": "high"
}
```

**Incident Types:**
- `vehicle_breakdown`
- `accident`
- `theft`
- `customer_dispute`
- `package_damage`
- `weather_delay`
- `other`

### Update Incident

```http
PUT /incidents/{id}
```

### Resolve Incident

```http
POST /incidents/{id}/resolve
```

**Request Body:**

```json
{
  "resolution": "Vehicle repaired, deliveries reassigned",
  "follow_up_required": false
}
```

---

## COD (Cash on Delivery)

### List COD Collections

```http
GET /cod/collections
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Filter by courier |
| `date` | string | Filter by date |
| `status` | string | Filter by status |

### Record COD Collection

```http
POST /cod/collect
```

**Request Body:**

```json
{
  "delivery_id": 123,
  "amount": 500.00,
  "payment_method": "cash",
  "notes": "Exact amount received"
}
```

### Process COD Settlement

```http
POST /cod/settle
```

**Request Body:**

```json
{
  "courier_id": 5,
  "collection_ids": [1, 2, 3, 4, 5],
  "settlement_date": "2024-12-10"
}
```

### Get COD Summary

```http
GET /cod/summary
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Courier ID |
| `date` | string | Date |

**Response:**

```json
{
  "courier_id": 5,
  "date": "2024-12-10",
  "summary": {
    "total_collections": 15,
    "total_amount": 7500.00,
    "settled_amount": 5000.00,
    "pending_amount": 2500.00
  }
}
```

---

## Handovers

### Create Handover

```http
POST /handovers
```

**Request Body:**

```json
{
  "from_courier_id": 5,
  "to_courier_id": 8,
  "delivery_ids": [123, 124, 125],
  "reason": "Shift change",
  "location": {
    "latitude": 24.7136,
    "longitude": 46.6753
  }
}
```

### Confirm Handover

```http
POST /handovers/{id}/confirm
```

**Request Body:**

```json
{
  "confirmed_by": "receiving_courier",
  "notes": "All packages received in good condition"
}
```
