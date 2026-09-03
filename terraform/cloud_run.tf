# ------------------------------------------------------------------------------
# Artifact Registry & Cloud Run Service
# ------------------------------------------------------------------------------

# 1. Artifact Registry for Docker Images
resource "google_artifact_registry_repository" "app_repo" {
  provider      = google-beta
  project       = var.project_id
  location      = var.region
  repository_id = var.artifact_registry_repo_name
  description   = "Docker repository for Nexus Deal Room images"
  format        = "DOCKER"

  depends_on = [google_project_service.enabled_services]
}

# 2. Cloud Run Runtime Service Account
resource "google_service_account" "cloud_run_sa" {
  account_id   = "nexus-deal-room-runner"
  display_name = "Nexus Deal Room Cloud Run Runtime SA"
  description  = "Service account used by Cloud Run instances to access Secret Manager and Google APIs"
  project      = var.project_id
}

# 3. Default image fallback (uses public gcr hello image until GitHub Actions builds & pushes the real app)
locals {
  image_url = var.container_image != "" ? var.container_image : "us-docker.pkg.dev/cloudrun/container/hello"
}

# 4. Cloud Run (v2) Service
resource "google_cloud_run_v2_service" "nexus_deal_room" {
  name     = var.service_name
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.cloud_run_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = local.image_url

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "1024Mi"
        }
      }

      # Standard Environment Variables
      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCP_LOCATION"
        value = var.region
      }

      # GEMINI_API_KEY Injected STRICTLY via GCP Secret Manager
      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = data.google_secret_manager_secret.gemini_api_key.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  lifecycle {
    ignore_changes = [
      template[0].containers[0].image,
      client,
      client_version
    ]
  }

  depends_on = [
    google_project_service.enabled_services,
    google_secret_manager_secret_iam_member.cloud_run_gemini_secret_accessor,
    google_artifact_registry_repository.app_repo
  ]
}

# 5. Public Invocation Policy (Optional / Default True for Web App)
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.nexus_deal_room.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
