# Cloud Run Module - Backend and Frontend Services

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_connector_id" {
  type = string
}

variable "database_connection" {
  type = string
}

variable "redis_host" {
  type = string
}

variable "redis_port" {
  type = number
}

# Backend Service
resource "google_cloud_run_v2_service" "backend" {
  name     = "barq-api-${var.environment}"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/barq-fleet/barq-api:latest"

      ports {
        container_port = 8000
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "POSTGRES_SERVER"
        value = "/cloudsql/${var.database_connection}"
      }

      env {
        name = "POSTGRES_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = "barq-postgres-password"
            version = "latest"
          }
        }
      }

      env {
        name = "SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = "barq-secret-key"
            version = "latest"
          }
        }
      }

      env {
        name  = "REDIS_HOST"
        value = var.redis_host
      }

      env {
        name  = "REDIS_PORT"
        value = tostring(var.redis_port)
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      startup_probe {
        http_get {
          path = "/api/v1/health"
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/api/v1/health"
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }
    }

    scaling {
      min_instance_count = var.environment == "production" ? 2 : 1
      max_instance_count = var.environment == "production" ? 100 : 10
    }

    vpc_access {
      connector = var.vpc_connector_id
      egress    = "PRIVATE_RANGES_ONLY"
    }

    timeout = "300s"

    service_account = google_service_account.backend.email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Backend Service Account
resource "google_service_account" "backend" {
  account_id   = "barq-backend-${var.environment}"
  display_name = "BARQ Backend Service Account (${var.environment})"
  project      = var.project_id
}

# Backend IAM Policy (allow unauthenticated access)
resource "google_cloud_run_v2_service_iam_member" "backend_public" {
  name   = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role   = "roles/run.invoker"
  member = "allUsers"
}

# Frontend Service
resource "google_cloud_run_v2_service" "frontend" {
  name     = "barq-web-${var.environment}"
  location = var.region
  project  = var.project_id

  template {
    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/barq-fleet/barq-web:latest"

      ports {
        container_port = 80
      }

      env {
        name  = "VITE_API_URL"
        value = google_cloud_run_v2_service.backend.uri
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      liveness_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 10
        timeout_seconds       = 3
        period_seconds        = 10
        failure_threshold     = 3
      }
    }

    scaling {
      min_instance_count = var.environment == "production" ? 1 : 0
      max_instance_count = var.environment == "production" ? 50 : 5
    }

    timeout = "60s"

    service_account = google_service_account.frontend.email
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
    ]
  }
}

# Frontend Service Account
resource "google_service_account" "frontend" {
  account_id   = "barq-frontend-${var.environment}"
  display_name = "BARQ Frontend Service Account (${var.environment})"
  project      = var.project_id
}

# Frontend IAM Policy (allow unauthenticated access)
resource "google_cloud_run_v2_service_iam_member" "frontend_public" {
  name   = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  role   = "roles/run.invoker"
  member = "allUsers"
}

# Outputs
output "backend_url" {
  value = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  value = google_cloud_run_v2_service.frontend.uri
}
