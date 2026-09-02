# Implementation Plan: Agent-Native Decision Environment

**Branch**: `004-agent-native-decision-env` | **Date**: 2026-09-02 | **Spec**: [`01_spec.md`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/01_spec.md) / [`spec.md`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/specs/004-agent-native-decision-env/spec.md)

**Input**: Feature specification from `specs/004-agent-native-decision-env/spec.md`

## Summary

Realign Nexus Deal Room into an **Agent-Native Decision Environment**. This implementation delivers a closed 4-node decision loop (Constraint Kitchen $\rightarrow$ Decision Twin $\rightarrow$ Agentic Strategist $\rightarrow$ Negotiation Room Execution). It incorporates natural language intent weight compilation, high decision density comparison views (Term Table & 3-Way Matrix), observable WebMCP tool streaming with `@xyflow/react` execution graph, and presentation-only Wire-Agent UI evolution with strict immutability guards on business terms. All changes maintain 100% backward compatibility with existing FastMCP endpoints, Zustand state, and backend tests.

## Technical Context

**Language/Version**: Python 3.13 (Backend), TypeScript 5.5 / Node.js (Frontend)  
**Primary Dependencies**: FastAPI, FastMCP, Pydantic, React 18, Vite, Tailwind CSS, Zustand, `@xyflow/react`, Google GenAI / Vertex AI  
**Storage**: In-memory SQLite / JSON seed (`backend/src/seeds/deal_room.json`)  
**Testing**: `pytest` (Backend), `eslint` + `vite build` (Frontend)  
**Target Platform**: Web (Desktop & Mobile Responsive)  
**Project Type**: Full-stack Web Application (FastAPI Backend + React Frontend + WebMCP Protocol)  
**Performance Goals**: $< 50\text{ms}$ Decision Twin evaluation time, $< 2\text{s}$ production frontend build  
**Constraints**: 100% schema-driven UI, mandatory WebMCP protocol pattern, zero breaking changes to existing 37 backend tests.  
**Scale/Scope**: 1 primary deal room scenario (Contract #1042-B) with 3 decision alternatives, 7-step demo flow.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Self-Evolving Architecture & Schema-Driven UI**: **PASS**. UI layout is rendered 100% dynamically from `backend/src/seeds/deal_room.json` via `SchemaRenderer`.
- **II. WebMCP Mandate (STRICT)**: **PASS**. All agent operations strictly use Model Context Protocol tools (`FastMCP`).
- **III. Tech Stack Constraints**: **PASS**. Built using Python FastAPI, React, Tailwind, Zustand, Vertex AI Gemini.
- **IV. Code Quality & Typing**: **PASS**. Enforces strict Python typing and TypeScript zero-error lint/build.

## Project Structure

### Documentation (this feature)

```text
specs/004-agent-native-decision-env/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── contracts/           # Phase 1 output
    └── webmcp-tools.md  # WebMCP protocol tool schemas
```

### Source Code Layout

```text
backend/
├── src/
│   ├── api/             # FastAPI simulation & schema routes
│   ├── mcp/             # FastMCP server, tools, handlers, presentation guard
│   ├── seeds/           # Active UI schema seeds (deal_room.json v2)
│   ├── services/        # Tradeoff simulation & Agentic client service
│   └── twin/            # Decision Twin deterministic logic engine
└── tests/               # 37 pytest test suites

frontend/
├── src/
│   ├── renderer/        # SchemaRenderer & node components
│   ├── store/           # Zustand state store (deal, DAG, alternatives)
│   └── App.tsx          # Action dispatcher & WebMCP browser binding
└── package.json         # React 18, Tailwind, Zustand, @xyflow/react
```

## Complexity Tracking

> **No violations**. All additions align strictly with Constitution Principles.
