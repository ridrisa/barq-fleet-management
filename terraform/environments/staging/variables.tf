# Staging Environment Variables

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "barq-fleet"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "artifact_registry" {
  description = "Artifact Registry URL"
  type        = string
  default     = "us-central1-docker.pkg.dev"
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
  default     = "10.10.0.0/16"
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

variable "alert_email" {
  description = "Email for alert notifications"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook URL (optional)"
  type        = string
  default     = ""
  sensitive   = true
}
