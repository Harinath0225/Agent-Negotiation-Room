# Implementation Plan: nexus-deal-room

**Branch**: `001-nexus-deal-room` | **Date**: 2026-09-02 | **Spec**: [spec.md](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/specs/001-nexus-deal-room/spec.md)

**Input**: Feature specification from `/specs/001-nexus-deal-room/spec.md`

## Summary

Build "Nexus Deal Room", an AI-assisted contract negotiation platform featuring a 100% schema-driven UI and strict WebMCP compliance. The system supports two distinct agents: the User Agent (assisting end-users with tradeoffs via a Decision Twin) and the Wire-Agent (assisting admins with live UI redesigns).

## Technical Context

**Language/Version**: Python 3.11+, TypeScript

**Primary Dependencies**: FastAPI, React, Tailwind CSS, Zustand, Microsoft Agentic AI Framework, MCP SDK

**Storage**: SQLite (MVP)

**Testing**: pytest, Jest

**Target Platform**: Web Browser

**Project Type**: web-application

**Performance Goals**: N/A

**Constraints**: Strict WebMCP client-server architecture; no hardcoded React components for core app (100% JSON schema-driven).

**Scale/Scope**: Hackathon MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] WebMCP Mandate strictly followed for agent communication.
- [x] Schema-Driven UI mandate followed.
- [x] Tech stack aligns with Constitution (FastAPI, React, Tailwind, Zustand).

## Project Structure

### Documentation (this feature)

```text
specs/001-nexus-deal-room/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (to be generated)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/ (SQLite schemas)
│   ├── mcp/ (WebMCP server endpoints & tools)
│   ├── twin/ (Decision Twin logic)
│   └── api/ (Standard REST for frontend)
└── tests/

frontend/
├── src/
│   ├── renderer/ (JSON Schema to React engine)
│   ├── store/ (Zustand state)
│   └── components/ (Base primitive components only)
└── tests/

agents/
├── src/
│   ├── wire_agent.py (Admin UI Mutator)
│   └── user_agent.py (Negotiation Assistant)
```

**Structure Decision**: A monolithic repository containing three distinct applications: the FastAPI backend, the React frontend, and the Agent CLI scripts.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
