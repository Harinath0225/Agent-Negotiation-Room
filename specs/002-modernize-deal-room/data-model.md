# Data Model: Modernize Deal Room

## SimulationRequest

| Field | Type | Validation |
|---|---|---|
| request_id | string | Unique client-generated identifier |
| contract_id | string | Required, non-empty |
| proposed_change | object | Must include a numeric price change or proposed price |
| submitted_at | datetime | Recorded at submission |
| status | enum | `ready`, `pending`, `succeeded`, or `failed` |

**State transitions**: `ready -> pending -> succeeded`; `ready -> pending -> failed`; `failed -> pending` on retry.

## SimulationOutcome

| Field | Type | Validation |
|---|---|---|
| request_id | string | Matches the originating request |
| contract_id | string | Matches the originating request |
| current_price | number | Non-negative |
| proposed_price | number | Non-negative |
| risk_score_delta | number | Required when successful |
| acceptance_probability | number | Between 0 and 1 when successful |
| recommendation | string | Non-empty user-readable guidance |
| affected_terms | list | Includes one or more changed or evaluated terms |
| completed_at | datetime | Recorded when resolved |

## ActivityEvent

| Field | Type | Validation |
|---|---|---|
| id | string | Unique event identifier |
| request_id | string | Associated simulation request |
| stage | enum | `negotiator`, `user_agent`, `webmcp`, `decision_twin`, or `deal_room` |
| status | enum | `started`, `completed`, or `failed` |
| message | string | Concise user-readable description |
| occurred_at | datetime | Recorded when the event occurs |

**Rules**: Keep at most 50 events, newest first. De-duplicate repeated events with the same request, stage, and status.

## WorkflowStage

| Field | Type | Validation |
|---|---|---|
| id | enum | One of the five activity stages |
| label | string | Human-readable label |
| description | string | Explains responsibility in the current workflow |
| state | enum | `idle`, `active`, `completed`, or `failed` |

## Relationships

One `SimulationRequest` produces zero or one `SimulationOutcome` and multiple `ActivityEvent` records. Each activity event maps to exactly one `WorkflowStage`. A deal room owns the currently active request, result, timeline, and workflow-stage selection.