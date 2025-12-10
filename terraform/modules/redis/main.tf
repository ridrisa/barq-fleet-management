# Redis Module - Memorystore Redis Instance
# This module creates Memorystore Redis instances for the BARQ Fleet Management platform

# -----------------------------------------------------------------------------
# Memorystore Redis Instance
# -----------------------------------------------------------------------------
resource "google_redis_instance" "main" {
  name               = "barq-${var.environment}-redis"
  project            = var.project_id
  region             = var.region
  display_name       = "BARQ Fleet Redis (${var.environment})"
  tier               = var.environment == "production" ? "STANDARD_HA" : "BASIC"
  memory_size_gb     = var.memory_size_gb
  redis_version      = var.redis_version
  authorized_network = var.vpc_network_id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  # Persistence Configuration (for Standard tier)
  dynamic "persistence_config" {
    for_each = var.environment == "production" ? [1] : []
    content {
      persistence_mode    = "RDB"
      rdb_snapshot_period = "TWELVE_HOURS"
    }
  }

  # Maintenance Policy
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  # Redis Configuration
  redis_configs = {
    maxmemory-policy = var.maxmemory_policy
    notify-keyspace-events = var.enable_keyspace_notifications ? "Ex" : ""
  }

  # Authentication
  auth_enabled = var.auth_enabled

  # Transit Encryption (for Standard tier)
  transit_encryption_mode = var.environment == "production" ? "SERVER_AUTHENTICATION" : "DISABLED"

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    project     = "barq-fleet"
  }

  lifecycle {
    prevent_destroy = false
  }
}

# -----------------------------------------------------------------------------
# Read Replica (Production Only with Standard HA tier)
# -----------------------------------------------------------------------------
resource "google_redis_instance" "read_replica" {
  count = var.environment == "production" && var.enable_read_replica ? 1 : 0

  name               = "barq-${var.environment}-redis-replica"
  project            = var.project_id
  region             = var.replica_region != "" ? var.replica_region : var.region
  display_name       = "BARQ Fleet Redis Replica (${var.environment})"
  tier               = "BASIC" # Read replicas are typically basic tier
  memory_size_gb     = var.replica_memory_size_gb
  redis_version      = var.redis_version
  authorized_network = var.vpc_network_id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_configs = {
    maxmemory-policy = var.maxmemory_policy
  }

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    project     = "barq-fleet"
    role        = "replica"
  }

  lifecycle {
    prevent_destroy = false
  }
}
