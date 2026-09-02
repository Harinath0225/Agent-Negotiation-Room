# WebMCP Interface Contracts

## 1. Wire-Agent UI Mutator Tool
Allows the Admin Wire-Agent to propose JSON schema mutations for the live UI.

- **Tool Name**: `mutate_ui_schema`
- **Description**: Submits a proposed JSON schema payload to update the frontend layout and styling.
- **Parameters**:
  - `schema_patch` (JSON): The new JSON representation of the UI to be previewed or published.
  - `component_target` (String): The ID or path of the component being mutated.
- **Returns**: A success confirmation or syntax validation errors.

## 2. User Agent Decision Twin Tool
Allows the User Agent to query the Decision Twin simulation model during a negotiation.

- **Tool Name**: `simulate_tradeoff`
- **Description**: Runs a simulation against the current contract terms using the Decision Twin to evaluate risk and price sensitivity.
- **Parameters**:
  - `contract_id` (String): The active negotiation session ID.
  - `proposed_change` (JSON): The tradeoff being requested (e.g., `{"price": -10}`).
- **Returns**: JSON object containing `risk_score_delta`, `acceptance_probability`, and analytical commentary.
