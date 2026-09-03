data "google_project" "current" {
  project_id = var.project_id
}

# ------------------------------------------------------------------------------
# Required GCP Service APIs
# ------------------------------------------------------------------------------
locals {
  services = [
    "run.googleapis.com",              # Cloud Run Admin API
    "artifactregistry.googleapis.com", # Artifact Registry API
    "secretmanager.googleapis.com",    # Secret Manager API
    "iam.googleapis.com",              # Identity and Access Management (IAM) API
    "iamcredentials.googleapis.com",   # IAM Service Account Credentials API
    "sts.googleapis.com",              # Security Token Service API (for Workload Identity)
    "cloudresourcemanager.googleapis.com"
  ]
}

resource "google_project_service" "enabled_services" {
  for_each           = toset(local.services)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
