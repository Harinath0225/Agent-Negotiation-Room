output "cloud_run_url" {
  description = "The publicly accessible HTTPS URL of the Nexus Deal Room Cloud Run service."
  value       = google_cloud_run_v2_service.nexus_deal_room.uri
}

output "workload_identity_provider" {
  description = "The Workload Identity Provider resource string for GitHub Actions authentication."
  value       = "projects/${data.google_project.current.number}/locations/global/workloadIdentityPools/${data.google_iam_workload_identity_pool.github_pool.workload_identity_pool_id}/providers/${data.google_iam_workload_identity_pool_provider.github_provider.workload_identity_pool_provider_id}"
}

output "github_actions_service_account_email" {
  description = "Service account email for GitHub Actions to impersonate."
  value       = google_service_account.github_actions.email
}

output "cloud_run_service_account_email" {
  description = "Runtime service account email attached to Cloud Run."
  value       = google_service_account.cloud_run_sa.email
}

output "artifact_registry_repository_url" {
  description = "Artifact Registry Docker repository endpoint."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.app_repo.repository_id}"
}

output "gemini_secret_id" {
  description = "The Secret Manager secret ID storing the Gemini API key."
  value       = data.google_secret_manager_secret.gemini_api_key.secret_id
}
