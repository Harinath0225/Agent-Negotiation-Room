# Research: Modernize Deal Room

## Decision: Provide a dedicated FastAPI simulation endpoint backed by a shared service

**Rationale**: The current UI only registers an in-browser WebMCP host tool and never invokes it from the rendered deal room, so button presses cannot produce visible results. A typed application endpoint gives the UI a reliable request/response contract, while the WebMCP tool delegates to the same service to preserve agent parity.

**Alternatives considered**:

- Invoke the MCP SSE transport from the browser for every user click: rejected because the current transport is agent-oriented and does not provide a typed user-facing result lifecycle.
- Duplicate Decision Twin calculations in the frontend: rejected because it breaks server authority and can diverge from agent results.

## Decision: Render actions and workflow content from the UI schema

**Rationale**: The constitution requires the core interface to remain schema-driven. The renderer will interpret a constrained action descriptor and dynamic presentation node types, routing events into typed client state rather than forwarding nonfunctional metadata to DOM elements.

**Alternatives considered**:

- Build a hardcoded React deal-room page: rejected because it violates the schema-driven UI mandate.
- Leave action metadata as button props: rejected because browser DOM props cannot supply the requested application behavior.

## Decision: Replace continuous schema polling with an initial fetch and bounded refresh strategy

**Rationale**: The 1.5-second polling loop is the source of repeated backend logs and unnecessary requests. Initial schema retrieval plus refresh after an approved schema mutation keeps the current experience accurate without creating a user-visible log flood. Realtime delivery can be added later when a server-push contract exists.

**Alternatives considered**:

- Continue polling and hide the logs: rejected because it retains avoidable backend load and masks the problem.
- Add server push now: deferred because the feature needs a dependable simulation flow first and no event-stream contract currently exists.

## Decision: Model simulation activity as explicit client state

**Rationale**: The UI needs a readable lifecycle independent of infrastructure logs. Typed activity events allow the interface to show request, WebMCP agent, Decision Twin, and outcome stages; the workflow diagram can highlight the stage selected from the timeline.

**Alternatives considered**:

- Stream raw Uvicorn logs into the UI: rejected because they are not stable user-facing events and do not describe business outcomes.
- Persist activity events in the database: deferred; per-session activity satisfies the requested observable workflow and avoids unnecessary retention scope.

## Decision: Use Microsoft Agentic AI Framework as the backend WebMCP client integration

**Rationale**: This is a constitutional requirement and user-requested emphasis. Implement an adapter that configures the framework from environment settings and invokes registered WebMCP tools, isolating framework-specific code from the FastAPI route and Decision Twin service.

**Alternatives considered**:

- Call model-provider APIs directly: rejected because it bypasses the mandated framework and weakens WebMCP ownership.
- Treat browser `modelContext` registration as the agent integration: rejected because it is optional host capability, not a backend agent client.