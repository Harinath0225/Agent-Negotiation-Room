# Feature Specification: nexus-deal-room

**Feature Branch**: `001-nexus-deal-room`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Define the product specifications for 'Nexus Deal Room'. This application features two distinct user journeys and two different agents: 1. The End-User Journey (Negotiation)... 2. The Admin Journey (Experience Studio)..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The End-User Journey: Contract Negotiation (Priority: P1)

A human user uses the Nexus Deal Room to negotiate a contract. During the negotiation, they are assisted by a 'User Agent' that acts as an interface to a 'Decision Twin'. The user can ask the agent to simulate tradeoffs (e.g., "If I lower the price, how does it affect my risk?"), and the agent provides analytical insights based on the Decision Twin's simulation. 

**Why this priority**: The core value proposition of the application is AI-assisted contract negotiation.

**Independent Test**: Can be tested independently by simulating a negotiation session, posing tradeoff questions to the User Agent, and verifying that the simulated outcomes correctly reflect the Decision Twin's risk/pricing logic.

**Acceptance Scenarios**:

1. **Given** an active negotiation session, **When** the human user asks the User Agent a tradeoff question, **Then** the User Agent must query the Decision Twin and return a simulated outcome (e.g., risk assessment).

---

### User Story 2 - The Admin Journey: Experience Studio (Priority: P1)

A human admin manages the platform's UI through the "Experience Studio". They are assisted by the "Wire-Agent". When the admin requests a redesign (e.g., "Make the cancellation clause more visible"), the Wire-Agent inspects the live UI, proposes a JSON schema mutation, and generates a visual preview. The admin approves the change, and the new UI version is instantly published.

**Why this priority**: This fulfills the strict "100% schema-driven UI" constitution mandate, allowing the platform to be self-evolving without code deployments.

**Independent Test**: Can be independently tested by requesting a UI mutation from the Wire-Agent and verifying that the resulting JSON schema accurately renders the desired UI changes in the preview before approval.

**Acceptance Scenarios**:

1. **Given** the Admin Experience Studio is open, **When** the admin asks the Wire-Agent to alter a UI component, **Then** the Wire-Agent generates a mutated JSON schema and displays a visual preview.
2. **Given** a proposed UI mutation in preview, **When** the admin approves the change, **Then** the updated JSON schema is persisted and immediately applied to the live application.

---

### User Story 3 - Agent-Backend Communication via WebMCP (Priority: P1)

Both the User Agent and the Wire-Agent function as MCP Clients (Microsoft Agentic AI Framework). They request application context, trigger simulations (Decision Twin), or execute mutations (Schema UI) by communicating with the Python FastAPI backend, which acts as the MCP Server.

**Why this priority**: WebMCP is the constitutionally mandated protocol for all agent-backend interactions.

**Independent Test**: Inspect the network traffic/logs between the agent client and the backend server to confirm WebMCP protocol compliance during agent interactions.

**Acceptance Scenarios**:

1. **Given** an active agent session, **When** the AI agent issues a request to the backend, **Then** the request and the backend's response must strictly adhere to the Model Context Protocol format.

### Edge Cases

- What happens when the Wire-Agent proposes a JSON schema mutation that contains invalid Tailwind CSS classes or malformed layout structures?
- How does the system handle concurrent UI mutations if multiple admins are using the Experience Studio?
- What happens if the Decision Twin simulation fails or times out during a live negotiation?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST render all core application UI components dynamically from a JSON schema provided by the backend (Schema-Driven UI).
- **FR-002**: The frontend MUST NOT use hardcoded React components for core application features.
- **FR-003**: The backend MUST act as a Model Context Protocol (WebMCP) Server.
- **FR-004**: The AI integration MUST act as a WebMCP Client using the Microsoft Agentic AI Framework.
- **FR-005**: AI model requests MUST be routed through GCP Vertex AI (using OpenAI models).
- **FR-006**: The system MUST support two distinct agent roles: 'User Agent' (for negotiations) and 'Wire-Agent' (for UI mutations).
- **FR-007**: The Wire-Agent MUST be able to mutate the JSON UI schema and provide a visual preview before publication.
- **FR-008**: The User Agent MUST be able to interface with a 'Decision Twin' to run tradeoff simulations for end-users.
- **FR-009**: The frontend MUST be implemented using React, Tailwind CSS, and Zustand.
- **FR-010**: The backend MUST be implemented using Python FastAPI.

### Key Entities

- **UI Schema**: JSON representation of the user interface layout, styling (Tailwind classes), and state bindings.
- **WebMCP Message**: Standardized payload conforming to the Model Context Protocol for client-server communication.
- **Negotiation Contract**: The core data structure representing the deal terms being negotiated.
- **Decision Twin State**: The analytical model that calculates risk, pricing, and tradeoffs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of core application feature views (including the Experience Studio) are generated exclusively from backend-supplied JSON schemas without requiring frontend deployments.
- **SC-002**: Admins can successfully modify live UI elements using natural language via the Wire-Agent with a 0% failure rate on schema syntax validation.
- **SC-003**: 100% of agent-to-backend communication strictly follows the Model Context Protocol.

## Assumptions

- The precise schema structure and vocabulary for the UI components will be defined during the planning phase.
- Standard WebMCP specifications are sufficient to handle all required agent-backend interactions (including schema mutations and Decision Twin queries) without custom protocol extensions.
- The 'Decision Twin' simulation logic will be managed by the backend.
