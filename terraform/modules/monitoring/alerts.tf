# Cloud Monitoring Alert Policies for BARQ Fleet Management

# Notification Channels
resource "google_monitoring_notification_channel" "email" {
  display_name = "DevOps Team Email"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_notification_channel" "slack" {
  count = var.slack_webhook_url != "" ? 1 : 0

  display_name = "Slack Channel"
  type         = "slack"

  labels = {
    channel_name = var.slack_channel_name
  }

  sensitive_labels {
    auth_token = var.slack_webhook_url
  }
}

# Alert Policy: High Error Rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "BARQ - High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 1%"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        resource.labels.service_name = "barq-api-production"
        metric.type = "run.googleapis.com/request_count"
        metric.labels.response_code_class = "5xx"
      EOT

      duration   = "300s"  # 5 minutes
      comparison = "COMPARISON_GT"
      threshold_value = 0.01  # 1% error rate

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = concat(
    [google_monitoring_notification_channel.email.id],
    var.slack_webhook_url != "" ? [google_monitoring_notification_channel.slack[0].id] : []
  )

  alert_strategy {
    auto_close = "1800s"  # Auto-close after 30 minutes

    notification_rate_limit {
      period = "300s"  # Limit notifications to once per 5 minutes
    }
  }

  documentation {
    content = <<-EOT
      ## High Error Rate Detected

      The error rate for barq-api-production has exceeded 1%.

      ### Immediate Actions:
      1. Check Cloud Logging for error details
      2. Review recent deployments
      3. Consider rolling back if errors persist

      ### Runbook:
      https://github.com/barq-fleet/barq-fleet-clean/blob/main/docs/ROLLBACK_PROCEDURES.md
    EOT
  }
}

# Alert Policy: High Latency
resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "BARQ - High API Latency (p95)"
  combiner     = "OR"

  conditions {
    display_name = "p95 latency > 1000ms"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        resource.labels.service_name = "barq-api-production"
        metric.type = "run.googleapis.com/request_latencies"
      EOT

      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 1000  # 1 second

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content = <<-EOT
      ## High API Latency Detected

      The p95 latency for barq-api-production has exceeded 1 second.

      ### Immediate Actions:
      1. Check database query performance
      2. Review Cloud Run instance metrics
      3. Check for external API slowdowns
      4. Consider scaling up resources

      ### Dashboard:
      https://console.cloud.google.com/monitoring
    EOT
  }
}

# Alert Policy: Service Unavailable
resource "google_monitoring_alert_policy" "service_unavailable" {
  display_name = "BARQ - Service Unavailable (Uptime Check)"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failed"

    condition_threshold {
      filter = <<-EOT
        resource.type = "uptime_url"
        metric.type = "monitoring.googleapis.com/uptime_check/check_passed"
        metric.labels.check_id = "${google_monitoring_uptime_check_config.production.uptime_check_id}"
      EOT

      duration   = "60s"
      comparison = "COMPARISON_LT"
      threshold_value = 1

      aggregations {
        alignment_period     = "60s"
        cross_series_reducer = "REDUCE_COUNT_FALSE"
        per_series_aligner   = "ALIGN_NEXT_OLDER"
        group_by_fields      = ["resource.label.*"]
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = concat(
    [google_monitoring_notification_channel.email.id],
    var.slack_webhook_url != "" ? [google_monitoring_notification_channel.slack[0].id] : []
  )

  alert_strategy {
    auto_close = "900s"

    notification_rate_limit {
      period = "60s"
    }
  }

  documentation {
    content = <<-EOT
      ## CRITICAL: Service Unavailable

      The production service is not responding to uptime checks!

      ### IMMEDIATE Actions (P0):
      1. Verify service status in Cloud Run console
      2. Check recent deployments
      3. Execute emergency rollback if needed:
         ```bash
         ./scripts/deployment/rollback-production.sh
         ```

      ### Escalation:
      - On-call DevOps: Immediate
      - Tech Lead: 5 minutes
      - CTO: 15 minutes (if not resolved)
    EOT
  }
}

# Alert Policy: Database Connection Pool Exhaustion
resource "google_monitoring_alert_policy" "db_connections_high" {
  display_name = "BARQ - Database Connection Pool High"
  combiner     = "OR"

  conditions {
    display_name = "Database connections > 80%"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloudsql_database"
        metric.type = "cloudsql.googleapis.com/database/network/connections"
      EOT

      duration   = "180s"
      comparison = "COMPARISON_GT"
      threshold_value = 400  # 80% of 500 max connections

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content = <<-EOT
      ## Database Connection Pool Running High

      Database connections are above 80% of maximum capacity.

      ### Actions:
      1. Check for connection leaks in application logs
      2. Review long-running queries
      3. Consider scaling up database or adjusting connection pool settings
      4. Monitor for connection exhaustion

      ### Query to Check:
      ```sql
      SELECT * FROM pg_stat_activity;
      ```
    EOT
  }
}

# Alert Policy: Database CPU High
resource "google_monitoring_alert_policy" "db_cpu_high" {
  display_name = "BARQ - Database CPU High"
  combiner     = "OR"

  conditions {
    display_name = "Database CPU > 85%"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloudsql_database"
        metric.type = "cloudsql.googleapis.com/database/cpu/utilization"
      EOT

      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 0.85

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content = <<-EOT
      ## Database CPU Utilization High

      Database CPU is consistently above 85%.

      ### Actions:
      1. Identify slow queries using Query Insights
      2. Review database indexes
      3. Consider database scaling
      4. Check for N+1 query problems
    EOT
  }
}

# Alert Policy: Cloud Run Instance Count High
resource "google_monitoring_alert_policy" "instance_count_high" {
  display_name = "BARQ - High Instance Count"
  combiner     = "OR"

  conditions {
    display_name = "Instance count > 80% of max"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        resource.labels.service_name = "barq-api-production"
        metric.type = "run.googleapis.com/container/instance_count"
      EOT

      duration   = "300s"
      comparison = "COMPARISON_GT"
      threshold_value = 40  # 80% of 50 max instances

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content = <<-EOT
      ## High Instance Count Warning

      Cloud Run instance count is above 80% of maximum.

      ### Actions:
      1. Check if this is expected traffic
      2. Review autoscaling settings
      3. Consider increasing max instances if legitimate traffic
      4. Investigate potential DDoS or abuse
    EOT
  }
}

# Alert Policy: Container Startup Latency
resource "google_monitoring_alert_policy" "startup_latency_high" {
  display_name = "BARQ - High Container Startup Latency"
  combiner     = "OR"

  conditions {
    display_name = "Startup latency > 10 seconds"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        resource.labels.service_name = "barq-api-production"
        metric.type = "run.googleapis.com/container/startup_latencies"
      EOT

      duration   = "180s"
      comparison = "COMPARISON_GT"
      threshold_value = 10000  # 10 seconds in milliseconds

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_MEAN"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content = <<-EOT
      ## High Container Startup Latency

      Containers are taking longer than 10 seconds to start.

      ### Actions:
      1. Optimize Docker image size
      2. Review application initialization code
      3. Consider using min instances to keep containers warm
      4. Check for slow database migrations on startup
    EOT
  }
}

# Uptime Check Configuration
resource "google_monitoring_uptime_check_config" "production" {
  display_name = "BARQ Production Health Check"
  timeout      = "10s"
  period       = "60s"  # Check every 60 seconds

  http_check {
    path         = "/health/live"
    port         = "443"
    use_ssl      = true
    validate_ssl = true

    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.production_domain  # e.g., "api.barq-fleet.com"
    }
  }

  content_matchers {
    content = "alive"
    matcher = "CONTAINS_STRING"
  }
}

resource "google_monitoring_uptime_check_config" "staging" {
  display_name = "BARQ Staging Health Check"
  timeout      = "10s"
  period       = "300s"  # Check every 5 minutes (less frequent for staging)

  http_check {
    path         = "/health/live"
    port         = "443"
    use_ssl      = true
    validate_ssl = true

    accepted_response_status_codes {
      status_class = "STATUS_CLASS_2XX"
    }
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.staging_domain  # Cloud Run URL
    }
  }
}

# Log-based Metrics for Custom Error Tracking
resource "google_logging_metric" "application_errors" {
  name   = "barq_application_errors"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    resource.labels.service_name=~"barq-api-.*"
    severity>=ERROR
    -textPayload=~"health"
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"

    labels {
      key         = "severity"
      value_type  = "STRING"
      description = "Log severity level"
    }

    labels {
      key         = "service_name"
      value_type  = "STRING"
      description = "Cloud Run service name"
    }
  }

  label_extractors = {
    "severity"     = "EXTRACT(severity)"
    "service_name" = "EXTRACT(resource.labels.service_name)"
  }
}

# Alert on Custom Log Metric
resource "google_monitoring_alert_policy" "application_errors_spike" {
  display_name = "BARQ - Application Error Spike"
  combiner     = "OR"

  conditions {
    display_name = "Error spike detected"

    condition_threshold {
      filter = <<-EOT
        resource.type = "cloud_run_revision"
        metric.type = "logging.googleapis.com/user/${google_logging_metric.application_errors.name}"
      EOT

      duration   = "180s"
      comparison = "COMPARISON_GT"
      threshold_value = 10  # More than 10 errors in 3 minutes

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content = <<-EOT
      ## Application Error Spike Detected

      An unusual number of application errors have been detected.

      ### Actions:
      1. Check Cloud Logging for error details
      2. Review recent code changes
      3. Check for infrastructure issues
      4. Consider rollback if errors are critical
    EOT
  }
}

# Output alert policy IDs
output "alert_policy_ids" {
  description = "IDs of all created alert policies"
  value = {
    high_error_rate          = google_monitoring_alert_policy.high_error_rate.id
    high_latency             = google_monitoring_alert_policy.high_latency.id
    service_unavailable      = google_monitoring_alert_policy.service_unavailable.id
    db_connections_high      = google_monitoring_alert_policy.db_connections_high.id
    db_cpu_high              = google_monitoring_alert_policy.db_cpu_high.id
    instance_count_high      = google_monitoring_alert_policy.instance_count_high.id
    startup_latency_high     = google_monitoring_alert_policy.startup_latency_high.id
    application_errors_spike = google_monitoring_alert_policy.application_errors_spike.id
  }
}
