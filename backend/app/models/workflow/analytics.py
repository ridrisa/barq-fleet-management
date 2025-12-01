from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, Text, DateTime, Date
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class WorkflowMetrics(BaseModel):
    """Aggregated metrics for workflow templates"""
    __tablename__ = "workflow_metrics"

    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    date = Column(Date, nullable=False)

    # Volume metrics
    total_instances = Column(Integer, default=0)
    completed_instances = Column(Integer, default=0)
    rejected_instances = Column(Integer, default=0)
    cancelled_instances = Column(Integer, default=0)
    in_progress_instances = Column(Integer, default=0)

    # Time metrics (in minutes)
    avg_completion_time = Column(Float)
    min_completion_time = Column(Float)
    max_completion_time = Column(Float)
    median_completion_time = Column(Float)

    # Step metrics
    avg_steps_completed = Column(Float)
    total_steps_executed = Column(Integer, default=0)

    # Approval metrics
    avg_approval_time = Column(Float)
    total_approvals = Column(Integer, default=0)
    total_rejections = Column(Integer, default=0)

    # SLA metrics
    sla_met_count = Column(Integer, default=0)
    sla_breached_count = Column(Integer, default=0)
    avg_sla_compliance = Column(Float)

    # Bottleneck identification
    bottleneck_steps = Column(JSON)  # Array of step indices with high wait times

    # Relationships
    workflow_template = relationship("WorkflowTemplate", back_populates="metrics")


class WorkflowStepMetrics(BaseModel):
    """Metrics for individual workflow steps"""
    __tablename__ = "workflow_step_metrics"

    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)
    date = Column(Date, nullable=False)

    # Execution metrics
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    skipped_executions = Column(Integer, default=0)

    # Time metrics (in minutes)
    avg_execution_time = Column(Float)
    min_execution_time = Column(Float)
    max_execution_time = Column(Float)

    # Wait time (time from previous step)
    avg_wait_time = Column(Float)
    max_wait_time = Column(Float)

    # Error tracking
    error_rate = Column(Float)
    common_errors = Column(JSON)  # Array of common error messages

    # Relationships
    workflow_template = relationship("WorkflowTemplate")


class WorkflowPerformanceSnapshot(BaseModel):
    """Real-time performance snapshot for dashboards"""
    __tablename__ = "workflow_performance_snapshots"

    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    snapshot_time = Column(DateTime, nullable=False)

    # Current state
    active_instances = Column(Integer, default=0)
    pending_approvals = Column(Integer, default=0)
    overdue_instances = Column(Integer, default=0)
    sla_at_risk = Column(Integer, default=0)

    # Recent performance (last 24 hours)
    completed_last_24h = Column(Integer, default=0)
    avg_completion_time_24h = Column(Float)
    success_rate_24h = Column(Float)

    # Capacity metrics
    throughput_per_hour = Column(Float)
    estimated_completion_time = Column(Float)

    # Alert metrics
    critical_alerts = Column(Integer, default=0)
    warning_alerts = Column(Integer, default=0)

    details = Column(JSON)  # Additional snapshot data

    # Relationships
    workflow_template = relationship("WorkflowTemplate")


class WorkflowUserMetrics(BaseModel):
    """User-specific workflow metrics"""
    __tablename__ = "workflow_user_metrics"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workflow_template_id = Column(Integer, ForeignKey("workflow_templates.id"))
    date = Column(Date, nullable=False)

    # Initiated workflows
    workflows_initiated = Column(Integer, default=0)

    # Approvals
    approvals_completed = Column(Integer, default=0)
    approvals_pending = Column(Integer, default=0)
    avg_approval_time = Column(Float)
    approval_rate = Column(Float)  # Percentage approved vs rejected

    # Tasks
    tasks_completed = Column(Integer, default=0)
    avg_task_completion_time = Column(Float)

    # Performance
    on_time_completion_rate = Column(Float)
    overdue_tasks = Column(Integer, default=0)

    # Relationships
    user = relationship("User")
    workflow_template = relationship("WorkflowTemplate")
