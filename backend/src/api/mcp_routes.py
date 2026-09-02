from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from mcp.server.sse import SseServerTransport
from ..mcp.server import app as mcp_server

router = APIRouter()
transport = SseServerTransport("/api/mcp/messages")

@router.get("/sse")
async def handle_sse(request: Request):
    async with transport.connect_sse(request.scope, request.receive, request._send) as sse:
        return EventSourceResponse(sse)

@router.post("/messages")
async def handle_messages(request: Request):
    await transport.handle_post_message(request.scope, request.receive, request._send)
    return {}
