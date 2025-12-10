# Production Environment Configuration
# BARQ Fleet Management - Production Infrastructure

terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
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

provider "google-beta" {
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
    "logging.googleapis.com",
    "cloudkms.googleapis.com",
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Service Account for Cloud Run Backend
resource "google_service_account" "barq_api" {
  account_id   = "barq-api-production"
  display_name = "BARQ API Production Service Account"
  description  = "Service account for BARQ API production environment"
}

# Service Account for Cloud Run Frontend
resource "google_service_account" "barq_web" {
  account_id   = "barq-web-production"
  display_name = "BARQ Web Production Service Account"
  description  = "Service account for BARQ Web production environment"
}

# Reserved range for private service access (required for VPC peering)
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

# Cloud SQL Database (Production - High Availability)
resource "google_sql_database_instance" "production" {
  name             = "barq-production-db"
  database_version = "POSTGRES_16"
  region           = var.region

  settings {
    tier              = var.db_tier
    availability_type = "REGIONAL"  # High availability for production
    disk_size         = var.db_disk_size
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
      day          = 7  # Sunday
      hour         = 3  # 3 AM
      update_track = "stable"
    }

    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }
  }

  deletion_protection = true  # Prevent accidental deletion in production
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

# VPC Access Connector for Serverless
resource "google_vpc_access_connector" "serverless" {
  name           = "barq-production-connector"
  region         = var.region
  network        = var.vpc_network_id
  min_throughput = 300
  max_throughput = 1000
  depends_on     = [google_project_service.services]
}

# Allow Cloud Run SA to use the VPC connector
resource "google_project_iam_member" "vpc_connector_user_api" {
  project = var.project_id
  role    = "roles/vpcaccess.user"
  member  = "serviceAccount:${google_service_account.barq_api.email}"
}

# =============================================================================
# Secret Manager - Production Secrets
# =============================================================================

# Database URL Secret
resource "google_secret_manager_secret" "production_database_url" {
  secret_id = "barq-database-url-prod"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "production_database_url_version" {
  secret      = google_secret_manager_secret.production_database_url.id
  secret_data = var.database_url
}

# Secret Key
resource "google_secret_manager_secret" "production_secret_key" {
  secret_id = "barq-secret-key-prod"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "production_secret_key_version" {
  secret      = google_secret_manager_secret.production_secret_key.id
  secret_data = var.secret_key
}

# Google OAuth Client ID
resource "google_secret_manager_secret" "google_client_id" {
  secret_id = "barq-google-client-id"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_client_id_version" {
  secret      = google_secret_manager_secret.google_client_id.id
  secret_data = var.google_client_id
}

# Google OAuth Client Secret
resource "google_secret_manager_secret" "google_client_secret" {
  secret_id = "barq-google-client-secret"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "google_client_secret_version" {
  secret      = google_secret_manager_secret.google_client_secret.id
  secret_data = var.google_client_secret
}

# Sentry DSN
resource "google_secret_manager_secret" "sentry_dsn" {
  secret_id = "barq-sentry-dsn-prod"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "sentry_dsn_version" {
  secret      = google_secret_manager_secret.sentry_dsn.id
  secret_data = var.sentry_dsn
}

# Redis Auth String (if using Memorystore)
resource "google_secret_manager_secret" "redis_auth" {
  secret_id = "barq-redis-auth-prod"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "redis_auth_version" {
  secret      = google_secret_manager_secret.redis_auth.id
  secret_data = var.redis_auth_string
}

# Secret Manager IAM - Allow API service account to access secrets
resource "google_secret_manager_secret_iam_member" "database_url_access" {
  secret_id = google_secret_manager_secret.production_database_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

resource "google_secret_manager_secret_iam_member" "secret_key_access" {
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

resource "google_secret_manager_secret_iam_member" "redis_auth_access" {
  secret_id = google_secret_manager_secret.redis_auth.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.barq_api.email}"
}

# =============================================================================
# Cloud Run - Backend API Service (Production)
# =============================================================================
resource "google_cloud_run_service" "barq_api_production" {
  name     = "barq-api-production"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = "2"   # Production: minimum 2 instances
        "autoscaling.knative.dev/maxScale"         = "50"  # Production: maximum 50 instances
        "run.googleapis.com/startup-cpu-boost"     = "true"
        "run.googleapis.com/execution-environment" = "gen2"
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.serverless.id
        "run.googleapis.com/vpc-access-egress"     = "all-traffic"
        "run.googleapis.com/cpu-throttling"        = "false"  # Always-on CPU for production
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
            cpu    = "4000m"  # 4 vCPU for production
            memory = "4Gi"
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
          name  = "LOG_LEVEL"
          value = "INFO"
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
          name  = "BACKEND_CORS_ORIGINS"
          value = var.cors_origins
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
          failure_threshold     = 5
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
    google_secret_manager_secret_version.google_client_id_version,
    google_secret_manager_secret_version.sentry_dsn_version,
    google_vpc_access_connector.serverless,
    google_project_iam_member.vpc_connector_user_api,
  ]

  lifecycle {
    ignore_changes = [
      template[0].spec[0].containers[0].image,
    ]
  }
}

# =============================================================================
# Cloud Run - Frontend Web Service (Production)
# =============================================================================
resource "google_cloud_run_service" "barq_web_production" {
  name     = "barq-web-production"
  location = var.region

  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = "2"   # Production: minimum 2 instances
        "autoscaling.knative.dev/maxScale"         = "20"  # Production: maximum 20 instances
        "run.googleapis.com/startup-cpu-boost"     = "true"
        "run.googleapis.com/execution-environment" = "gen2"
      }
    }

    spec {
      service_account_name  = google_service_account.barq_web.email
      container_concurrency = 200
      timeout_seconds       = 60

      containers {
        image = "${var.artifact_registry}/${var.project_id}/${var.repository_name}/barq-web:production"

        resources {
          limits = {
            cpu    = "2000m"  # 2 vCPU for frontend
            memory = "1Gi"
          }
        }

        ports {
          name           = "http1"
          container_port = 80
        }

        env {
          name  = "VITE_API_URL"
          value = var.api_url
        }

        env {
          name  = "VITE_ENVIRONMENT"
          value = "production"
        }

        env {
          name  = "VITE_GOOGLE_CLIENT_ID"
          value = var.google_client_id
        }

        # Health check probes
        startup_probe {
          http_get {
            path = "/health"
            port = 80
          }
          initial_delay_seconds = 5
          timeout_seconds       = 3
          period_seconds        = 5
          failure_threshold     = 3
        }

        liveness_probe {
          http_get {
            path = "/health"
            port = 80
          }
          initial_delay_seconds = 10
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
  depends_on = [
    google_service_account.barq_web,
  ]

  lifecycle {
    ignore_changes = [
      template[0].spec[0].containers[0].image,
    ]
  }
}

# =============================================================================
# IAM - Public Access for Cloud Run Services
# =============================================================================
resource "google_cloud_run_service_iam_member" "api_public_access" {
  service  = google_cloud_run_service.barq_api_production.name
  location = google_cloud_run_service.barq_api_production.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "web_public_access" {
  service  = google_cloud_run_service.barq_web_production.name
  location = google_cloud_run_service.barq_web_production.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# =============================================================================
# Monitoring Module
# =============================================================================
module "monitoring" {
  source = "../../modules/monitoring"

  project_id         = var.project_id
  environment        = "production"
  alert_email        = var.alert_email
  slack_webhook_url  = var.slack_webhook_url
  slack_channel_name = var.slack_channel_name
  staging_domain     = var.staging_api_url
  production_domain  = google_cloud_run_service.barq_api_production.status[0].url
}

# =============================================================================
# Cloud Armor - DDoS Protection (Optional, requires Load Balancer)
# =============================================================================
resource "google_compute_security_policy" "barq_api_policy" {
  name        = "barq-api-production-policy"
  description = "Security policy for BARQ API production"

  # Default rule - allow all traffic
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default rule"
  }

  # Rate limiting rule
  rule {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 1000
        interval_sec = 60
      }
      ban_duration_sec = 300
    }
    description = "Rate limit - 1000 requests per minute per IP"
  }
}
