from mcp.server.fastmcp import FastMCP
from .tools import (
    mutate_ui_schema, 
    simulate_tradeoff,
    get_current_deal,
    get_constraints,
    evaluate_offer,
    propose_counteroffer,
    inspect_ui_schema,
    preview_ui_mutation,
    publish_ui_mutation,
)

mcp_server = FastMCP(
    name="nexus-deal-room-mcp",
    instructions="Exposes UI mutation, deal discovery, constraint evaluation, and proposal tools to AI agents."
)

# ============================================================================
# Phase 1: Presentation Mutation Tool
# ============================================================================

@mcp_server.tool(
    name="mutate_ui_schema",
    description="Submits a proposed JSON schema payload to update the frontend layout and Tailwind styling."
)
def tool_mutate_ui_schema(schema_patch: str, component_target: str = "root") -> str:
    return mutate_ui_schema(schema_patch=schema_patch, component_target=component_target)

@mcp_server.tool(
    name="simulate_tradeoff",
    description="Runs a simulation against contract terms using the Decision Twin to evaluate risk and price sensitivity."
)
def tool_simulate_tradeoff(contract_id: str, proposed_change: str) -> str:
    return simulate_tradeoff(contract_id=contract_id, proposed_change=proposed_change)

# ============================================================================
# Phase 4 (US2): Deal Discovery and Evaluation Tools
# ============================================================================

@mcp_server.tool(
    name="get_current_deal",
    description="Retrieves the current deal with all material terms and constraint targets. Used in discover/read phase."
)
def tool_get_current_deal(contract_id: str) -> str:
    return get_current_deal(contract_id=contract_id)

@mcp_server.tool(
    name="get_constraints",
    description="Retrieves all hard and advisory constraints for the deal. Used in discover/read phase."
)
def tool_get_constraints(contract_id: str) -> str:
    return get_constraints(contract_id=contract_id)

@mcp_server.tool(
    name="evaluate_offer",
    description="Evaluates a proposed offer against all constraints using the Decision Twin. Returns score, feasibility, hard failures, and trade-offs. Used in evaluate phase."
)
def tool_evaluate_offer(contract_id: str, offer_data: str) -> str:
    return evaluate_offer(contract_id=contract_id, offer_data=offer_data)

@mcp_server.tool(
    name="propose_counteroffer",
    description="Creates a pending counteroffer proposal from an agent or human. Used in propose phase. Returns pending approval status."
)
def tool_propose_counteroffer(contract_id: str, proposal_data: str) -> str:
    return propose_counteroffer(contract_id=contract_id, proposal_data=proposal_data)

# ============================================================================
# Phase 6 (US4): Wire-Agent Schema Inspection, Preview, and Publish Tools
# ============================================================================

@mcp_server.tool(
    name="inspect_ui_schema",
    description="Inspects currently published UI schema version and layout tree. Used by Wire-Agent."
)
def tool_inspect_ui_schema(schema_id: str = "deal_room_v1") -> str:
    return inspect_ui_schema(schema_id=schema_id)

@mcp_server.tool(
    name="preview_ui_mutation",
    description="Validates a presentation-only schema patch and creates a staged preview without publishing."
)
def tool_preview_ui_mutation(base_version: int, patch_data: str, component_target: str = "root") -> str:
    return preview_ui_mutation(base_version=base_version, patch_data=patch_data, component_target=component_target)

@mcp_server.tool(
    name="publish_ui_mutation",
    description="Publishes a reviewed and staged presentation-only schema mutation, incrementing the version."
)
def tool_publish_ui_mutation(mutation_id: str) -> str:
    return publish_ui_mutation(mutation_id=mutation_id)
