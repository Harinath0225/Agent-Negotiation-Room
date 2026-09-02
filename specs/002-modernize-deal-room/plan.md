# Implementation Plan: Modernize Deal Room

**Branch**: `002-modernize-deal-room` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-modernize-deal-room/spec.md`

## Summary

Replace the unstyled schema output with a responsive operational deal-room experience, implement a visible end-to-end simulation lifecycle, and make agent interactions understandable through a bounded activity timeline and React workflow diagram. Repair the backend boundary by exposing a typed FastAPI simulation endpoint that shares the Decision Twin service with the existing WebMCP tool. Preserve schema-driven UI rendering and establish Microsoft Agentic AI Framework as the production agent client for WebMCP calls.

## Technical Context

**Language/Version**: Python 3.x backend; TypeScript 5.6 frontend

**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, MCP Python SDK, React 18, Zustand, Tailwind CSS 4, Microsoft Agentic AI Framework

**Storage**: SQLAlchemy-backed local schema store; simulation outcomes and activity are in-memory client state for this feature

**Testing**: pytest for FastAPI service and route behavior; frontend typecheck, lint, production build, and browser workflow validation

**Target Platform**: Modern desktop and mobile browsers; local FastAPI service

**Project Type**: Web application with React frontend and FastAPI backend

**Performance Goals**: Visible simulation pending state within one second; user-facing simulation result in under five seconds under local development conditions; activity timeline capped at 50 events

**Constraints**: Core UI stays backend schema-driven; all AI-agent-to-backend operations use WebMCP; no raw server log stream is rendered to users; no overlapping or horizontally scrolling primary content at desktop or mobile widths

**Scale/Scope**: One negotiation deal-room screen, one simulation workflow, a five-stage workflow diagram, and backend service/route corrections

## Constitution Check

| Principle | Design response | Status |
|---|---|---|
| Schema-driven UI | Extend the schema vocabulary and renderer rather than replacing core views with hardcoded page composition. | Pass |
| WebMCP mandate | Keep `simulate_tradeoff` as a registered MCP tool; Agentic AI invokes this tool through WebMCP. The direct FastAPI route is limited to explicit user interaction and shares the same service. | Pass |
| Required stack | Use FastAPI, React, Tailwind CSS, Zustand, and Microsoft Agentic AI Framework. | Pass |
| Quality and typing | Define typed Pydantic request/response models and TypeScript state contracts; validate unit, API, and browser behaviors. | Pass |

**Post-design re-check**: Pass. The data and interface contracts preserve all governing boundaries.

## Project Structure

### Documentation (this feature)

```text
specs/002-modernize-deal-room/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── simulation-api.md
```

### Source Code (repository root)

```text
backend/
├── requirements.txt
└── src/
    ├── api/
    │   └── simulation_routes.py
    ├── mcp/
    │   ├── server.py
    │   └── tools.py
    ├── services/
    │   ├── simulation_service.py
    │   └── agent_client.py
    └── twin/
        └── decision_logic.py

frontend/
└── src/
    ├── App.tsx
    ├── renderer/
    │   └── SchemaRenderer.tsx
    ├── store/
    │   └── index.ts
    └── styles/
        └── deal-room.css
```

**Structure Decision**: Maintain the existing web application split. Add backend service modules for shared simulation and agent behavior, extend the existing schema renderer for interactive schema node types, and use the Zustand store for simulation/activity UI state.
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
