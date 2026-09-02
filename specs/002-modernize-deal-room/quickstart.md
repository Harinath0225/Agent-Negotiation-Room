# Quickstart: Modernize Deal Room Validation

## Prerequisites

- Python environment with [backend/requirements.txt](../../../backend/requirements.txt) installed.
- Node.js dependencies installed from [frontend/package.json](../../../frontend/package.json).
- Any required Microsoft Agentic AI Framework and model-provider environment configuration available to the backend.

## Start the application

1. Start the backend from `backend` with `uvicorn src.main:app --reload --port 8000`.
2. Start the frontend from `frontend` with `npm run dev`.
3. Open the Vite URL in a desktop browser, then repeat at a mobile viewport.

## Validate the schema-driven deal room

1. Confirm the contract summary, terms, negotiation control, latest result, activity timeline, and WebMCP workflow diagram are visible and visually separated.
2. Resize to a mobile viewport. Confirm no primary text or control overlaps and the page has no horizontal scroll.
3. Confirm the backend produces no repeated schema requests while the page is idle.

## Validate tradeoff execution

1. Trigger the default proposed price change.
2. Confirm the control immediately shows a pending state and cannot be submitted twice.
3. Confirm the response presents the proposed price, risk impact, acceptance probability, recommendation, and affected term.
4. Exercise an invalid or unavailable request and confirm a readable error with retry action.
5. Verify the same valid payload against the contract in [simulation-api.md](contracts/simulation-api.md) produces the expected structured response.

## Validate observable WebMCP workflow

1. Run a successful simulation.
2. Confirm the activity timeline records the negotiator, user agent, WebMCP, Decision Twin, and deal-room stages.
3. Select an activity event and confirm the corresponding workflow diagram stage is highlighted.
4. Run enough simulations to exceed 50 events and confirm the timeline remains capped while retaining the newest outcome events.

## Quality checks

Run `npm run build` and `npm run lint` in `frontend`. Run the backend test suite after adding route and service tests. Verify the Microsoft Agentic AI Framework adapter can invoke the registered `simulate_tradeoff` WebMCP tool in the configured environment.