# Production Environment Configuration
# BARQ Fleet Management - Production Infrastructure

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
    prefix = "production"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
    "compute.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "monitoring.googleapis.com",
    "cloudkms.googleapis.com",
    "redis.googleapis.com",
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Service Account for Cloud Run
resource "google_service_account" "barq_api" {
  account_id   = "barq-api-production"
  display_name = "BARQ API Production Service Account"
  description  = "Service account for BARQ API production environment"
}

# Reserved range for private service access (required for peering)
resource "google_compute_global_address" "private_service_range" {
  name          = "barq-production-psa-range"
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

# Cloud SQL Database (private IP) - Production Grade
resource "google_sql_database_instance" "production" {
  name             = "barq-production-db"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = "db-custom-4-16384" # 4 vCPU, 16GB RAM for production
    availability_type = "REGIONAL"          # High availability with automatic failover
    disk_size         = 100
    disk_type         = "PD_SSD"
    disk_autoresize   = true
    disk_autoresize_limit = 500

    backup_configuration {
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_network_id
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "500"
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }

    maintenance_window {
      day          = 7 # Sunday
      hour         = 3 # 3 AM
      update_track = "stable"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 4500
      record_application_tags = true
      record_client_address   = true
    }
  }

  deletion_protection = true # Prevent accidental deletion in production
  depends_on          = [google_service_networking_connection.default]
}

resource "google_sql_database" "production" {
  name     = "barq_production"
  instance = google_sql_database_instance.production.name
}

resource "google_sql_user" "production_app" {
  instance = google_sql_database_instance.production.name
  name     = var.db_user
  password = var.db_password
}

# Read Replica for production (optional, for read scaling)
resource "google_sql_database_instance" "production_replica" {
  count                = var.enable_read_replica ? 1 : 0
  name                 = "barq-production-db-replica"
  master_instance_name = google_sql_database_instance.production.name
  region               = var.region
  database_version     = "POSTGRES_16"

  replica_configuration {
    failover_target = false
  }

  settings {
    tier              = "db-custom-2-8192" # Smaller replica
    availability_type = "ZONAL"
    disk_size         = 100
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_network_id
      require_ssl     = true
    }
  }

  depends_on = [google_sql_database_instance.production]
}

# Redis (Memorystore) for caching and rate limiting
resource "google_redis_instance" "production" {
  name           = "barq-production-redis"
  tier           = "STANDARD_HA" # High availability
  memory_size_gb = 5
  region         = var.region

  authorized_network = var.vpc_network_id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version = "REDIS_7_0"
  display_name  = "BARQ Production Redis"

  redis_configs = {
    maxmemory-policy = "allkeys-lru"
  }

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 4
        minutes = 0
      }
    }
  }

  depends_on = [google_service_networking_connection.default]
}

# VPC Access Connector
resource "google_vpc_access_connector" "serverless" {
  name           = "barq-production-connector"
  region         = var.region
  network        = var.vpc_network_id
  min_throughput = 300
  max_throughput = 1000 # Higher throughput for production
  depends_on     = [google_project_service.services]
}

# Allow Cloud Run SA to use the VPC connector
resource "google_project_iam_member" "vpc_connector_user" {
  project = var.project_id
  role    = "roles/vpcaccess.user"
  member  = "serviceAccount:${google_service_account.barq_api.email}"
}

# Secret Manager - Database URL
resource "google_secret_manager_secret" "production_database_url" {
  secret_id = "production-database-url"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "production_database_url_version" {
  secret      = google_secret_manager_secret.production_database_url.id
  secret_data = var.database_url
}

# Secret Manager - Secret Key
resource "google_secret_manager_secret" "production_secret_key" {
  secret_id = "production-secret-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "production_secret_key_version" {
  secret      = google_secret_manager_secret.production_secret_key.id
  secret_data = var.secret_key
}

# Secret Manager - Google OAuth Client ID
resource "google_secret_manager_secret" "google_client_id" {
  secret_id = "production-google-client-id"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "google_client_id_version" {
  secret      = google_secret_manager_secret.google_client_id.id
  secret_data = var.google_client_id
}

# Secret Manager - Google OAuth Client Secret
resource "google_secret_manager_secret" "google_client_secret" {
  secret_id = "production-google-client-secret"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "google_client_secret_version" {
  secret      = google_secret_manager_secret.google_client_secret.id
  secret_data = var.google_client_secret
}

# Secret Manager - Sentry DSN
resource "google_secret_manager_secret" "sentry_dsn" {
  secret_id = "production-sentry-dsn"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "sentry_dsn_version" {
  secret      = google_secret_manager_secret.sentry_dsn.id
  secret_data = var.sentry_dsn
}

# Grant access to secrets
resource "google_secret_manager_secret_iam_member" "production_database_url_access" {
  secret_id = google_secret_manager_secret.production_database_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

resource "google_secret_manager_secret_iam_member" "production_secret_key_access" {
  secret_id = google_secret_manager_secret.production_secret_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

resource "google_secret_manager_secret_iam_member" "google_client_id_access" {
  secret_id = google_secret_manager_secret.google_client_id.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

resource "google_secret_manager_secret_iam_member" "google_client_secret_access" {
  secret_id = google_secret_manager_secret.google_client_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

resource "google_secret_manager_secret_iam_member" "sentry_dsn_access" {
  secret_id = google_secret_manager_secret.sentry_dsn.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

# Cloud Run Service - Production Backend
resource "google_cloud_run_service" "barq_api_production" {
  name     = "barq-api-production"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = "2"   # Always keep 2 instances running
        "autoscaling.knative.dev/maxScale"         = "50"  # Scale up to 50 instances
        "run.googleapis.com/startup-cpu-boost"     = "true"
        "run.googleapis.com/execution-environment" = "gen2"
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.serverless.id
        "run.googleapis.com/vpc-access-egress"     = "all-traffic"
        "run.googleapis.com/cpu-throttling"        = "false" # Always allocate CPU
      }
    }

    spec {
      service_account_name  = google_service_account.barq_api.email
      container_concurrency = 100
      timeout_seconds       = 300

      containers {
        image = "${var.artifact_registry}/${var.project_id}/${var.repository_name}/barq-api:production"

        resources {
          limits = {
            cpu    = "4000m" # 4 vCPU for production
            memory = "4Gi"   # 4GB RAM for production
          }
        }

        ports {
          name           = "http1"
          container_port = 8000
        }

        env {
          name  = "ENVIRONMENT"
          value = "production"
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
              name = google_secret_manager_secret.production_database_url.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.production_secret_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GOOGLE_CLIENT_ID"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.google_client_id.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GOOGLE_CLIENT_SECRET"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.google_client_secret.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "SENTRY_DSN"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.sentry_dsn.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "DB_CONNECTION_NAME"
          value = google_sql_database_instance.production.connection_name
        }

        env {
          name  = "REDIS_HOST"
          value = google_redis_instance.production.host
        }

        env {
          name  = "REDIS_PORT"
          value = tostring(google_redis_instance.production.port)
        }

        # Health check probes
        startup_probe {
          http_get {
            path = "/health/live"
            port = 8000
          }
          initial_delay_seconds = 10
          timeout_seconds       = 5
          period_seconds        = 10
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health/live"
            port = 8000
          }
          initial_delay_seconds = 30
          timeout_seconds       = 5
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
    google_secret_manager_secret_version.production_database_url_version,
    google_secret_manager_secret_version.production_secret_key_version,
    google_vpc_access_connector.serverless,
    google_project_iam_member.vpc_connector_user,
    google_redis_instance.production,
  ]
}

# Cloud Run Service - Production Frontend
resource "google_cloud_run_service" "barq_web_production" {
  name     = "barq-web-production"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = "1"
        "autoscaling.knative.dev/maxScale"         = "20"
        "run.googleapis.com/startup-cpu-boost"     = "true"
        "run.googleapis.com/execution-environment" = "gen2"
      }
    }

    spec {
      container_concurrency = 200
      timeout_seconds       = 60

      containers {
        image = "${var.artifact_registry}/${var.project_id}/${var.repository_name}/barq-web:production"

        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        ports {
          name           = "http1"
          container_port = 8080
        }

        env {
          name  = "VITE_API_URL"
          value = "https://api.barq-fleet.com/api/v1"
        }

        env {
          name  = "VITE_ENVIRONMENT"
          value = "production"
        }

        startup_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 5
          timeout_seconds       = 3
          period_seconds        = 5
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health"
            port = 8080
          }
          initial_delay_seconds = 15
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

# IAM Policy - Allow unauthenticated access to API
resource "google_cloud_run_service_iam_member" "api_public_access" {
  service  = google_cloud_run_service.barq_api_production.name
  location = google_cloud_run_service.barq_api_production.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# IAM Policy - Allow unauthenticated access to Frontend
resource "google_cloud_run_service_iam_member" "web_public_access" {
  service  = google_cloud_run_service.barq_web_production.name
  location = google_cloud_run_service.barq_web_production.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Monitoring Module
module "monitoring" {
  source = "../../modules/monitoring"

  project_id         = var.project_id
  environment        = "production"
  alert_email        = var.alert_email
  slack_webhook_url  = var.slack_webhook_url
  slack_channel_name = "#production-alerts"
  staging_domain     = "https://barq-api-staging-frydalfroq-ww.a.run.app"
  production_domain  = google_cloud_run_service.barq_api_production.status[0].url
}

# Outputs
output "api_service_url" {
  description = "URL of the Cloud Run API service"
  value       = google_cloud_run_service.barq_api_production.status[0].url
}

output "web_service_url" {
  description = "URL of the Cloud Run Web service"
  value       = google_cloud_run_service.barq_web_production.status[0].url
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.production.connection_name
}

output "database_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.production.private_ip_address
}

output "redis_host" {
  description = "Redis host address"
  value       = google_redis_instance.production.host
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.production.port
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.barq_api.email
}
