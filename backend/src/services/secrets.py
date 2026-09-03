"""
GCP Secret Manager integration module.
Fetches sensitive credentials (e.g. GEMINI_API_KEY) strictly via Secret Manager.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger("secrets_service")


def get_gemini_api_key(
    project_id: Optional[str] = None,
    secret_id: str = "gemini-api-key",
    version: str = "latest",
) -> Optional[str]:
    """
    Fetches the Gemini API key.
    
    Order of operations:
    1. First checks environment variable GEMINI_API_KEY. On Cloud Run, this is directly
       injected at container startup from Secret Manager via Cloud Run's value_source.secret_key_ref.
    2. If not present in environment and running on GCP, fetches dynamically using
       the Google Cloud Secret Manager client library.
    """
    # 1. Check direct environment variable (injected from Secret Manager by Cloud Run)
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("VERTEX_AI_API_KEY")
    if env_key and env_key.strip():
        logger.info("[SecretManager] Retrieved GEMINI_API_KEY from Secret Manager container environment reference.")
        return env_key.strip()

    # 2. Dynamic Secret Manager API lookup
    gcp_project = project_id or os.environ.get("GCP_PROJECT_ID")
    target_secret = os.environ.get("GEMINI_SECRET_NAME", secret_id)

    if gcp_project:
        try:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{gcp_project}/secrets/{target_secret}/versions/{version}"
            logger.info(f"[SecretManager] Fetching secret dynamically: {name}")
            response = client.access_secret_version(request={"name": name})
            payload = response.payload.data.decode("UTF-8").strip()
            return payload
        except ImportError:
            logger.debug("[SecretManager] google-cloud-secret-manager package not installed. Skipping API fetch.")
        except Exception as e:
            logger.warning(f"[SecretManager] Failed to fetch {target_secret} from Secret Manager API: {e}")

    return None
