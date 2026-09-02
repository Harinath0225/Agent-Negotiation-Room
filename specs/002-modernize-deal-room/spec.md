# Feature Specification: modernize-deal-room

**Feature Branch**: `002-modernize-deal-room`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Modernize the Nexus Deal Room UI and UX, make contract simulations work and visible, and show WebMCP activity in a workflow diagram."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review a modern deal room (Priority: P1)

A negotiator opens a deal room and can immediately understand the contract, key commercial terms, negotiation status, and available actions in a visually coherent workspace.

**Why this priority**: The existing unstyled presentation prevents users from reading and acting on the deal with confidence.

**Independent Test**: Open a deal room at desktop and mobile widths and verify that users can identify the contract, terms, current status, and simulation action without scrolling through unstructured content.

**Acceptance Scenarios**:

1. **Given** a deal room is available, **When** a negotiator opens it, **Then** the page presents a clear contract summary, organized terms, negotiation assistance, and current deal status in a consistent visual hierarchy.
2. **Given** a user views the deal room on a narrow screen, **When** the layout adapts, **Then** all primary information and actions remain legible and usable without overlapping content or horizontal scrolling.

---

### User Story 2 - Run and understand a tradeoff simulation (Priority: P1)

A negotiator starts a proposed tradeoff simulation and can see its progress, final recommendation, and the effect on deal terms and risk without interpreting server logs.

**Why this priority**: A simulation control that gives no visible feedback makes the core negotiation workflow appear broken.

**Independent Test**: Start a simulation for a proposed contract term and verify that the interface presents a pending state followed by a completed outcome or a clear recoverable failure state.

**Acceptance Scenarios**:

1. **Given** an active deal room, **When** the negotiator requests a tradeoff simulation, **Then** the request receives a visible in-progress state within one second and duplicate submissions are prevented while it runs.
2. **Given** a simulation completes, **When** the outcome is available, **Then** the negotiator sees the proposed tradeoff, recommendation, risk impact, and relevant updated terms in the deal room.
3. **Given** a simulation cannot complete, **When** the failure is returned or times out, **Then** the negotiator sees a clear explanation and can retry the request.

---

### User Story 3 - Observe agent activity and WebMCP workflow (Priority: P1)

A negotiator can follow a concise activity timeline and an interactive workflow diagram that makes visible how their request moves between the user agent, WebMCP service, decision twin, and the resulting deal-room update.

**Why this priority**: Raw, rapidly repeating logs do not communicate what the system is doing or why a negotiation result changed.

**Independent Test**: Run a simulation and verify that its activity appears as a bounded chronological sequence and its workflow diagram advances through each participating stage.

**Acceptance Scenarios**:

1. **Given** a simulation request is submitted, **When** each workflow stage begins or completes, **Then** the activity timeline records a human-readable event with timestamp, status, and outcome.
2. **Given** a workflow event is selected, **When** the negotiator inspects it, **Then** the associated stage in the diagram and a concise description of its role are highlighted.
3. **Given** multiple simulations are performed, **When** new activity arrives, **Then** the activity view remains bounded, ordered newest first, and does not obscure the current deal details.

### Edge Cases

- A simulation response is delayed, incomplete, or contains no recommendation.
- A user starts a new simulation immediately after a prior simulation fails.
- The activity timeline receives repeated status events for the same workflow stage.
- The deal room has no available contract terms or deal data.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST present the negotiation experience in an organized, modern visual layout that separates deal context, contract terms, assistant actions, simulation results, and activity.
- **FR-002**: The system MUST preserve schema-driven rendering for all core deal-room interface elements.
- **FR-003**: The system MUST provide clear visual states for simulation readiness, submission, in-progress execution, completion, and failure.
- **FR-004**: The system MUST prevent duplicate simulation requests while an equivalent request is in progress.
- **FR-005**: The system MUST display each completed simulation's proposed change, recommendation, risk impact, and affected deal terms in user-readable language.
- **FR-006**: The system MUST provide a retry action after a failed simulation without requiring a page refresh.
- **FR-007**: The system MUST replace raw server-log presentation with a bounded, user-readable activity timeline for relevant negotiation events.
- **FR-008**: The system MUST provide an interactive workflow diagram that depicts the negotiator, user agent, WebMCP service, decision twin, and deal-room outcome as distinct stages.
- **FR-009**: The system MUST synchronize timeline events and the workflow diagram so that selecting an event highlights its corresponding stage and result.
- **FR-010**: The system MUST ensure primary deal-room content remains usable at common desktop and mobile viewport sizes.

### Key Entities

- **Simulation Request**: A negotiator's proposed contract tradeoff and its execution state.
- **Simulation Outcome**: The recommendation, risk impact, affected terms, and explanatory result returned for a request.
- **Activity Event**: A timestamped, human-readable record of a meaningful negotiation workflow stage.
- **Workflow Stage**: A named participant or step in the visible path from user request to deal-room outcome.
- **Deal Room**: The negotiation workspace containing contract context, terms, simulation controls, results, and activity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In usability testing, at least 90% of participants can identify the contract's current status, key terms, and simulation action within 30 seconds of opening the deal room.
- **SC-002**: For completed simulations, 100% of users receive a visible pending, success, or failure result without consulting developer tools or server logs.
- **SC-003**: At least 90% of participants can identify the sequence from their simulation request to its deal impact using the workflow diagram without assistance.
- **SC-004**: The deal-room primary workflow can be completed at desktop and mobile viewport sizes with no overlapping controls, clipped text, or horizontal page scrolling.
- **SC-005**: The activity timeline displays no more than 50 recent events while retaining the most recent event for each completed or failed simulation.

## Assumptions

- The existing negotiation data and decision logic provide enough information to summarize a simulation's proposed change, recommendation, risk impact, and affected terms.
- The workflow diagram describes the existing WebMCP interaction path and does not introduce a separate communication channel.
- The deal-room visual direction will align with the existing Nexus Deal Room product identity while prioritizing dense, operational information over marketing presentation.