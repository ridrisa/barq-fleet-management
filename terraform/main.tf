# BARQ Fleet Management - Main Terraform Configuration
# Provider: Google Cloud Platform
# Infrastructure: Cloud Run, Cloud SQL, Redis, Monitoring

terraform {
  required_version = ">= 1.5"

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
    prefix = "terraform/state"
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (staging/production)"
  type        = string
  default     = "production"
}

variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-custom-2-7680"
}

# Providers
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Data sources
data "google_project" "project" {
  project_id = var.project_id
}

# Modules
module "network" {
  source = "./modules/network"

  project_id  = var.project_id
  region      = var.region
  environment = var.environment
}

module "database" {
  source = "./modules/database"

  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  vpc_id      = module.network.vpc_id
}

module "redis" {
  source = "./modules/redis"

  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  vpc_id      = module.network.vpc_id
}

module "cloud_run" {
  source = "./modules/cloud_run"

  project_id          = var.project_id
  region              = var.region
  environment         = var.environment
  vpc_connector_id    = module.network.vpc_connector_id
  database_connection = module.database.connection_name
  redis_host          = module.redis.host
  redis_port          = module.redis.port
}

module "monitoring" {
  source = "./modules/monitoring"

  project_id  = var.project_id
  environment = var.environment
}

module "artifact_registry" {
  source = "./modules/artifact_registry"

  project_id  = var.project_id
  region      = var.region
  environment = var.environment
}

# Outputs
output "backend_url" {
  description = "Backend Cloud Run URL"
  value       = module.cloud_run.backend_url
}

output "frontend_url" {
  description = "Frontend Cloud Run URL"
  value       = module.cloud_run.frontend_url
}

output "database_connection" {
  description = "Database connection name"
  value       = module.database.connection_name
  sensitive   = true
}

output "redis_host" {
  description = "Redis host"
  value       = module.redis.host
}

output "artifact_registry_url" {
  description = "Artifact Registry URL"
  value       = module.artifact_registry.repository_url
}
