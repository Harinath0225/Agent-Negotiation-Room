# Simulation API Contract

## `POST /api/simulations/tradeoff`

Runs the same server-owned Decision Twin calculation used by the `simulate_tradeoff` WebMCP tool and returns a user-facing simulation outcome.

### Request

```json
{
  "request_id": "sim-20260902-001",
  "contract_id": "1042-B",
  "proposed_change": {
    "current_price": 120000,
    "price_delta": -20000
  }
}
```

### Success response: `200`

```json
{
  "request_id": "sim-20260902-001",
  "contract_id": "1042-B",
  "current_price": 120000,
  "proposed_price": 100000,
  "risk_score_delta": 0.5,
  "acceptance_probability": 0.8,
  "recommendation": "Lowering the price significantly increases acceptance probability but also increases risk.",
  "affected_terms": ["Base Price"],
  "completed_at": "2026-09-02T12:00:00Z"
}
```

### Client errors: `422`

Returned when `contract_id` is blank, a price input is missing, numeric inputs are invalid, or a proposed price is negative. The response identifies the invalid field in user-safe terms.

### Server failure: `500`

```json
{
  "request_id": "sim-20260902-001",
  "detail": "The tradeoff simulation could not be completed. Try again."
}
```

## WebMCP parity

`simulate_tradeoff(contract_id, proposed_change)` remains registered with the WebMCP server. It delegates to the same simulation service and serializes the same outcome fields as the HTTP endpoint. The Microsoft Agentic AI Framework adapter is the production client that invokes this MCP tool; browser host registration remains optional enhancement only.