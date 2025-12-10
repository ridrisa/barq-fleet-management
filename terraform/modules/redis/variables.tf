# Redis Module Variables

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

variable "redis_version" {
  description = "Redis version"
  type        = string
  default     = "REDIS_7_0"
}

variable "memory_size_gb" {
  description = "Memory size in GB"
  type        = number
  default     = 1
}

variable "maxmemory_policy" {
  description = "Redis maxmemory eviction policy"
  type        = string
  default     = "volatile-lru"
  validation {
    condition = contains([
      "volatile-lru",
      "allkeys-lru",
      "volatile-lfu",
      "allkeys-lfu",
      "volatile-random",
      "allkeys-random",
      "volatile-ttl",
      "noeviction"
    ], var.maxmemory_policy)
    error_message = "Invalid maxmemory policy."
  }
}

variable "auth_enabled" {
  description = "Enable Redis AUTH"
  type        = bool
  default     = true
}

variable "enable_keyspace_notifications" {
  description = "Enable Redis keyspace notifications"
  type        = bool
  default     = false
}

variable "enable_read_replica" {
  description = "Whether to create a read replica (production only)"
  type        = bool
  default     = false
}

variable "replica_region" {
  description = "Region for the read replica (defaults to same region)"
  type        = string
  default     = ""
}

variable "replica_memory_size_gb" {
  description = "Memory size in GB for read replica"
  type        = number
  default     = 1
}
