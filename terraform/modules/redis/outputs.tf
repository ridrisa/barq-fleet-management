# Redis Module Outputs

output "instance_id" {
  description = "The ID of the Redis instance"
  value       = google_redis_instance.main.id
}

output "instance_name" {
  description = "The name of the Redis instance"
  value       = google_redis_instance.main.name
}

output "host" {
  description = "The IP address of the Redis instance"
  value       = google_redis_instance.main.host
}

output "port" {
  description = "The port number of the Redis instance"
  value       = google_redis_instance.main.port
}

output "read_endpoint" {
  description = "The read endpoint for the Redis instance"
  value       = google_redis_instance.main.read_endpoint
}

output "auth_string" {
  description = "The AUTH string for the Redis instance"
  value       = google_redis_instance.main.auth_string
  sensitive   = true
}

output "current_location_id" {
  description = "The current zone where the Redis endpoint is placed"
  value       = google_redis_instance.main.current_location_id
}

output "server_ca_certs" {
  description = "List of server CA certificates for TLS"
  value       = google_redis_instance.main.server_ca_certs
  sensitive   = true
}

output "replica_host" {
  description = "The IP address of the Redis replica (if enabled)"
  value       = var.environment == "production" && var.enable_read_replica ? google_redis_instance.read_replica[0].host : null
}

output "replica_port" {
  description = "The port number of the Redis replica (if enabled)"
  value       = var.environment == "production" && var.enable_read_replica ? google_redis_instance.read_replica[0].port : null
}

output "connection_string" {
  description = "Redis connection string (redis://host:port)"
  value       = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}"
}
