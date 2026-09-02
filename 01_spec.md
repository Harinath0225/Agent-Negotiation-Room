# Specification: Nexus Deal Room — Agent-Native Decision Environment

**Document ID**: `01_spec.md`  
**Feature Directory**: `specs/004-agent-native-decision-env`  
**Status**: DRAFT / APPROVED FOR PLANNING  
**Core Architectural Pivot**: Shift from a generic conversational "AI negotiator" to an **Agent-Native Decision Environment** powered by deterministic simulation, natural language intent compilation, protocol-bound WebMCP execution, and visual schema meta-mutation.

---

## 1. The Core Architecture (The Decision Loop)

The **Nexus Deal Room** is structured around a closed-loop, machine-readable 4-node execution machine called **The Decision Loop**. This loop separates human strategic intent from deterministic risk computation, LLM tactical reasoning, and WebMCP protocol execution.

```
                   +---------------------------------------+
                   |  1. Constraint Kitchen (Intent)       |
                   |  Human natural language intent        |
                   |  --> Dynamic mathematical weights     |
                   +-------------------+-------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |  2. Decision Twin (Simulation)        |
                   |  Deterministic evaluation engine      |
                   |  --> Scores, hard limits & trade-offs |
                   +-------------------+-------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |  3. Agentic Strategist (Strategy)     |
                   |  LLM reasoning over Twin outputs      |
                   |  --> Multi-step negotiation plans     |
                   +-------------------+-------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |  4. Negotiation Room (Execution)      |
                   |  WebMCP Tool Execution + Human Sign-off|
                   |  --> live schema render & audit log   |
                   +---------------------------------------+
```

### The 4 Nodes

1. **Constraint Kitchen (Intent)**:
   - **Role**: The human intent compiler where dealmakers state priorities in plain language (e.g., *"Closing fast is critical; flexibility on price is allowed if liability cap stays above 1.5x"*).
   - **Function**: Translates qualitative statements into quantitative constraint weights ($w_i$), target ranges, and strict hard boundary rules.

2. **Decision Twin (Simulation)**:
   - **Role**: The single source of truth for financial and legal reality.
   - **Function**: A deterministic Python engine (`backend/src/twin/decision_logic.py`) that evaluates contract terms against weighted constraints, calculating feasibility, acceptance probability ($0\text{--}100\%$), risk score deltas, and hard limit violations (e.g., liability cap $< 1.5\times$ contract value).

3. **Agentic Strategist (Strategy)**:
   - **Role**: The tactical reasoning agent (Microsoft Agentic AI / Vertex AI Gemini).
   - **Function**: Reads the Decision Twin's deterministic output (not raw subjective text), devises multi-step negotiation tactics, replans dynamically when roadblocks occur, and invokes WebMCP tools.

4. **Negotiation Room (Execution)**:
   - **Role**: The interactive, protocol-bound execution environment.
   - **Function**: Executes WebMCP tool calls, streams tool calls into a live **Agent Activity Log**, renders dense comparison tables, and enforces **Human-in-the-Loop Approval** boundaries before binding counteroffers.

---

## 2. Feature Deep-Dive

### 2.1 Constraint Kitchen (Intent Translation)
- **Problem**: Traditional contract software forces users to fill rigid form fields or leaves priorities hidden in unstructured chat.
- **Solution**: Natural Language to Mathematical Weight Compiler.
- **Mechanism**:
  - Takes natural language inputs (e.g., *"Speed is more important than budget right now"*).
  - Adjusts normalized weight distributions across material terms:
    - Baseline: $\text{PRICE: } 35\%, \text{SPEED: } 15\%, \text{LIABILITY: } 30\%, \text{PAYMENT: } 20\%$
    - Compiled: $\text{PRICE: } 25\%, \text{SPEED: } 35\%, \text{LIABILITY: } 30\%, \text{PAYMENT: } 10\%$
  - Emits dynamic configuration payload into backend Decision Twin state without modifying core math logic.

### 2.2 Decision Twin (Deterministic Truth Engine)
- **Problem**: Non-deterministic LLM hallucinations in financial/legal scoring create unquantifiable enterprise risk.
- **Solution**: 100% deterministic score & constraint evaluator with high **Decision Density**.
- **Outputs**:
  - **Overall Score**: Weighted acceptance probability ($0\text{--}100\%$).
  - **Feasibility Flag**: Boolean `is_feasible` (`False` immediately if any hard constraint is breached).
  - **Hard Limit Failures**: Array of non-negotiable breaches (e.g., `["Liability Cap: 0.8x is below non-negotiable minimum 1.5x"]`).
  - **Trade-Off Recommendations**: Strategic guidance for next best move.
- **Decision Density UI**: Renders dense comparison views:
  - **Term Table**: `Term`, `Current`, `Target`, `Status` (compliances vs. hard failure badges).
  - **3-Way Alternative Matrix**: Side-by-side comparison of `Current Deal`, `Counter Proposal A` (Next Best Move), and `Restrictive Seller Offer`.

### 2.3 Agentic Strategist (Live Activity & WebMCP Streaming)
- **Problem**: Users do not trust "black box" background agent actions.
- **Solution**: Observable WebMCP execution pipeline.
- **Mechanism**:
  - Agent consumes Decision Twin evaluation results via WebMCP tool calls (`get_current_deal`, `get_constraints`, `evaluate_offer`, `propose_counteroffer`).
  - Formulates a 3-step tactical plan (e.g., 1. Anchor on delivery; 2. Offer \$105k price concession; 3. Require 1.5x liability).
  - Streams tool call start, arguments, and completion events into the **Agent Activity Log**.
  - Projects execution progress onto the visible **React Flow Execution DAG** (`@xyflow/react`).

### 2.4 Wire-Agent Experience Studio (Schema Meta-Mutation)
- **Problem**: UI requirements evolve during negotiations, but custom frontend code edits can break underlying business logic.
- **Solution**: Presentation-only Schema Meta-Mutation via WebMCP.
- **Mechanism**:
  - Wire-Agent (Admin/UI Agent) inspects schema via `inspect_ui_schema`.
  - Stages visual-only updates via `preview_ui_mutation` (e.g., adding high-contrast danger borders for hard limit violations).
  - Publishes layout updates via `publish_ui_mutation` (bumping schema version v2 $\rightarrow$ v3).
  - **Safety Guard**: Backend handler (`backend/src/mcp/handlers.py::validate_presentation_patch`) strictly blocks any patch attempting to mutate `/deal/`, `/constraints/`, `/evaluation/`, `/approval/`, or `price` fields. Decision Twin outputs remain **100% invariant**.

---

## 3. The Killer Demo Flow (7-Step Hackathon Narrative)

The application demonstrates an end-to-end hackathon narrative:

```
+-----------------------------------------------------------------------------------+
| STEP 1: Human sets intent in Constraint Kitchen ("Speed > Budget")               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 2: Agent creates 3-step strategy (Anchor delivery -> Concede price -> Sign)  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 3: Counterparty Roadblock occurs (Seller refuses liability change < 1.5x)    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 4: Agent dynamically replans (Switches negotiation dimension to payment/time)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 5: Decision Twin generates 3 alternative scenarios (Current, Counter A, Alt B)|
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 6: Human approves Counter A ($105k, 1.5x) -> WebMCP executes proposal        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| STEP 7: Wire-Agent redesigns UI (High-contrast hard constraint banner) v2 -> v3   |
+-----------------------------------------------------------------------------------+
```

### Detailed Steps

1. **Human Sets Intent in Constraint Kitchen**:
   - User types: *"Delivery speed is our top priority for Phase 1. We can concede up to \$15k on price if timeline is guaranteed within 90 days."*
   - System updates weight distribution: `SPEED: 35%`, `PRICE: 25%`.

2. **Agent Creates 3-Step Negotiation Strategy**:
   - Agent calls `get_constraints` and `evaluate_offer`.
   - Generates plan: 1. Confirm 90-day delivery timeline; 2. Propose \$105,000 price concession; 3. Retain 1.5x liability cap.

3. **Counterparty Roadblock Occurs**:
   - Seller submits a restrictive counteroffer (\$95,000 price, but liability dropped to 0.8x).
   - Decision Twin evaluates offer and flags **HARD FAILURE**: `is_feasible = False` due to liability violation.

4. **Agent Dynamically Replans**:
   - Agent detects hard failure, abandons single-dimension price concessions, and pivots to trading payment terms (Net 30) for liability compliance (1.5x).

5. **Decision Twin Generates 3 Alternative Scenarios**:
   - Renders 3-way matrix:
     1. *Current Deal* (\$120k, 2.0x liability, 50% score)
     2. *Counter Proposal A* (\$105k, 1.5x liability, 65% score — **Next Best Move**)
     3. *Restrictive Seller Offer* (\$95k, 0.8x liability, 36% score — **Hard Failure**)

6. **Human Approves Scenario & WebMCP Executes**:
   - Human dealmaker clicks **`✓ Approve`** on Counter Proposal A (\$105,000).
   - Approval state updates to `APPROVED`, DAG node `6. Human Approval` completes green, and WebMCP records official proposal submission.

7. **Wire-Agent Redesigns UI (UX Evolution)**:
   - Admin triggers Wire-Agent to enhance hard constraint visibility.
   - Wire-Agent previews (`mut-wire-01`) and publishes schema v3 with prominent danger styling on hard violations.
   - Safety validation confirms Decision Twin output for Contract #1042-B is 100% identical before and after UI mutation.

---

## 4. Alignment & Non-Breaking Contract Strategy

To preserve all existing working code and functionality while realigning to this specification:

### Preserved & Realigned System Assets

| Asset / File | Current Functionality | Alignment to New Spec |
| :--- | :--- | :--- |
| `backend/src/twin/decision_logic.py` | Evaluates terms, hard limit 1.5x liability, score computation | Preserved 100%. Serves as Node 2 (Decision Twin) truth engine. |
| `backend/src/mcp/server.py` | FastMCP server exposing tools | Preserved 100%. Exposes tools for Node 3 (Agent) and Node 4 (Execution). |
| `backend/src/mcp/handlers.py` | Safety validator for presentation patches | Preserved 100%. Enforces Wire-Agent immutability guard. |
| `frontend/src/store/index.ts` | Zustand store with deal, alternatives, DAG, proposals | Preserved 100%. Extended with intent weight compiler state. |
| `frontend/src/renderer/SchemaRenderer.tsx` | Schema-driven renderer (`term-table`, `deal-comparison`, `agent-workflow-dag`) | Preserved 100%. Adds `constraint-kitchen` node. |
| `backend/src/seeds/deal_room.json` | Active UI schema seed (v2) | Preserved & upgraded to include `constraint-kitchen` and `agent-workflow-dag`. |

### Zero Breaking Changes Guarantee
- **API Endpoints**: `GET /api/ui-schema`, `POST /api/simulations/tradeoff`, `POST /api/mcp/messages` remain unchanged.
- **Schema Engine**: Backward compatibility maintained for all existing schema node types (`simulation-control`, `simulation-result`, `hard-constraint-result`, `next-best-move`, `proposal-approval`, `agent-activity-log`, `agent-workflow-dag`, `schema-mutation-panel`).
- **Automated Tests**: All 37 pytest backend tests and frontend production build pipeline (`npm run build`) remain 100% passing.

---

## 5. Functional Requirements & Acceptance Criteria

### Requirement 1: Intent Weight Compiler (Constraint Kitchen)
- **User Story**: As a dealmaker, I want to type natural language priorities so that the Decision Twin adjusts mathematical weights dynamically.
- **Acceptance Criteria**:
  1. Submitting text containing speed/timeline emphasis increases `SPEED` weight by at least 15%.
  2. Total weight distribution remains normalized to 100%.
  3. Re-evaluating alternatives with compiled weights immediately updates relative score rankings.

### Requirement 2: Decision Density Alternatives Matrix
- **User Story**: As a dealmaker, I want a 3-way decision comparison so that I can evaluate tradeoffs without reading verbose documents.
- **Acceptance Criteria**:
  1. Displays Current Deal, Counter A, and Restrictive Offer side-by-side.
  2. Clearly displays price, score, feasibility badge, trade-off move, and hard failure warnings.
  3. Selecting an alternative updates Zustand comparison state deterministically.

### Requirement 3: WebMCP Protocol Security & Invariance Guard
- **User Story**: As a platform administrator, I want UI mutation tools guarded so that AI presentation tweaks cannot alter underlying legal terms.
- **Acceptance Criteria**:
  1. Schema patches attempting to mutate `/deal/`, `/constraints/`, `/evaluation/`, or `price` return 400 validation error.
  2. Presentation-only patches (Tailwind styles, titles, banners) preview as staged mutations and publish as schema v3.
  3. Decision Twin evaluation results on schema v1, v2, and v3 are identical.

---

## 6. Success Criteria & Metrics

1. **Deterministic Repeatability**: 100 consecutive runs of Decision Twin on identical terms yield identical scores and hard failure lists (0 variance).
2. **Safety Enforcement**: 100% of illegal presentation patch attempts targeting business terms are blocked.
3. **Execution Observability**: Every WebMCP tool call logs an activity event and updates the visible `@xyflow/react` DAG within $< 50\text{ms}$.
4. **Codebase Health**: 0 TypeScript errors, 0 ESLint errors, and 37/37 passing backend tests.
