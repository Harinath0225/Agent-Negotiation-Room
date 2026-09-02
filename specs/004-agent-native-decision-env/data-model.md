# Phase 1 Data Model: Agent-Native Decision Environment

**Feature**: `004-agent-native-decision-env`  
**Date**: 2026-09-02  

## Entities & Interfaces

### 1. IntentWeights (Constraint Kitchen)
Defines normalized weights applied to contract evaluation terms:

```typescript
export interface IntentWeights {
  price: number;      // e.g. 0.25 (25%)
  speed: number;      // e.g. 0.35 (35%)
  liability: number;  // e.g. 0.30 (30%)
  payment: number;    // e.g. 0.10 (10%)
  raw_intent?: string; // Natural language input string
}
```

### 2. DecisionTwinEvaluation (Simulation Output)
Deterministic evaluation result emitted by `backend/src/twin/decision_logic.py`:

```typescript
export interface DecisionTwinEvaluation {
  id: string;
  deal_id: string;
  alternative_id: string;
  score: number;              // 0 to 100 acceptance score
  is_feasible: boolean;       // False if any hard constraint fails
  constraint_results: Array<{
    constraint_id: string;
    constraint_name: string;
    target_value: number;
    actual_value: number;
    passed: boolean;
    explanation: string;
  }>;
  hard_failures: string[];     // Non-negotiable limit breaches
  trade_offs: string[];        // Recommended next best moves
  evaluated_at: string;
}
```

### 3. AlternativeScenario (3-Way Comparison)
Represents a contract offer scenario in the comparison matrix:

```typescript
export interface AlternativeScenario {
  id: string;                 // 'alt_current' | 'alt_counter_a' | 'alt_restrictive'
  label: string;              // Human-readable title
  deal_id: string;
  price: number;              // Concession price
  terms: {
    liability: number;        // Multiplier e.g. 1.5
    payment_terms: string;    // e.g. 'Net 30'
    delivery_timeline: number; // e.g. 90 days
  };
  source: 'system' | 'agent_strategic' | 'seller_offer';
  evaluation?: DecisionTwinEvaluation;
}
```

### 4. PresentationPatch (Wire-Agent Mutation)
Staged presentation-only UI mutation:

```typescript
export interface StagedMutation {
  mutation_id?: string;
  base_version: number;
  status: 'none' | 'previewed' | 'published';
  patch?: {
    className?: string;
    props?: Record<string, unknown>;
  };
}
```

### 5. DAGNode & DAGEdge (React Flow Execution Graph)
Interactive execution graph node models:

```typescript
export interface DAGNode {
  id: string;                 // e.g. 'node-discover', 'node-evaluate'
  label: string;
  stage: 'negotiator' | 'user_agent' | 'webmcp' | 'decision_twin' | 'deal_room';
  status: 'idle' | 'active' | 'completed' | 'failed';
  request_id?: string;
  details?: {
    tool_name?: string;
    summary?: string;
    event?: Record<string, unknown>;
  };
}

export interface DAGEdge {
  id: string;
  source: string;
  target: string;
}
```
