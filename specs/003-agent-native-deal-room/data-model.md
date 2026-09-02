# Data Model: Agent-Native Deal Room

## Deal and Constraint

| Entity | Fields | Rules |
|--------|--------|-------|
| Deal | `id`, `current_terms`, `targets`, `approval_state` | Material terms and targets are present; state is draft, pending, approved, or rejected. |
| Constraint | `id`, `term`, `operator`, `limit`, `severity`, `message` | Severity is hard or advisory; every hard result names term and governing limit. |
| Deal Alternative | `id`, `label`, `terms`, `source` | Labels include Current Deal, Counter A, Counter B; all material terms are complete. |

## Decision Twin Evaluation

| Field | Rule |
|-------|------|
| `alternative_id` | References the evaluated alternative. |
| `score` | Deterministic integer 0-100. |
| `feasible` | False when any hard constraint fails. |
| `constraint_results` | Outcome for every evaluated constraint. |
| `hard_failures` | Includes term, actual value, limit, and explanation. |
| `trade_offs` | Derived gains and losses against targets. |

## Counteroffer Proposal

| Field | Rule |
|-------|------|
| `id`, `alternative`, `rationale`, `evaluation`, `status` | Evaluation and complete alternative are required. |
| Status | `pending_approval` -> `approved` or `rejected`; incomplete submissions become `invalid`. |

## Agent Activity Event

| Field | Rule |
|-------|------|
| `id`, `deal_id`, `request_id`, `tool_name`, `stage`, `status`, `summary`, `occurred_at` | Required; status is started, completed, or failed. |

The active client view retains the newest 50 events.

## Interface Mutation

| Field | Rule |
|-------|------|
| `id`, `base_schema_version`, `patch`, `preview_layout`, `status`, `published_version` | Patch can contain presentation schema fields only. |
| Status | `proposed` -> `previewed` -> `published`; safety violation -> `rejected`. |