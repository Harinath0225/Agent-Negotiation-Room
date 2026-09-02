# Phase 0 Research: Agent-Native Decision Environment

**Feature**: `004-agent-native-decision-env`  
**Date**: 2026-09-02  

## Overview

This document records technical research, architectural choices, and design rationale for realigning Nexus Deal Room into an **Agent-Native Decision Environment**.

---

## Technical Decisions & Rationale

### 1. Intent Weight Compiler (Constraint Kitchen)
- **Decision**: Parse natural language priority phrases (e.g. *"Speed > Budget"*, *"Liability is non-negotiable"*) into normalized weight multipliers ($w_i$) that adjust term scoring in the Decision Twin.
- **Rationale**: Keeps human intent high-level while ensuring the Decision Twin evaluates contract options deterministically.
- **Alternatives Considered**:
  - *Direct LLM subjective scoring*: Rejected due to lack of determinism and risk of hallucinations.
  - *Manual slider inputs*: Rejected because non-technical dealmakers prefer natural language intent declarations.

### 2. High Decision Density Comparison Matrix
- **Decision**: Render a 4-column Term Table (`Term`, `Current`, `Target`, `Status`) alongside a 3-way alternative comparison matrix (`Current Deal`, `Counter Proposal A`, `Restrictive Seller Offer`).
- **Rationale**: Eliminates text clutter, allowing human dealmakers to evaluate tradeoffs, acceptance scores, and hard constraint violations in a single glance.
- **Alternatives Considered**:
  - *Multi-tab pagination*: Rejected because comparing 3 options across tabs creates cognitive load.

### 3. Wire-Agent Presentation Safety Guard
- **Decision**: Enforce an explicit JSON Pointer blocklist (`/deal/`, `/constraints/`, `/evaluation/`, `/approval/`, `price`) in `backend/src/mcp/handlers.py::validate_presentation_patch`.
- **Rationale**: Allows Wire-Agent to enhance Tailwind CSS styling, badges, and layout banners without compromising financial or legal contract logic.
- **Alternatives Considered**:
  - *Unrestricted schema mutation*: Rejected because AI agents could inadvertently alter contract terms or scoring logic.

### 4. Visible Execution Graph (@xyflow/react)
- **Decision**: Project WebMCP tool calls directly onto a 6-stage `@xyflow/react` directed graph (`discover -> read -> evaluate -> reason -> propose -> approve`).
- **Rationale**: Provides full transparency into agent operations, giving dealmakers immediate visibility into active, completed, or failed WebMCP steps.

---

## Resolved Clarifications & Constraints

All technical context parameters are 100% resolved:
- **Backend**: Python 3.13, FastAPI, FastMCP.
- **Frontend**: React 18, Vite, Tailwind CSS, Zustand, `@xyflow/react`.
- **Integrations**: Vertex AI / Gemini API, Model Context Protocol (WebMCP).
- **Test Baseline**: 37/37 passing pytest tests, 0 ESLint / TypeScript errors.
