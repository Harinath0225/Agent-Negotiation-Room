# ☁️ Nexus Deal Room: Cloud Run & Workload Identity Federation Terraform

This directory provides a production-ready Terraform infrastructure-as-code suite to deploy **Nexus Deal Room** to **Google Cloud Run** using **GitHub Actions Workload Identity Federation (WIF)** and **Google Cloud Secret Manager**.

---

## 🏛️ Architecture & Security Model

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                     GitHub Actions CI/CD Pipeline                 │
 └─────────────────────────────────┬────────────────────────────────┘
                                   │ OIDC Token (Zero Long-Lived Keys!)
                                   ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │          GCP Workload Identity Pool & Provider                   │
 │   - Validates repository claim: "owner/repo"                     │
 │   - Impersonates: github-actions-deployer service account        │
 └─────────────────────────────────┬────────────────────────────────┘
                                   │
               ┌───────────────────┴───────────────────┐
               ▼                                       ▼
 ┌───────────────────────────┐           ┌──────────────────────────┐
 │ Artifact Registry (Docker)│           │   Cloud Run Deployment   │
 │ - Builds & pushes image   │           │ - Deploys latest tag     │
 └───────────────────────────┘           └─────────────┬────────────┘
                                                       │
                                                       ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │               Cloud Run Service (nexus-deal-room)                │
 │   - Runtime Service Account: nexus-deal-room-runner              │
 │   - Multi-stage: React SPA static frontend + FastAPI WebMCP API  │
 └─────────────────────────────────┬────────────────────────────────┘
                                   │ Fetched securely at startup
                                   │ (roles/secretmanager.secretAccessor)
                                   ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │             GCP Secret Manager: `gemini-api-key`                 │
 │   - Holds sensitive Gemini / Vertex AI API key                   │
 │   - NOT baked into container images, git, or build arguments     │
 └──────────────────────────────────────────────────────────────────┘
```

---

## 🔒 Security Principles Enforced

1. **Zero Long-Lived Service Account Keys**: GitHub Actions exchanges short-lived OIDC tokens directly with Google Cloud's Security Token Service (STS).
2. **Strict Repository Assertion**: The Workload Identity Provider attribute condition enforces that *only* your specific GitHub repository (`assertion.repository == "OWNER/REPO"`) can authenticate.
3. **Secret Manager Isolation**:
   - `GEMINI_API_KEY` is provisioned in GCP Secret Manager.
   - Only the runtime Cloud Run service account (`nexus-deal-room-runner`) is granted `roles/secretmanager.secretAccessor` on the `gemini-api-key` secret.
   - Cloud Run mounts the secret directly into the container environment via `value_source.secret_key_ref`, ensuring the key is never exposed in container builds or git history.

---

## 🚀 Step-by-Step Deployment Instructions

### 1. Prerequisites
- [Google Cloud SDK (gcloud)](https://cloud.google.com/sdk/docs/install) installed and authenticated.
- [Terraform](https://developer.hashicorp.com/terraform/install) (version `>= 1.5.0`).
- A GCP Project with billing enabled.

---

### 2. Authenticate to Google Cloud
```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID
```

---

### 3. Initialize & Configure Terraform

1. Navigate to the `terraform` directory:
   ```powershell
   cd terraform
   ```

2. Copy the example configuration file:
   ```powershell
   cp terraform.tfvars.example terraform.tfvars
   ```

3. Edit `terraform.tfvars`:
   ```hcl
   project_id        = "your-actual-gcp-project-id"
   region            = "us-central1"
   service_name      = "nexus-deal-room"
   github_repository = "Harinath0225/Agent-Negotiation-Room"
   gemini_api_key    = "AIzaSyYourActualGeminiApiKey" # Or provide via CLI prompt
   ```

---

### 4. Apply Infrastructure

Run Terraform to provision all GCP services, IAM bindings, Workload Identity Provider, Secret Manager, and Cloud Run:

```powershell
terraform init
terraform plan
terraform apply
```

Upon successful completion, Terraform outputs:
- `workload_identity_provider`: Full WIF resource path.
- `github_actions_service_account_email`: Email of the CI/CD service account.
- `artifact_registry_repository_url`: Docker repository endpoint.
- `gemini_secret_id`: ID of the secret in Secret Manager.
- `cloud_run_url`: The deployed application URL.

---

### 5. Configure GitHub Repository Secrets

In your GitHub repository, go to **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions** $\rightarrow$ **New repository secret**, and add:

| Secret Name | Value from Terraform Output | Description |
|---|---|---|
| `GCP_PROJECT_ID` | Your GCP Project ID | e.g. `my-deal-room-project` |
| `GCP_REGION` | `us-central1` | GCP Region |
| `WIF_PROVIDER` | `workload_identity_provider` | `projects/123456.../locations/global/workloadIdentityPools/...` |
| `WIF_SERVICE_ACCOUNT` | `github_actions_service_account_email` | `github-actions-deployer@...` |
| `CLOUD_RUN_SERVICE_NAME`| `nexus-deal-room` | Cloud Run service name |
| `ARTIFACT_REGISTRY_REPO`| `nexus-deal-room` | Artifact Registry repo |

---

### 6. Trigger Continuous Deployment

Push code to your `main` branch or manually dispatch the GitHub Action:

```powershell
git add .
git commit -m "Configure Cloud Run deployment with Workload Identity Federation"
git push origin main
```

1. GitHub Actions initiates `.github/workflows/deploy.yml`.
2. Authenticates seamlessly via Workload Identity Provider without any stored private key.
3. Builds the unified multi-stage Docker image (React frontend + FastAPI backend).
4. Pushes the image to Artifact Registry and updates Cloud Run.
5. Cloud Run starts and securely retrieves `GEMINI_API_KEY` from Secret Manager.
