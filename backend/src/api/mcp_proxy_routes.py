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
