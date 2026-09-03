# ------------------------------------------------------------------------------
# Google Cloud Secret Manager for GEMINI_API_KEY
# References existing secret in GCP and authorizes Cloud Run to read it
# ------------------------------------------------------------------------------

# 1. Reference the existing secret in GCP Secret Manager
data "google_secret_manager_secret" "gemini_api_key" {
  secret_id = var.gemini_secret_name
  project   = var.project_id
}

# 2. Grant Secret Accessor role STRICTLY to the Cloud Run Runtime Service Account
resource "google_secret_manager_secret_iam_member" "cloud_run_gemini_secret_accessor" {
  project   = var.project_id
  secret_id = data.google_secret_manager_secret.gemini_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
