# Phase 1: Data Model & Contracts

## Data Entities

### 1. UISchema
Represents the dynamic layout and styling of the application.
- `id`: string (UUID)
- `version`: integer
- `layout`: JSON Object (Recursive component tree)
  - `type`: string (e.g., "div", "button", "text")
  - `props`: Object (e.g., onClick, text content)
  - `className`: string (Tailwind CSS classes)
  - `children`: Array of Layout Objects
- `is_published`: boolean

### 2. NegotiationContract
Represents the core deal terms being negotiated by the end-user.
- `id`: string (UUID)
- `parties`: Array of strings
- `terms`: JSON Object (price, duration, risk_score, clauses)
- `status`: string (draft, proposed, accepted)

### 3. DecisionTwinState
Represents the simulation state and analytical model for tradeoffs.
- `id`: string (UUID)
- `contract_id`: string (Foreign Key)
- `risk_matrix`: JSON Object
- `price_sensitivity`: float

## State Transitions
- **UI Schema**: Draft -> Mutated by Wire-Agent -> Preview -> Approved (Published)
- **Negotiation**: Draft -> Simulated Tradeoffs -> Proposed -> Accepted
