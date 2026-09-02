# Phase 0: Research & Architecture Decisions

## Decision 1: Storage and State Management
- **Decision**: SQLite for MVP backend storage; Zustand for frontend state.
- **Rationale**: The project specification does not explicitly define the database. For a hackathon and rapid prototyping, SQLite provides sufficient relational capability without infrastructure overhead, easily scaling to PostgreSQL later. Zustand is constitutionally mandated for frontend state.
- **Alternatives considered**: PostgreSQL (too heavy for initial scaffold), In-memory (lacks persistence for UI schema mutations).

## Decision 2: WebMCP Implementation
- **Decision**: FastAPI acts as the MCP Server exposing tools and resources; Microsoft Agentic AI acts as the MCP Client.
- **Rationale**: This is a strict constitutional requirement. The frontend will likely interact with the backend via REST/WebSockets, while the Agents (User Agent and Wire-Agent) will interact with the backend via WebMCP stdio or SSE (Server-Sent Events) to access the Decision Twin and UI Schema Mutator tools.
- **Alternatives considered**: None (mandated by Constitution).

## Decision 3: Schema-Driven UI Format
- **Decision**: Custom JSON schema defining component types, props, Tailwind classes, and Zustand state bindings.
- **Rationale**: Allows the Wire-Agent to easily mutate the UI by altering the JSON. The frontend will have a generic recursive renderer that maps schema `type` (e.g., `Card`, `Button`, `Text`) to standard HTML/Tailwind elements.
- **Alternatives considered**: Existing standards like JSON Forms (too rigid, lacks Tailwind styling flexibility).
