# BARQ Workflow Engine - Complete API Documentation

## Overview
Comprehensive workflow management system with state machines, multi-level approvals, SLA tracking, automations, and tamper-evident audit trails.

**Base URL**: `/api/v1/workflow`

---

## Table of Contents
1. [Workflow Templates](#workflow-templates)
2. [Workflow Instances](#workflow-instances)
3. [Approval Chains](#approval-chains)
4. [SLA Tracking](#sla-tracking)
5. [Automations](#automations)
6. [Triggers](#triggers)
7. [Comments](#comments)
8. [Attachments](#attachments)
9. [History & Audit Trail](#history--audit-trail)
10. [Notifications](#notifications)
11. [Analytics](#analytics)

---

## 1. Workflow Templates

### List Templates
```
GET /api/v1/workflow/templates
Query Parameters:
  - skip: int (default: 0)
  - limit: int (default: 100)
  - category: string (optional)
  - is_active: boolean (optional)
```

### Create Template
```
POST /api/v1/workflow/templates
Body: WorkflowTemplateCreate
  - name: string (required, 3-100 chars)
  - description: string (optional)
  - steps: array (required, JSON workflow steps)
  - category: string (optional: courier, vehicle, delivery, hr, finance, general)
  - estimated_duration: int (optional, minutes)
  - is_active: boolean (default: true)
```

### Get Template
```
GET /api/v1/workflow/templates/{template_id}
```

### Update Template
```
PUT /api/v1/workflow/templates/{template_id}
Body: WorkflowTemplateUpdate (all fields optional)
```

### Delete Template
```
DELETE /api/v1/workflow/templates/{template_id}
```

### Clone Template
```
POST /api/v1/workflow/templates/{template_id}/clone
Query Parameters:
  - name: string (required, name for cloned template)
```

### Activate/Deactivate Template
```
PATCH /api/v1/workflow/templates/{template_id}/activate
PATCH /api/v1/workflow/templates/{template_id}/deactivate
```

---

## 2. Workflow Instances

### List Instances
```
GET /api/v1/workflow/instances
Query Parameters:
  - skip: int (default: 0)
  - limit: int (default: 100)
  - status: WorkflowStatus (optional)
  - template_id: int (optional)
```

**WorkflowStatus enum**: draft, in_progress, pending_approval, approved, rejected, completed, cancelled

### Create Instance
```
POST /api/v1/workflow/instances
Body: WorkflowInstanceCreate
  - template_id: int (required)
  - initiated_by: int (required, user ID)
  - data: object (optional, workflow data)
```

### Start Workflow
```
POST /api/v1/workflow/instances/start
Body:
  - template_id: int (required)
  - initiated_by: int (required)
  - initial_data: object (optional)
```

### Get Instance
```
GET /api/v1/workflow/instances/{instance_id}
```

### Get Instance Status
```
GET /api/v1/workflow/instances/{instance_id}/status
Returns: Detailed status including progress, current step, approvals
```

### Update Instance
```
PUT /api/v1/workflow/instances/{instance_id}
Body: WorkflowInstanceUpdate
```

### Advance Workflow Step
```
POST /api/v1/workflow/instances/{instance_id}/advance
Body:
  - step_data: object (optional)
```

### Transition Workflow Status
```
POST /api/v1/workflow/instances/{instance_id}/transition
Body:
  - new_status: WorkflowStatus (required)
  - notes: string (optional)
```

### Cancel Workflow
```
POST /api/v1/workflow/instances/{instance_id}/cancel
Body:
  - reason: string (optional)
```

### Delete Instance
```
DELETE /api/v1/workflow/instances/{instance_id}
```

---

## 3. Approval Chains

### List Approval Chains
```
GET /api/v1/workflow/approvals/chains
Query Parameters:
  - skip: int
  - limit: int
```

### Create Approval Chain
```
POST /api/v1/workflow/approvals/chains
Body: ApprovalChainCreate
  - name: string (required)
  - description: string (optional)
  - workflow_template_id: int (optional)
  - levels: int (default: 1)
  - is_sequential: boolean (default: true)
  - allow_delegation: boolean (default: false)
  - auto_escalate: boolean (default: true)
  - escalation_hours: int (default: 24)
```

### Get Approval Chain
```
GET /api/v1/workflow/approvals/chains/{chain_id}
```

### Update Approval Chain
```
PUT /api/v1/workflow/approvals/chains/{chain_id}
Body: ApprovalChainUpdate
```

### Delete Approval Chain
```
DELETE /api/v1/workflow/approvals/chains/{chain_id}
```

### List Approval Requests
```
GET /api/v1/workflow/approvals/requests
Query Parameters:
  - skip: int
  - limit: int
```

### Get Approval Request
```
GET /api/v1/workflow/approvals/requests/{request_id}
```

### Process Approval Action
```
POST /api/v1/workflow/approvals/requests/{request_id}/action
Body:
  - action: string (approve, reject, delegate)
  - approver_id: int (required)
  - comments: string (optional)
  - delegate_to_id: int (required if action=delegate)
```

**ApprovalStatus enum**: pending, approved, rejected, delegated, expired

---

## 4. SLA Tracking

### List SLAs
```
GET /api/v1/workflow/sla
Query Parameters:
  - skip: int
  - limit: int
```

### Create SLA
```
POST /api/v1/workflow/sla
Body: WorkflowSLACreate
  - name: string (required)
  - description: string (optional)
  - workflow_template_id: int (optional)
  - priority: SLAPriority (low, medium, high, critical)
  - response_time: int (minutes, optional)
  - resolution_time: int (minutes, required)
  - warning_threshold: int (percentage, optional)
  - use_business_hours: boolean (default: false)
  - escalate_on_warning: boolean (default: false)
  - escalate_on_breach: boolean (default: true)
```

### Get SLA
```
GET /api/v1/workflow/sla/{sla_id}
```

### Update SLA
```
PUT /api/v1/workflow/sla/{sla_id}
Body: WorkflowSLAUpdate
```

### Delete SLA
```
DELETE /api/v1/workflow/sla/{sla_id}
```

### Monitor SLA Instances
```
GET /api/v1/workflow/sla/instances
Returns: Active SLA instances with status
```

### Get SLA Reports
```
GET /api/v1/workflow/sla/reports
Query Parameters:
  - start_date: datetime
  - end_date: datetime
Returns: SLA compliance statistics
```

**SLAStatus enum**: active, warning, breached, paused, completed

---

## 5. Automations

### List Automations
```
GET /api/v1/workflow/automations
Query Parameters:
  - skip: int
  - limit: int
```

### Create Automation
```
POST /api/v1/workflow/automations
Body: WorkflowAutomationCreate
  - name: string (required)
  - description: string (optional)
  - workflow_template_id: int (optional)
  - trigger_type: AutomationTriggerType (manual, scheduled, event, condition, webhook)
  - trigger_config: object
  - conditions: array (optional)
  - condition_logic: string (AND/OR)
  - action_type: AutomationActionType
  - action_config: object
  - is_active: boolean (default: true)
```

**AutomationActionType enum**: create_workflow, update_workflow, send_notification, send_email, send_sms, update_record, webhook_call, custom_script

### Get Automation
```
GET /api/v1/workflow/automations/{automation_id}
```

### Update Automation
```
PUT /api/v1/workflow/automations/{automation_id}
Body: WorkflowAutomationUpdate
```

### Delete Automation
```
DELETE /api/v1/workflow/automations/{automation_id}
```

### Execute Automation
```
POST /api/v1/workflow/automations/{automation_id}/execute
Body: AutomationExecuteRequest
```

### Test Automation
```
POST /api/v1/workflow/automations/{automation_id}/test
Body: AutomationTestRequest
Returns: Test results without actually executing
```

---

## 6. Triggers

### List Triggers
```
GET /api/v1/workflow/triggers
Query Parameters:
  - skip: int
  - limit: int
```

### Create Trigger
```
POST /api/v1/workflow/triggers
Body: WorkflowTriggerCreate
  - name: string (required)
  - description: string (optional)
  - workflow_template_id: int (required)
  - trigger_type: TriggerType (manual, automatic, scheduled, event_based, api, webhook)
  - event_type: TriggerEventType (optional)
  - entity_type: string (optional)
  - field_conditions: object (optional)
  - conditions: array (optional)
  - is_active: boolean (default: true)
```

**TriggerEventType enum**: record_created, record_updated, record_deleted, workflow_started, workflow_completed, workflow_failed, approval_requested, approval_approved, approval_rejected, sla_warning, sla_breached, custom

### Get Trigger
```
GET /api/v1/workflow/triggers/{trigger_id}
```

### Update Trigger
```
PUT /api/v1/workflow/triggers/{trigger_id}
Body: WorkflowTriggerUpdate
```

### Delete Trigger
```
DELETE /api/v1/workflow/triggers/{trigger_id}
```

### Test Trigger
```
POST /api/v1/workflow/triggers/{trigger_id}/test
Body: TriggerTestRequest
Returns: Test results
```

---

## 7. Comments

### List Comments
```
GET /api/v1/workflow/comments
Query Parameters:
  - workflow_instance_id: int (optional)
  - skip: int
  - limit: int
```

### Create Comment
```
POST /api/v1/workflow/comments
Body: WorkflowCommentCreate
  - workflow_instance_id: int (required)
  - user_id: int (required)
  - comment: string (required, 1-5000 chars)
  - is_internal: boolean (default: false)
  - parent_comment_id: int (optional, for threaded comments)
```

### Get Comment
```
GET /api/v1/workflow/comments/{comment_id}
```

### Update Comment
```
PUT /api/v1/workflow/comments/{comment_id}
Body: WorkflowCommentUpdate
  - comment: string (optional)
  - is_internal: boolean (optional)
```

### Delete Comment
```
DELETE /api/v1/workflow/comments/{comment_id}
```

### Get Comment Thread
```
GET /api/v1/workflow/comments/instance/{instance_id}/thread
Returns: Threaded comments for a workflow instance
```

---

## 8. Attachments

### List Attachments
```
GET /api/v1/workflow/attachments
Query Parameters:
  - workflow_instance_id: int (optional)
  - skip: int
  - limit: int
```

### Upload Attachment
```
POST /api/v1/workflow/attachments/upload
Content-Type: multipart/form-data
Body:
  - workflow_instance_id: int (required)
  - uploaded_by_id: int (required)
  - description: string (optional)
  - is_public: boolean (default: false)
  - file: file (required)
```

### Get Attachment
```
GET /api/v1/workflow/attachments/{attachment_id}
```

### Get Download URL
```
GET /api/v1/workflow/attachments/{attachment_id}/download
Returns: Temporary download URL (expires in 1 hour)
```

### Update Attachment
```
PUT /api/v1/workflow/attachments/{attachment_id}
Body: WorkflowAttachmentUpdate
  - file_name: string (optional)
  - description: string (optional)
  - is_public: boolean (optional)
```

### Delete Attachment
```
DELETE /api/v1/workflow/attachments/{attachment_id}
```

### Trigger Virus Scan
```
POST /api/v1/workflow/attachments/{attachment_id}/scan
Returns: Updated attachment with scan results
```

---

## 9. History & Audit Trail

### List History
```
GET /api/v1/workflow/history
Query Parameters:
  - workflow_instance_id: int (optional)
  - event_type: WorkflowHistoryEventType (optional)
  - actor_id: int (optional)
  - start_date: datetime (optional)
  - end_date: datetime (optional)
  - skip: int
  - limit: int
```

**WorkflowHistoryEventType enum**: created, started, step_completed, status_changed, assigned, approved, rejected, delegated, comment_added, attachment_added, attachment_removed, data_updated, sla_warning, sla_breached, escalated, cancelled, completed, custom

### Get History Entry
```
GET /api/v1/workflow/history/{history_id}
```

### Get Workflow Timeline
```
GET /api/v1/workflow/history/instance/{instance_id}/timeline
Returns: Complete timeline with all events and step executions
```

### Get Audit Trail
```
GET /api/v1/workflow/history/instance/{instance_id}/audit
Returns: Tamper-evident audit trail with checksums
```

### Get Step History
```
GET /api/v1/workflow/history/instance/{instance_id}/steps
Returns: Detailed step execution history
```

### Get Field Changes
```
GET /api/v1/workflow/history/instance/{instance_id}/changes
Query Parameters:
  - field_name: string (optional)
Returns: All field changes over time
```

### Export Audit Trail
```
GET /api/v1/workflow/history/export/{instance_id}
Query Parameters:
  - format: string (json, csv, pdf)
Returns: Exported audit trail for compliance
```

---

## 10. Notifications

### Templates

#### List Templates
```
GET /api/v1/workflow/notifications/templates
Query Parameters:
  - skip: int
  - limit: int
  - is_active: boolean (optional)
```

#### Create Template
```
POST /api/v1/workflow/notifications/templates
Body: WorkflowNotificationTemplateCreate
  - name: string (required, unique)
  - description: string (optional)
  - notification_type: NotificationType
  - subject_template: string (optional)
  - body_template: string (required)
  - sms_template: string (optional, max 160 chars)
  - channels: array (default: ["email", "in_app"])
  - priority: string (default: "normal")
  - is_active: boolean (default: true)
```

**NotificationType enum**: workflow_started, workflow_completed, workflow_failed, approval_required, approval_approved, approval_rejected, approval_delegated, task_assigned, sla_warning, sla_breached, comment_mentioned, comment_replied, status_changed, escalated, custom

**NotificationChannel enum**: in_app, email, sms, push, webhook

#### Get Template
```
GET /api/v1/workflow/notifications/templates/{template_id}
```

#### Update Template
```
PUT /api/v1/workflow/notifications/templates/{template_id}
Body: WorkflowNotificationTemplateUpdate
```

#### Delete Template
```
DELETE /api/v1/workflow/notifications/templates/{template_id}
```

### Notifications

#### List Notifications
```
GET /api/v1/workflow/notifications
Query Parameters:
  - recipient_id: int (optional)
  - status: NotificationStatus (optional)
  - unread_only: boolean (default: false)
  - skip: int
  - limit: int
```

**NotificationStatus enum**: pending, sent, delivered, read, failed, cancelled

#### Send Notification
```
POST /api/v1/workflow/notifications/send
Body: NotificationSendRequest
  - template_id: int (required)
  - recipient_id: int (required)
  - workflow_instance_id: int (optional)
  - variables: object (optional)
  - channel: NotificationChannel (optional)
  - scheduled_at: datetime (optional)
```

#### Send Bulk Notifications
```
POST /api/v1/workflow/notifications/bulk-send
Body: BulkNotificationRequest
  - template_id: int (required)
  - recipient_ids: array[int] (required)
  - workflow_instance_id: int (optional)
  - variables: object (optional)
  - scheduled_at: datetime (optional)
Returns: Status and notification IDs
```

#### Get Notification
```
GET /api/v1/workflow/notifications/{notification_id}
```

#### Mark as Read
```
POST /api/v1/workflow/notifications/{notification_id}/mark-read
```

#### Mark All as Read
```
POST /api/v1/workflow/notifications/mark-all-read
Body:
  - recipient_id: int (required)
```

#### Get User Statistics
```
GET /api/v1/workflow/notifications/user/{user_id}/statistics
Returns: Notification statistics (total, sent, delivered, read, failed, rates)
```

### Preferences

#### Get User Preferences
```
GET /api/v1/workflow/notifications/preferences/{user_id}
```

#### Create Preference
```
POST /api/v1/workflow/notifications/preferences
Body: NotificationPreferenceCreate
  - user_id: int (required)
  - notification_type: NotificationType (required)
  - enable_email: boolean (default: true)
  - enable_in_app: boolean (default: true)
  - enable_sms: boolean (default: false)
  - enable_push: boolean (default: true)
  - do_not_disturb_start: string (optional, e.g., "22:00")
  - do_not_disturb_end: string (optional, e.g., "08:00")
  - batch_notifications: boolean (default: false)
  - batch_interval_minutes: int (default: 60)
  - max_notifications_per_day: int (optional)
  - digest_mode: boolean (default: false)
```

#### Update Preference
```
PUT /api/v1/workflow/notifications/preferences/{preference_id}
Body: NotificationPreferenceUpdate
```

---

## 11. Analytics

### Get Workflow Metrics
```
GET /api/v1/workflow/analytics/metrics
Query Parameters:
  - workflow_template_id: int (optional)
  - start_date: date (optional)
  - end_date: date (optional)
Returns: Aggregated workflow metrics
```

### Get Step Metrics
```
GET /api/v1/workflow/analytics/steps/{template_id}
Query Parameters:
  - start_date: date (optional)
  - end_date: date (optional)
Returns: Metrics for individual workflow steps
```

### Get Performance Snapshot
```
GET /api/v1/workflow/analytics/performance
Query Parameters:
  - workflow_template_id: int (optional)
Returns: Real-time performance dashboard data
```

### Get User Metrics
```
GET /api/v1/workflow/analytics/users/{user_id}
Query Parameters:
  - workflow_template_id: int (optional)
  - start_date: date (optional)
  - end_date: date (optional)
Returns: User-specific workflow metrics
```

### Identify Bottlenecks
```
GET /api/v1/workflow/analytics/bottlenecks/{template_id}
Returns: Steps causing delays and bottlenecks
```

### Get Performance Report
```
GET /api/v1/workflow/analytics/report
Query Parameters:
  - template_id: int (optional)
  - start_date: date (required)
  - end_date: date (required)
  - include_steps: boolean (default: false)
Returns: Comprehensive performance report
```

---

## State Machine Diagram

```
[DRAFT] ──> [IN_PROGRESS] ──> [PENDING_APPROVAL] ──> [APPROVED] ──> [COMPLETED]
   │             │                    │                  │
   │             │                    │                  │
   └─────────────┴────────────────────┴──────────────────┴──> [CANCELLED]
                                      │
                                      └──> [REJECTED]
```

### State Transitions
- **DRAFT → IN_PROGRESS**: Workflow started
- **IN_PROGRESS → PENDING_APPROVAL**: Approval required
- **IN_PROGRESS → COMPLETED**: Direct completion (no approval)
- **PENDING_APPROVAL → APPROVED**: All approvals granted
- **PENDING_APPROVAL → REJECTED**: Any approval rejected
- **APPROVED → COMPLETED**: Workflow finalized
- **Any → CANCELLED**: Workflow cancelled

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async operation) |
| 204 | No Content (successful deletion) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Common Models

### Workflow Template Step Schema
```json
{
  "step_index": 0,
  "step_name": "string",
  "step_type": "approval|task|automation|notification",
  "required": true,
  "timeout_minutes": 60,
  "assignee_type": "user|role|department",
  "assignee_id": 1,
  "form_fields": [],
  "conditions": [],
  "on_success": "next_step",
  "on_failure": "cancel"
}
```

### Workflow Data Schema
```json
{
  "requester_id": 1,
  "request_type": "leave|loan|vehicle_assignment|termination",
  "request_data": {},
  "supporting_documents": [],
  "priority": "low|medium|high|urgent",
  "metadata": {}
}
```

---

## Authentication
All endpoints require authentication via Bearer token:
```
Authorization: Bearer <token>
```

## Rate Limiting
- 1000 requests per hour per user
- 10000 requests per hour per organization

---

## Webhooks
Configure webhooks for real-time notifications:
- workflow.created
- workflow.started
- workflow.completed
- workflow.failed
- approval.requested
- approval.approved
- approval.rejected
- sla.warning
- sla.breached

---

## Best Practices

1. **Workflow Design**:
   - Keep workflows simple and linear when possible
   - Use parallel approvals sparingly
   - Set realistic SLA times
   - Include clear step names and descriptions

2. **Performance**:
   - Use pagination for large result sets
   - Filter queries to reduce payload size
   - Cache frequently accessed templates
   - Use bulk operations for multiple items

3. **Security**:
   - Scan all attachments for viruses
   - Validate user permissions before approvals
   - Use internal comments for sensitive information
   - Enable audit logging for compliance

4. **Notifications**:
   - Respect user preferences
   - Use appropriate channels (email for urgent, in-app for info)
   - Batch non-urgent notifications
   - Include clear action buttons

5. **Audit Trail**:
   - Never delete audit entries
   - Verify checksums for compliance
   - Export regularly for archival
   - Track all state changes

---

## Support
For API support, contact: dev@barq.com
Documentation: https://docs.barq.com/workflow-api
