# Database Module Variables

variable "project_id" {
  description = "GCP Project ID"
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

variable "vpc_network_id" {
  description = "The ID of the VPC network"
  type        = string
}

variable "private_vpc_connection" {
  description = "The private VPC connection dependency"
  type        = string
}

variable "database_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "POSTGRES_15"
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-custom-2-4096" # 2 vCPU, 4GB RAM
}

variable "replica_tier" {
  description = "Cloud SQL read replica tier"
  type        = string
  default     = "db-custom-1-3840" # 1 vCPU, 3.75GB RAM
}

variable "disk_size" {
  description = "Initial disk size in GB"
  type        = number
  default     = 20
}

variable "database_name" {
  description = "Name of the database to create"
  type        = string
  default     = "barq"
}

variable "database_user" {
  description = "Database user name"
  type        = string
  default     = "barq_app"
}

variable "database_password" {
  description = "Database user password"
  type        = string
  sensitive   = true
}

variable "enable_read_replica" {
  description = "Whether to create a read replica (production only)"
  type        = bool
  default     = false
}
