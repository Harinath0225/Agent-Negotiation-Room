# Quickstart: Validate the Agent-Native Deal Room

## Prerequisites

- Install [backend/requirements.txt](../../../backend/requirements.txt).
- Install [frontend/package.json](../../../frontend/package.json) dependencies, including `@xyflow/react` after implementation.

## Scenario A: Restrictive Offer

1. Start backend and frontend using their existing project commands; open deal `#1042-B`.
2. Through WebMCP, retrieve the deal and constraints, then evaluate a low-price offer with liability above 1.5x.
3. Confirm the result is a liability hard failure and the activity log plus React Flow DAG show each WebMCP call.
4. Propose a higher-price, compliant-liability counteroffer and confirm it remains pending human approval.

## Scenario B: Decision Density

1. Load Current Deal, Counter A, and Counter B.
2. Confirm the table displays Term, Current, Target, and Status and comparison displays scores, constraint state, and trade-offs.
3. Run 100 repeated evaluations of the same input and confirm every score and hard-failure list is identical.

## Scenario C: Wire-Agent Safety

1. Inspect the published UI schema and preview hard-constraint warning banners.
2. Publish the reviewed preview as version 2.
3. Re-evaluate the fixed restrictive offer and confirm its decision result matches version 1.
4. Attempt a decision-logic mutation and confirm it is rejected.

## Automated Validation

From `backend`:

```powershell
pytest
```

From `frontend`:

```powershell
npm run lint
npm run build
```