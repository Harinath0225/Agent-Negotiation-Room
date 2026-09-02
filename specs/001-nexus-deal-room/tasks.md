# Implementation Tasks: nexus-deal-room

## Phase 1: Foundation
**Purpose**: Project initialization and basic skeletons.

- [x] T001 Initialize Python virtual environment and FastAPI dependencies in backend/requirements.txt
- [x] T002 Create FastAPI application entrypoint in backend/src/main.py
- [x] T003 Setup initial SQLite database connection and models in backend/src/models/db.py
- [x] T004 [P] Initialize React project (Vite) with Tailwind CSS in frontend/package.json
- [x] T005 [P] Configure Zustand for frontend state management in frontend/src/store/index.ts
- [x] T006 Setup proxy configuration for React to communicate with FastAPI in frontend/vite.config.ts

## Phase 2: Schema Engine
**Purpose**: Implement the dynamic JSON renderer and backend provider.

- [x] T007 [US1] Define UISchema SQLAlchemy model in backend/src/models/schema.py
- [x] T008 [US1] Create FastAPI endpoint to fetch current UI schema in backend/src/api/schema_routes.py
- [x] T009 [P] [US1] Create recursive JSON UI renderer component in frontend/src/renderer/SchemaRenderer.tsx
- [x] T010 [US1] Integrate SchemaRenderer with Zustand to fetch and display layout from backend in frontend/src/App.tsx

## Phase 3: WebMCP Infrastructure
**Purpose**: Implement the Python MCP SDK in FastAPI and expose the tool registry.

- [x] T011 [US3] Install and configure the Python MCP SDK in backend/requirements.txt
- [x] T012 [US3] Implement WebMCP Server transport (SSE or stdio) in backend/src/mcp/server.py
- [x] T013 [US3] Register `mutate_ui_schema` tool in the MCP tool registry in backend/src/mcp/tools.py
- [x] T014 [US3] Register `simulate_tradeoff` tool in the MCP tool registry in backend/src/mcp/tools.py
- [x] T015 [US3] Connect FastAPI routing to MCP Server transport in backend/src/api/mcp_routes.py

## Phase 4: Agent Integration
**Purpose**: Connect Microsoft Agentic AI Framework to Vertex AI and the WebMCP tools.

- [x] T016 [US3] Initialize agent environments and install Microsoft Agentic AI Framework in agents/requirements.txt
- [x] T017 [US3] Create User Agent script connecting to Vertex AI and WebMCP backend in agents/src/user_agent.py
- [x] T018 [P] [US3] Create Wire-Agent script connecting to Vertex AI and WebMCP backend in agents/src/wire_agent.py
- [x] T019 [US3] Implement Decision Twin simulation logic backing the `simulate_tradeoff` tool in backend/src/twin/decision_logic.py

## Phase 5: UI & Admin Studio
**Purpose**: Build the Deal Room view and the Admin preview dashboard.

- [x] T020 [US1] Create foundational JSON UI schemas for the Deal Room negotiation view in backend/src/seeds/deal_room.json
- [x] T021 [US2] Create foundational JSON UI schemas for the Experience Studio admin view in backend/src/seeds/admin_studio.json
- [x] T022 [US2] Implement schema mutation logic in backend handling the `mutate_ui_schema` tool execution in backend/src/mcp/handlers.py
- [x] T023 [US2] Add visual preview toggles (Draft vs Published schema) in frontend/src/renderer/PreviewContext.tsx
- [x] T024 [US2] Test end-to-end Wire-Agent schema mutation and User Agent negotiation flow in docs/walkthrough.md

## Dependencies & Execution Order
- **Phase 1** must be completed first to establish the skeletons.
- **Phase 2** and **Phase 3** can be executed in parallel once Phase 1 is done, as they touch different domains (React UI rendering vs backend WebMCP infrastructure).
- **Phase 4** depends on Phase 3 (WebMCP Infrastructure) to be complete.
- **Phase 5** depends on Phase 2 and Phase 3, tying the UI mutation logic to the agent tools.
- **Phase 6 (Convergence)** depends on Phase 4 and Phase 5 to complete live LLM tool execution and live website updates.

## Phase 6: Convergence
**Purpose**: Complete live LLM engagement (Gemini / ChatGPT) with the website via WebMCP.

- [x] T025 Connect `mutate_ui_schema` tool in backend/src/mcp/tools.py to persist mutations via `handle_schema_mutation` per FR-007 (partial)
- [x] T026 Implement database seeder on FastAPI startup to load `deal_room.json` and `admin_studio.json` into SQLite per plan.md (partial)
- [x] T027 Implement active MCP Client runtime with Gemini/OpenAI tool-calling loop in agents/src/wire_agent.py and agents/src/user_agent.py per FR-004, FR-005 (partial)
- [x] T028 Add live schema polling/refresh to frontend/src/App.tsx so the website dynamically re-renders when AI mutates the schema per FR-001, FR-007 (partial)
