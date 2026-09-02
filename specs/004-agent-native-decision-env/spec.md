# Feature Specification: Agent-Native Decision Environment

**Feature ID**: `004-agent-native-decision-env`  
**Root Spec Reference**: [`01_spec.md`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/01_spec.md)  
**Status**: APPROVED FOR PLANNING  

## Executive Summary

Realign Nexus Deal Room to an **Agent-Native Decision Environment**. This architecture establishes a closed 4-node decision loop (Constraint Kitchen $\rightarrow$ Decision Twin $\rightarrow$ Agentic Strategist $\rightarrow$ Negotiation Room Execution), while maintaining 100% backward compatibility and zero breaking changes across existing FastAPI endpoints, FastMCP tools, schema rendering, and test suites.

## Core Requirements & Section Mapping

1. **The Core Architecture (The Decision Loop)**
   - Node 1: Constraint Kitchen (Natural Language Intent $\rightarrow$ Dynamic Weights)
   - Node 2: Decision Twin (Deterministic Evaluation Engine $\rightarrow$ Scores, Hard Limits)
   - Node 3: Agentic Strategist (LLM Strategy $\rightarrow$ Multi-step Negotiation Plans)
   - Node 4: Negotiation Room Execution (WebMCP Tool Execution + Human Sign-off)

2. **Feature Deep-Dive**
   - Natural language compiler converting priority text to normalized weights ($w_i$).
   - High decision density UI (Term Table & 3-Way Alternative Matrix).
   - Live WebMCP streaming and interactive React Flow DAG (@xyflow/react).
   - Wire-Agent Experience Studio presentation-only mutation with strict immutability guards.

3. **The 7-Step Killer Demo Narrative**
   - Step 1: Human intent in Constraint Kitchen.
   - Step 2: Agent 3-step strategy.
   - Step 3: Counterparty roadblock (Liability failure $< 1.5x$).
   - Step 4: Agent dynamic replan across payment/timeline dimensions.
   - Step 5: Decision Twin 3-way alternative generation.
   - Step 6: Human approval & WebMCP execution.
   - Step 7: Wire-Agent UI redesign (schema v2 $\rightarrow$ v3).

4. **Alignment & Non-Breaking Strategy**
   - Preserve existing files: `decision_logic.py`, `server.py`, `handlers.py`, `store/index.ts`, `SchemaRenderer.tsx`.
   - All 37 pytest backend tests and frontend build remain 100% passing.
