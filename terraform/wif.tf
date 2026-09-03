# ------------------------------------------------------------------------------
# Workload Identity Federation (WIF) for GitHub Actions
# Connects new GitHub repository to existing Workload Identity Pool
# ------------------------------------------------------------------------------

# 1. Reference Existing Workload Identity Pool in GCP
data "google_iam_workload_identity_pool" "github_pool" {
  provider                  = google-beta
  workload_identity_pool_id = var.workload_identity_pool_id
  project                   = var.project_id
}

# 2. Reference Existing Workload Identity Provider in GCP
data "google_iam_workload_identity_pool_provider" "github_provider" {
  provider                           = google-beta
  workload_identity_pool_id          = data.google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = var.workload_identity_pool_provider_id
  project                            = var.project_id
}

# 3. Service Account for GitHub Actions CI/CD (already created in previous apply)
resource "google_service_account" "github_actions" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployer"
  description  = "Service account assumed by GitHub Actions via Workload Identity Provider"
  project      = var.project_id
}

# 4. Bind the NEW GitHub Repository to Impersonate this Service Account via Existing WIF
resource "google_service_account_iam_member" "github_actions_wif_binding" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${data.google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_repository}"
}

# 5. Grant Permissions to GitHub Actions Service Account
# Push container images to Artifact Registry
resource "google_project_iam_member" "github_actions_artifact_registry" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Deploy revisions to Cloud Run
resource "google_project_iam_member" "github_actions_cloud_run" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Allow GitHub Actions to act as the Cloud Run runtime service account
resource "google_service_account_iam_member" "github_actions_act_as_runtime_sa" {
  service_account_id = google_service_account.cloud_run_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions.email}"
}
