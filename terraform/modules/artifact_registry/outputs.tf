# Artifact Registry Module Outputs

output "docker_repository_id" {
  description = "The ID of the Docker repository"
  value       = google_artifact_registry_repository.docker.id
}

output "docker_repository_name" {
  description = "The name of the Docker repository"
  value       = google_artifact_registry_repository.docker.name
}

output "docker_repository_url" {
  description = "The URL of the Docker repository"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
}

output "api_image_url" {
  description = "Full URL for the API container image"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/barq-api"
}

output "web_image_url" {
  description = "Full URL for the Web container image"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/barq-web"
}

output "npm_repository_id" {
  description = "The ID of the NPM repository (if created)"
  value       = var.create_npm_registry ? google_artifact_registry_repository.npm[0].id : null
}

output "npm_repository_url" {
  description = "The URL of the NPM repository (if created)"
  value       = var.create_npm_registry ? "${var.region}-npm.pkg.dev/${var.project_id}/${google_artifact_registry_repository.npm[0].repository_id}" : null
}

output "python_repository_id" {
  description = "The ID of the Python repository (if created)"
  value       = var.create_python_registry ? google_artifact_registry_repository.python[0].id : null
}

output "python_repository_url" {
  description = "The URL of the Python repository (if created)"
  value       = var.create_python_registry ? "${var.region}-python.pkg.dev/${var.project_id}/${google_artifact_registry_repository.python[0].repository_id}" : null
}

output "docker_push_command" {
  description = "Example command to push a Docker image"
  value       = "docker push ${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/IMAGE_NAME:TAG"
}

output "docker_auth_command" {
  description = "Command to authenticate Docker with the registry"
  value       = "gcloud auth configure-docker ${var.region}-docker.pkg.dev"
}
