"""
Tests for MCP JSON-RPC HTTP proxy route used by browser-side WebMCP calls.
"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_mcp_proxy_get_current_deal_success():
    response = client.post(
        "/api/mcp/tool-call",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_current_deal",
                "arguments": {"contract_id": "1042-B"},
            },
            "id": "proxy-get-deal-1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == "proxy-get-deal-1"
    assert "result" in payload
    assert "content" in payload["result"]


def test_mcp_proxy_unknown_tool_returns_jsonrpc_error():
    response = client.post(
        "/api/mcp/tool-call",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "unknown_tool",
                "arguments": {},
            },
            "id": "proxy-unknown-1",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["jsonrpc"] == "2.0"
    assert payload["id"] == "proxy-unknown-1"
    assert payload["error"]["code"] == -32602
