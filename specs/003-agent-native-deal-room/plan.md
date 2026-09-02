# Implementation Plan: Agent-Native Deal Room

**Branch**: `003-agent-native-deal-room` | **Date**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-agent-native-deal-room/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Reframe Nexus Deal Room as an agent-operable decision environment. Extend the deterministic Decision Twin to evaluate complete deal alternatives, expose its results through discoverable WebMCP tools, and record every agent action. Render the same deal state for people and agents through schema-driven React nodes, including a small React Flow DAG that visibly traces each WebMCP call.

## Technical Context

**Language/Version**: Python 3 with FastAPI; TypeScript 5.6 with React 18

**Primary Dependencies**: FastAPI, SQLAlchemy, MCP Python SDK, React, Tailwind CSS 4, Zustand 5, `@xyflow/react`, Microsoft Agentic AI Framework client

**Storage**: Existing relational storage for published UI schemas; current demo-backed deal state until durable deal persistence is introduced

**Testing**: pytest; TypeScript compilation, ESLint, and Vite production build

**Target Platform**: Modern desktop and mobile browsers with a FastAPI service

**Project Type**: Web application with an MCP server and React client

**Performance Goals**: Deterministic single-offer evaluation completes within 1 second; workflow activity reaches the UI within 250 ms of receipt

**Constraints**: No private agent business API; agents use WebMCP. Core UI is schema rendered. Visual-only mutations cannot change Decision Twin results.

**Scale/Scope**: One active demo deal, current state, two counteroffers, bounded 50-event activity history, and one Wire-Agent visual mutation flow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| Schema-driven UI | PASS | Decision table, comparison, activity log, and DAG are schema node types rendered by `SchemaRenderer`. |
| WebMCP mandate | PASS | Agent discovery, retrieval, evaluation, proposal, schema inspection, preview, and publish use MCP tools. |
| Required stack | PASS | Uses existing stack plus focused `@xyflow/react` for the requested visible DAG. |
| Quality and typing | PASS | Typed tool payloads and UI state; deterministic evaluator tests. |

## Project Structure

### Documentation (this feature)

```text
specs/003-agent-native-deal-room/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
│   ├── mcp/
│   └── twin/
└── tests/

frontend/
├── src/
│   ├── renderer/
│   └── store/
└── package.json
```

**Structure Decision**: Keep the existing web-application split. The backend owns deterministic decisions, WebMCP contracts, and schema publication. The frontend adds schema node renderers and Zustand state for the decision workspace and React Flow DAG. No private agent API is introduced.

## Delivery Slices

1. **Truth Engine**: Model alternatives and constraints; return deterministic score, hard failures, and trade-offs for the restrictive liability offer.
2. **Decision Density**: Render schema-driven term table and comparison; make hard failures prominent before approval.
3. **Agent Workflow**: Add discoverable WebMCP tools for deal, constraints, evaluation, and pending counteroffer proposals; emit activity events.
4. **Visible DAG**: Add `@xyflow/react` within a schema-rendered node. Project events to the directed path `discover -> read -> evaluate -> reason -> propose -> approve`, with live state and selected-node details.
5. **Wire-Agent UX Evolution**: Add schema inspection, visual-only preview, guarded publication, and v1/v2 decision invariance validation.

## Implementation Sequence

1. Implement typed deterministic evaluation according to [data-model.md](./data-model.md), retaining one evaluator for both browser and WebMCP paths.
2. Update tool registration and handlers according to [webmcp-workflow.md](./contracts/webmcp-workflow.md); test hard failures, incomplete proposals, and activity emission.
3. Add frontend types and Zustand transitions for alternatives, activity, and graph state.
4. Extend `SchemaRenderer` with focused nodes for the dense table, comparison, activity log, and React Flow DAG; retain the schema-rendering boundary.
5. Add approval UI and label the strategic recommendation "Next Best Negotiation Move."
6. Implement Wire-Agent schema inspection, preview, guarded publish, and regression tests proving visual changes do not affect the evaluator.
7. Run the end-to-end scenarios and commands in [quickstart.md](./quickstart.md).

## Complexity Tracking

No constitution violations require justification.
