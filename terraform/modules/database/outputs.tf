# Database Module Outputs

output "instance_name" {
  description = "The name of the Cloud SQL instance"
  value       = google_sql_database_instance.main.name
}

output "instance_connection_name" {
  description = "The connection name of the instance (project:region:instance)"
  value       = google_sql_database_instance.main.connection_name
}

output "instance_self_link" {
  description = "The self link of the Cloud SQL instance"
  value       = google_sql_database_instance.main.self_link
}

output "instance_ip_address" {
  description = "The private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.main.private_ip_address
}

output "database_name" {
  description = "The name of the database"
  value       = google_sql_database.main.name
}

output "database_user" {
  description = "The database user name"
  value       = google_sql_user.main.name
  sensitive   = true
}

output "replica_instance_name" {
  description = "The name of the read replica instance (if enabled)"
  value       = var.environment == "production" && var.enable_read_replica ? google_sql_database_instance.read_replica[0].name : null
}

output "replica_connection_name" {
  description = "The connection name of the read replica (if enabled)"
  value       = var.environment == "production" && var.enable_read_replica ? google_sql_database_instance.read_replica[0].connection_name : null
}

output "replica_ip_address" {
  description = "The private IP address of the read replica (if enabled)"
  value       = var.environment == "production" && var.enable_read_replica ? google_sql_database_instance.read_replica[0].private_ip_address : null
}
