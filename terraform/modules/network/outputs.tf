# Network Module Outputs

output "vpc_id" {
  description = "The ID of the VPC network"
  value       = google_compute_network.main.id
}

output "vpc_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.main.name
}

output "vpc_self_link" {
  description = "The self link of the VPC network"
  value       = google_compute_network.main.self_link
}

output "app_subnet_id" {
  description = "The ID of the application subnet"
  value       = google_compute_subnetwork.app.id
}

output "app_subnet_name" {
  description = "The name of the application subnet"
  value       = google_compute_subnetwork.app.name
}

output "app_subnet_cidr" {
  description = "The CIDR range of the application subnet"
  value       = google_compute_subnetwork.app.ip_cidr_range
}

output "db_subnet_id" {
  description = "The ID of the database subnet"
  value       = google_compute_subnetwork.db.id
}

output "db_subnet_name" {
  description = "The name of the database subnet"
  value       = google_compute_subnetwork.db.name
}

output "db_subnet_cidr" {
  description = "The CIDR range of the database subnet"
  value       = google_compute_subnetwork.db.ip_cidr_range
}

output "redis_subnet_id" {
  description = "The ID of the Redis subnet"
  value       = google_compute_subnetwork.redis.id
}

output "redis_subnet_name" {
  description = "The name of the Redis subnet"
  value       = google_compute_subnetwork.redis.name
}

output "redis_subnet_cidr" {
  description = "The CIDR range of the Redis subnet"
  value       = google_compute_subnetwork.redis.ip_cidr_range
}

output "vpc_connector_id" {
  description = "The ID of the VPC Access Connector"
  value       = google_vpc_access_connector.main.id
}

output "vpc_connector_name" {
  description = "The name of the VPC Access Connector"
  value       = google_vpc_access_connector.main.name
}

output "private_vpc_connection" {
  description = "The private VPC connection for service networking"
  value       = google_service_networking_connection.private_vpc_connection.id
}

output "router_id" {
  description = "The ID of the Cloud Router"
  value       = google_compute_router.main.id
}

output "nat_id" {
  description = "The ID of the Cloud NAT"
  value       = google_compute_router_nat.main.id
}
