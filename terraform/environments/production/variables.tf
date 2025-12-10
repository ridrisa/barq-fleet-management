# Production Environment Variables
# BARQ Fleet Management - Production Configuration

# =============================================================================
# Project Configuration
# =============================================================================
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "barq-fleet"
}

variable "region" {
  description = "GCP Region for deployment"
  type        = string
  default     = "me-central1"  # Middle East (Doha) - closest to Saudi Arabia
}

# =============================================================================
# Artifact Registry
# =============================================================================
variable "artifact_registry" {
  description = "Artifact Registry URL"
  type        = string
  default     = "me-central1-docker.pkg.dev"
}

variable "repository_name" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "barq-artifacts"
}

# =============================================================================
# Network Configuration
# =============================================================================
variable "vpc_network_id" {
  description = "VPC Network ID for Cloud SQL and VPC connector"
  type        = string
  default     = "projects/barq-fleet/global/networks/default"
}

variable "private_service_cidr_range" {
  description = "Reserved peering range for service networking (CIDR)"
  type        = string
  default     = "10.20.0.0/16"  # Different from staging (10.10.0.0/16)
}

# =============================================================================
# Database Configuration
# =============================================================================
variable "db_tier" {
  description = "Cloud SQL instance tier for production"
  type        = string
  default     = "db-custom-4-15360"  # 4 vCPU, 15GB RAM for production
}

variable "db_disk_size" {
  description = "Initial disk size for Cloud SQL in GB"
  type        = number
  default     = 50
}

variable "db_user" {
  description = "Database username for application"
  type        = string
}

variable "db_password" {
  description = "Database password for application"
  type        = string
  sensitive   = true
}

variable "database_url" {
  description = "Full database connection URL stored in Secret Manager"
  type        = string
  sensitive   = true
}

# =============================================================================
# Application Secrets
# =============================================================================
variable "secret_key" {
  description = "Application secret key for JWT signing"
  type        = string
  sensitive   = true
}

variable "google_client_id" {
  description = "Google OAuth Client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth Client Secret"
  type        = string
  sensitive   = true
}

variable "sentry_dsn" {
  description = "Sentry DSN for error tracking"
  type        = string
  sensitive   = true
  default     = ""
}

variable "redis_auth_string" {
  description = "Redis AUTH string for Memorystore"
  type        = string
  sensitive   = true
  default     = ""
}

# =============================================================================
# CORS Configuration
# =============================================================================
variable "cors_origins" {
  description = "Allowed CORS origins (comma-separated)"
  type        = string
  default     = "https://barq-fleet.com,https://www.barq-fleet.com,https://app.barq-fleet.com"
}

# =============================================================================
# URLs
# =============================================================================
variable "api_url" {
  description = "Production API URL for frontend configuration"
  type        = string
  default     = "https://api.barq-fleet.com"
}

variable "staging_api_url" {
  description = "Staging API URL for monitoring comparison"
  type        = string
  default     = "https://barq-api-staging-frydalfroq-ww.a.run.app"
}

# =============================================================================
# Monitoring & Alerting
# =============================================================================
variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications (optional)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "slack_channel_name" {
  description = "Slack channel name for production alerts"
  type        = string
  default     = "#production-alerts"
}

# =============================================================================
# Feature Flags
# =============================================================================
variable "enable_cloud_armor" {
  description = "Enable Cloud Armor DDoS protection"
  type        = bool
  default     = true
}

variable "enable_cdn" {
  description = "Enable Cloud CDN for frontend"
  type        = bool
  default     = false
}
