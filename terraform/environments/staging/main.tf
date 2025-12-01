# Staging Environment Configuration

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "barq-fleet-terraform-state"
    prefix = "staging"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Run Service - Staging
resource "google_cloud_run_service" "barq_api_staging" {
  name     = "barq-api-staging"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"      = "1"
        "autoscaling.knative.dev/maxScale"      = "10"
        "run.googleapis.com/startup-cpu-boost"  = "true"
        "run.googleapis.com/execution-environment" = "gen2"
      }
    }

    spec {
      service_account_name = google_service_account.barq_api.email
      container_concurrency = 80
      timeout_seconds       = 300

      containers {
        image = "${var.artifact_registry}/${var.project_id}/${var.repository_name}/barq-api:staging"

        resources {
          limits = {
            cpu    = "2000m"  # 2 vCPU
            memory = "2Gi"
          }
        }

        ports {
          name           = "http1"
          container_port = 8000
        }

        env {
          name  = "ENVIRONMENT"
          value = "staging"
        }

        env {
          name  = "PORT"
          value = "8000"
        }

        env {
          name  = "PYTHON_ENV"
          value = "production"
        }

        # Database connection from Secret Manager
        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.staging_database_url.secret_id
              key  = "latest"
            }
          }
        }

        # Secret key from Secret Manager
        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.staging_secret_key.secret_id
              key  = "latest"
            }
          }
        }

        # Health check probes
        startup_probe {
          http_get {
            path = "/health/live"
            port = 8000
          }
          initial_delay_seconds = 10
          timeout_seconds       = 3
          period_seconds        = 10
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health/live"
            port = 8000
          }
          initial_delay_seconds = 30
          timeout_seconds       = 3
          period_seconds        = 30
          failure_threshold     = 3
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

# Service Account for Cloud Run
resource "google_service_account" "barq_api" {
  account_id   = "barq-api-staging"
  display_name = "BARQ API Staging Service Account"
  description  = "Service account for BARQ API staging environment"
}

# IAM Policy - Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.barq_api_staging.name
  location = google_cloud_run_service.barq_api_staging.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Secret Manager - Database URL
resource "google_secret_manager_secret" "staging_database_url" {
  secret_id = "staging-database-url"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_iam_member" "staging_database_url_access" {
  secret_id = google_secret_manager_secret.staging_database_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

# Secret Manager - Secret Key
resource "google_secret_manager_secret" "staging_secret_key" {
  secret_id = "staging-secret-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_iam_member" "staging_secret_key_access" {
  secret_id = google_secret_manager_secret.staging_secret_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

# Cloud SQL Database (if needed)
resource "google_sql_database_instance" "staging" {
  name             = "barq-staging-db"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = "db-f1-micro"  # Small instance for staging
    availability_type = "ZONAL"
    disk_size         = 10
    disk_type         = "PD_SSD"

    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 3
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_network_id
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }

  deletion_protection = false  # Allow deletion in staging
}

resource "google_sql_database" "staging" {
  name     = "barq_staging"
  instance = google_sql_database_instance.staging.name
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"

  project_id        = var.project_id
  environment       = "staging"
  alert_email       = var.alert_email
  slack_webhook_url = var.slack_webhook_url
  slack_channel_name = "#staging-alerts"
  staging_domain    = google_cloud_run_service.barq_api_staging.status[0].url
  production_domain = "api.barq-fleet.com"
}

# Outputs
output "service_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_service.barq_api_staging.status[0].url
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.staging.connection_name
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.barq_api.email
}
