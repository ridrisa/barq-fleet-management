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

resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "monitoring.googleapis.com",
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Service Account for Cloud Run
resource "google_service_account" "barq_api" {
  account_id   = "barq-api-staging"
  display_name = "BARQ API Staging Service Account"
  description  = "Service account for BARQ API staging environment"
}

# Reserved range for private service access (required for peering)
resource "google_compute_global_address" "private_service_range" {
  name          = "barq-staging-psa-range"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  address       = split("/", var.private_service_cidr_range)[0]
  prefix_length = tonumber(split("/", var.private_service_cidr_range)[1])
  network       = var.vpc_network_id
}

# Service Networking for private IP Cloud SQL
resource "google_service_networking_connection" "default" {
  network                 = var.vpc_network_id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_range.name]
  depends_on              = [google_project_service.services, google_compute_global_address.private_service_range]
}

# Cloud SQL Database (private IP)
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
      enabled                        = true
      start_time                     = "03:00"
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
  depends_on          = [google_service_networking_connection.default]
}

resource "google_sql_database" "staging" {
  name     = "barq_staging"
  instance = google_sql_database_instance.staging.name
}

resource "google_sql_user" "staging_app" {
  instance = google_sql_database_instance.staging.name
  name     = var.db_user
  password = var.db_password
}

resource "google_vpc_access_connector" "serverless" {
  name           = "barq-staging-connector"
  region         = var.region
  network        = var.vpc_network_id
  min_throughput = 200
  max_throughput = 300
  depends_on     = [google_project_service.services]
}

# Allow Cloud Run SA to use the VPC connector
resource "google_project_iam_member" "vpc_connector_user" {
  project = var.project_id
  role    = "roles/vpcaccess.user"
  member  = "serviceAccount:${google_service_account.barq_api.email}"
}

# Secret Manager - Database URL
resource "google_secret_manager_secret" "staging_database_url" {
  secret_id = "staging-database-url"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "staging_database_url_version" {
  secret      = google_secret_manager_secret.staging_database_url.id
  secret_data = var.database_url
}

# Secret Manager - Secret Key
resource "google_secret_manager_secret" "staging_secret_key" {
  secret_id = "staging-secret-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "staging_secret_key_version" {
  secret      = google_secret_manager_secret.staging_secret_key.id
  secret_data = var.secret_key
}

resource "google_secret_manager_secret_iam_member" "staging_database_url_access" {
  secret_id = google_secret_manager_secret.staging_database_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

resource "google_secret_manager_secret_iam_member" "staging_secret_key_access" {
  secret_id = google_secret_manager_secret.staging_secret_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

# Cloud Run Service - Staging
resource "google_cloud_run_service" "barq_api_staging" {
  name     = "barq-api-staging"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = "1"
        "autoscaling.knative.dev/maxScale"         = "10"
        "run.googleapis.com/startup-cpu-boost"     = "true"
        "run.googleapis.com/execution-environment" = "gen2"
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.serverless.id
        "run.googleapis.com/vpc-access-egress"     = "all-traffic"
      }
    }

    spec {
      service_account_name  = google_service_account.barq_api.email
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

        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.staging_database_url.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.staging_secret_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "DB_CONNECTION_NAME"
          value = google_sql_database_instance.staging.connection_name
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

      vpc_access {
        connector = google_vpc_access_connector.serverless.id
        egress    = "ALL_TRAFFIC"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
  depends_on = [
    google_service_account.barq_api,
    google_secret_manager_secret_version.staging_database_url_version,
    google_secret_manager_secret_version.staging_secret_key_version,
    google_vpc_access_connector.serverless,
    google_project_iam_member.vpc_connector_user,
  ]
}

# IAM Policy - Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.barq_api_staging.name
  location = google_cloud_run_service.barq_api_staging.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"

  project_id         = var.project_id
  environment        = "staging"
  alert_email        = var.alert_email
  slack_webhook_url  = var.slack_webhook_url
  slack_channel_name = "#staging-alerts"
  staging_domain     = google_cloud_run_service.barq_api_staging.status[0].url
  production_domain  = "api.barq-fleet.com"
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
