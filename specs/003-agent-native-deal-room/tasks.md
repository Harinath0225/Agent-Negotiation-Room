# Tasks: Agent-Native Deal Room

**Input**: Design documents from `/specs/003-agent-native-deal-room/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [webmcp-workflow.md](./contracts/webmcp-workflow.md)

**Tests**: Backend determinism, contract behavior, and frontend validation are required by the feature success criteria.

## Phase 1: Setup

**Purpose**: Add focused graph tooling and test locations.

 - [x] T001 Add `@xyflow/react` and stylesheet import convention in `frontend/package.json`
 - [x] T002 [P] Create Decision Twin test module in `backend/tests/test_decision_twin.py`
 - [x] T003 [P] Create WebMCP workflow test module in `backend/tests/test_agent_native_workflow.py`

---

## Phase 2: Foundational

**Purpose**: Establish shared typed contracts and deterministic evaluation before any story implementation.

 - [x] T004 Define typed Deal, Constraint, DealAlternative, DecisionTwinEvaluation, CounterofferProposal, and AgentActivityEvent models in `backend/src/services/simulation_service.py`
 - [x] T005 Implement deterministic full-alternative constraint evaluation, score calculation, and trade-off generation in `backend/src/twin/decision_logic.py`
 - [x] T006 Implement a shared typed evaluation service and stable errors in `backend/src/services/simulation_service.py`
 - [x] T007 Add 100-repeat determinism and hard-liability-failure tests in `backend/tests/test_decision_twin.py`
 - [x] T008 Extend schema-node typings, activity event shape, and bounded event storage in `frontend/src/store/index.ts`

**Checkpoint**: One evaluator produces stable score, feasibility, hard failures, and trade-offs for every caller.

---

## Phase 3: User Story 1 - Evaluate a Restrictive Offer (Priority: P1) MVP

**Goal**: Make the Decision Twin visibly reject a low-price offer that violates the 1.5x liability hard constraint.

**Independent Test**: Evaluate the restrictive offer and confirm score, liability hard failure, affected term, and blocked approval are visible.

 - [x] T009 [US1] Add restrictive seller offer and liability target fixture in `backend/src/seeds/deal_room.json`
 - [x] T010 [US1] Route existing tradeoff simulation through the full evaluator in `backend/src/services/simulation_service.py`
 - [x] T011 [US1] Return score, feasibility, hard failures, and trade-offs from `simulate_tradeoff` in `backend/src/mcp/tools.py`
 - [x] T012 [US1] Add restrictive-offer MCP simulation test in `backend/tests/test_mcp_simulation.py`
 - [x] T013 [US1] Render schema-driven hard-constraint result that blocks approval in `frontend/src/renderer/SchemaRenderer.tsx`
 - [x] T014 [US1] Render "Next Best Negotiation Move" after Decision Twin evidence in `frontend/src/renderer/SchemaRenderer.tsx`
 - [x] T015 [US1] Wire restrictive-offer loading and evaluation result state in `frontend/src/App.tsx`

**Checkpoint**: The restrictive offer cannot be mistaken for acceptable because of its low price.

---

## Phase 4: User Story 2 - Propose a Strategic Counteroffer (Priority: P2)

**Goal**: Let an external agent complete discover-read-evaluate-propose through WebMCP and leave a human-approved proposal.

**Independent Test**: Invoke only published MCP tools to retrieve deal and constraints, evaluate the offer, and create a pending counteroffer.

 - [x] T016 [P] [US2] Register `get_current_deal` and `get_constraints` tool definitions in `backend/src/mcp/server.py`
 - [x] T017 [P] [US2] Implement typed current-deal and constraints handlers in `backend/src/mcp/tools.py`
 - [x] T018 [US2] Register and implement `evaluate_offer` through the shared evaluator in `backend/src/mcp/server.py`
 - [x] T019 [US2] Implement `propose_counteroffer` validation and pending approval state in `backend/src/mcp/tools.py`
 - [x] T020 [US2] Record started, completed, and failed tool calls as activity events in `backend/src/mcp/tools.py`
 - [x] T021 [US2] Add discovery, hard-failure, incomplete-proposal, and pending-approval tests in `backend/tests/test_agent_native_workflow.py`
 - [x] T022 [US2] Render schema-driven Agent Activity log in `frontend/src/renderer/SchemaRenderer.tsx`
 - [x] T023 [US2] Add pending, approve, and reject counteroffer transitions in `frontend/src/store/index.ts`
 - [x] T024 [US2] Connect WebMCP activity and human proposal actions in `frontend/src/App.tsx`

**Checkpoint**: Agents have no hidden deal-action path, and a human remains final approver.

---

## Phase 5: User Story 3 - Compare Decision Alternatives (Priority: P2)

**Goal**: Make Current Deal, Counter A, and Counter B quickly comparable by decision evidence.

**Independent Test**: Load three alternatives and compare score, hard status, trade-offs, and Term/Current/Target/Status in one schema-rendered view.

- [x] T025 [US3] Add typed current deal and two-counteroffer comparison state in `frontend/src/store/index.ts`
- [x] T026 [US3] Add schema-driven term table with Term, Current, Target, and Status columns in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T027 [US3] Add schema-driven Current Deal, Counter A, and Counter B comparison node in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T028 [US3] Supply evaluated comparison alternatives through active schema data in `backend/src/seeds/deal_room.json`
- [x] T029 [US3] Compose table and comparison nodes in `frontend/src/App.tsx`

**Checkpoint**: A deal owner can compare three alternatives without scanning bloated term cards.

---

## Phase 6: User Story 4 - Publish a Safety-Focused UX Mutation (Priority: P3)

**Goal**: Let Wire-Agent preview and publish hard-constraint warning banners without altering Decision Twin behavior.

**Independent Test**: Preview and publish a warning-banner mutation as v2, then prove the restrictive offer evaluates exactly as it did on v1.

- [x] T030 [US4] Register `inspect_ui_schema`, `preview_ui_mutation`, and `publish_ui_mutation` in `backend/src/mcp/server.py`
- [x] T031 [US4] Add schema inspection and preview-only mutation handlers in `backend/src/mcp/tools.py`
- [x] T032 [US4] Guard schema patches against deal, constraint, evaluator, approval, and strategy fields in `backend/src/mcp/handlers.py`
- [x] T033 [US4] Require reviewed preview and matching base version before publishing in `backend/src/mcp/handlers.py`
- [x] T034 [US4] Add v1/v2 decision-invariance and forbidden-mutation tests in `backend/tests/test_agent_native_workflow.py`
- [x] T035 [US4] Render schema-mutation preview, approval, and published version state in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T036 [US4] Add Wire-Agent preview-to-publish demonstration action in `frontend/src/App.tsx`

**Checkpoint**: A published visual warning improvement leaves Decision Twin output untouched.

---

## Phase 7: Visible React Flow DAG and Cross-Cutting Validation

**Purpose**: Complete the requested live WebMCP workflow explanation and validate all vertical slices.

- [x] T037 Add canonical React Flow nodes and edges for discover, read, evaluate, reason, propose, and approve in `frontend/src/store/index.ts`
- [x] T038 Implement schema-rendered `agent-workflow-dag` with selectable `@xyflow/react` nodes and directed edges in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T039 Project activity events onto active, completed, and failed DAG nodes with request/result details in `frontend/src/renderer/SchemaRenderer.tsx`
- [x] T040 [P] Add DAG and activity-log schema configuration in `backend/src/seeds/deal_room.json`
- [x] T041 Integrate visible DAG into active schema rendering in `frontend/src/App.tsx`
- [x] T042 [P] Update demonstration and validation instructions in `docs/walkthrough.md`
- [x] T043 Run Decision Twin and WebMCP tests in `backend/tests/test_decision_twin.py` and `backend/tests/test_agent_native_workflow.py`
- [x] T044 Run lint and production build from `frontend/package.json`
- [x] T045 Execute the three end-to-end scenarios in `specs/003-agent-native-deal-room/quickstart.md`

## Dependencies & Execution Order

- Phase 1 enables testing and graph tooling.
- Phase 2 blocks all stories because it defines the sole deterministic evaluation contract and frontend activity types.
- US1 is the MVP and should stabilize the decision contract before US2 integration.
- US2 depends on Phase 2 and US1 outcome semantics.
- US3 depends on Phase 2 data shapes and can proceed in parallel with US2 once US1 is stable.
- US4 depends on Phase 2 and is otherwise independent.
- Phase 7 depends on US2 activity events and completes after all selected stories.

## Parallel Opportunities

- T002 and T003 can run in parallel.
- T016 and T017 can run in parallel because they affect registration and handlers separately.
- T025 and T028 can run in parallel after Phase 2.
- T040 and T042 can run in parallel with DAG implementation.

## Implementation Strategy

1. Complete Phase 1 and 2, then deliver and validate US1 as the MVP.
2. Add the WebMCP proposal path in US2 and decision comparison in US3 as focused increments.
3. Add Wire-Agent mutation safeguards in US4.
4. Finish with the live React Flow DAG and quickstart scenarios, ensuring the graph explains actual tool execution rather than a static simulation.
