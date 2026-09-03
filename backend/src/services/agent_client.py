"""
Microsoft Agentic AI Framework WebMCP client adapter.
Connects the agent runtime to the backend WebMCP server tools.
"""
import os
import json
import uuid
import logging
from typing import Any, Dict, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("agent_client")

# Configuration
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
AGENT_MODEL_PROVIDER = os.environ.get("AGENT_MODEL_PROVIDER", "auto").lower()
from src.services.secrets import get_gemini_api_key

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
VERTEX_AI_API_KEY = get_gemini_api_key()
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_LOCATION = os.environ.get("GCP_LOCATION", "us-central1")
VERTEX_AI_MODEL = os.environ.get("VERTEX_AI_MODEL", "gemini-1.5-pro")


class AgenticWebMCPClient:
    """
    Microsoft Agentic AI Framework WebMCP client adapter.
    Dispatches tool execution requests to the WebMCP server.
    """

    def __init__(self, backend_url: str = BACKEND_URL):
        self.backend_url = backend_url.rstrip("/")
        self.session_id = f"agent-{uuid.uuid4().hex[:8]}"
        self._kernel = None
        self._initialize_kernel()

    def _initialize_kernel(self) -> None:
        """
        Initializes the Microsoft Semantic Kernel / Agentic AI Framework instance.
        """
        try:
            import semantic_kernel as sk
            self._kernel = sk.Kernel()
            logger.info(f"[Agentic Client] Initialized Semantic Kernel for session {self.session_id}")
        except Exception as exc:
            logger.warning(f"[Agentic Client] Semantic Kernel initialization fallback: {exc}")
            self._kernel = None

    async def invoke_simulate_tradeoff(
        self,
        contract_id: str,
        proposed_change: Dict[str, Any],
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Invokes the simulate_tradeoff WebMCP tool on the server.
        Uses structured request identifiers and logs at the integration boundary.
        """
        call_id = request_id or f"agent-req-{uuid.uuid4().hex[:8]}"
        logger.info(
            f"[Agent Client Boundary] Starting tool invocation: simulate_tradeoff "
            f"call_id={call_id} contract_id={contract_id}"
        )

        payload_str = json.dumps(proposed_change) if isinstance(proposed_change, dict) else str(proposed_change)

        # 1. Primary path: Call the backend's WebMCP tools directly or via WebMCP HTTP endpoint
        try:
            from ..mcp.tools import simulate_tradeoff
            raw_result = simulate_tradeoff(contract_id=contract_id, proposed_change=payload_str)
            parsed = json.loads(raw_result)
            logger.info(
                f"[Agent Client Boundary] Tool invocation completed successfully call_id={call_id}"
            )
            return parsed
        except Exception as local_err:
            logger.warning(
                f"[Agent Client Boundary] Direct MCP dispatch failed ({local_err}); attempting HTTP WebMCP endpoint"
            )

        # 2. Network WebMCP fallback path
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.backend_url}/api/mcp/messages",
                    json={
                        "jsonrpc": "2.0",
                        "method": "tools/call",
                        "params": {
                            "name": "simulate_tradeoff",
                            "arguments": {
                                "contract_id": contract_id,
                                "proposed_change": payload_str,
                            },
                        },
                        "id": call_id,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"[Agent Client Boundary] WebMCP HTTP call succeeded call_id={call_id}")
                    return data
                else:
                    err_msg = f"WebMCP HTTP response status {response.status_code}: {response.text}"
                    logger.error(f"[Agent Client Boundary] {err_msg} call_id={call_id}")
                    return {"status": "error", "message": err_msg}
            except Exception as http_err:
                logger.error(f"[Agent Client Boundary] WebMCP HTTP request failed: {http_err} call_id={call_id}")
                return {"status": "error", "message": str(http_err)}


# Default singleton instance
default_agent_client = AgenticWebMCPClient()
