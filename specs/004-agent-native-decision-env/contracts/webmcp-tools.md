# WebMCP Tool Contracts Specification

**Feature**: `004-agent-native-decision-env`  
**Protocol**: FastMCP / JSON-RPC 2.0  
**Base URL**: `http://127.0.0.1:8000/api/mcp`  

---

## Registered MCP Tools

### 1. `get_current_deal`
Retrieves current contract terms and target terms for a given contract.
- **Parameters**: `contract_id` (string, default: `"#1042-B"`)
- **Returns**: JSON object containing baseline price, liability cap, payment schedule, and timeline.

### 2. `get_constraints`
Retrieves non-negotiable hard limits and advisory evaluation rules.
- **Parameters**: `contract_id` (string, default: `"#1042-B"`)
- **Returns**: Array of hard and advisory constraints (e.g. `liability >= 1.5x`).

### 3. `evaluate_offer`
Runs deterministic Decision Twin evaluation against a set of proposed terms.
- **Parameters**:
  - `contract_id` (string)
  - `proposed_price` (number)
  - `liability_cap` (number)
- **Returns**: `DecisionResult` JSON containing `score`, `is_feasible`, `hard_failures`, and `trade_offs`.

### 4. `propose_counteroffer`
Validates terms and records a pending counteroffer proposal requiring human sign-off.
- **Parameters**:
  - `contract_id` (string)
  - `proposed_price` (number)
  - `liability_cap` (number)
  - `counterparty` (string)
- **Returns**: Proposal record object with `status: "pending"`.

### 5. `inspect_ui_schema`
Inspects active UI schema version and layout tree structure.
- **Parameters**: None
- **Returns**: `version` (number) and `layout` JSON tree.

### 6. `preview_ui_mutation`
Stages a presentation-only UI schema patch without publishing.
- **Parameters**:
  - `base_version` (integer)
  - `patch` (object containing optional `className` or `props`)
- **Returns**: `mutation_id` (string e.g. `"mut-wire-01"`), `status: "previewed"`.

### 7. `publish_ui_mutation`
Publishes a reviewed presentation mutation, incrementing active schema version.
- **Parameters**:
  - `mutation_id` (string)
  - `base_version` (integer)
- **Returns**: Published schema record with `version: base_version + 1`.
