from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# Workflow Metrics Schemas
class WorkflowMetricsBase(BaseModel):
    workflow_template_id: int
    date: date
    total_instances: int = 0
    completed_instances: int = 0
    rejected_instances: int = 0
    cancelled_instances: int = 0
    in_progress_instances: int = 0
    avg_completion_time: Optional[float] = None
    min_completion_time: Optional[float] = None
    max_completion_time: Optional[float] = None
    median_completion_time: Optional[float] = None
    avg_steps_completed: Optional[float] = None
    total_steps_executed: int = 0
    avg_approval_time: Optional[float] = None
    total_approvals: int = 0
    total_rejections: int = 0
    sla_met_count: int = 0
    sla_breached_count: int = 0
    avg_sla_compliance: Optional[float] = None
    bottleneck_steps: Optional[List[Dict[str, Any]]] = None


class WorkflowMetricsCreate(WorkflowMetricsBase):
    pass


class WorkflowMetricsUpdate(BaseModel):
    total_instances: Optional[int] = Field(None, ge=0)
    completed_instances: Optional[int] = Field(None, ge=0)
    rejected_instances: Optional[int] = Field(None, ge=0)
    cancelled_instances: Optional[int] = Field(None, ge=0)
    in_progress_instances: Optional[int] = Field(None, ge=0)
    avg_completion_time: Optional[float] = None
    min_completion_time: Optional[float] = None
    max_completion_time: Optional[float] = None
    median_completion_time: Optional[float] = None
    avg_steps_completed: Optional[float] = None
    total_steps_executed: Optional[int] = Field(None, ge=0)
    avg_approval_time: Optional[float] = None
    total_approvals: Optional[int] = Field(None, ge=0)
    total_rejections: Optional[int] = Field(None, ge=0)
    sla_met_count: Optional[int] = Field(None, ge=0)
    sla_breached_count: Optional[int] = Field(None, ge=0)
    avg_sla_compliance: Optional[float] = None
    bottleneck_steps: Optional[List[Dict[str, Any]]] = None


class WorkflowMetricsResponse(WorkflowMetricsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Workflow Step Metrics Schemas
class WorkflowStepMetricsBase(BaseModel):
    workflow_template_id: int
    step_index: int
    step_name: str
    date: date
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    skipped_executions: int = 0
    avg_execution_time: Optional[float] = None
    min_execution_time: Optional[float] = None
    max_execution_time: Optional[float] = None
    avg_wait_time: Optional[float] = None
    max_wait_time: Optional[float] = None
    error_rate: Optional[float] = None
    common_errors: Optional[List[Dict[str, Any]]] = None


class WorkflowStepMetricsCreate(WorkflowStepMetricsBase):
    pass


class WorkflowStepMetricsUpdate(BaseModel):
    total_executions: Optional[int] = Field(None, ge=0)
    successful_executions: Optional[int] = Field(None, ge=0)
    failed_executions: Optional[int] = Field(None, ge=0)
    skipped_executions: Optional[int] = Field(None, ge=0)
    avg_execution_time: Optional[float] = None
    min_execution_time: Optional[float] = None
    max_execution_time: Optional[float] = None
    avg_wait_time: Optional[float] = None
    max_wait_time: Optional[float] = None
    error_rate: Optional[float] = None
    common_errors: Optional[List[Dict[str, Any]]] = None


class WorkflowStepMetricsResponse(WorkflowStepMetricsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Workflow Performance Snapshot Schemas
class WorkflowPerformanceSnapshotBase(BaseModel):
    workflow_template_id: Optional[int] = None
    snapshot_time: datetime
    active_instances: int = 0
    pending_approvals: int = 0
    overdue_instances: int = 0
    sla_at_risk: int = 0
    completed_last_24h: int = 0
    avg_completion_time_24h: Optional[float] = None
    success_rate_24h: Optional[float] = None
    throughput_per_hour: Optional[float] = None
    estimated_completion_time: Optional[float] = None
    critical_alerts: int = 0
    warning_alerts: int = 0
    details: Optional[Dict[str, Any]] = None


class WorkflowPerformanceSnapshotCreate(WorkflowPerformanceSnapshotBase):
    pass


class WorkflowPerformanceSnapshotResponse(WorkflowPerformanceSnapshotBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Workflow User Metrics Schemas
class WorkflowUserMetricsBase(BaseModel):
    user_id: int
    workflow_template_id: Optional[int] = None
    date: date
    workflows_initiated: int = 0
    approvals_completed: int = 0
    approvals_pending: int = 0
    avg_approval_time: Optional[float] = None
    approval_rate: Optional[float] = None
    tasks_completed: int = 0
    avg_task_completion_time: Optional[float] = None
    on_time_completion_rate: Optional[float] = None
    overdue_tasks: int = 0


class WorkflowUserMetricsCreate(WorkflowUserMetricsBase):
    pass


class WorkflowUserMetricsUpdate(BaseModel):
    workflows_initiated: Optional[int] = Field(None, ge=0)
    approvals_completed: Optional[int] = Field(None, ge=0)
    approvals_pending: Optional[int] = Field(None, ge=0)
    avg_approval_time: Optional[float] = None
    approval_rate: Optional[float] = None
    tasks_completed: Optional[int] = Field(None, ge=0)
    avg_task_completion_time: Optional[float] = None
    on_time_completion_rate: Optional[float] = None
    overdue_tasks: Optional[int] = Field(None, ge=0)


class WorkflowUserMetricsResponse(WorkflowUserMetricsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Analytics Query Schemas
class WorkflowAnalyticsQuery(BaseModel):
    """Query parameters for workflow analytics"""
    workflow_template_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    user_id: Optional[int] = None
    group_by: Optional[str] = Field(None, pattern="^(day|week|month)$")


class WorkflowBottleneckResponse(BaseModel):
    """Bottleneck analysis response"""
    workflow_template_id: int
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[str]


class WorkflowPerformanceReport(BaseModel):
    """Comprehensive performance report"""
    workflow_template_id: int
    period_start: date
    period_end: date
    overview: WorkflowMetricsResponse
    step_metrics: List[WorkflowStepMetricsResponse]
    bottlenecks: List[Dict[str, Any]]
    trends: Dict[str, Any]
    recommendations: List[str]
