# Artifact Registry Module - Container Registries
# This module creates Artifact Registry repositories for the BARQ Fleet Management platform

# -----------------------------------------------------------------------------
# Docker Repository - Main container images
# -----------------------------------------------------------------------------
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  project       = var.project_id
  repository_id = "barq-fleet"
  description   = "Docker repository for BARQ Fleet Management container images (${var.environment})"
  format        = "DOCKER"
  mode          = "STANDARD_REPOSITORY"

  docker_config {
    immutable_tags = var.environment == "production" ? true : false
  }

  cleanup_policies {
    id     = "keep-minimum-versions"
    action = "KEEP"
    most_recent_versions {
      keep_count            = var.environment == "production" ? 10 : 5
      package_name_prefixes = ["barq-api", "barq-web"]
    }
  }

  cleanup_policies {
    id     = "delete-old-images"
    action = "DELETE"
    condition {
      tag_state    = "ANY"
      older_than   = var.environment == "production" ? "2592000s" : "604800s" # 30 days or 7 days
      tag_prefixes = ["temp-", "dev-", "test-"]
    }
  }

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    project     = "barq-fleet"
  }
}

# -----------------------------------------------------------------------------
# NPM Repository - Frontend packages (optional)
# -----------------------------------------------------------------------------
resource "google_artifact_registry_repository" "npm" {
  count = var.create_npm_registry ? 1 : 0

  location      = var.region
  project       = var.project_id
  repository_id = "barq-npm"
  description   = "NPM repository for BARQ Fleet Management packages (${var.environment})"
  format        = "NPM"
  mode          = "STANDARD_REPOSITORY"

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    project     = "barq-fleet"
  }
}

# -----------------------------------------------------------------------------
# Python Repository - Backend packages (optional)
# -----------------------------------------------------------------------------
resource "google_artifact_registry_repository" "python" {
  count = var.create_python_registry ? 1 : 0

  location      = var.region
  project       = var.project_id
  repository_id = "barq-python"
  description   = "Python repository for BARQ Fleet Management packages (${var.environment})"
  format        = "PYTHON"
  mode          = "STANDARD_REPOSITORY"

  labels = {
    environment = var.environment
    managed-by  = "terraform"
    project     = "barq-fleet"
  }
}

# -----------------------------------------------------------------------------
# IAM Bindings
# -----------------------------------------------------------------------------

# Cloud Build Service Account - Push images
resource "google_artifact_registry_repository_iam_member" "cloudbuild_writer" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.docker.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Compute Engine Default Service Account - Pull images
resource "google_artifact_registry_repository_iam_member" "compute_reader" {
  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.docker.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

# Cloud Run Service Account - Pull images
resource "google_artifact_registry_repository_iam_member" "cloudrun_reader" {
  for_each = toset(var.cloud_run_service_accounts)

  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.docker.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${each.value}"
}

# GitHub Actions Service Account - Push images (if using GitHub Actions)
resource "google_artifact_registry_repository_iam_member" "github_writer" {
  count = var.github_service_account != "" ? 1 : 0

  project    = var.project_id
  location   = var.region
  repository = google_artifact_registry_repository.docker.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${var.github_service_account}"
}

# -----------------------------------------------------------------------------
# Vulnerability Scanning
# -----------------------------------------------------------------------------
resource "google_artifact_registry_repository" "docker" {
  count = 0 # This is handled by the main docker resource

  # Vulnerability scanning is enabled by default in Artifact Registry
  # Configure Container Analysis API for detailed vulnerability reports
}
