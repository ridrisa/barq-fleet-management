# Variables for Monitoring Module

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

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
  description = "Slack channel name for notifications"
  type        = string
  default     = "#alerts"
}

variable "production_domain" {
  description = "Production domain for uptime checks"
  type        = string
  default     = "api.barq-fleet.com"
}

variable "staging_domain" {
  description = "Staging domain for uptime checks"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
}
