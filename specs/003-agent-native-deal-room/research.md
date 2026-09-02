# Research: Agent-Native Deal Room

## WebMCP is the exclusive agent surface

**Decision**: Use published WebMCP tools for every agent-facing deal action.

**Rationale**: The MCP server and tool modules already provide the correct visible boundary; a private agent API contradicts the product identity.

**Alternatives considered**: Private REST agent interface, rejected because it creates a second unobservable decision path.

## Deterministic evaluation is separate from agent strategy

**Decision**: The Decision Twin returns stable score, hard failures, and trade-offs; agents use those facts to compose a pending proposal.

**Rationale**: A model must neither set evaluation results nor auto-apply a deal.

**Alternatives considered**: Model-owned scoring or auto-approval, rejected because it makes constraint enforcement non-deterministic.

## React Flow renders the visible WebMCP DAG

**Decision**: Use `@xyflow/react` inside a schema-rendered DAG node.

**Rationale**: Directed edges, selection, viewport behavior, and live node state are required to show an ADK-style flow of WebMCP calls.

**Alternatives considered**: Custom SVG, rejected due to duplicated graph behavior; static Mermaid, rejected because it cannot reflect active calls.

## Wire-Agent mutations remain presentation-only

**Decision**: Preview and publish JSON-schema patches that cannot target decision behavior.

**Rationale**: Existing schema versioning supports controlled UI evolution while an immutability guard preserves Decision Twin results.

**Alternatives considered**: Allowing evaluator/configuration mutations, rejected because the journey specifies a visual-only update.