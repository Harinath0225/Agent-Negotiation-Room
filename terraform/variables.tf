variable "project_id" {
  description = "The Google Cloud Project ID where resources will be provisioned."
  type        = string
}

variable "region" {
  description = "The Google Cloud region for Cloud Run and Artifact Registry."
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
  default     = "nexus-deal-room"
}

variable "github_repository" {
  description = "GitHub repository path in the format 'owner/repo' allowed to authenticate via Workload Identity Federation."
  type        = string
  default     = "Harinath0225/Agent-Negotiation-Room"
}

variable "workload_identity_pool_id" {
  description = "The existing GCP Workload Identity Pool ID."
  type        = string
  default     = "github-actions-pool"
}

variable "workload_identity_pool_provider_id" {
  description = "The existing Workload Identity Provider ID within the pool."
  type        = string
  default     = "github-actions-provider"
}

variable "gemini_secret_name" {
  description = "The name of the existing Gemini API key secret in GCP Secret Manager."
  type        = string
  default     = "gemini-api-key"
}

variable "artifact_registry_repo_name" {
  description = "Artifact Registry Docker repository name."
  type        = string
  default     = "nexus-deal-room"
}

variable "container_image" {
  description = "The container image to deploy to Cloud Run. If empty, defaults to the Artifact Registry repository image."
  type        = string
  default     = ""
}

variable "allow_unauthenticated" {
  description = "Whether to allow unauthenticated public access to the Cloud Run service."
  type        = bool
  default     = true
}
