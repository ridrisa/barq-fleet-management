# Database Module - Cloud SQL PostgreSQL Instance
# This module creates Cloud SQL PostgreSQL instances for the BARQ Fleet Management platform

# -----------------------------------------------------------------------------
# Cloud SQL Instance
# -----------------------------------------------------------------------------
resource "google_sql_database_instance" "main" {
  name                = "barq-${var.environment}-db"
  project             = var.project_id
  region              = var.region
  database_version    = var.database_version
  deletion_protection = var.environment == "production" ? true : false

  settings {
    tier              = var.db_tier
    availability_type = var.environment == "production" ? "REGIONAL" : "ZONAL"
    disk_size         = var.disk_size
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    # IP Configuration - private only for security
    ip_configuration {
      ipv4_enabled                                  = false
      private_network                               = var.vpc_network_id
      enable_private_path_for_google_cloud_services = true
    }

    # Backup Configuration
    backup_configuration {
      enabled                        = true
      start_time                     = "02:00" # 2 AM UTC
      location                       = var.region
      point_in_time_recovery_enabled = var.environment == "production" ? true : false
      transaction_log_retention_days = var.environment == "production" ? 7 : 3

      backup_retention_settings {
        retained_backups = var.environment == "production" ? 30 : 7
        retention_unit   = "COUNT"
      }
    }

    # Maintenance Window - Sunday at 3 AM UTC
    maintenance_window {
      day          = 7 # Sunday
      hour         = 3
      update_track = "stable"
    }

    # Insights Configuration
    insights_config {
      query_insights_enabled  = true
      query_plans_per_minute  = 5
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = false
    }

    # Database Flags
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

    database_flags {
      name  = "log_temp_files"
      value = "0"
    }

    database_flags {
      name  = "max_connections"
      value = var.environment == "production" ? "200" : "100"
    }

    user_labels = {
      environment = var.environment
      managed-by  = "terraform"
      project     = "barq-fleet"
    }
  }

  depends_on = [var.private_vpc_connection]

  lifecycle {
    prevent_destroy = false
  }
}

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
resource "google_sql_database" "main" {
  name     = var.database_name
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  charset  = "UTF8"
}

# -----------------------------------------------------------------------------
# Database User
# -----------------------------------------------------------------------------
resource "google_sql_user" "main" {
  name     = var.database_user
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  password = var.database_password

  deletion_policy = "ABANDON"
}

# -----------------------------------------------------------------------------
# Read Replica (Production Only)
# -----------------------------------------------------------------------------
resource "google_sql_database_instance" "read_replica" {
  count = var.environment == "production" && var.enable_read_replica ? 1 : 0

  name                 = "barq-${var.environment}-db-replica"
  project              = var.project_id
  region               = var.region
  database_version     = var.database_version
  master_instance_name = google_sql_database_instance.main.name

  replica_configuration {
    failover_target = false
  }

  settings {
    tier            = var.replica_tier
    disk_size       = var.disk_size
    disk_type       = "PD_SSD"
    disk_autoresize = true

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_network_id
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }

    user_labels = {
      environment = var.environment
      managed-by  = "terraform"
      project     = "barq-fleet"
      role        = "replica"
    }
  }

  lifecycle {
    prevent_destroy = false
  }
}
