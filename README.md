# Nexus Deal Room 🤝 ⚡

**Nexus Deal Room** is a self-evolving, agent-native contract negotiation platform powered by a **100% schema-driven UI** and the **Model Context Protocol (WebMCP)**.

---

## 🏛️ System Architecture

The application implements a dual-journey, dual-agent architecture:

1. **End-User Journey (Deal Room Negotiation)**:
   - A human user negotiates contract terms assisted by the **User Agent**.
   - The User Agent interacts with a backend **Decision Twin** via WebMCP (`simulate_tradeoff`) to model risk scores, margin impacts, and counterparty acceptance probabilities.
2. **Admin Journey (Experience Studio)**:
   - An administrator customizes and redesigns the live application assisted by **Wire-Agent**.
   - Wire-Agent inspects the live UI structure, proposes JSON schema mutations via WebMCP (`mutate_ui_schema`), and renders instant live/draft previews.
3. **Core Architectural Mandate**:
   - The frontend contains **zero hardcoded page structures**; layout and styling are 100% dynamically rendered from JSON schemas provided by the FastAPI WebMCP server.

```
┌─────────────────────────────────────────────────────────────┐
│                       Nexus Frontend                        │
│             React + TypeScript + Tailwind + Zustand         │
│               [Dynamic Recursive SchemaRenderer]            │
└───────────────▲─────────────────────────────▲───────────────┘
                │ HTTP / REST                 │ SSE (Server-Sent Events)
┌───────────────▼─────────────────────────────▼───────────────┐
│                    FastAPI WebMCP Server                    │
│    • Schema Engine (`/api/ui-schema`)                       │
│    • WebMCP Tools Registry (`/api/mcp/sse`, `/messages`)    │
│    • SQLite DB (UISchema, Draft/Published Versions)        │
└───────────────▲─────────────────────────────▲───────────────┘
                │ WebMCP Client Protocol      │
┌───────────────┴──────────────┐┌─────────────┴───────────────┐
│          User Agent          ││         Wire-Agent          │
│ (Decision Twin Tradeoffs)    ││   (Schema-Driven Redesign)  │
│      GCP Vertex AI / Gemini  ││     GCP Vertex AI / Gemini  │
└──────────────────────────────┘└─────────────────────────────┘
```

---

## 📁 Repository Structure

```text
├── backend/
│   ├── requirements.txt            # FastAPI, Uvicorn, SQLAlchemy, MCP SDK, Semantic Kernel, pytest
│   ├── src/
│   │   ├── main.py                 # FastAPI application entrypoint & schema seeder
│   │   ├── api/                    # REST routes (schema_routes, simulation_routes)
│   │   ├── mcp/                    # WebMCP FastMCP server, tool registry, and handlers
│   │   ├── models/                 # SQLAlchemy DB & UISchema models
│   │   ├── seeds/                  # Seed JSON schemas (deal_room v2, admin_studio)
│   │   ├── services/               # Shared simulation_service and agent_client adapter
│   │   └── twin/                   # Decision Twin simulation logic
│   └── tests/                      # pytest test suite for routes, service, and MCP parity
├── frontend/
│   ├── package.json                # React 18, Vite, Tailwind CSS, Zustand
│   ├── vite.config.ts              # Reverse proxy to FastAPI backend (:8000)
│   └── src/
│       ├── renderer/               # Dynamic SchemaRenderer (simulation, workflow, timeline nodes)
│       ├── store/                  # Zustand store for schema, simulation, and activity events
│       └── App.tsx                 # Schema-driven root component (no idle polling)
├── agents/
│   ├── requirements.txt            # Microsoft Agentic AI Framework / Semantic Kernel
│   └── src/
│       ├── user_agent.py           # User Agent client
│       └── wire_agent.py           # Wire-Agent admin redesign client
└── specs/                          # System specs, data models, contracts, and tasks
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- **Python**: 3.10+ (Recommended: 3.11)
- **Node.js**: 18+ or 20+
- **Google Cloud Platform**: Vertex AI enabled project **or** Google AI Studio Gemini API Key

---

### 2. Backend Setup (FastAPI & WebMCP Server)

Open a terminal at the repository root:

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
# Windows (PowerShell):
py -3 -m venv venv
.\venv\Scripts\activate
# (or use `py -3` if `python` is aliased to Windows Store)

# macOS / Linux:
# python3 -m venv venv
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI WebMCP server with auto-reload
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be live at:
- **API Base**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **UI Schema Endpoint**: [http://127.0.0.1:8000/api/ui-schema](http://127.0.0.1:8000/api/ui-schema)
- **WebMCP SSE Endpoint**: [http://127.0.0.1:8000/api/mcp/sse](http://127.0.0.1:8000/api/mcp/sse)

---

### 3. Frontend Setup (React & Schema-Driven Renderer)

Open a second terminal at the repository root:

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies (React, Tailwind CSS, Zustand)
npm install

# Start the Vite development server
npm run dev
```

The frontend will be live at:
- **Web App**: [http://localhost:5173](http://localhost:5173)

> **Note**: Vite is configured with reverse proxy rules in `frontend/vite.config.ts` to automatically route `/api` and `/mcp` requests directly to `http://127.0.0.1:8000`.

---

### 4. Agent Setup (Microsoft Agentic AI Framework & WebMCP Client)

Open a third terminal for running the agents:

```bash
# Navigate to agents directory
cd agents

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate      # On Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🔑 Configuring Vertex AI & Gemini Models

The agents query Gemini models via **Google Cloud Vertex AI** or direct **Google GenAI / Gemini API**.

### Option A: Google Cloud Platform (GCP) Vertex AI Agent Platform / Model Registry

1. **Authentication**:
   - Authenticate via Google Cloud CLI:
     ```bash
     gcloud auth application-default login
     ```
   - **OR** create a GCP Service Account with the role **Vertex AI User** (`roles/aiplatform.user`), download the JSON key, and specify its path in `agents/.env`:
     ```env
     GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
     ```

2. **Configure `agents/.env`**:
   ```env
   # Enable Vertex AI Model Registry mode
   USE_VERTEX_AI=true
   GCP_PROJECT_ID=your-gcp-project-id
   GCP_LOCATION=us-central1

   # Model from Vertex AI Model Registry / Model Garden:
   VERTEX_AI_MODEL=gemini-1.5-pro
   # (Or your custom Model Registry Endpoint: projects/<NUM>/locations/<REGION>/endpoints/<ID>)
   ```

---

### Option B: Google AI Studio Gemini API Key (Direct API Key)

If you have a direct Gemini API key from [Google AI Studio](https://aistudio.google.com/):

1. **Export the API Key**:
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="AIzaSy..."
   
   # macOS / Linux
   export GEMINI_API_KEY="AIzaSy..."
   ```

2. **Add to `.env` file**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-pro-latest
   WEBMCP_SERVER_URL=http://127.0.0.1:8000/api/mcp/sse
   ```

---

### 5. Running the Agents

With the backend running, execute either agent:

#### Running the User Agent (Negotiation & Decision Twin):
```bash
cd agents
python src/user_agent.py
```
*Evaluates price discounts, delivery timeline risks, and liability caps using the `simulate_tradeoff` WebMCP tool.*

#### Running Wire-Agent (Admin Studio & Live UI Redesign):
```bash
cd agents
python src/wire_agent.py
```
*Inspects the active JSON schema, proposes Tailwind/layout modifications, and invokes `mutate_ui_schema` to update the user interface.*

---

## 🧪 Verification & Demo Checklist

1. **Verify Backend Health**:
   ```bash
   curl http://127.0.0.1:8000/health
   # Response: {"status":"ok"}
   ```

2. **Verify Dynamic UI Schema Delivery**:
   ```bash
   curl http://127.0.0.1:8000/api/ui-schema
   ```

3. **Verify WebMCP Tool Registration**:
   Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and verify WebMCP endpoints, or test the tool logic in `backend/src/mcp/tools.py`.

4. **Verify Frontend Schema Rendering**:
   Open [http://localhost:5173](http://localhost:5173) in your browser. You will see the rendered schema delivered dynamically from the backend rather than static HTML/JSX components.

---

## 🛠️ Tech Stack Reference

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Zustand, Vite |
| **Backend** | Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite, SSE Starlette |
| **Protocol** | Model Context Protocol (WebMCP) via SSE Transport |
| **AI / Agentic** | Microsoft Agentic AI Framework (Semantic Kernel), Google Cloud Vertex AI / Gemini Models |
