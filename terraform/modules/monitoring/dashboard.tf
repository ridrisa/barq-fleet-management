# Cloud Monitoring Dashboard for BARQ Fleet Management

resource "google_monitoring_dashboard" "barq_main" {
  dashboard_json = jsonencode({
    displayName = "BARQ Fleet Management - Main Dashboard"

    gridLayout = {
      widgets = [
        # Row 1: Service Health Overview
        {
          title = "Service Health Status"
          scorecard = {
            timeSeriesQuery = {
              timeSeriesFilter = {
                filter = <<-EOT
                  resource.type="cloud_run_revision"
                  resource.labels.service_name=monitoring.regex.full_match("barq-api-(production|staging)")
                  metric.type="run.googleapis.com/request_count"
                EOT

                aggregation = {
                  alignmentPeriod    = "60s"
                  perSeriesAligner   = "ALIGN_RATE"
                  crossSeriesReducer = "REDUCE_SUM"
                  groupByFields      = ["resource.service_name"]
                }
              }
            }
            sparkChartView = {
              sparkChartType = "SPARK_LINE"
            }
          }
        },

        # Row 1: Request Rate
        {
          title = "Request Rate (req/s)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name=monitoring.regex.full_match("barq-api-(production|staging)")
                    metric.type="run.googleapis.com/request_count"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.service_name"]
                  }
                }
              }
              plotType = "LINE"
            }]
            yAxis = {
              label = "Requests/sec"
              scale = "LINEAR"
            }
            chartOptions = {
              mode = "COLOR"
            }
          }
        },

        # Row 1: Success Rate
        {
          title = "Success Rate (%)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name=monitoring.regex.full_match("barq-api-(production|staging)")
                    metric.type="run.googleapis.com/request_count"
                    metric.labels.response_code_class="2xx"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.service_name"]
                  }
                }
              }
              plotType = "LINE"
            }]
            thresholds = [{
              value = 99.0
              color = "YELLOW"
              label = "99% threshold"
            }]
          }
        },

        # Row 2: Response Latency (p50, p95, p99)
        {
          title = "Response Latency (ms)"
          xyChart = {
            dataSets = [
              # p50
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = <<-EOT
                      resource.type="cloud_run_revision"
                      resource.labels.service_name="barq-api-production"
                      metric.type="run.googleapis.com/request_latencies"
                    EOT

                    aggregation = {
                      alignmentPeriod     = "60s"
                      perSeriesAligner    = "ALIGN_DELTA"
                      crossSeriesReducer  = "REDUCE_PERCENTILE_50"
                      groupByFields       = ["resource.service_name"]
                    }
                  }
                }
                plotType = "LINE"
                legendTemplate = "p50"
              },
              # p95
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = <<-EOT
                      resource.type="cloud_run_revision"
                      resource.labels.service_name="barq-api-production"
                      metric.type="run.googleapis.com/request_latencies"
                    EOT

                    aggregation = {
                      alignmentPeriod     = "60s"
                      perSeriesAligner    = "ALIGN_DELTA"
                      crossSeriesReducer  = "REDUCE_PERCENTILE_95"
                      groupByFields       = ["resource.service_name"]
                    }
                  }
                }
                plotType = "LINE"
                legendTemplate = "p95"
              },
              # p99
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = <<-EOT
                      resource.type="cloud_run_revision"
                      resource.labels.service_name="barq-api-production"
                      metric.type="run.googleapis.com/request_latencies"
                    EOT

                    aggregation = {
                      alignmentPeriod     = "60s"
                      perSeriesAligner    = "ALIGN_DELTA"
                      crossSeriesReducer  = "REDUCE_PERCENTILE_99"
                      groupByFields       = ["resource.service_name"]
                    }
                  }
                }
                plotType = "LINE"
                legendTemplate = "p99"
              }
            ]
            yAxis = {
              label = "Latency (ms)"
              scale = "LINEAR"
            }
            thresholds = [
              {
                value = 500
                color = "YELLOW"
                label = "500ms threshold"
              },
              {
                value = 1000
                color = "RED"
                label = "1s threshold"
              }
            ]
          }
        },

        # Row 2: Error Rate
        {
          title = "Error Rate (%)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name="barq-api-production"
                    metric.type="run.googleapis.com/request_count"
                    metric.labels.response_code_class="5xx"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
              plotType = "LINE"
            }]
            yAxis = {
              label = "Error Rate"
              scale = "LINEAR"
            }
            thresholds = [
              {
                value = 0.01  # 1% error rate
                color = "RED"
                label = "1% error threshold"
              }
            ]
          }
        },

        # Row 2: Container Instance Count
        {
          title = "Container Instances"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name=monitoring.regex.full_match("barq-api-(production|staging)")
                    metric.type="run.googleapis.com/container/instance_count"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_MEAN"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.service_name"]
                  }
                }
              }
              plotType = "STACKED_AREA"
            }]
            yAxis = {
              label = "Instances"
              scale = "LINEAR"
            }
          }
        },

        # Row 3: Database Connections (Cloud SQL)
        {
          title = "Database Connections"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloudsql_database"
                    metric.type="cloudsql.googleapis.com/database/network/connections"
                  EOT

                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
              plotType = "LINE"
            }]
            yAxis = {
              label = "Connections"
              scale = "LINEAR"
            }
            thresholds = [{
              value = 400  # 80% of max (assuming 500 max)
              color = "YELLOW"
              label = "80% capacity"
            }]
          }
        },

        # Row 3: Database CPU Utilization
        {
          title = "Database CPU Utilization (%)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloudsql_database"
                    metric.type="cloudsql.googleapis.com/database/cpu/utilization"
                  EOT

                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
              plotType = "LINE"
            }]
            yAxis = {
              label = "CPU %"
              scale = "LINEAR"
            }
            thresholds = [
              {
                value = 0.70
                color = "YELLOW"
                label = "70% threshold"
              },
              {
                value = 0.85
                color = "RED"
                label = "85% threshold"
              }
            ]
          }
        },

        # Row 3: Database Memory Utilization
        {
          title = "Database Memory Utilization (%)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloudsql_database"
                    metric.type="cloudsql.googleapis.com/database/memory/utilization"
                  EOT

                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
              plotType = "LINE"
            }]
            yAxis = {
              label = "Memory %"
              scale = "LINEAR"
            }
            thresholds = [
              {
                value = 0.80
                color = "YELLOW"
                label = "80% threshold"
              },
              {
                value = 0.90
                color = "RED"
                label = "90% threshold"
              }
            ]
          }
        },

        # Row 4: Log-based Error Count
        {
          title = "Application Errors (Last Hour)"
          scorecard = {
            timeSeriesQuery = {
              timeSeriesFilter = {
                filter = <<-EOT
                  resource.type="cloud_run_revision"
                  resource.labels.service_name="barq-api-production"
                  severity>=ERROR
                EOT

                aggregation = {
                  alignmentPeriod  = "60s"
                  perSeriesAligner = "ALIGN_RATE"
                }
              }
            }
            sparkChartView = {
              sparkChartType = "SPARK_BAR"
            }
          }
        },

        # Row 4: Traffic by Response Code
        {
          title = "Requests by Response Code"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name="barq-api-production"
                    metric.type="run.googleapis.com/request_count"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["metric.response_code_class"]
                  }
                }
              }
              plotType = "STACKED_AREA"
            }]
            yAxis = {
              label = "Requests/sec"
              scale = "LINEAR"
            }
          }
        },

        # Row 4: Billable Instance Time
        {
          title = "Billable Instance Time (vCPU-seconds)"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name=monitoring.regex.full_match("barq-api-(production|staging)")
                    metric.type="run.googleapis.com/container/billable_instance_time"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.service_name"]
                  }
                }
              }
              plotType = "STACKED_AREA"
            }]
            yAxis = {
              label = "vCPU-seconds/sec"
              scale = "LINEAR"
            }
          }
        }
      ]
    }
  })
}

# Deployment Dashboard
resource "google_monitoring_dashboard" "barq_deployments" {
  dashboard_json = jsonencode({
    displayName = "BARQ - Deployments & Revisions"

    gridLayout = {
      widgets = [
        {
          title = "Active Revisions"
          text = {
            content = "Monitor active Cloud Run revisions and traffic distribution"
            format  = "MARKDOWN"
          }
        },

        {
          title = "Request Count by Revision"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name="barq-api-production"
                    metric.type="run.googleapis.com/request_count"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.revision_name"]
                  }
                }
              }
              plotType = "STACKED_AREA"
            }]
          }
        },

        {
          title = "Error Rate by Revision"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = <<-EOT
                    resource.type="cloud_run_revision"
                    resource.labels.service_name="barq-api-production"
                    metric.type="run.googleapis.com/request_count"
                    metric.labels.response_code_class="5xx"
                  EOT

                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.revision_name"]
                  }
                }
              }
              plotType = "LINE"
            }]
          }
        }
      ]
    }
  })
}

output "main_dashboard_url" {
  description = "URL to the main monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.barq_main.id}"
}

output "deployment_dashboard_url" {
  description = "URL to the deployment monitoring dashboard"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.barq_deployments.id}"
}
