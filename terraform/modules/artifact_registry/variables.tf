# Artifact Registry Module Variables

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_number" {
  description = "GCP Project Number"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

variable "create_npm_registry" {
  description = "Whether to create an NPM repository"
  type        = bool
  default     = false
}

variable "create_python_registry" {
  description = "Whether to create a Python repository"
  type        = bool
  default     = false
}

variable "cloud_run_service_accounts" {
  description = "List of Cloud Run service account emails that need read access"
  type        = list(string)
  default     = []
}

variable "github_service_account" {
  description = "GitHub Actions service account email (for CI/CD)"
  type        = string
  default     = ""
}

variable "retention_days" {
  description = "Number of days to retain untagged images"
  type        = number
  default     = 30
}
