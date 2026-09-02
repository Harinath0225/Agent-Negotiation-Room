# Feature Specification: Agent-Native Deal Room

**Feature Branch**: `003-agent-native-deal-room`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Redefine Nexus Deal Room as an Agent-Native Deal Room: a machine-readable decision environment operated by people and external agents through WebMCP."

## Product Positioning

Nexus Deal Room is an Agent-Native Deal Room, not an autonomous contract negotiation product. It is a machine-readable decision environment in which people and external agents work from the same deal facts, constraints, and decision outcomes. External agents discover and use the Deal Room's published WebMCP actions rather than relying on private integrations.

The Decision Twin provides transparent, deterministic feasibility, risk, score, and hard-constraint outcomes. An agent uses those facts to formulate negotiation strategy; it does not replace the Decision Twin or silently make the final deal decision. This differentiates Nexus from AI contract negotiators that autonomously optimize or accept agreements without making the governing decision logic and agent actions visible.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Evaluate a Restrictive Offer (Priority: P1)

As a deal owner, I can review a seller's low-cost but restrictive offer and see the Decision Twin identify whether it is feasible before approving a response.

**Why this priority**: Reliable, explainable decision support is the core value of the Deal Room.

**Independent Test**: Present an offer below the target price but above the liability limit and confirm that the hard failure, score, and affected term are visible before a response can be approved.

**Acceptance Scenarios**:

1. **Given** an offer with a liability cap above the deal's allowed maximum, **When** it is evaluated, **Then** the Decision Twin reports a hard failure that identifies the violated liability constraint and does not represent the offer as acceptable solely because of its price.
2. **Given** an evaluated offer, **When** the Decision Twin finds no hard failure, **Then** the deal owner can compare its score and trade-offs with the current deal before deciding whether to proceed.

---

### User Story 2 - Propose a Strategic Counteroffer (Priority: P2)

As an authorized external agent, I can discover the Deal Room's available actions, read the current deal and constraints, evaluate an offer, and tee up a counteroffer for human approval.

**Why this priority**: Agent operability through discoverable WebMCP actions is the defining product capability.

**Independent Test**: Use only the published WebMCP actions to retrieve the deal, retrieve constraints, evaluate a restrictive offer, and submit a counteroffer proposal without using a private backend interface.

**Acceptance Scenarios**:

1. **Given** an external agent has access to the Deal Room, **When** it discovers the available actions, **Then** it can identify actions for the current deal, constraints, offer evaluation, and counteroffer proposals.
2. **Given** the Decision Twin flags a hard liability failure, **When** an agent proposes trading a higher price for a compliant liability cap or other needed flexibility, **Then** the proposal is presented to a human for approval and is not applied automatically.
3. **Given** an agent executes a Deal Room action, **When** a human is viewing the same deal, **Then** the action and its outcome appear in the Agent Activity log.

---

### User Story 3 - Compare Decision Alternatives (Priority: P2)

As a deal owner, I can rapidly compare the current deal and proposed counteroffers so that the Decision Twin's evidence is the focal point of negotiation.

**Why this priority**: Comparison prevents agents or people from optimizing one term while overlooking constraints or risk.

**Independent Test**: Evaluate the current deal and two counteroffers, then confirm that their scores, hard failures, and material trade-offs can be compared in one view.

**Acceptance Scenarios**:

1. **Given** a current deal and two evaluated counteroffers, **When** the owner opens the comparison, **Then** Current Deal, Counter A, and Counter B each show a score and constraint status.
2. **Given** deal terms are displayed, **When** the owner scans them, **Then** each material term shows its current value, target value, and status in a compact comparison table.

---

### User Story 4 - Publish a Safety-Focused UX Mutation (Priority: P3)

As a human administrator, I can ask Wire-Agent to make hard constraints impossible to overlook, review its schema-based preview, and publish the approved visual change as version 2 without altering negotiation rules.

**Why this priority**: This demonstrates that agent-native operation includes controlled evolution of the human interface, not just deal negotiation.

**Independent Test**: Ask Wire-Agent for prominent hard-constraint warnings, inspect its discovered schema and preview, then publish version 2 and verify that the Decision Twin returns identical results for the same offer.

**Acceptance Scenarios**:

1. **Given** users have missed a hard liability constraint, **When** the administrator requests a visual safety improvement, **Then** Wire-Agent reads the live schema through WebMCP and proposes warning banners for hard constraints.
2. **Given** Wire-Agent has proposed a visual mutation, **When** the administrator opens the preview, **Then** the preview shows the new warnings before publication.
3. **Given** the administrator publishes version 2, **When** a previously evaluated offer is evaluated again, **Then** its score and constraint outcome are unchanged by the visual update.

### Edge Cases

- An unavailable or failed external agent action records a clear failed outcome in Agent Activity and leaves the current deal unchanged.
- A counteroffer with incomplete terms is not eligible for approval and identifies the missing information.
- Two alternatives with the same score remain distinguishable by their hard-constraint status and listed trade-offs.
- A proposed interface mutation that changes decision behavior cannot be published as a visual-only update.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST serve a shared deal experience for human users and authorized external agents.
- **FR-002**: The system MUST expose discoverable WebMCP actions for retrieving the current deal, retrieving constraints, evaluating offers, and proposing counteroffers.
- **FR-003**: External agents MUST be able to complete the supported deal-evaluation workflow exclusively through the published WebMCP actions, without a secret backend API.
- **FR-004**: The Decision Twin MUST produce deterministic scores, feasibility findings, trade-offs, and hard-constraint violation results for the same deal input.
- **FR-005**: The Decision Twin MUST identify every hard-constraint violation by the affected term and the governing limit.
- **FR-006**: The system MUST keep strategic recommendation separate from deterministic evaluation: agents may formulate proposals from Decision Twin outcomes, while a human approves or rejects proposed counteroffers.
- **FR-007**: The system MUST display a dense term comparison with Term, Current, Target, and Status for material deal terms.
- **FR-008**: The system MUST show a visible Agent Activity log containing the timestamp, WebMCP action, outcome, and concise result of each agent action for the active deal.
- **FR-009**: The system MUST support side-by-side comparison of the Current Deal and at least two evaluated counteroffers, including each alternative's score and constraint status.
- **FR-010**: The system MUST label the strategic recommendation experience as "Next Best Negotiation Move."
- **FR-011**: The system MUST allow Wire-Agent to inspect the published live interface schema through WebMCP and propose a previewable visual mutation.
- **FR-012**: The system MUST require human review before a proposed interface mutation is published as a new version.
- **FR-013**: The system MUST reject or flag a proposed visual mutation that changes Decision Twin rules or negotiation behavior.

### Key Entities *(include if feature involves data)*

- **Deal**: The active negotiation context, including current terms, targets, participants, and approval state.
- **Constraint**: A governing deal limit, classified as hard or advisory, with its term, limit, and status.
- **Decision Twin Evaluation**: The deterministic assessment of one deal alternative, including score, feasibility, violations, and trade-offs.
- **Counteroffer Proposal**: An agent- or human-originated alternative that awaits human approval.
- **Agent Activity Event**: A visible record of an external agent's WebMCP action and outcome for a deal.
- **Interface Mutation**: A previewable proposal to change the Deal Room's schema-defined presentation, tracked by version and publication status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a usability test, at least 95% of deal owners identify a hard liability violation before approving or rejecting the restrictive-offer scenario.
- **SC-002**: A deal owner can compare the Current Deal and two counteroffers, including score and constraint status, in under 60 seconds.
- **SC-003**: For 100 repeated evaluations of identical inputs, the Decision Twin returns the same score and hard-constraint findings every time.
- **SC-004**: In the restrictive-offer demonstration, 100% of external-agent actions needed to evaluate and propose the trade-off are visible in Agent Activity with a result.
- **SC-005**: An administrator can preview and publish the hard-constraint warning version without changing the Decision Twin outcome for the fixed demonstration offer.

## Assumptions

- Authorized external agents can access the Deal Room in the same governance context as the human deal owner.
- The initial demonstration uses a liability cap of 1.5x as a hard constraint and a low-price restrictive seller offer.
- Counteroffers remain proposals until a human explicitly approves them.
- The first Wire-Agent mutation scope is limited to presentation changes, including hard-constraint warning banners.
- Existing deal records and authorization practices remain in use for this feature.