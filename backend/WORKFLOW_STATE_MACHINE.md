# Workflow State Machine - Quick Reference

## State Diagram

```
                     ┌──────────────────────────────────────────────────┐
                     │                                                  │
                     │                 CANCELLED                        │
                     │                    (Any state can cancel)        │
                     │                                                  │
                     └──────────────────────────────────────────────────┘
                              ▲         ▲         ▲         ▲
                              │         │         │         │
                              │         │         │         │
    ┌─────────┐      ┌────────┴───┐   ┌┴─────────┴──┐   ┌─┴────────┐   ┌───────────┐
    │         │      │            │   │             │   │          │   │           │
    │  DRAFT  ├─────>│IN_PROGRESS├──>│PENDING_     ├──>│ APPROVED ├──>│ COMPLETED │
    │         │      │            │   │APPROVAL     │   │          │   │           │
    └─────────┘      └────────────┘   └─────────────┘   └──────────┘   └───────────┘
                              │               │
                              │               │
                              │               ▼
                              │        ┌─────────────┐
                              │        │             │
                              └───────>│  REJECTED   │
                                       │             │
                                       └─────────────┘
```

## States

| State | Description | Can Transition To | Typical Duration |
|-------|-------------|-------------------|------------------|
| **DRAFT** | Initial state, workflow created but not started | IN_PROGRESS, CANCELLED | Minutes to days |
| **IN_PROGRESS** | Workflow actively being processed | PENDING_APPROVAL, COMPLETED, REJECTED, CANCELLED | Hours to days |
| **PENDING_APPROVAL** | Waiting for one or more approvals | APPROVED, REJECTED, CANCELLED | Hours to days (SLA tracked) |
| **APPROVED** | All approvals granted | COMPLETED | Minutes to hours |
| **REJECTED** | Approval denied or workflow failed | (Terminal state) | N/A |
| **COMPLETED** | Workflow successfully finished | (Terminal state) | N/A |
| **CANCELLED** | Workflow cancelled by user/system | (Terminal state) | N/A |

## Transition Rules

### From DRAFT
- **→ IN_PROGRESS**: `POST /instances/start` - Start the workflow
- **→ CANCELLED**: `POST /instances/{id}/cancel` - Cancel before starting

### From IN_PROGRESS
- **→ PENDING_APPROVAL**: Automatic when approval step reached
- **→ COMPLETED**: Direct completion for workflows without approvals
- **→ REJECTED**: Manual rejection or business rule failure
- **→ CANCELLED**: `POST /instances/{id}/cancel`

### From PENDING_APPROVAL
- **→ APPROVED**: All required approvals granted
- **→ REJECTED**: Any approval rejected (if rejection policy = "any")
- **→ CANCELLED**: `POST /instances/{id}/cancel`

### From APPROVED
- **→ COMPLETED**: Finalize workflow, execute completion actions

### Terminal States (No Transitions)
- **REJECTED**: Workflow ended unsuccessfully
- **COMPLETED**: Workflow ended successfully
- **CANCELLED**: Workflow ended by cancellation

## Transition API Calls

### Start Workflow (DRAFT → IN_PROGRESS)
```http
POST /api/v1/workflow/instances/start
{
  "template_id": 1,
  "initiated_by": 123,
  "initial_data": { ... }
}
```

### Advance to Next Step
```http
POST /api/v1/workflow/instances/{id}/advance
{
  "step_data": { ... }
}
```

### Transition Status (Manual)
```http
POST /api/v1/workflow/instances/{id}/transition
{
  "new_status": "COMPLETED",
  "notes": "Manual completion"
}
```

### Cancel Workflow (Any → CANCELLED)
```http
POST /api/v1/workflow/instances/{id}/cancel
{
  "reason": "No longer needed"
}
```

### Process Approval (PENDING_APPROVAL → APPROVED/REJECTED)
```http
POST /api/v1/workflow/approvals/requests/{id}/action
{
  "action": "approve",
  "approver_id": 456,
  "comments": "Looks good"
}
```

## Automatic Transitions

### System-Triggered
1. **IN_PROGRESS → PENDING_APPROVAL**: When workflow reaches approval step
2. **PENDING_APPROVAL → APPROVED**: When all approvals granted
3. **PENDING_APPROVAL → REJECTED**: When any approval rejected (depends on policy)
4. **APPROVED → COMPLETED**: When final actions completed

### SLA-Triggered
1. **Any → ESCALATED**: SLA breach triggers escalation (state remains, flag set)
2. **PENDING_APPROVAL → REJECTED**: SLA timeout with auto-reject policy

## State Guards (Conditions)

### Can Start Workflow?
- State must be DRAFT
- Template must be active
- User must have permission
- Required fields must be populated

### Can Approve?
- State must be PENDING_APPROVAL
- User must be in approval chain
- Approval must not be expired
- Previous level must be approved (if sequential)

### Can Complete?
- State must be APPROVED
- All required steps must be completed
- No pending tasks
- Final validation must pass

### Can Cancel?
- State must not be terminal (COMPLETED, REJECTED, CANCELLED)
- User must have permission
- Cancellation must be allowed for workflow type

## Event Hooks

### On State Change
```python
# Automatic actions on state transitions
state_change_hooks = {
    "IN_PROGRESS": [
        "create_audit_log",
        "notify_initiator",
        "start_sla_timer"
    ],
    "PENDING_APPROVAL": [
        "create_approval_requests",
        "notify_approvers",
        "set_approval_deadline"
    ],
    "APPROVED": [
        "notify_initiator",
        "execute_approval_actions",
        "stop_sla_timer"
    ],
    "REJECTED": [
        "notify_initiator",
        "execute_rejection_actions",
        "archive_workflow"
    ],
    "COMPLETED": [
        "notify_stakeholders",
        "execute_completion_actions",
        "calculate_metrics"
    ],
    "CANCELLED": [
        "notify_stakeholders",
        "cleanup_resources",
        "update_metrics"
    ]
}
```

## Best Practices

### 1. Always Check Current State
```python
# Before transition
current_state = instance.status
if current_state not in allowed_previous_states:
    raise InvalidTransitionError()
```

### 2. Use Transition Endpoint
```python
# Don't manually update state
# instance.status = "COMPLETED"  # ❌ BAD

# Use transition endpoint
POST /instances/{id}/transition  # ✅ GOOD
```

### 3. Handle Concurrent Updates
```python
# Use optimistic locking
# Check version/updated_at before transition
if instance.updated_at != expected_updated_at:
    raise ConcurrentUpdateError()
```

### 4. Log All Transitions
```python
# Every transition creates history entry
workflow_history.create({
    "event_type": "status_changed",
    "previous_state": old_status,
    "new_state": new_status,
    "actor_id": user_id,
    "event_time": now()
})
```

## State-Specific Behaviors

### DRAFT
- **Editable**: Yes, all fields can be modified
- **Deletable**: Yes
- **Visible**: Only to creator
- **SLA**: Not tracked

### IN_PROGRESS
- **Editable**: Limited, only certain fields
- **Deletable**: No, must cancel
- **Visible**: To participants
- **SLA**: Active

### PENDING_APPROVAL
- **Editable**: No
- **Deletable**: No
- **Visible**: To approvers and participants
- **SLA**: Critical, with escalation

### APPROVED
- **Editable**: No
- **Deletable**: No
- **Visible**: To all stakeholders
- **SLA**: Completion timer

### REJECTED
- **Editable**: No
- **Deletable**: Archival only
- **Visible**: To all stakeholders
- **SLA**: Stopped

### COMPLETED
- **Editable**: No
- **Deletable**: Archival only
- **Visible**: To all stakeholders
- **SLA**: Recorded for metrics

### CANCELLED
- **Editable**: No
- **Deletable**: Archival only
- **Visible**: To all stakeholders
- **SLA**: Stopped

## Metrics by State

```sql
-- Workflows by state
SELECT status, COUNT(*)
FROM workflow_instances
GROUP BY status;

-- Average time in each state
SELECT status, AVG(duration_minutes)
FROM workflow_state_durations
GROUP BY status;

-- Stuck workflows (in state too long)
SELECT id, template_id, status, started_at
FROM workflow_instances
WHERE status = 'PENDING_APPROVAL'
  AND started_at < NOW() - INTERVAL '7 days';
```

## Troubleshooting

### Workflow Stuck in PENDING_APPROVAL
1. Check approval requests: `GET /approvals/requests?workflow_instance_id={id}`
2. Check SLA status: `GET /sla/instances?workflow_instance_id={id}`
3. Manual intervention: `POST /approvals/requests/{id}/action`

### Cannot Transition State
1. Verify current state: `GET /instances/{id}`
2. Check transition rules
3. Verify user permissions
4. Check state guards

### State Mismatch
1. Check audit trail: `GET /history/instance/{id}/audit`
2. Verify last state change
3. Check for concurrent updates

## Quick Reference Commands

```bash
# Get current state
GET /instances/{id}

# Get state history
GET /history/instance/{id}/timeline

# Force state transition (admin only)
POST /instances/{id}/transition
{
  "new_status": "COMPLETED",
  "notes": "Admin override",
  "force": true
}

# Check if transition is allowed
GET /instances/{id}/allowed-transitions
# Returns: ["COMPLETED", "CANCELLED"]
```

---

**Remember**: The state machine is the heart of workflow reliability. Always use proper transition endpoints and respect state guards!
