# Tasks: Agent-Native Decision Environment

**Feature**: `004-agent-native-decision-env`  
**Spec Reference**: [`01_spec.md`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/01_spec.md) / [`spec.md`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/specs/004-agent-native-decision-env/spec.md)  
**Plan Reference**: [`plan.md`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/specs/004-agent-native-decision-env/plan.md)  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and environment readiness.

- [x] T001 Verify project structure and `.specify/feature.json` setup
- [x] T002 [P] Verify Python virtual environment dependencies in `backend/` (`FastAPI`, `FastMCP`, `Pydantic`)
- [x] T003 [P] Verify Node.js dependencies in `frontend/package.json` (`React 18`, `Tailwind CSS`, `Zustand`, `@xyflow/react`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Decision Twin deterministic evaluation contract and FastMCP registration.

- [x] T004 Verify deterministic constraint evaluation in `backend/src/twin/decision_logic.py`
- [x] T005 [P] Verify FastMCP server tool registrations in `backend/src/mcp/server.py`
- [x] T006 [P] Verify schema rendering pipeline in `frontend/src/renderer/SchemaRenderer.tsx`

**Checkpoint**: Core foundation verified - user story implementation can proceed.

---

## Phase 3: User Story 1 - Natural Language Intent Weight Compiler (Priority: P1) 🌟 MVP

**Goal**: Enable dealmakers to state natural language priorities (e.g., *"Speed is more important than budget right now"*), compiling them into normalized mathematical weights ($w_i$) that adjust Decision Twin evaluation.

**Independent Test**: Submit natural language intent text, verify weights update in store (`SPEED: 35%`, `PRICE: 25%`), and confirm Decision Twin score rankings recompute deterministically.

### Implementation for User Story 1

- [x] T007 [P] [US1] Add `IntentWeights` interface and weight compilation state in `frontend/src/store/index.ts`
- [x] T008 [P] [US1] Add intent compiler function `compile_intent_weights` in `backend/src/twin/decision_logic.py`
- [x] T009 [US1] Add `constraint-kitchen` schema node with input prompt and dynamic weight sliders in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T010 [US1] Add `compileIntent` action dispatcher in `frontend/src/App.tsx`
- [x] T011 [US1] Add `constraint-kitchen` node configuration in `backend/src/seeds/deal_room.json`
- [x] T012 [US1] Add unit tests for intent weight compilation in `backend/tests/test_decision_twin.py`

**Checkpoint**: Dealmakers can state natural language intent and see mathematical weights recompile in real-time.

---

## Phase 4: User Story 2 - High Decision Density Alternatives Comparison Matrix (Priority: P1)

**Goal**: Render a 3-way alternative comparison matrix (`Current Deal`, `Counter Proposal A`, `Restrictive Seller Offer`) alongside a 4-column Term Table (`Term`, `Current`, `Target`, `Status`) for immediate decision density.

**Independent Test**: Load the three alternatives side-by-side; confirm `Counter Proposal A` is marked **★ Next Best Move** and `Restrictive Seller Offer` is marked **HARD FAILURE** (0.8x liability $< 1.5x$ limit).

### Implementation for User Story 2

- [x] T013 [P] [US2] Define typed `AlternativeScenario` state and 3 baseline alternatives in `frontend/src/store/index.ts`
- [x] T014 [P] [US2] Enhance `term-table` node with compliance (emerald) vs. hard failure (rose) badges in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T015 [US2] Enhance `deal-comparison` node with side-by-side cards, trade-off moves, and score deltas in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T016 [US2] Compose `term-table` and `deal-comparison` nodes in `backend/src/seeds/deal_room.json`
- [x] T017 [US2] Wire interactive alternative selection in `frontend/src/App.tsx`

**Checkpoint**: Dealmakers can compare 3 alternatives and governing terms without scanning text clutter.

---

## Phase 5: User Story 3 - Observable Agentic Strategy & WebMCP Execution Graph (Priority: P2)

**Goal**: Stream WebMCP tool executions into the Agent Activity Log and project execution status onto an interactive `@xyflow/react` directed graph (`discover -> read -> evaluate -> reason -> propose -> approve`).

**Independent Test**: Run a WebMCP tool call or approve a counteroffer; verify the tool event logs in the activity timeline and the corresponding React Flow DAG node highlights green (`completed`).

### Implementation for User Story 3

- [x] T018 [P] [US3] Define canonical DAG nodes, edges, and `projectActivityToDAG` in `frontend/src/store/index.ts`
- [x] T019 [P] [US3] Implement `agent-workflow-dag` with `@xyflow/react` canvas and inspector drawer in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T020 [US3] Connect counteroffer proposal approval boundary with Zustand store in `frontend/src/renderer/SchemaRenderer.tsx` and `frontend/src/App.tsx`
- [x] T021 [US3] Add FastMCP tool handlers for `get_current_deal`, `get_constraints`, `evaluate_offer`, `propose_counteroffer` in `backend/src/mcp/tools.py`
- [x] T022 [US3] Add automated tests for WebMCP workflow execution in `backend/tests/test_agent_native_workflow.py`

**Checkpoint**: All WebMCP agent operations are 100% observable via live activity logs and interactive React Flow graph.

---

## Phase 6: User Story 4 - Wire-Agent Presentation Safety & UI Schema Evolution (Priority: P3)

**Goal**: Allow Wire-Agent (Admin UI agent) to preview (`preview_ui_mutation`) and publish (`publish_ui_mutation` to v3) presentation-only schema mutations while strictly blocking modifications to business terms or decision logic.

**Independent Test**: Preview and publish visual patch `mut-wire-01` to schema v3; prove Decision Twin evaluations for Contract #1042-B remain 100% invariant between v1, v2, and v3.

### Implementation for User Story 4

- [x] T023 [P] [US4] Enforce patch immutability guard `validate_presentation_patch` in `backend/src/mcp/handlers.py`
- [x] T024 [P] [US4] Register `inspect_ui_schema`, `preview_ui_mutation`, `publish_ui_mutation` in `backend/src/mcp/server.py`
- [x] T025 [US4] Render `schema-mutation-panel` with preview and publish controls in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T026 [US4] Wire `previewWireAgentMutation` and `publishWireAgentMutation` actions in `frontend/src/App.tsx`
- [x] T027 [US4] Add decision invariance and forbidden-mutation unit tests in `backend/tests/test_agent_native_workflow.py`

**Checkpoint**: Wire-Agent can safely evolve UI layouts while backend immutability guards protect financial/legal integrity.

---

## Phase 7: Polish & Cross-Cutting Validation

**Purpose**: Final verification, linting, build validation, and documentation updates.

- [x] T028 [P] Run full backend test suite (`.venv\Scripts\python.exe -m pytest`)
- [x] T029 [P] Run frontend lint (`npm run lint` in `frontend/`)
- [x] T030 [P] Run production build (`npm run build` in `frontend/`)
- [x] T031 Update walkthrough documentation in `docs/walkthrough.md`
- [x] T032 Execute the three validation scenarios in `specs/004-agent-native-decision-env/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all User Stories.
- **User Stories (Phases 3-6)**: Depend on Foundational completion.
  - US1 (Intent Compiler - P1) and US2 (Decision Density - P1) run as MVP.
  - US3 (WebMCP DAG - P2) depends on Phase 2 FastMCP tools.
  - US4 (Wire-Agent Safety - P3) depends on Phase 2 handlers.
- **Polish (Phase 7)**: Depends on completion of User Stories 1-4.

### Parallel Opportunities

- T002, T003 can run in parallel.
- T007, T008 can run in parallel.
- T013, T014 can run in parallel.
- T018, T019 can run in parallel.
- T023, T024 can run in parallel.
- T028, T029, T030 can run in parallel.

---

## Implementation Strategy

### MVP Scope (User Stories 1 & 2)
1. Complete Phase 1 & 2.
2. Deliver US1 (Constraint Kitchen Intent Compiler) and US2 (High Decision Density Matrix).
3. Validate deterministic scoring and 3-way comparison matrix.

### Incremental Delivery
1. Add US3 (Observable WebMCP DAG & Human Approval Boundary).
2. Add US4 (Wire-Agent Presentation Safety Guard & Schema v3 Evolution).
3. Complete Phase 7 polish and quickstart scenario validation.
