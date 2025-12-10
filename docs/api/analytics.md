# Analytics API Documentation

The Analytics API provides endpoints for dashboards, KPIs, reports, and business intelligence.

## Base URL

```
/api/v1/analytics
```

## Authentication

All endpoints require a valid JWT token.

---

## Dashboard

### Get Dashboard Overview

```http
GET /dashboard/overview
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `period` | string | Time period: `today`, `week`, `month`, `quarter`, `year` |
| `city` | string | Filter by city |

**Response:**

```json
{
  "period": "today",
  "date": "2024-12-10",
  "deliveries": {
    "total": 1250,
    "completed": 1100,
    "in_progress": 100,
    "pending": 30,
    "failed": 20,
    "completion_rate": 88.0
  },
  "couriers": {
    "total": 150,
    "active": 135,
    "on_delivery": 120,
    "available": 15,
    "on_leave": 10
  },
  "vehicles": {
    "total": 75,
    "in_use": 60,
    "available": 10,
    "maintenance": 5
  },
  "revenue": {
    "total": 125000.00,
    "cod_collected": 85000.00,
    "delivery_fees": 40000.00
  },
  "sla": {
    "on_time_percentage": 94.5,
    "average_delivery_time_minutes": 28.3,
    "breaches": 12
  }
}
```

### Get Real-time Metrics

```http
GET /dashboard/realtime
```

**Response:**

```json
{
  "timestamp": "2024-12-10T10:30:00Z",
  "active_deliveries": 125,
  "active_couriers": 120,
  "deliveries_per_hour": 45,
  "average_eta_minutes": 18,
  "hotspots": [
    {
      "zone": "Riyadh Central",
      "active_deliveries": 35,
      "couriers_available": 8
    }
  ],
  "alerts": [
    {
      "type": "sla_risk",
      "count": 5,
      "message": "5 deliveries at risk of SLA breach"
    }
  ]
}
```

---

## KPIs

### Get KPIs

```http
GET /kpis
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Category: `delivery`, `fleet`, `hr`, `finance` |
| `period` | string | Time period |
| `compare` | boolean | Include comparison with previous period |

**Response:**

```json
{
  "period": "2024-12",
  "kpis": [
    {
      "name": "Delivery Success Rate",
      "category": "delivery",
      "value": 96.5,
      "unit": "percentage",
      "target": 95.0,
      "status": "on_target",
      "previous_value": 95.2,
      "change_percentage": 1.37
    },
    {
      "name": "Average Delivery Time",
      "category": "delivery",
      "value": 28.3,
      "unit": "minutes",
      "target": 30.0,
      "status": "on_target",
      "previous_value": 29.1,
      "change_percentage": -2.75
    },
    {
      "name": "Fleet Utilization",
      "category": "fleet",
      "value": 82.5,
      "unit": "percentage",
      "target": 80.0,
      "status": "on_target"
    },
    {
      "name": "Courier Productivity",
      "category": "fleet",
      "value": 15.2,
      "unit": "deliveries_per_day",
      "target": 15.0,
      "status": "on_target"
    }
  ]
}
```

### Get KPI Trends

```http
GET /kpis/{kpi_name}/trends
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date |
| `end_date` | string | End date |
| `granularity` | string | `daily`, `weekly`, `monthly` |

**Response:**

```json
{
  "kpi_name": "Delivery Success Rate",
  "granularity": "daily",
  "data": [
    {"date": "2024-12-01", "value": 95.8},
    {"date": "2024-12-02", "value": 96.2},
    {"date": "2024-12-03", "value": 94.5},
    {"date": "2024-12-04", "value": 97.1}
  ],
  "statistics": {
    "min": 94.5,
    "max": 97.1,
    "average": 95.9,
    "trend": "increasing"
  }
}
```

---

## Reports

### List Available Reports

```http
GET /reports
```

**Response:**

```json
{
  "reports": [
    {
      "id": "daily_operations",
      "name": "Daily Operations Report",
      "category": "operations",
      "description": "Summary of daily delivery operations",
      "formats": ["pdf", "xlsx", "csv"]
    },
    {
      "id": "courier_performance",
      "name": "Courier Performance Report",
      "category": "fleet",
      "description": "Individual courier performance metrics"
    },
    {
      "id": "financial_summary",
      "name": "Financial Summary Report",
      "category": "finance",
      "description": "Revenue, costs, and profitability analysis"
    }
  ]
}
```

### Generate Report

```http
POST /reports/generate
```

**Request Body:**

```json
{
  "report_id": "daily_operations",
  "parameters": {
    "date": "2024-12-10",
    "city": "Riyadh"
  },
  "format": "pdf"
}
```

**Response:**

```json
{
  "job_id": "rpt_abc123",
  "status": "processing",
  "estimated_completion": "2024-12-10T10:35:00Z"
}
```

### Get Report Status

```http
GET /reports/jobs/{job_id}
```

**Response:**

```json
{
  "job_id": "rpt_abc123",
  "status": "completed",
  "download_url": "https://storage.barq.com/reports/daily_ops_20241210.pdf",
  "expires_at": "2024-12-11T10:30:00Z"
}
```

### Schedule Report

```http
POST /reports/schedule
```

**Request Body:**

```json
{
  "report_id": "daily_operations",
  "schedule": "0 8 * * *",
  "parameters": {
    "city": "Riyadh"
  },
  "format": "pdf",
  "recipients": ["manager@barq.com", "ops@barq.com"]
}
```

---

## Fleet Analytics

### Get Fleet Performance

```http
GET /fleet/performance
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date |
| `end_date` | string | End date |
| `group_by` | string | Group by: `courier`, `city`, `vehicle_type` |

**Response:**

```json
{
  "period": {
    "start": "2024-12-01",
    "end": "2024-12-10"
  },
  "summary": {
    "total_deliveries": 15000,
    "total_distance_km": 45000,
    "average_deliveries_per_courier": 15.5,
    "average_delivery_time_minutes": 28.3
  },
  "by_courier": [
    {
      "courier_id": 5,
      "courier_name": "Ahmed Al-Rashid",
      "deliveries": 180,
      "success_rate": 98.5,
      "average_time_minutes": 25.2,
      "rating": 4.9
    }
  ],
  "by_city": [
    {
      "city": "Riyadh",
      "deliveries": 8500,
      "couriers": 85,
      "success_rate": 96.2
    }
  ]
}
```

### Get Vehicle Analytics

```http
GET /fleet/vehicles
```

**Response:**

```json
{
  "summary": {
    "total_vehicles": 75,
    "utilization_rate": 82.5,
    "total_distance_km": 45000,
    "fuel_cost": 15000.00
  },
  "by_type": [
    {
      "type": "motorcycle",
      "count": 50,
      "utilization_rate": 85.0,
      "average_daily_distance_km": 80
    },
    {
      "type": "van",
      "count": 20,
      "utilization_rate": 78.0,
      "average_daily_distance_km": 120
    }
  ],
  "maintenance": {
    "scheduled_this_month": 12,
    "overdue": 3,
    "cost_mtd": 8500.00
  }
}
```

---

## HR Analytics

### Get HR Overview

```http
GET /hr/overview
```

**Response:**

```json
{
  "headcount": {
    "total": 150,
    "active": 140,
    "on_leave": 8,
    "terminated_mtd": 2,
    "hired_mtd": 5
  },
  "attendance": {
    "average_attendance_rate": 95.2,
    "late_arrivals_mtd": 45,
    "absences_mtd": 12
  },
  "leaves": {
    "pending_requests": 8,
    "approved_mtd": 25,
    "leave_utilization_rate": 68.5
  },
  "loans": {
    "active_loans": 15,
    "total_outstanding": 75000.00,
    "delinquent": 2
  }
}
```

### Get Payroll Summary

```http
GET /hr/payroll-summary
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `month` | integer | Month |
| `year` | integer | Year |

**Response:**

```json
{
  "month": 12,
  "year": 2024,
  "summary": {
    "total_employees": 150,
    "total_gross_salary": 850000.00,
    "total_deductions": 125000.00,
    "total_net_salary": 725000.00,
    "gosi_contribution": 45000.00
  },
  "breakdown": {
    "basic_salary": 600000.00,
    "housing_allowance": 150000.00,
    "transportation": 75000.00,
    "overtime": 25000.00,
    "bonuses": 35000.00,
    "deductions": {
      "gosi": 45000.00,
      "loans": 50000.00,
      "penalties": 15000.00,
      "other": 15000.00
    }
  }
}
```

---

## Financial Analytics

### Get Revenue Analytics

```http
GET /finance/revenue
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date |
| `end_date` | string | End date |
| `group_by` | string | `daily`, `weekly`, `monthly` |

**Response:**

```json
{
  "period": {
    "start": "2024-12-01",
    "end": "2024-12-10"
  },
  "summary": {
    "total_revenue": 450000.00,
    "delivery_fees": 180000.00,
    "cod_fees": 15000.00,
    "subscription_revenue": 255000.00
  },
  "by_client": [
    {
      "client_id": 1,
      "client_name": "E-Commerce Store A",
      "revenue": 85000.00,
      "deliveries": 2500
    }
  ],
  "trends": [
    {"date": "2024-12-01", "revenue": 42000.00},
    {"date": "2024-12-02", "revenue": 45000.00}
  ]
}
```

### Get Cost Analysis

```http
GET /finance/costs
```

**Response:**

```json
{
  "period": "2024-12",
  "total_costs": 320000.00,
  "breakdown": {
    "salaries": 725000.00,
    "fuel": 15000.00,
    "maintenance": 8500.00,
    "accommodation": 25000.00,
    "insurance": 12000.00,
    "other": 5000.00
  },
  "cost_per_delivery": 8.50,
  "margin_percentage": 28.9
}
```

---

## Export

### Export Analytics Data

```http
POST /export
```

**Request Body:**

```json
{
  "data_type": "deliveries",
  "filters": {
    "start_date": "2024-12-01",
    "end_date": "2024-12-10",
    "city": "Riyadh"
  },
  "columns": ["tracking_number", "status", "courier_name", "delivery_time"],
  "format": "xlsx"
}
```

**Response:**

```json
{
  "download_url": "https://storage.barq.com/exports/deliveries_20241210.xlsx",
  "expires_at": "2024-12-11T10:30:00Z",
  "row_count": 8500
}
```
