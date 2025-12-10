# HR API Documentation

The HR API provides endpoints for managing human resources operations including leaves, loans, salaries, attendance, penalties, and bonuses.

## Base URL

```
/api/v1/hr
```

## Authentication

All endpoints require a valid JWT token. Some endpoints require `hr_manager` or `admin` role.

---

## Leaves

### List Leave Requests

```http
GET /leaves
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page (default: 20) |
| `courier_id` | integer | Filter by courier |
| `status` | string | Filter by status: `pending`, `approved`, `rejected`, `cancelled` |
| `leave_type` | string | Filter by type |
| `start_date` | string | Filter leaves starting from date |
| `end_date` | string | Filter leaves ending before date |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "courier_id": 5,
      "courier_name": "Ahmed Al-Rashid",
      "leave_type": "annual",
      "start_date": "2024-12-20",
      "end_date": "2024-12-27",
      "days": 7,
      "status": "pending",
      "reason": "Family vacation",
      "created_at": "2024-12-10T10:00:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "pages": 3
}
```

### Create Leave Request

```http
POST /leaves
```

**Request Body:**

```json
{
  "courier_id": 5,
  "leave_type": "annual",
  "start_date": "2024-12-20",
  "end_date": "2024-12-27",
  "reason": "Family vacation",
  "emergency_contact": "+966501234567"
}
```

**Leave Types:**
- `annual` - Annual leave
- `sick` - Sick leave
- `emergency` - Emergency leave
- `unpaid` - Unpaid leave
- `maternity` - Maternity leave
- `paternity` - Paternity leave
- `bereavement` - Bereavement leave
- `hajj` - Hajj pilgrimage leave

### Approve Leave

```http
POST /leaves/{id}/approve
```

**Request Body:**

```json
{
  "notes": "Approved as requested"
}
```

### Reject Leave

```http
POST /leaves/{id}/reject
```

**Request Body:**

```json
{
  "reason": "Insufficient leave balance"
}
```

### Get Leave Balance

```http
GET /couriers/{courier_id}/leave-balance
```

**Response:**

```json
{
  "courier_id": 5,
  "annual_leave": {
    "entitled": 30,
    "used": 10,
    "pending": 7,
    "remaining": 13
  },
  "sick_leave": {
    "entitled": 15,
    "used": 2,
    "remaining": 13
  },
  "emergency_leave": {
    "entitled": 5,
    "used": 0,
    "remaining": 5
  }
}
```

---

## Loans

### List Loans

```http
GET /loans
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Filter by courier |
| `status` | string | Filter by status |
| `loan_type` | string | Filter by type |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "courier_id": 5,
      "courier_name": "Ahmed Al-Rashid",
      "loan_type": "salary_advance",
      "amount": 5000.00,
      "installments": 5,
      "installment_amount": 1000.00,
      "paid_installments": 2,
      "remaining_amount": 3000.00,
      "status": "active",
      "start_date": "2024-11-01",
      "created_at": "2024-10-25T08:00:00Z"
    }
  ],
  "total": 12
}
```

### Create Loan Request

```http
POST /loans
```

**Request Body:**

```json
{
  "courier_id": 5,
  "loan_type": "salary_advance",
  "amount": 5000.00,
  "installments": 5,
  "reason": "Personal emergency",
  "start_date": "2024-12-01"
}
```

**Loan Types:**
- `salary_advance` - Salary advance
- `personal` - Personal loan
- `emergency` - Emergency loan
- `housing` - Housing loan
- `vehicle` - Vehicle loan

### Approve Loan

```http
POST /loans/{id}/approve
```

### Reject Loan

```http
POST /loans/{id}/reject
```

**Request Body:**

```json
{
  "reason": "Exceeds maximum loan limit"
}
```

### Record Loan Payment

```http
POST /loans/{id}/payments
```

**Request Body:**

```json
{
  "amount": 1000.00,
  "payment_date": "2024-12-01",
  "payment_method": "salary_deduction",
  "notes": "December 2024 installment"
}
```

---

## Salaries

### List Salary Records

```http
GET /salaries
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Filter by courier |
| `month` | integer | Filter by month (1-12) |
| `year` | integer | Filter by year |
| `status` | string | Filter by status: `draft`, `calculated`, `approved`, `paid` |

### Calculate Salary

```http
POST /salaries/calculate
```

**Request Body:**

```json
{
  "courier_id": 5,
  "month": 12,
  "year": 2024
}
```

**Response:**

```json
{
  "courier_id": 5,
  "month": 12,
  "year": 2024,
  "breakdown": {
    "basic_salary": 4000.00,
    "housing_allowance": 1000.00,
    "transportation_allowance": 500.00,
    "food_allowance": 300.00,
    "overtime": {
      "hours": 20,
      "rate": 1.5,
      "amount": 750.00
    },
    "bonus": 500.00,
    "commission": 1200.00,
    "gross_salary": 8250.00,
    "deductions": {
      "gosi": 375.00,
      "loan_installment": 1000.00,
      "penalties": 150.00,
      "other": 0.00,
      "total": 1525.00
    },
    "net_salary": 6725.00
  }
}
```

### Approve Salary

```http
POST /salaries/{id}/approve
```

### Process Payroll

```http
POST /salaries/process-payroll
```

**Request Body:**

```json
{
  "month": 12,
  "year": 2024,
  "payment_date": "2024-12-28"
}
```

### Export GOSI Report

```http
GET /salaries/gosi-export
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `month` | integer | Report month |
| `year` | integer | Report year |

**Response:** CSV file download

---

## Attendance

### List Attendance Records

```http
GET /attendance
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Filter by courier |
| `date` | string | Filter by date |
| `start_date` | string | Start of date range |
| `end_date` | string | End of date range |
| `status` | string | Filter by status |

### Record Check-In

```http
POST /attendance/check-in
```

**Request Body:**

```json
{
  "courier_id": 5,
  "location": {
    "latitude": 24.7136,
    "longitude": 46.6753
  }
}
```

### Record Check-Out

```http
POST /attendance/check-out
```

**Request Body:**

```json
{
  "courier_id": 5,
  "location": {
    "latitude": 24.7140,
    "longitude": 46.6758
  }
}
```

### Get Attendance Summary

```http
GET /attendance/summary
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `courier_id` | integer | Courier ID |
| `month` | integer | Month |
| `year` | integer | Year |

**Response:**

```json
{
  "courier_id": 5,
  "month": 12,
  "year": 2024,
  "working_days": 22,
  "present_days": 20,
  "absent_days": 1,
  "late_days": 2,
  "half_days": 0,
  "leave_days": 1,
  "overtime_hours": 15.5,
  "attendance_percentage": 95.45
}
```

---

## Penalties

### List Penalties

```http
GET /penalties
```

### Create Penalty

```http
POST /penalties
```

**Request Body:**

```json
{
  "courier_id": 5,
  "penalty_type": "late_arrival",
  "amount": 50.00,
  "date": "2024-12-10",
  "reason": "Late arrival by 45 minutes",
  "deduct_from_salary": true
}
```

**Penalty Types:**
- `late_arrival` - Late arrival
- `absence` - Unauthorized absence
- `misconduct` - Misconduct
- `damage` - Vehicle/equipment damage
- `violation` - Traffic/policy violation
- `customer_complaint` - Customer complaint
- `policy_breach` - Policy breach

---

## Bonuses

### List Bonuses

```http
GET /bonuses
```

### Create Bonus

```http
POST /bonuses
```

**Request Body:**

```json
{
  "courier_id": 5,
  "bonus_type": "performance",
  "amount": 500.00,
  "date": "2024-12-01",
  "reason": "Exceeded monthly delivery targets",
  "add_to_salary": true
}
```

**Bonus Types:**
- `performance` - Performance bonus
- `attendance` - Perfect attendance bonus
- `referral` - Referral bonus
- `holiday` - Holiday bonus
- `special` - Special bonus
- `retention` - Retention bonus

---

## End of Service (EOS)

### Calculate EOS

```http
POST /eos/calculate
```

**Request Body:**

```json
{
  "courier_id": 5,
  "termination_date": "2024-12-31",
  "termination_reason": "resignation",
  "final_basic_salary": 4000.00
}
```

**Response:**

```json
{
  "courier_id": 5,
  "service_years": 3.5,
  "termination_reason": "resignation",
  "calculation": {
    "first_5_years": 7000.00,
    "after_5_years": 0.00,
    "total_eos": 7000.00,
    "unpaid_leave_deduction": 0.00,
    "pending_loan_deduction": 2000.00,
    "other_deductions": 0.00,
    "net_eos": 5000.00
  },
  "accrued_benefits": {
    "unused_annual_leave_days": 5,
    "unused_leave_amount": 666.67
  },
  "final_settlement": 5666.67
}
```

**Termination Reasons:**
- `resignation` - Voluntary resignation
- `termination` - Employer termination
- `contract_end` - Contract end
- `retirement` - Retirement
- `death` - Death
