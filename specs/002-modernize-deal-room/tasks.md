# Tasks: Modernize Deal Room

**Input**: Design documents from `specs/002-modernize-deal-room/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [simulation-api.md](contracts/simulation-api.md), and [quickstart.md](quickstart.md)

**Tests**: Automated test tasks are included because the plan requires FastAPI route/service verification. Each implementation task should use focused methods and add concise comments only at non-obvious lifecycle, error, or integration boundaries to speed debugging.

**Organization**: Tasks are grouped by user story. All file paths are repository-relative.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the dependencies and shared module locations for the FastAPI and Agentic AI work.

- [X] T001 Add the Microsoft Agentic AI Framework package and its documented runtime configuration to `backend/requirements.txt` and `backend/.env.example`.
- [X] T002 [P] Create service and API package initializers in `backend/src/services/__init__.py` and `backend/src/api/__init__.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared typed simulation boundary used by direct UI requests, WebMCP tools, and the agent client.

**CRITICAL**: No user-story integration starts until this phase is complete.

- [X] T003 Define typed simulation request, successful outcome, and safe error models with field validation in `backend/src/services/simulation_service.py`.
- [X] T004 Implement focused `resolve_proposed_price`, `build_recommendation`, and `run_tradeoff_simulation` service methods with concise error-boundary comments in `backend/src/services/simulation_service.py`.
- [X] T005 Create `POST /api/simulations/tradeoff` with explicit request validation and user-safe failure responses in `backend/src/api/simulation_routes.py`.
- [X] T006 Register the simulation router in `backend/src/main.py`.
- [X] T007 Refactor `simulate_tradeoff` to delegate to `run_tradeoff_simulation` and preserve the WebMCP response contract in `backend/src/mcp/tools.py`.
- [X] T008 Implement a focused Microsoft Agentic AI Framework WebMCP client adapter that loads configuration, connects, and invokes `simulate_tradeoff` in `backend/src/services/agent_client.py`.
- [X] T009 Add focused FastAPI service and route tests for valid, invalid, and failing simulation requests in `backend/tests/test_simulation_routes.py`.
- [X] T010 Add a WebMCP parity test confirming the registered tool returns the same simulation outcome fields in `backend/tests/test_mcp_simulation.py`.

**Checkpoint**: The typed API, shared Decision Twin service, WebMCP tool, and agent adapter are independently verifiable.

---

## Phase 3: User Story 1 - Review a Modern Deal Room (Priority: P1)

**Goal**: Deliver an organized, responsive schema-driven workspace that makes contract information and primary action immediately understandable.

**Independent Test**: Load the published schema at desktop and mobile viewport sizes and verify contract summary, terms, current status, and simulation action are visible with no overlap or horizontal page scrolling.

- [X] T011 [US1] Replace the published deal-room schema with a responsive operational layout, including summary, terms, status, action, result, activity, and workflow regions in `backend/src/seeds/deal_room.json`.
- [X] T012 [US1] Extend the schema node type definitions and focused render dispatch methods for semantic layout and status presentation in `frontend/src/renderer/SchemaRenderer.tsx`.
- [X] T013 [US1] Add the deal-room visual system, responsive grid, typography, contrast, and stable control dimensions in `frontend/src/App.css`.
- [X] T014 [US1] Load the schema once at startup and add an explicit `refreshSchema` method used only after UI-schema mutations in `frontend/src/App.tsx`.
- [X] T015 [US1] Remove the periodic schema polling lifecycle and its related stale connection logic from `frontend/src/App.tsx`.
- [X] T016 [US1] Update the schema seed/reset behavior so local development loads the modern published layout consistently in `backend/src/main.py`.

**Checkpoint**: The modern schema-driven deal room is independently usable and does not emit repeated idle schema requests.

---

## Phase 4: User Story 2 - Run and Understand a Tradeoff Simulation (Priority: P1)

**Goal**: Make simulation execution reliable and show a complete user-readable lifecycle and outcome.

**Independent Test**: Submit the default price tradeoff and observe pending, success, result details, and a disabled duplicate action; submit an invalid request and observe an error plus retry.

- [X] T017 [US2] Add typed client contracts and focused state transition methods for simulation requests, results, retries, and failures in `frontend/src/store/index.ts`.
- [X] T018 [US2] Extend the schema renderer with a constrained `simulateTradeoff` action descriptor and an explicit click dispatch method in `frontend/src/renderer/SchemaRenderer.tsx`.
- [X] T019 [US2] Implement focused `submitSimulation`, `applySimulationOutcome`, and `applySimulationFailure` methods that call the FastAPI contract in `frontend/src/App.tsx`.
- [X] T020 [US2] Render schema-bound pending, success, failure, retry, and result-detail states in `frontend/src/renderer/SchemaRenderer.tsx`.
- [X] T021 [US2] Add status-specific simulation result and retry-control styling in `frontend/src/App.css`.
- [X] T022 [US2] Verify the direct endpoint and WebMCP tool invoke the same Decision Twin calculation and recommendation fields in `backend/src/services/simulation_service.py`.

**Checkpoint**: A negotiator can complete or retry a simulation without developer tools, logs, or page refresh.

---

## Phase 5: User Story 3 - Observe Agent Activity and WebMCP Workflow (Priority: P1)

**Goal**: Turn hidden request processing into a bounded readable timeline and interactive React workflow diagram.

**Independent Test**: Run a simulation, verify events appear for all five workflow stages, and select an event to highlight its associated diagram stage and description.

- [X] T023 [US3] Define typed activity-event and workflow-stage contracts plus focused append, de-duplicate, trim, and select methods in `frontend/src/store/index.ts`.
- [X] T024 [US3] Append readable negotiator, user-agent, WebMCP, Decision Twin, and deal-room activity events at each simulation lifecycle boundary in `frontend/src/App.tsx`.
- [X] T025 [US3] Extend the schema renderer with focused `renderActivityTimeline` and `renderWorkflowDiagram` methods, selection dispatch, and accessible labels in `frontend/src/renderer/SchemaRenderer.tsx`.
- [X] T026 [US3] Add timeline state, selected-stage, and workflow connection styling in `frontend/src/App.css`.
- [X] T027 [US3] Add activity and workflow node descriptors, including stage-to-event bindings, to the published layout in `backend/src/seeds/deal_room.json`.

**Checkpoint**: The current simulation path is visible in a bounded activity timeline and selectable five-stage WebMCP workflow diagram.

---

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Finish debugging ergonomics, validate the complete journey, and ensure the implementation is production-ready.

- [X] T028 [P] Add structured request identifiers and concise integration-boundary logs without emitting idle polling noise in `backend/src/services/simulation_service.py` and `backend/src/services/agent_client.py`.
- [X] T029 [P] Update user-facing setup and validation instructions for FastAPI, frontend, and Agentic AI configuration in `README.md` and `docs/walkthrough.md`.
- [X] T030 Run the backend test suite and resolve feature-specific failures in `backend/tests/test_simulation_routes.py` and `backend/tests/test_mcp_simulation.py`.
- [X] T031 Run frontend typecheck, lint, and production build; resolve feature-specific issues in `frontend/src/App.tsx`, `frontend/src/renderer/SchemaRenderer.tsx`, `frontend/src/store/index.ts`, and `frontend/src/App.css`.
- [X] T032 Perform desktop and mobile browser validation from `specs/002-modernize-deal-room/quickstart.md` and record outcomes in `docs/walkthrough.md`.

---

## Dependencies and Execution Order

```text
Setup (T001-T002)
  -> Foundational backend and agent boundary (T003-T010)
    -> US1 modern schema-driven workspace (T011-T016)
      -> US2 working simulation lifecycle (T017-T022)
        -> US3 observable activity and workflow (T023-T027)
          -> Polish and validation (T028-T032)
```

### User Story Dependencies

- **US1** depends on the foundational typed simulation boundary only because its schema must include the shared action and result regions.
- **US2** depends on US1 because it binds interactive behavior to the modern schema regions.
- **US3** depends on US2 because its timeline reflects actual simulation lifecycle transitions.

### Parallel Opportunities

- T001 and T002 can proceed independently.
- T009 and T010 can be authored in parallel after the service and MCP delegation contract are settled.
- T028 and T029 can proceed in parallel after all stories function.

## Parallel Examples

### Foundational phase

```text
Task: "Add the Agentic AI dependency and configuration in backend/requirements.txt and backend/.env.example"
Task: "Create service and API package initializers in backend/src/services/__init__.py and backend/src/api/__init__.py"
```

### Final polish

```text
Task: "Add structured diagnostic logs in backend/src/services/simulation_service.py and backend/src/services/agent_client.py"
Task: "Update setup documentation in README.md and docs/walkthrough.md"
```

## Implementation Strategy

### MVP: Reliable Simulation and Modern Deal Room

1. Complete setup and foundational backend work.
2. Complete US1 to establish the clean, schema-driven visual surface.
3. Complete US2 and validate the FastAPI endpoint plus visible user lifecycle.
4. Demonstrate the working simulation before adding the workflow visualization.

### Incremental Delivery

1. Deliver US1 as a readable, responsive deal room without polling noise.
2. Deliver US2 as a reliable, observable simulation workflow backed by FastAPI and WebMCP parity.
3. Deliver US3 as the activity timeline and React workflow visualization.
4. Complete quality checks, browser validation, and Agentic AI Framework integration verification.

## Notes

- Every task follows the required checkbox, identifier, optional parallel marker, story label, and file-path format.
- Separate methods should own parsing, validation, state transitions, request execution, result handling, and rendering branches; comments are reserved for non-obvious integration and failure boundaries.