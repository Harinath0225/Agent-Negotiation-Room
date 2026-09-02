# Walkthrough: Agent-Native Deal Room
Branches: `002-modernize-deal-room`, `003-agent-native-deal-room`

## Overview

This walkthrough documents the agent-operable decision environment of Nexus Deal Room:
1. **Deterministic Decision Twin**: Evaluates complete deal alternatives against constraints, detecting hard failures (e.g. 1.5x liability requirement) and generating strategic trade-offs with 100% repeatability across 100+ runs.
2. **WebMCP Deal Operations**: Exposes discoverable Model Context Protocol tools (`get_current_deal`, `get_constraints`, `evaluate_offer`, `propose_counteroffer`) for external agents, recording every tool execution as an activity event with human-in-the-loop approval.
3. **Decision Density & 3-Way Comparison**: Renders a dense Contract Terms & Constraints table (`Term`, `Current`, `Target`, `Status`) and a 3-way comparison matrix (`Current Deal`, `Counter Proposal A`, and `Restrictive Seller Offer`).
4. **Wire-Agent Presentation Safety Guard**: Enables Wire-Agent to inspect schemas, stage visual previews (`preview_ui_mutation`), and publish layout refinements (`publish_ui_mutation` to v3) while strictly guarding against modifications to deal terms, constraints, or decision logic. Proves Decision Twin outputs remain 100% invariant across schema versions.
5. **Visible React Flow DAG**: Renders an interactive `@xyflow/react` execution graph tracing the 6-stage sequence (`discover -> read -> evaluate -> reason -> propose -> approve`) with status coloring and a selectable node payload inspector.

---

## What Was Implemented

### 1. Deterministic Decision Twin (US1)
- Implemented `evaluate_constraints`, `calculate_score`, `generate_tradeoffs`, and `detect_hard_failures` in `backend/src/twin/decision_logic.py`.
- Enforces strict liability hard constraints (liability must be >= 1.5x annual contract value, otherwise `is_feasible = False`).
- Generates "Next Best Negotiation Move" recommendations for alternatives.
- Verified with 100-run repeat determinism tests in `backend/tests/test_decision_twin.py`.

### 2. Strategic Counteroffer via WebMCP (US2)
- Implemented WebMCP tools in `backend/src/mcp/tools.py` and registered them with FastMCP in `backend/src/mcp/server.py`:
  - `get_current_deal`: Retrieves active terms and targets.
  - `get_constraints`: Retrieves hard and advisory constraints.
  - `evaluate_offer`: Evaluates candidate terms against Decision Twin constraints.
  - `propose_counteroffer`: Validates terms and creates a pending proposal requiring human approval.
- Emits started, completed, and failed activity events into the timeline.
- Verified in `backend/tests/test_agent_native_workflow.py`.

### 3. Decision Alternative Comparison (US3)
- Built `term-table` node in `frontend/src/renderer/SchemaRenderer.tsx`:
  - Displays Term, Current, Target, and Status.
  - Highlights compliant terms (emerald) vs. hard failures (rose badge).
- Built `deal-comparison` 3-way matrix:
  - Compares Current Deal ($120k, 2.0x, 50% score), Counter A ($105k, 1.5x, 65% score, "Next Best Move"), and Restrictive Offer ($95k, 0.8x, 36% score, HARD FAILURE).
  - Enables one-click alternative selection in Zustand state store.

### 4. Wire-Agent UX Evolution & Safety Guard (US4)
- Added `validate_presentation_patch`, `handle_preview_mutation`, and `handle_publish_mutation` in `backend/src/mcp/handlers.py`.
- Rejects any patch targeting `/deal/`, `/constraints/`, `/evaluation/`, `/approval/`, `/strategy/`, `price`, `target`, `hard_limit`, etc.
- Exposed `inspect_ui_schema`, `preview_ui_mutation`, and `publish_ui_mutation` in `backend/src/mcp/server.py`.
- Added interactive Wire-Agent panel in `frontend/src/renderer/SchemaRenderer.tsx` and actions in `frontend/src/App.tsx`.
- Verified decision invariance (v1 and v2/v3 evaluations are identical) in `backend/tests/test_agent_native_workflow.py`.

### 5. Visible React Flow Execution DAG (Phase 7)
- Integrated `@xyflow/react` into `agent-workflow-dag` node in `frontend/src/renderer/SchemaRenderer.tsx`.
- Displays canonical directed path: `Discover Tools -> Read Deal State -> Evaluate Offer -> Agent Strategy -> Propose Counteroffer -> Human Approval`.
- Displays node states: completed (emerald), active (sky glow), failed (rose).
- Clicking any node displays the tool name, request ID, status, and payload summary in an inspector card.

---

## Validation & Verification Results

### Backend Automated Test Suite
```powershell
.venv\Scripts\python.exe -m pytest
```
Results:
- `tests/test_agent_native_workflow.py`: 16 passed
- `tests/test_decision_twin.py`: 6 passed
- `tests/test_mcp_simulation.py`: 7 passed
- `tests/test_simulation_routes.py`: 8 passed
- **Total: 37 passed in 4.05s (100% pass rate)**.

### Frontend Typecheck, Lint, and Production Build
```powershell
npm run lint
npm run build
```
Results:
- `eslint .`: 0 errors.
- `tsc -b && vite build`: built in 2.79s with 0 errors.
- Bundle output: `dist/index.html` (0.90 kB), `dist/assets/index-BDNM-iAj.js` (377.37 kB).

### Quickstart Scenarios Validated
- **Scenario A (Restrictive Offer)**: Evaluated 0.8x liability offer via Decision Twin, confirmed hard failure verdict, verified activity log and React Flow DAG recorded the calls, and confirmed counteroffer proposal remains pending human approval.
- **Scenario B (Decision Density)**: Verified 3 alternatives compared side-by-side with Term/Current/Target/Status and 100 repeated evaluations yielding identical scores and failure lists.
- **Scenario C (Wire-Agent Safety)**: Verified preview and publish of presentation-only schema patch to v3, confirmed forbidden mutations are rejected, and confirmed Decision Twin results remain 100% invariant.
