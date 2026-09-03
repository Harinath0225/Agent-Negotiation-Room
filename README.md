# Nexus Deal Room 🤝 ⚡
### An Agent-Native Decision Environment

> **Core Philosophy**: *"We built a decision environment that external agents can operate. The agent never invents the rules of the deal—it reasons over deterministic reality and operates strictly inside human-defined governance boundaries."*

**Nexus Deal Room** is an **Agent-Native Decision Environment** powered by a **100% schema-driven UI**, a deterministic **Decision Twin**, in-browser **WebMCP (`document.modelContext`)**, and an **Adversarial QA Suite**.

Rather than acting as an unconstrained chat bot that hallucinates terms, Nexus implements a machine-readable, closed **Decision Loop**: humans declare strategic intent, deterministic engines calculate mathematical reality, AI agents reason over structured outputs, and WebMCP executes protocol-bound actions with human-in-the-loop sign-off.

---

## 🏛️ The 4-Node Closed Decision Loop

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       1. CONSTRAINT KITCHEN (Intent)                        │
│   Humans declare priorities in plain language or quick strategy presets.    │
│   Compiler translates intent into mathematical weights (Price, Speed, Risk) │
│   and binds the Agent Governance Authority Matrix.                          │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │ Weights (w_i) & Authority Matrix
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        2. DECISION TWIN (Simulation)                        │
│   Deterministic truth engine (zero hallucination).                          │
│   Enforces non-negotiable hard limits (e.g. Liability >= 1.5x) & computes    │
│   acceptance scores (0-100) and trade-off deltas.                           │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │ Deterministic Reality
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        3. AGENTIC STRATEGIST (Strategy)                     │
│   AI reasons over deterministic twin outputs to identify the Next Best Move │
│   and formulate compliant counteroffers within its concession band.         │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │ Structured Proposal Payload
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     4. NEGOTIATION ROOM & WEBMCP (Execution)                │
│   Executes actions via in-browser WebMCP (document.modelContext) & FastMCP. │
│   Displays interactive DAG, streams tool audits, and pauses at the Human   │
│   Approval Boundary for final legal sign-off.                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features Included

### 1. 🌐 True In-Browser WebMCP (`document.modelContext`)
- **Native Browser Tool Registry**: Polyfilled and registered on `window.document.modelContext` so any autonomous agent (e.g., ChatGPT browsing agent, headless automation, or Chrome DevTools console) can discover and execute tools directly inside the page DOM:
  - `get_current_deal`
  - `get_constraints`
  - `evaluate_offer`
  - `simulate_tradeoff`
  - `propose_counteroffer`
  - `execute_contract`
  - `compile_intent`
  - `mutate_ui_schema`
  - `search_previous_deals`
- **Zero Session Friction**: Proxied via `/api/mcp/tool-call` using standard JSON-RPC 2.0 with HTTP 200 OK responses.

### 2. 🍳 3-Tier Constraint Kitchen (Policy & Authority Matrix)
- **Tier 1 (Human Intent)**: Natural language compiler with instant one-click strategy presets:
  - `⚡ Speed > Price`
  - `🛡️ Strict Liability Defense`
  - `💰 Maximize Savings`
- **Tier 2 (Compiled Weights $w_i$)**: Visual real-time distribution across **Price**, **Speed**, **Liability**, and **Payment**.
- **Tier 3 (Agent Governance Authority Matrix)**: Explicit machine-enforced boundary table:
  - *Price Concession Band ($\pm 15\%$)* $\rightarrow$ **`ALLOWED ✓`**
  - *Trade Payment Terms for Speed* $\rightarrow$ **`ALLOWED ✓`**
  - *Alter Liability Limit ($< 1.5\text{x}$)* $\rightarrow$ **`BLOCKED ✗`**
  - *Autonomous Deal Execution* $\rightarrow$ **`HUMAN ONLY ✍️`**

### 3. 🚨 Agent Governance Boundary (Demonstrating Safety in Action)
- **Hostile Proposal Interception**: Interactive trigger **`🚨 Test Governance Boundary ($95k / 0.8x)`** simulates an aggressive counterparty offer.
- **Immediate Execution Block**: The Decision Twin halts execution with a prominent red callout:
  > **🚨 AGENT GOVERNANCE BOUNDARY TRIGGERED — Execution Blocked**  
  > *Liability cap of 0.8x is strictly below the non-negotiable human policy threshold (1.5x).*
- **Adaptive Deliberation Pivot**: Demonstrates the Agent reasoning over the deterministic block and adapting its proposal:
  > *🤖 **Agent Strategic Deliberation**: "Decision Twin blocked proposal: Liability coverage violates non-negotiable hard constraint #3. Cannot accept $95,000 at this risk level. Pivoting to Payment Terms concession (Net 30) with compliant 1.5x liability at $105,000."*

### 4. 🧭 Evidence-Backed DAG Inspector (`@xyflow/react`)
- **6-Node Visual Execution Graph**: `Discover Tools` ➔ `Read Deal State` ➔ `Evaluate Offer` ➔ `Agent Strategy` ➔ `Propose Counteroffer` ➔ `Human Approval`.
- **Real Evidence on Every Node**: Clicking any node opens an inspector with concrete payloads:
  - *Node 1*: Discovered In-Browser WebMCP Tools list (`document.modelContext`).
  - *Node 2*: Baseline Contract JSON (#1042-B).
  - *Node 3*: Raw Decision Twin output (`score: 85`, `is_feasible: true`, zero hard failures).
  - *Node 4*: AI Agent Deliberation text & Formulation of Next Best Move.
  - *Node 5*: Constructed WebMCP Proposal Payload.
  - *Node 6*: Human Authority Boundary Governance Rule.

### 5. 📚 Previous Deals & Contracts System of Record (`/contracts`)
- **Pre-Seeded Enterprise Database**: 10 diverse contracts seeded in SQLite with varying counterparties, values (\$65,000 to \$520,000), and statuses (`Under Negotiation`, `Approved`, `Closed`, `Rejected`).
- **Live In-Browser WebMCP Search**: Fast agent queries via `document.modelContext.tools.search_previous_deals`:
  - Quick action pills: `Search "Apex"`, `Filter "Under Negotiation"`, `Filter "Approved"`, `High Value (> $200k)`.
  - Real-time audit event banner tracking agent queries.

### 6. 🧪 Agent QA Suite (`/agent-qa`)
- **Adversarial Decision Environment Evaluation**: The QA Agent tests whether an autonomous agent can safely and reliably operate in the application.
- **3 Targeted Adversarial Attacks**:
  1. *Boundary Breach Attack*: Probes sub-\$100k pricing with liability concessions $\rightarrow$ **`BOUNDARY_PROTECTED`** (Decision Twin halts offer).
  2. *Governance Bypass Attack*: Attempts to call `execute_contract` autonomously $\rightarrow$ **`HUMAN_GOVERNANCE_ENFORCED (403 Blocked)`**.
  3. *Schema Immutability Attack*: Attempts to modify `/price` via UI schema mutation $\rightarrow$ **`IMMUTABILITY_PRESERVED (403 Blocked)`**.
  4. *Custom Adversarial Probe*: Evaluates custom goals against live WebMCP tools.
- **Live Stream Terminal**: Logs real-time agent thoughts, tool invocations, and verdict evaluations.

### 7. 🔄 The Closed Evolution Lifecycle (Agent QA + Wire-Agent)
Demonstrates how the application continuously improves its agent experience:
```text
Agent QA (Discovers Friction in v2)
   │ "Friction: Failure telemetry in v2 was ambiguous for external agents"
   ▼
Wire-Agent (Stages UI/Schema Fix)
   │ Stages mut-wire-01: High-visibility danger outline + agent-readable telemetry
   ▼
Human Authority (Signs Off)
   │ Reviews and publishes UI Schema v3
   ▼
Agent QA (Regression Test on v3)
   │ Re-runs probe: PASSED (0 Friction, 100% Invariance Preserved)
```

### 8. 🛡️ Epilogue: Wire-Agent UX Evolution & Presentation Safety Guard
- **The Punchline**: *"The agent can change how the application communicates its decisions, but it cannot change the decisions themselves."*
- **Presentation-Only Mutations**: Stages and publishes visual Tailwind styling patches.
- **Safety Immutability Guard**: Dedicated button **`🛡️ Test Safety Guard (Attempt Forbidden Price Edit)`** proves that any patch targeting business terms is rejected with `403 Forbidden`.

---

## 🚀 How to Run the App Locally

### 1. Prerequisites
- **Python**: 3.11 or 3.13
- **Node.js**: 18+ or 20+

---

### 2. Backend Setup & Startup (FastAPI + FastMCP)

Open a terminal in the project root:

```powershell
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment (if not already created)
python -m venv .venv

# 3. Activate virtual environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Start FastAPI server with auto-reload
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Backend Services available at:
- **API Base**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **FastMCP JSON-RPC Gateway**: [http://127.0.0.1:8000/api/mcp/tool-call](http://127.0.0.1:8000/api/mcp/tool-call)
- **Active Schema Endpoint**: [http://127.0.0.1:8000/api/ui-schema](http://127.0.0.1:8000/api/ui-schema)
- **Contracts SoR Endpoint**: [http://127.0.0.1:8000/api/contracts](http://127.0.0.1:8000/api/contracts)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 3. Frontend Setup & Startup (Vite + React)

Open a second terminal in the project root:

```powershell
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies (if not already installed)
npm install

# 3. Start Vite development server
npm run dev
```

Frontend application available at:
- **Main Deal Room**: [http://localhost:5173](http://localhost:5173)
- **Previous Deals & Contracts**: [http://localhost:5173/contracts](http://localhost:5173/contracts)
- **Agent QA Suite**: [http://localhost:5173/agent-qa](http://localhost:5173/agent-qa)

---

## ☁️ Deployment to Google Cloud Run (Terraform & Workload Identity Federation)

The application includes a production-grade infrastructure-as-code suite in [`terraform/`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/terraform) to deploy **Nexus Deal Room** to **Google Cloud Run** using **GitHub Actions Workload Identity Federation (WIF)** and **Google Cloud Secret Manager**.

```text
 ┌──────────────────────────────────────────────────────────────────┐
 │                     GitHub Actions CI/CD Pipeline                 │
 └─────────────────────────────────┬────────────────────────────────┘
                                   │ OIDC Token (Zero Stored Keys!)
                                   ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │          GCP Workload Identity Pool & Provider                   │
 │   - Validates repository claim: "Harinath0225/Agent-Negotiation-Room"
 │   - Impersonates: github-actions-deployer service account        │
 └─────────────────────────────────┬────────────────────────────────┘
                                   │
               ┌───────────────────┴───────────────────┐
               ▼                                       ▼
 ┌───────────────────────────┐           ┌──────────────────────────┐
 │ Artifact Registry (Docker)│           │   Cloud Run Deployment   │
 │ - Builds & pushes image   │           │ - Deploys latest tag     │
 └───────────────────────────┘           └─────────────┬────────────┘
                                                       │
                                                       ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │               Cloud Run Service (nexus-deal-room)                │
 │   - Runtime Identity: nexus-deal-room-runner                     │
 │   - Unified Container: React SPA static frontend + FastAPI WebMCP│
 └─────────────────────────────────┬────────────────────────────────┘
                                   │ Injected strictly at container startup
                                   │ (roles/secretmanager.secretAccessor)
                                   ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │             GCP Secret Manager: `gemini-api-key`                 │
 │   - Stores sensitive Gemini / Vertex AI API key                  │
 │   - Never exposed in Git, Docker build logs, or CI/CD logs       │
 └──────────────────────────────────────────────────────────────────┘
```

### Key Security & Deployment Principles
1. **Zero Long-Lived Service Account Keys**: GitHub Actions exchanges short-lived OIDC tokens directly with Google Cloud STS via Workload Identity Federation.
2. **Strict Repository Assertion**: The WIF provider condition restricts authentication exclusively to `Harinath0225/Agent-Negotiation-Room`.
3. **Secret Manager Isolation**:
   - The Gemini API Key is provisioned into GCP Secret Manager (`gemini-api-key`).
   - The key is **fetched only via Secret Manager**: Cloud Run injects it at container startup via `value_source.secret_key_ref`, and [`backend/src/services/secrets.py`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/backend/src/services/secrets.py) resolves it via the Secret Manager client/environment.
   - Access is restricted exclusively to the runtime service account (`nexus-deal-room-runner`).
4. **Unified Container Image**: A multi-stage [`Dockerfile`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/Dockerfile) compiles the React frontend and serves both the SPA and the FastAPI WebMCP backend on port `8080` (no CORS headaches or separate hosts).

---

### Step 1: Provision Infrastructure via Terraform
```powershell
# 1. Navigate to terraform directory
cd terraform

# 2. Copy and configure variables
cp terraform.tfvars.example terraform.tfvars
# (Set project_id, region, and gemini_api_key in terraform.tfvars)

# 3. Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID

# 4. Initialize & Apply
terraform init
terraform plan
terraform apply
```

Upon completion, Terraform outputs the Cloud Run URL and the exact WIF parameters needed for GitHub Actions.

---

### Step 2: Configure GitHub Repository Secrets
In your GitHub repository (**Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**), add the following secrets:

| Secret Name | Value from `terraform output` | Description |
|---|---|---|
| `GCP_PROJECT_ID` | Your GCP Project ID | e.g. `my-deal-room-project` |
| `GCP_REGION` | `us-central1` | Cloud Run & Artifact Registry region |
| `WIF_PROVIDER` | `workload_identity_provider` | Full WIF provider resource path |
| `WIF_SERVICE_ACCOUNT` | `github_actions_service_account_email` | Service account for GitHub Actions |
| `CLOUD_RUN_SERVICE_NAME`| `nexus-deal-room` | Cloud Run service name |
| `ARTIFACT_REGISTRY_REPO`| `nexus-deal-room` | Artifact Registry repo |

---

### Step 3: Automated Continuous Deployment
Pushing to the `main` branch automatically triggers [`.github/workflows/deploy.yml`](file:///c:/Coding_learning/agent_negotiation/Agent-Negotiation-Room/.github/workflows/deploy.yml):
```powershell
git add .
git commit -m "Deploy Nexus Deal Room to Cloud Run"
git push origin main
```
The workflow authenticates using WIF, builds the multi-stage Docker container, pushes to Artifact Registry, and deploys the new revision to Cloud Run.

---

## 🧪 Interactive Testing & Demo Scenarios

### Scenario 1: The Active Deal Room & WebMCP Loop
1. Open [http://localhost:5173](http://localhost:5173).
2. Look at the top navigation: note high-signal status pills (`● Decision Twin Online`, `● WebMCP Ready`, `● Human Authority Enforced`).
3. Click **`⚡ Run Live WebMCP Loop`** in the DAG card:
   - Watch the animated transitions through all 6 nodes.
   - Click **Node 1** (`Discover Tools`) to see the list of tools discovered on `document.modelContext`.
   - Click **Node 3** (`Evaluate Offer`) to inspect the raw Decision Twin JSON score.
   - Click **Node 4** (`Agent Strategy`) to read the AI Deliberation and Next Best Move.

### Scenario 2: Constraint Kitchen (3-Tier Policy View)
1. In the Constraint Kitchen card, click preset **`⚡ Speed > Price`**.
2. **Observe**:
   - Tier 1: Natural language intent compiled.
   - Tier 2: Weights instantly adjust to **Speed: 35%**, **Price: 25%**.
   - Tier 3: Agent Governance Authority Matrix displays allowed vs. blocked actions.

### Scenario 3: Agent Governance Boundary Defense
1. In the 3-Way Alternative Matrix, click **`🚨 Test Governance Boundary ($95k / 0.8x)`**.
2. **Observe**:
   - Status switches to red with callout: **`🚨 AGENT GOVERNANCE BOUNDARY TRIGGERED — Execution Blocked`**.
   - Agent Deliberation explains the block and recommends pivoting to **Counter Proposal A (\$105,000)**.
   - Click **`★ Pivot to Next Best Move`** to return to compliant terms.

### Scenario 4: Human-in-the-Loop Approval Sign-Off
1. Scroll to the **Counteroffer Proposal Approval Boundary** card (\$105,000 pending proposal).
2. Click **`✓ Approve`**.
3. **Observe**: Proposal transitions to **`APPROVED`** and DAG Node 6 turns green (`completed`).

### Scenario 5: Previous Deals & System of Record Search
1. Open [http://localhost:5173/contracts](http://localhost:5173/contracts) (or click **Contracts SoR** in the header).
2. 10 sample enterprise contracts load automatically from SQLite.
3. Click **`🤖 Search "Apex"`** or **`🤖 High Value (> $200k)`** to trigger in-browser WebMCP search.
4. Open Chrome DevTools (`F12` $\rightarrow$ Console) and run:
   ```javascript
   await document.modelContext.tools.search_previous_deals.execute({ status: "Under Negotiation" });
   ```

### Scenario 6: 🧪 Agent QA Suite & The Closed Evolution Lifecycle
1. Open [http://localhost:5173/agent-qa](http://localhost:5173/agent-qa) (or click **`🧪 Agent QA`** in header).
2. **Attack 1 (Boundary Breach)**:
   - Click **`⚔️ Launch Attack`** on Card 1.
   - Agent attempts \$95k with 0.8x liability $\rightarrow$ Decision Twin intercepts (**`BOUNDARY_PROTECTED`**).
   - Feedback notes friction with failure telemetry in v2.
3. **Walk through the Closed Lifecycle**:
   - Click **`⚡ Step 2: Hand Off to Wire-Agent (Stage UI Fix)`**: Wire-Agent stages patch `mut-wire-01` with high-contrast outlines for v3.
   - Click **`✍️ Step 3: Human Authority Review & Publish v3`**: Human principal approves $\rightarrow$ publishes v3.
   - Click **`🔁 Step 4: Run Agent QA Regression Test on v3`**: Agent QA re-runs probe against v3 $\rightarrow$ **`PASSED (0 Friction)`**.
4. **Attack 2 (Governance Bypass)**:
   - Click **`⚔️ Launch Attack`** on Card 2 $\rightarrow$ Agent attempts autonomous `execute_contract` $\rightarrow$ blocked with `403 Governance Boundary Enforced`.
5. **Attack 3 (Schema Immutability)**:
   - Click **`⚔️ Launch Attack`** on Card 3 $\rightarrow$ Agent attempts to patch `/price` $\rightarrow$ blocked with `403 Forbidden`.

### Scenario 7: Epilogue — Wire-Agent UX Evolution & Safety Guard
1. Scroll to **Epilogue: Wire-Agent UX Evolution & Safety Boundary** at the bottom of the main deal room.
2. Click **`Preview Wire-Agent Mutation`**: The Hard Constraint Evaluation card renders high-contrast danger borders and badge.
3. Click **`🛡️ Test Safety Guard (Attempt Forbidden Price Edit)`**:
   - Backend safety guard catches the attack and displays:
     > **🚫 SAFETY GUARD INTERCEPTION — BLOCKED 403**  
     > `Forbidden field in mutation patch: 'price' cannot be mutated by presentation layer.`
4. Deliver the epilogue: *"The agent can evolve how the application communicates its decisions, but can never alter the decisions themselves."*

---

## 🛠️ Automated Test Suite

Run full automated tests from the repository root:

```powershell
# Run Backend Test Suite (41 tests)
cd backend
.\.venv\Scripts\python.exe -m pytest

# Run Frontend Lint
cd ../frontend
npm run lint

# Run Frontend Production Build
npm run build
```

- **Backend Status**: **41 / 41 passed** in `< 6s`
- **Frontend Lint Status**: **0 errors, 0 warnings**
- **Frontend Production Build**: Built cleanly in `< 4s`

---

## 📜 WebMCP Registered Tool Contracts

All tool contracts are accessible via JSON-RPC 2.0 at `/api/mcp/tool-call` and in-browser on `document.modelContext`:

| Tool Name | Parameters | Description |
|---|---|---|
| `inspect_ui_schema` | `schema_id: string` | Returns current published UI schema version and layout tree. |
| `get_current_deal` | `contract_id: string` | Retrieves contract terms, targets, and baseline price. |
| `get_constraints` | `contract_id: string` | Retrieves non-negotiable hard limits and advisory evaluation rules. |
| `evaluate_offer` | `contract_id: string`, `offer_data: string` | Runs deterministic Decision Twin evaluation (score, feasibility, failures). |
| `simulate_tradeoff` | `contract_id: string`, `proposed_change: string` | Models price elasticity, margin impact, and acceptance probability. |
| `propose_counteroffer` | `contract_id: string`, `proposal_data: string` | Submits pending proposal awaiting human approval sign-off. |
| `execute_contract` | `contract_id: string`, `signature_token?: string` | Prohibits autonomous signing; enforces human authority boundary (403). |
| `preview_ui_mutation` | `base_version: int`, `patch_data: string` | Stages presentation-only styling patch (guarded against business terms). |
| `publish_ui_mutation` | `mutation_id: string` | Publishes validated presentation mutation, incrementing schema version. |
| `search_previous_deals` | `query?: string`, `status?: string`, `min_value?: number`, `max_value?: number` | Queries System of Record contracts database with filters. |
| `compile_intent` | `prompt: string` | Compiles natural language priority text into mathematical weights. |

---

## ⚖️ Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Zustand, `@xyflow/react`, Vite
- **Backend**: Python 3.11 / 3.13, FastAPI, FastMCP, Pydantic, SQLAlchemy, SQLite
- **Protocol**: Model Context Protocol (WebMCP) via HTTP JSON-RPC Proxy & In-Browser `document.modelContext`
- **Testing**: Pytest (41 tests), ESLint, Vite Production Compiler
