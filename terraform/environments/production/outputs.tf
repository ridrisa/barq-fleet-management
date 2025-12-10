# Production Environment Outputs
# BARQ Fleet Management - Production Infrastructure Outputs

# =============================================================================
# Cloud Run Service URLs
# =============================================================================
output "api_service_url" {
  description = "URL of the production API Cloud Run service"
  value       = google_cloud_run_service.barq_api_production.status[0].url
}

output "web_service_url" {
  description = "URL of the production Web Cloud Run service"
  value       = google_cloud_run_service.barq_web_production.status[0].url
}

# =============================================================================
# Database Outputs
# =============================================================================
output "database_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.production.name
}

output "database_connection_name" {
  description = "Cloud SQL connection name for Cloud Run"
  value       = google_sql_database_instance.production.connection_name
}

output "database_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.production.private_ip_address
  sensitive   = true
}

# =============================================================================
# Service Account Outputs
# =============================================================================
output "api_service_account_email" {
  description = "API service account email"
  value       = google_service_account.barq_api.email
}

output "web_service_account_email" {
  description = "Web service account email"
  value       = google_service_account.barq_web.email
}

# =============================================================================
# VPC Connector
# =============================================================================
output "vpc_connector_id" {
  description = "VPC Access Connector ID"
  value       = google_vpc_access_connector.serverless.id
}

output "vpc_connector_name" {
  description = "VPC Access Connector name"
  value       = google_vpc_access_connector.serverless.name
}

# =============================================================================
# Secret Manager Resources
# =============================================================================
output "secret_database_url_id" {
  description = "Secret Manager ID for database URL"
  value       = google_secret_manager_secret.production_database_url.secret_id
}

output "secret_secret_key_id" {
  description = "Secret Manager ID for secret key"
  value       = google_secret_manager_secret.production_secret_key.secret_id
}

output "secret_google_client_id" {
  description = "Secret Manager ID for Google Client ID"
  value       = google_secret_manager_secret.google_client_id.secret_id
}

output "secret_sentry_dsn_id" {
  description = "Secret Manager ID for Sentry DSN"
  value       = google_secret_manager_secret.sentry_dsn.secret_id
}

# =============================================================================
# Cloud Armor
# =============================================================================
output "security_policy_id" {
  description = "Cloud Armor security policy ID"
  value       = google_compute_security_policy.barq_api_policy.id
}

output "security_policy_self_link" {
  description = "Cloud Armor security policy self link"
  value       = google_compute_security_policy.barq_api_policy.self_link
}

# =============================================================================
# Summary Output
# =============================================================================
output "production_summary" {
  description = "Summary of production deployment"
  value = {
    environment       = "production"
    region            = var.region
    api_url           = google_cloud_run_service.barq_api_production.status[0].url
    web_url           = google_cloud_run_service.barq_web_production.status[0].url
    database_instance = google_sql_database_instance.production.name
    api_min_instances = 2
    api_max_instances = 50
    web_min_instances = 2
    web_max_instances = 20
  }
}
