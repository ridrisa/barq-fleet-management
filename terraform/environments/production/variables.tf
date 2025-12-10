# Production Environment Variables
# BARQ Fleet Management

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "barq-fleet"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "me-central1" # Middle East for Saudi Arabia
}

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

variable "vpc_network_id" {
  description = "VPC Network ID for Cloud SQL"
  type        = string
  default     = "projects/barq-fleet/global/networks/default"
}

variable "private_service_cidr_range" {
  description = "Reserved peering range for service networking (CIDR)"
  type        = string
  default     = "10.20.0.0/16"
}

variable "db_user" {
  description = "Database user for application"
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

variable "secret_key" {
  description = "Application secret key stored in Secret Manager"
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
}

variable "alert_email" {
  description = "Email for alert notifications"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  default     = ""
  sensitive   = true
}

variable "enable_read_replica" {
  description = "Enable Cloud SQL read replica for scaling"
  type        = bool
  default     = false
}
