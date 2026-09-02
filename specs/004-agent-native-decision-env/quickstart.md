# Quickstart & Validation Guide: Agent-Native Decision Environment

**Feature**: `004-agent-native-decision-env`  
**Date**: 2026-09-02  

---

## 🚀 Environment Setup

### 1. Backend Server (FastAPI + FastMCP)
```powershell
cd backend
.venv\Scripts\activate
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```
- API Endpoint: `http://127.0.0.1:8000/api/ui-schema`
- WebMCP Gateway: `http://127.0.0.1:8000/api/mcp`

### 2. Frontend Development Server (Vite + React)
```powershell
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 🧪 Runnable End-to-End Validation Scenarios

### Scenario A: Deterministic Decision Twin & Hard Failure Guard
1. Open `http://localhost:5173`.
2. Observe the **Decision Alternative Comparison** matrix:
   - Select **Restrictive Seller Offer (\$95,000)**.
   - Verify badge displays **HARD FAILURE**.
   - Verify failure text: `"Liability Cap: 0.8x is below non-negotiable minimum 1.5x"`.
3. Run backend automated verification:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_decision_twin.py
   ```
   - **Expected Result**: 6/6 tests pass (100% deterministic score & hard limit enforcement).

### Scenario B: Strategic Counteroffer & Human Approval
1. Scroll to **Counteroffer Proposal Approval Boundary** (\$105,000 pending proposal).
2. Click **`✓ Approve`**.
3. Verify:
   - Status transitions to **APPROVED** (green badge).
   - Text displays: `✓ Proposal approved. Deal progressing to closure.`
   - In the React Flow DAG below, node **`6. Human Approval`** turns green (`completed`).

### Scenario C: Wire-Agent Safety-Focused UX Evolution
1. Scroll to **Wire-Agent UX Evolution & Safety Guard**.
2. Click **`Preview Wire-Agent Mutation`** $\rightarrow$ verifies staged preview `mut-wire-01`.
3. Click **`Publish Mutation to v3`** $\rightarrow$ schema version bumps to v3.
4. Run backend invariance test:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/test_agent_native_workflow.py
   ```
   - **Expected Result**: 16/16 tests pass (proves visual mutation leaves Decision Twin scoring 100% invariant).

---

## 🛠️ Verification Suite

```powershell
# Backend Test Suite
cd backend
.venv\Scripts\python.exe -m pytest

# Frontend Typecheck & Build
cd frontend
npm run lint
npm run build
```
- **Backend Pass Target**: 37/37 tests passing.
- **Frontend Pass Target**: 0 lint errors, production bundle built in $< 3\text{s}$.
