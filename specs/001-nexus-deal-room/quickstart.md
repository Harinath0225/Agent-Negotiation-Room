# Quickstart & Validation Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- GCP Vertex AI credentials (or OpenAI API key proxy)

## Setup Commands

### Backend (FastAPI WebMCP Server)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (React/Zustand UI Renderer)
```bash
cd frontend
npm install
npm run dev
```

### Agent Client (WebMCP)
```bash
# In a separate terminal
cd agents
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python wire_agent.py --server http://localhost:8000/mcp
```

## End-to-End Validation Scenarios

### Scenario 1: Validate Schema-Driven UI
1. Start backend and frontend.
2. Navigate to `http://localhost:5173`.
3. Verify the frontend makes a `GET /api/ui-schema` request and dynamically renders the initial layout based on the JSON response.
4. The page should display without errors using Tailwind styling defined in the schema.

### Scenario 2: Wire-Agent UI Mutation (Admin Journey)
1. Launch the `wire_agent.py` client.
2. Provide prompt: "Change the background color of the main card to blue-500."
3. Verify the Wire-Agent sends a WebMCP tool call to mutate the schema on the backend.
4. Refresh the frontend and verify the background color updates.

### Scenario 3: Decision Twin Simulation (End-User Journey)
1. Launch the `user_agent.py` client.
2. Provide prompt: "If I lower the price by 10%, how does it affect my risk?"
3. Verify the User Agent queries the Decision Twin via WebMCP and returns an analytical risk assessment.
