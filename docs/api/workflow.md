# Workflow API Documentation

The Workflow API provides endpoints for managing workflow templates, instances, and task automation.

## Base URL

```
/api/v1/workflow
```

## Authentication

All endpoints require a valid JWT token.

---

## Overview

The workflow system allows you to:
- Create reusable workflow templates
- Start workflow instances from templates
- Track workflow progress and step completion
- Handle approvals and escalations

---

## Templates

### List Templates

```http
GET /templates
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `limit` | integer | Items per page |
| `category` | string | Filter by category |
| `status` | string | Filter by status: `active`, `inactive`, `draft` |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "name": "Leave Approval Workflow",
      "category": "hr",
      "description": "Standard leave request approval process",
      "status": "active",
      "version": 2,
      "steps_count": 3,
      "created_at": "2024-01-15T08:00:00Z",
      "updated_at": "2024-06-01T10:00:00Z"
    }
  ],
  "total": 15
}
```

### Get Template

```http
GET /templates/{id}
```

**Response:**

```json
{
  "id": 1,
  "name": "Leave Approval Workflow",
  "category": "hr",
  "description": "Standard leave request approval process",
  "status": "active",
  "version": 2,
  "trigger_type": "manual",
  "steps": [
    {
      "id": 1,
      "order": 1,
      "name": "Manager Approval",
      "type": "approval",
      "assignee_type": "role",
      "assignee_value": "fleet_manager",
      "timeout_hours": 48,
      "auto_escalate": true,
      "escalate_to": "hr_manager"
    },
    {
      "id": 2,
      "order": 2,
      "name": "HR Review",
      "type": "approval",
      "assignee_type": "role",
      "assignee_value": "hr_manager",
      "timeout_hours": 24,
      "conditions": {
        "leave_days": { "gt": 5 }
      }
    },
    {
      "id": 3,
      "order": 3,
      "name": "Update Leave Balance",
      "type": "action",
      "action": "update_leave_balance",
      "automatic": true
    }
  ],
  "metadata": {
    "entity_type": "leave_request",
    "notifications": ["email", "in_app"]
  }
}
```

### Create Template

```http
POST /templates
```

**Request Body:**

```json
{
  "name": "Loan Approval Workflow",
  "category": "hr",
  "description": "Process for approving employee loans",
  "trigger_type": "manual",
  "steps": [
    {
      "order": 1,
      "name": "Manager Review",
      "type": "approval",
      "assignee_type": "role",
      "assignee_value": "fleet_manager",
      "timeout_hours": 48
    },
    {
      "order": 2,
      "name": "Finance Approval",
      "type": "approval",
      "assignee_type": "role",
      "assignee_value": "admin",
      "timeout_hours": 24,
      "conditions": {
        "amount": { "gt": 5000 }
      }
    }
  ]
}
```

**Step Types:**
- `approval` - Requires user approval
- `review` - Requires user review (no rejection option)
- `action` - Automatic system action
- `notification` - Send notification
- `condition` - Branch based on condition

### Update Template

```http
PUT /templates/{id}
```

### Delete Template

```http
DELETE /templates/{id}
```

### Clone Template

```http
POST /templates/{id}/clone
```

**Request Body:**

```json
{
  "name": "Leave Approval Workflow v2"
}
```

---

## Instances

### List Instances

```http
GET /instances
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Filter by template |
| `status` | string | Filter by status: `pending`, `in_progress`, `completed`, `cancelled`, `failed` |
| `created_by` | integer | Filter by creator |
| `entity_type` | string | Filter by entity type |
| `entity_id` | integer | Filter by entity ID |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "template_id": 1,
      "template_name": "Leave Approval Workflow",
      "status": "in_progress",
      "current_step": 2,
      "total_steps": 3,
      "entity_type": "leave_request",
      "entity_id": 45,
      "created_by": 5,
      "created_at": "2024-12-10T08:00:00Z",
      "updated_at": "2024-12-10T10:00:00Z"
    }
  ]
}
```

### Get Instance

```http
GET /instances/{id}
```

**Response:**

```json
{
  "id": 1,
  "template_id": 1,
  "template_name": "Leave Approval Workflow",
  "status": "in_progress",
  "entity_type": "leave_request",
  "entity_id": 45,
  "entity_data": {
    "courier_name": "Ahmed Al-Rashid",
    "leave_type": "annual",
    "start_date": "2024-12-20",
    "end_date": "2024-12-27",
    "days": 7
  },
  "steps": [
    {
      "id": 1,
      "name": "Manager Approval",
      "status": "completed",
      "completed_at": "2024-12-10T10:00:00Z",
      "completed_by": 10,
      "completed_by_name": "Manager Ali",
      "decision": "approved",
      "comments": "Approved as requested"
    },
    {
      "id": 2,
      "name": "HR Review",
      "status": "pending",
      "assignee_id": null,
      "assignee_role": "hr_manager",
      "due_at": "2024-12-11T10:00:00Z"
    },
    {
      "id": 3,
      "name": "Update Leave Balance",
      "status": "waiting"
    }
  ],
  "created_by": 5,
  "created_at": "2024-12-10T08:00:00Z",
  "history": [
    {
      "action": "created",
      "timestamp": "2024-12-10T08:00:00Z",
      "user_id": 5
    },
    {
      "action": "step_completed",
      "step": "Manager Approval",
      "decision": "approved",
      "timestamp": "2024-12-10T10:00:00Z",
      "user_id": 10
    }
  ]
}
```

### Start Instance

```http
POST /instances
```

**Request Body:**

```json
{
  "template_id": 1,
  "entity_type": "leave_request",
  "entity_id": 45,
  "metadata": {
    "priority": "normal"
  }
}
```

### Cancel Instance

```http
POST /instances/{id}/cancel
```

**Request Body:**

```json
{
  "reason": "Leave request withdrawn by employee"
}
```

---

## Steps

### Complete Step

```http
POST /instances/{instance_id}/steps/{step_id}/complete
```

**Request Body:**

```json
{
  "decision": "approved",
  "comments": "Approved after review"
}
```

**Decision Values:**
- `approved` - Approve and continue
- `rejected` - Reject and stop workflow
- `returned` - Return for revision
- `escalated` - Escalate to next level

### Reassign Step

```http
POST /instances/{instance_id}/steps/{step_id}/reassign
```

**Request Body:**

```json
{
  "assignee_id": 15,
  "reason": "Original assignee on leave"
}
```

### Get Pending Steps

```http
GET /steps/pending
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `assignee_id` | integer | Filter by assignee |
| `role` | string | Filter by role |

**Response:**

```json
{
  "items": [
    {
      "instance_id": 1,
      "step_id": 2,
      "step_name": "HR Review",
      "template_name": "Leave Approval Workflow",
      "entity_type": "leave_request",
      "entity_id": 45,
      "entity_summary": "Ahmed - Annual Leave (7 days)",
      "due_at": "2024-12-11T10:00:00Z",
      "overdue": false,
      "created_at": "2024-12-10T08:00:00Z"
    }
  ],
  "total": 5
}
```

---

## Automation

### Trigger Workflows

```http
POST /automation/trigger
```

**Request Body:**

```json
{
  "event_type": "leave_request_created",
  "entity_type": "leave_request",
  "entity_id": 45
}
```

### Get Workflow Rules

```http
GET /automation/rules
```

**Response:**

```json
{
  "rules": [
    {
      "id": 1,
      "event_type": "leave_request_created",
      "template_id": 1,
      "conditions": {
        "leave_days": { "gt": 2 }
      },
      "enabled": true
    }
  ]
}
```

### Create Automation Rule

```http
POST /automation/rules
```

**Request Body:**

```json
{
  "event_type": "loan_request_created",
  "template_id": 2,
  "conditions": {
    "amount": { "gt": 1000 }
  },
  "enabled": true
}
```

---

## Analytics

### Workflow Statistics

```http
GET /analytics/statistics
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `template_id` | integer | Filter by template |
| `start_date` | string | Start date |
| `end_date` | string | End date |

**Response:**

```json
{
  "period": {
    "start": "2024-12-01",
    "end": "2024-12-10"
  },
  "summary": {
    "total_instances": 150,
    "completed": 120,
    "in_progress": 25,
    "cancelled": 5,
    "completion_rate": 80.0,
    "average_duration_hours": 36.5
  },
  "by_template": [
    {
      "template_id": 1,
      "template_name": "Leave Approval Workflow",
      "count": 80,
      "average_duration_hours": 24.2
    }
  ]
}
```

### Bottleneck Analysis

```http
GET /analytics/bottlenecks
```

**Response:**

```json
{
  "bottlenecks": [
    {
      "template_id": 1,
      "step_name": "HR Review",
      "average_wait_hours": 18.5,
      "max_wait_hours": 48,
      "pending_count": 12,
      "escalation_rate": 15.0
    }
  ]
}
```
