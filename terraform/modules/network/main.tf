# Network Module - VPC, Subnets, and VPC Connectors
# This module creates the networking infrastructure for the BARQ Fleet Management platform

# -----------------------------------------------------------------------------
# VPC Network
# -----------------------------------------------------------------------------
resource "google_compute_network" "main" {
  name                            = "barq-${var.environment}-vpc"
  project                         = var.project_id
  auto_create_subnetworks         = false
  routing_mode                    = "REGIONAL"
  delete_default_routes_on_create = false

  description = "VPC network for BARQ Fleet Management (${var.environment})"
}

# -----------------------------------------------------------------------------
# Subnets
# -----------------------------------------------------------------------------

# Application Subnet - for Cloud Run and other services
resource "google_compute_subnetwork" "app" {
  name                     = "barq-${var.environment}-app-subnet"
  project                  = var.project_id
  region                   = var.region
  network                  = google_compute_network.main.id
  ip_cidr_range            = var.app_subnet_cidr
  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }

  description = "Application subnet for Cloud Run services"
}

# Database Subnet - for Cloud SQL
resource "google_compute_subnetwork" "db" {
  name                     = "barq-${var.environment}-db-subnet"
  project                  = var.project_id
  region                   = var.region
  network                  = google_compute_network.main.id
  ip_cidr_range            = var.db_subnet_cidr
  private_ip_google_access = true

  description = "Database subnet for Cloud SQL instances"
}

# Redis Subnet - for Memorystore
resource "google_compute_subnetwork" "redis" {
  name                     = "barq-${var.environment}-redis-subnet"
  project                  = var.project_id
  region                   = var.region
  network                  = google_compute_network.main.id
  ip_cidr_range            = var.redis_subnet_cidr
  private_ip_google_access = true

  description = "Redis subnet for Memorystore instances"
}

# -----------------------------------------------------------------------------
# VPC Serverless Connector - for Cloud Run to access VPC resources
# -----------------------------------------------------------------------------
resource "google_vpc_access_connector" "main" {
  name           = "barq-${var.environment}-connector"
  project        = var.project_id
  region         = var.region
  network        = google_compute_network.main.id
  ip_cidr_range  = var.connector_cidr
  min_throughput = var.environment == "production" ? 300 : 200
  max_throughput = var.environment == "production" ? 1000 : 300

  depends_on = [google_compute_network.main]
}

# -----------------------------------------------------------------------------
# Private Service Connection - for Cloud SQL Private IP
# -----------------------------------------------------------------------------
resource "google_compute_global_address" "private_ip_address" {
  name          = "barq-${var.environment}-private-ip"
  project       = var.project_id
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id

  description = "Private IP range for service networking"
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  depends_on = [google_compute_global_address.private_ip_address]
}

# -----------------------------------------------------------------------------
# Cloud NAT - for outbound internet access from private instances
# -----------------------------------------------------------------------------
resource "google_compute_router" "main" {
  name    = "barq-${var.environment}-router"
  project = var.project_id
  region  = var.region
  network = google_compute_network.main.id

  bgp {
    asn = 64514
  }
}

resource "google_compute_router_nat" "main" {
  name                               = "barq-${var.environment}-nat"
  project                            = var.project_id
  router                             = google_compute_router.main.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# -----------------------------------------------------------------------------
# Firewall Rules
# -----------------------------------------------------------------------------

# Allow internal communication within the VPC
resource "google_compute_firewall" "allow_internal" {
  name    = "barq-${var.environment}-allow-internal"
  project = var.project_id
  network = google_compute_network.main.id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [
    var.app_subnet_cidr,
    var.db_subnet_cidr,
    var.redis_subnet_cidr,
    var.connector_cidr,
  ]

  description = "Allow internal communication within VPC"
}

# Allow health checks from Google Load Balancers
resource "google_compute_firewall" "allow_health_checks" {
  name    = "barq-${var.environment}-allow-health-checks"
  project = var.project_id
  network = google_compute_network.main.id

  allow {
    protocol = "tcp"
  }

  # Google Cloud health check IP ranges
  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]

  target_tags = ["allow-health-check"]

  description = "Allow health checks from Google Load Balancers"
}

# Deny all ingress by default (implicit, but explicit for documentation)
resource "google_compute_firewall" "deny_all_ingress" {
  name     = "barq-${var.environment}-deny-all-ingress"
  project  = var.project_id
  network  = google_compute_network.main.id
  priority = 65534

  deny {
    protocol = "all"
  }

  source_ranges = ["0.0.0.0/0"]

  description = "Deny all ingress traffic by default"
}
