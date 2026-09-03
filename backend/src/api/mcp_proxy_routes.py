"""
HTTP JSON-RPC proxy for WebMCP tool invocation.
This avoids SSE session coupling for browser-side tool calls.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..mcp import tools as mcp_tools

router = APIRouter(prefix="/mcp", tags=["mcp"])


class ToolCallParams(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class JsonRpcToolCall(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: ToolCallParams
    id: Any = None


def _to_json_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value)


def _build_handlers() -> Dict[str, Callable[[Dict[str, Any]], str]]:
    return {
        "mutate_ui_schema": lambda args: mcp_tools.mutate_ui_schema(
            schema_patch=_to_json_text(args.get("schema_patch", "{}")),
            component_target=str(args.get("component_target", "root")),
        ),
        "simulate_tradeoff": lambda args: mcp_tools.simulate_tradeoff(
            contract_id=str(args["contract_id"]),
            proposed_change=_to_json_text(args.get("proposed_change", {})),
        ),
        "get_current_deal": lambda args: mcp_tools.get_current_deal(
            contract_id=str(args["contract_id"]),
        ),
        "get_constraints": lambda args: mcp_tools.get_constraints(
            contract_id=str(args["contract_id"]),
        ),
        "evaluate_offer": lambda args: mcp_tools.evaluate_offer(
            contract_id=str(args["contract_id"]),
            offer_data=_to_json_text(args.get("offer_data", {})),
        ),
        "propose_counteroffer": lambda args: mcp_tools.propose_counteroffer(
            contract_id=str(args["contract_id"]),
            proposal_data=_to_json_text(args.get("proposal_data", {})),
        ),
        "execute_contract": lambda args: mcp_tools.execute_contract(
            contract_id=str(args.get("contract_id", "1042-B")),
            signature_token=args.get("signature_token"),
        ),
        "inspect_ui_schema": lambda args: mcp_tools.inspect_ui_schema(
            schema_id=str(args.get("schema_id", "deal_room_v1")),
        ),
        "preview_ui_mutation": lambda args: mcp_tools.preview_ui_mutation(
            base_version=int(args["base_version"]),
            patch_data=_to_json_text(args.get("patch_data", {})),
            component_target=str(args.get("component_target", "root")),
        ),
        "publish_ui_mutation": lambda args: mcp_tools.publish_ui_mutation(
            mutation_id=str(args["mutation_id"]),
        ),
        "create_deal": lambda args: mcp_tools.create_deal(
            company=str(args["company"]),
            value=int(args["value"]),
            stage=str(args.get("stage", "Draft")),
            title=args.get("title"),
            liability_cap=args.get("liability_cap", "1.5x"),
        ),
        "get_deals": lambda args: mcp_tools.get_deals(
            query=args.get("query"),
            status=args.get("status"),
            min_value=args.get("min_value"),
            max_value=args.get("max_value"),
        ),
        "move_deal_stage": lambda args: mcp_tools.move_deal_stage(
            contract_id=str(args["contract_id"]),
            stage=str(args["stage"]),
        ),
        "add_deal_note": lambda args: mcp_tools.add_deal_note(
            contract_id=str(args["contract_id"]),
            note=str(args["note"]),
            author=args.get("author", "WebMCP Agent"),
        ),
    }


@router.get("/manifest.json")
def get_manifest():
    """Returns machine-readable WebMCP tool catalog for AI agents (ChatGPT, etc.)."""
    return {
        "protocol": "WebMCP",
        "version": "1.0.0",
        "name": "Nexus Deal Room WebMCP Server",
        "description": "Agent-native decision environment with deterministic Decision Twin and WebMCP tool interface.",
        "discovery": {
            "browser_context": "window.document.modelContext",
            "json_rpc_endpoint": "/api/mcp/tool-call",
            "rest_endpoint": "/api/contracts"
        },
        "tools": [
            {
                "name": "create_deal",
                "title": "Create Deal",
                "description": "Create a new enterprise deal in the Nexus Deal Room.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string", "description": "Counterparty company name"},
                        "value": {"type": "number", "description": "Annual contract value in USD"},
                        "stage": {"type": "string", "description": "Deal stage: Draft, Negotiation, Approved, Closed Won"}
                    },
                    "required": ["company", "value"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_deals",
                "title": "Get Deals",
                "description": "Search and list deals across the pipeline.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search keyword"},
                        "status": {"type": "string", "description": "Filter by status"}
                    }
                }
            },
            {
                "name": "move_deal_stage",
                "title": "Move Deal Stage",
                "description": "Transition a deal to a new stage (e.g. Negotiation, Closed Won).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {"type": "string", "description": "Contract ID (e.g. #1042-B)"},
                        "stage": {"type": "string", "description": "Target stage"}
                    },
                    "required": ["contract_id", "stage"]
                }
            },
            {
                "name": "add_deal_note",
                "title": "Add Deal Note",
                "description": "Append a negotiation or context note to a contract record.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {"type": "string", "description": "Contract ID"},
                        "note": {"type": "string", "description": "Note content"},
                        "author": {"type": "string", "description": "Author name"}
                    },
                    "required": ["contract_id", "note"]
                }
            },
            {
                "name": "get_current_deal",
                "title": "Get Current Deal",
                "description": "Retrieve active deal state, current price, and negotiated terms.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {"type": "string", "description": "Contract identifier"}
                    },
                    "required": ["contract_id"]
                }
            },
            {
                "name": "evaluate_offer",
                "title": "Evaluate Offer",
                "description": "Runs deterministic mathematical evaluation through the Decision Twin.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {"type": "string"},
                        "offer_data": {"type": "object"}
                    },
                    "required": ["contract_id", "offer_data"]
                }
            },
            {
                "name": "simulate_tradeoff",
                "title": "Simulate Tradeoff",
                "description": "Simulates price/liability elasticity trade-offs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {"type": "string"},
                        "proposed_change": {"type": "object"}
                    },
                    "required": ["contract_id", "proposed_change"]
                }
            },
            {
                "name": "execute_contract",
                "title": "Execute Contract",
                "description": "Attempts to sign and execute a finalized contract. Strictly requires human approval cryptographic token.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "contract_id": {"type": "string"},
                        "signature_token": {"type": "string"}
                    },
                    "required": ["contract_id"]
                }
            }
        ]
    }


@router.post("/tool-call")
@router.post("/messages")
@router.post("/messages/")
async def tool_call(payload: JsonRpcToolCall):
    if payload.method != "tools/call":
        return {
            "jsonrpc": "2.0",
            "id": payload.id,
            "error": {
                "code": -32601,
                "message": f"Unsupported method: {payload.method}",
            },
        }

    handlers = _build_handlers()
    handler = handlers.get(payload.params.name)
    if handler is None:
        return {
            "jsonrpc": "2.0",
            "id": payload.id,
            "error": {
                "code": -32602,
                "message": f"Unknown tool: {payload.params.name}",
            },
        }

    try:
        raw = handler(payload.params.arguments)
        return {
            "jsonrpc": "2.0",
            "id": payload.id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": raw,
                    }
                ]
            },
        }
    except KeyError as exc:
        return {
            "jsonrpc": "2.0",
            "id": payload.id,
            "error": {
                "code": -32602,
                "message": f"Missing required argument: {str(exc)}",
            },
        }
    except Exception as exc:
        return {
            "jsonrpc": "2.0",
            "id": payload.id,
            "error": {
                "code": -32000,
                "message": str(exc),
            },
        }
