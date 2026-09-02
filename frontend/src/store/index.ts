import { create } from 'zustand';

// ============================================================================
// Phase 2: Extended Schema Node Typings, Activity Events, and DAG State
// ============================================================================

export interface UISchemaState {
  id: string;
  version: number;
  is_published: boolean;
  layout: unknown;
}

export type SimulationStatus = 'ready' | 'pending' | 'succeeded' | 'failed';

export interface SimulationOutcome {
  request_id: string;
  contract_id: string;
  current_price: number;
  proposed_price: number;
  risk_score_delta: number;
  acceptance_probability: number;
  recommendation: string;
  affected_terms: string[];
  completed_at: string;
}

export type WorkflowStageId =
  | 'negotiator'
  | 'user_agent'
  | 'webmcp'
  | 'decision_twin'
  | 'deal_room';

export type EventStatus = 'started' | 'completed' | 'failed';

export interface ActivityEvent {
  id: string;
  request_id: string;
  stage: WorkflowStageId;
  status: EventStatus;
  message: string;
  occurred_at: string;
}

export interface IntentWeights {
  price: number;
  speed: number;
  liability: number;
  payment: number;
  raw_intent?: string;
}

// ============================================================================
// Phase 2 Extended: Decision Twin and Comparison Types
// ============================================================================

export interface ConstraintResult {
  constraint_id: string;
  constraint_name: string;
  term?: string;
  actual_value?: number;
  target_value: number;
  hard_limit?: number;
  passed: boolean;
  explanation: string;
}

export interface DecisionTwinEvaluation {
  id: string;
  deal_id: string;
  alternative_id: string;
  score: number;
  is_feasible: boolean;
  constraint_results: ConstraintResult[];
  hard_failures: string[];
  trade_offs: string[];
  evaluated_at: string;
}

export interface DealAlternative {
  id: string;
  label: string;
  deal_id: string;
  price: number;
  terms: Record<string, unknown>;
  source?: string;
  evaluation?: DecisionTwinEvaluation;
  created_at: string;
}

export interface Deal {
  id: string;
  contract_id: string;
  current_price: number;
  current_terms?: Record<string, unknown>;
  targets?: Record<string, unknown>;
  counterparty: string;
  approval_state: 'draft' | 'pending' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface CounterofferProposal {
  id: string;
  deal_id: string;
  alternative_id: string;
  agent_id?: string;
  proposed_price: number;
  proposed_terms: Record<string, unknown>;
  rationale: string;
  evaluation?: DecisionTwinEvaluation;
  approval_status: 'pending' | 'approved' | 'rejected' | 'invalid';
  created_at: string;
}

export interface ComparisonState {
  current_deal?: DealAlternative;
  counterA?: DealAlternative;
  counterB?: DealAlternative;
  selected_id?: string;
}

export interface StagedMutation {
  mutation_id?: string;
  base_version: number;
  status: 'none' | 'previewed' | 'published';
  patch?: Record<string, unknown>;
  preview_layout?: unknown;
}

export const CANONICAL_DAG_NODES: DAGNode[] = [
  {
    id: 'node-discover',
    label: '1. Discover Tools',
    stage: 'discover',
    status: 'completed',
    details: {
      tool_name: 'FastMCP.list_tools',
      summary: 'Agent enumerates discoverable WebMCP tools',
      request_id: 'mcp-init-01',
    },
  },
  {
    id: 'node-read',
    label: '2. Read Deal State',
    stage: 'read',
    status: 'completed',
    details: {
      tool_name: 'get_current_deal & get_constraints',
      summary: 'Retrieves contract #1042-B terms, targets, and constraints',
      request_id: 'mcp-read-02',
    },
  },
  {
    id: 'node-evaluate',
    label: '3. Evaluate Offer',
    stage: 'evaluate',
    status: 'completed',
    details: {
      tool_name: 'evaluate_offer',
      summary: 'Decision Twin runs deterministic constraint evaluation',
      request_id: 'mcp-eval-03',
    },
  },
  {
    id: 'node-reason',
    label: '4. Agent Strategy',
    stage: 'reason',
    status: 'completed',
    details: {
      tool_name: 'AgenticAI.reason',
      summary: 'Identifies Next Best Negotiation Move balancing price and risk',
      request_id: 'mcp-reason-04',
    },
  },
  {
    id: 'node-propose',
    label: '5. Propose Counteroffer',
    stage: 'propose',
    status: 'completed',
    details: {
      tool_name: 'propose_counteroffer',
      summary: 'Submits compliant proposal for $105,000 awaiting human sign-off',
      request_id: 'mcp-prop-05',
    },
  },
  {
    id: 'node-approve',
    label: '6. Human Approval',
    stage: 'approve',
    status: 'active',
    details: {
      tool_name: 'deal_approval',
      summary: 'Human-in-the-loop final acceptance boundary',
      request_id: 'mcp-appr-06',
    },
  },
];

export const CANONICAL_DAG_EDGES: DAGEdge[] = [
  { id: 'edge-1-2', source: 'node-discover', target: 'node-read', label: 'tools verified' },
  { id: 'edge-2-3', source: 'node-read', target: 'node-evaluate', label: 'terms & constraints' },
  { id: 'edge-3-4', source: 'node-evaluate', target: 'node-reason', label: 'twin verdict' },
  { id: 'edge-4-5', source: 'node-reason', target: 'node-propose', label: 'counter proposal' },
  { id: 'edge-5-6', source: 'node-propose', target: 'node-approve', label: 'pending sign-off' },
];

export const INITIAL_ALTERNATIVES: DealAlternative[] = [
  {
    id: 'alt_current',
    label: 'Current Deal',
    deal_id: 'deal_1042',
    price: 120000,
    terms: {
      liability: 2.0,
      payment_terms: 'Net 30',
      delivery_timeline: 90,
    },
    source: 'system',
    evaluation: {
      id: 'eval_current',
      deal_id: 'deal_1042',
      alternative_id: 'alt_current',
      score: 50,
      is_feasible: true,
      constraint_results: [
        {
          constraint_id: 'constraint_liability',
          constraint_name: 'Liability Coverage',
          target_value: 1.5,
          actual_value: 2.0,
          passed: true,
          explanation: 'Liability Coverage: 2.0 vs target 1.5',
        },
      ],
      hard_failures: [],
      trade_offs: ['Price is above baseline. Negotiate reduction to improve margins.'],
      evaluated_at: new Date().toISOString(),
    },
    created_at: new Date().toISOString(),
  },
  {
    id: 'alt_counter_a',
    label: 'Counter Proposal A',
    deal_id: 'deal_1042',
    price: 105000,
    terms: {
      liability: 1.5,
      payment_terms: 'Net 30',
      delivery_timeline: 90,
    },
    source: 'agent_strategic',
    evaluation: {
      id: 'eval_counter_a',
      deal_id: 'deal_1042',
      alternative_id: 'alt_counter_a',
      score: 65,
      is_feasible: true,
      constraint_results: [
        {
          constraint_id: 'constraint_liability',
          constraint_name: 'Liability Coverage',
          target_value: 1.5,
          actual_value: 1.5,
          passed: true,
          explanation: 'Liability Coverage: 1.5 vs target 1.5',
        },
      ],
      hard_failures: [],
      trade_offs: [
        'Recommended Next Best Move: meets 1.5x liability requirement while offering $15,000 price savings.',
      ],
      evaluated_at: new Date().toISOString(),
    },
    created_at: new Date().toISOString(),
  },
  {
    id: 'alt_restrictive',
    label: 'Restrictive Seller Offer',
    deal_id: 'deal_1042',
    price: 95000,
    terms: {
      liability: 0.8,
      payment_terms: 'Net 30',
      delivery_timeline: 90,
    },
    source: 'counterparty',
    evaluation: {
      id: 'eval_restrictive',
      deal_id: 'deal_1042',
      alternative_id: 'alt_restrictive',
      score: 36,
      is_feasible: false,
      constraint_results: [
        {
          constraint_id: 'constraint_liability',
          constraint_name: 'Liability Coverage',
          target_value: 1.5,
          actual_value: 0.8,
          hard_limit: 1.5,
          passed: false,
          explanation: 'Liability Coverage: 0.8 vs target 1.5 (hard limit: 1.5) - FAILED',
        },
      ],
      hard_failures: [
        'Liability Coverage: 0.8 vs target 1.5 (hard limit: 1.5) - FAILED',
      ],
      trade_offs: [
        'Increase price to $105,000 to pass liability constraint',
        'Request seller to accept shared liability structure',
      ],
      evaluated_at: new Date().toISOString(),
    },
    created_at: new Date().toISOString(),
  },
];

export interface DAGNode {
  id: string;
  label: string;
  stage: 'discover' | 'read' | 'evaluate' | 'reason' | 'propose' | 'approve';
  status: 'idle' | 'active' | 'completed' | 'failed';
  request_id?: string;
  details?: Record<string, unknown>;
}

export interface DAGEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'blocked';

export interface WorkflowStage {
  id: WorkflowStageId;
  label: string;
  role: string;
  description: string;
  state: 'idle' | 'active' | 'completed' | 'failed';
}

export const INITIAL_WORKFLOW_STAGES: WorkflowStage[] = [
  {
    id: 'negotiator',
    label: '1. Negotiator',
    role: 'Human Dealmaker',
    description: 'Initiates contract price adjustments and reviews strategic recommendations.',
    state: 'idle',
  },
  {
    id: 'user_agent',
    label: '2. User Agent',
    role: 'Analytical Co-Pilot',
    description: 'Microsoft Agentic AI Framework client managing negotiation prompts & tool routing.',
    state: 'idle',
  },
  {
    id: 'webmcp',
    label: '3. WebMCP Gateway',
    role: 'Model Context Protocol',
    description: 'Secure server hosting simulate_tradeoff and mutate_ui_schema tool boundaries.',
    state: 'idle',
  },
  {
    id: 'decision_twin',
    label: '4. Decision Twin',
    role: 'Analytical Engine',
    description: 'Calculates risk deltas, elasticity margins, and counterparty acceptance probability.',
    state: 'idle',
  },
  {
    id: 'deal_room',
    label: '5. Deal Room',
    role: 'Schema-Driven Workspace',
    description: 'Renders verified outcome metrics, affected terms, and responsive visual layout.',
    state: 'idle',
  },
];

interface DealRoomStore {
  // Schema
  uiSchema: UISchemaState | null;
  lastUpdated: number;
  setUiSchema: (schema: UISchemaState) => void;

  // Simulation state
  simulationStatus: SimulationStatus;
  currentRequestId: string | null;
  activeContractId: string;
  lastOutcome: SimulationOutcome | null;
  simulationError: string | null;

  startSimulation: (requestId: string, contractId: string) => void;
  completeSimulation: (outcome: SimulationOutcome) => void;
  failSimulation: (error: string) => void;
  resetSimulation: () => void;

  // Activity & Workflow state
  activityEvents: ActivityEvent[];
  workflowStages: WorkflowStage[];
  selectedStageId: WorkflowStageId | null;

  addActivityEvent: (event: Omit<ActivityEvent, 'id' | 'occurred_at'>) => void;
  selectStage: (stageId: WorkflowStageId | null) => void;
  setStageState: (stageId: WorkflowStageId, state: WorkflowStage['state']) => void;
  resetStages: () => void;
  clearActivityEvents: () => void;

  // Phase 2: Deal and comparison state
  currentDeal: Deal | null;
  alternatives: DealAlternative[];
  comparison: ComparisonState;
  
  setCurrentDeal: (deal: Deal) => void;
  setAlternatives: (alternatives: DealAlternative[]) => void;
  selectAlternative: (alternative_id: string) => void;
  clearComparison: () => void;

  // Phase 2: Pending proposals and approval state
  pendingProposals: CounterofferProposal[];
  approvalStatus: ApprovalStatus;
  
  addProposal: (proposal: CounterofferProposal) => void;
  approveProposal: (proposal_id: string) => void;
  rejectProposal: (proposal_id: string) => void;
  setApprovalStatus: (status: ApprovalStatus) => void;

  // Phase 7: React Flow DAG nodes, selection, and edges
  dagNodes: DAGNode[];
  dagEdges: DAGEdge[];
  selectedDAGNodeId: string | null;
  
  setDAGNodes: (nodes: DAGNode[]) => void;
  setDAGEdges: (edges: DAGEdge[]) => void;
  selectDAGNode: (nodeId: string | null) => void;
  updateDAGNodeStatus: (nodeId: string, status: DAGNode['status']) => void;
  projectActivityToDAG: () => void;

  // Phase 6: Wire-Agent Mutation Staging
  stagedMutation: StagedMutation;
  setStagedMutation: (mutation: StagedMutation) => void;
  clearStagedMutation: () => void;

  // Constraint Kitchen: Intent Weight Compiler
  intentWeights: IntentWeights;
  setIntentWeights: (weights: IntentWeights) => void;
  compileIntentFromText: (promptText: string) => void;
}

export const useDealRoomStore = create<DealRoomStore>((set) => ({
  uiSchema: null,
  lastUpdated: Date.now(),
  setUiSchema: (schema) => set({ uiSchema: schema, lastUpdated: Date.now() }),

  simulationStatus: 'ready',
  currentRequestId: null,
  activeContractId: '#1042-B',
  lastOutcome: null,
  simulationError: null,

  startSimulation: (requestId: string, contractId: string) =>
    set((state) => ({
      simulationStatus: 'pending',
      currentRequestId: requestId,
      activeContractId: contractId,
      simulationError: null,
      workflowStages: state.workflowStages.map((s) => ({
        ...s,
        state: s.id === 'negotiator' ? 'active' : 'idle',
      })),
    })),

  completeSimulation: (outcome: SimulationOutcome) =>
    set((state) => ({
      simulationStatus: 'succeeded',
      lastOutcome: outcome,
      simulationError: null,
      workflowStages: state.workflowStages.map((s) => ({
        ...s,
        state: 'completed',
      })),
    })),

  failSimulation: (error: string) =>
    set((state) => ({
      simulationStatus: 'failed',
      simulationError: error,
      workflowStages: state.workflowStages.map((s) => ({
        ...s,
        state: s.state === 'active' ? 'failed' : s.state,
      })),
    })),

  resetSimulation: () =>
    set({
      simulationStatus: 'ready',
      currentRequestId: null,
      lastOutcome: null,
      simulationError: null,
    }),

  activityEvents: [
    {
      id: 'init-01',
      request_id: 'sys-init',
      stage: 'deal_room',
      status: 'completed',
      message: 'Deal Room loaded with contract #1042-B published schema.',
      occurred_at: new Date().toISOString(),
    },
  ],
  workflowStages: INITIAL_WORKFLOW_STAGES,
  selectedStageId: null,

  addActivityEvent: (eventData) =>
    set((state) => {
      // De-duplicate repeated events with same request, stage, and status
      const isDuplicate = state.activityEvents.some(
        (e) =>
          e.request_id === eventData.request_id &&
          e.stage === eventData.stage &&
          e.status === eventData.status
      );
      if (isDuplicate) return state;

      const newEvent: ActivityEvent = {
        ...eventData,
        id: `evt-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        occurred_at: new Date().toISOString(),
      };

      // Keep at most 50 events, newest first
      const updatedEvents = [newEvent, ...state.activityEvents].slice(0, 50);
      return { activityEvents: updatedEvents };
    }),

  selectStage: (stageId) => set({ selectedStageId: stageId }),

  setStageState: (stageId, stageState) =>
    set((state) => ({
      workflowStages: state.workflowStages.map((s) =>
        s.id === stageId ? { ...s, state: stageState } : s
      ),
    })),

  resetStages: () =>
    set({
      workflowStages: INITIAL_WORKFLOW_STAGES,
      selectedStageId: null,
    }),

  clearActivityEvents: () => set({ activityEvents: [] }),

  // Phase 2: Deal and comparison state
  currentDeal: null,
  alternatives: INITIAL_ALTERNATIVES,
  comparison: {
    current_deal: INITIAL_ALTERNATIVES[0],
    counterA: INITIAL_ALTERNATIVES[1],
    counterB: INITIAL_ALTERNATIVES[2],
    selected_id: 'alt_counter_a',
  },

  setCurrentDeal: (deal) => set({ currentDeal: deal }),

  setAlternatives: (alternatives) => set({ alternatives }),

  selectAlternative: (alternative_id) =>
    set((state) => ({
      comparison: {
        ...state.comparison,
        selected_id: alternative_id,
      },
    })),

  clearComparison: () => set({ comparison: {} }),

  // Phase 2: Pending proposals and approval state
  pendingProposals: [],
  approvalStatus: 'pending',

  addProposal: (proposal) =>
    set((state) => ({
      pendingProposals: [...state.pendingProposals, proposal],
    })),

  approveProposal: (proposal_id) =>
    set((state) => ({
      pendingProposals: state.pendingProposals.map((p) =>
        p.id === proposal_id ? { ...p, approval_status: 'approved' } : p
      ),
      approvalStatus: 'approved',
    })),

  rejectProposal: (proposal_id) =>
    set((state) => ({
      pendingProposals: state.pendingProposals.map((p) =>
        p.id === proposal_id ? { ...p, approval_status: 'rejected' } : p
      ),
      approvalStatus: 'rejected',
    })),

  setApprovalStatus: (status) => set({ approvalStatus: status }),

  // Phase 7: React Flow DAG nodes, selection, and edges
  dagNodes: CANONICAL_DAG_NODES,
  dagEdges: CANONICAL_DAG_EDGES,
  selectedDAGNodeId: 'node-propose',

  setDAGNodes: (nodes) => set({ dagNodes: nodes }),

  setDAGEdges: (edges) => set({ dagEdges: edges }),

  selectDAGNode: (nodeId) => set({ selectedDAGNodeId: nodeId }),

  updateDAGNodeStatus: (nodeId, status) =>
    set((state) => ({
      dagNodes: state.dagNodes.map((n) =>
        n.id === nodeId ? { ...n, status } : n
      ),
    })),

  projectActivityToDAG: () =>
    set((state) => {
      const updatedNodes = state.dagNodes.map((node) => {
        const relatedEvent = state.activityEvents.find(
          (e) => e.request_id === node.request_id || e.stage === (node.stage as unknown as WorkflowStageId)
        );
        return relatedEvent
          ? {
              ...node,
              status: (relatedEvent.status === 'completed'
                ? 'completed'
                : relatedEvent.status === 'failed'
                ? 'failed'
                : 'active') as DAGNode['status'],
              details: { ...node.details, event: relatedEvent },
            }
          : node;
      });
      return { dagNodes: updatedNodes };
    }),

  // Phase 6: Wire-Agent Mutation Staging
  stagedMutation: {
    base_version: 2,
    status: 'none',
  },
  setStagedMutation: (mutation) => set({ stagedMutation: mutation }),
  clearStagedMutation: () =>
    set({
      stagedMutation: {
        base_version: 2,
        status: 'none',
      },
    }),
  // Constraint Kitchen: Intent weight state and compilation
  intentWeights: {
    price: 0.35,
    speed: 0.15,
    liability: 0.30,
    payment: 0.20,
    raw_intent: 'Balanced priority: Default weighting distribution',
  },
  setIntentWeights: (weights: IntentWeights) => set({ intentWeights: weights }),
  compileIntentFromText: (promptText: string) =>
    set(() => {
      const text = promptText.toLowerCase();
      let price = 0.35;
      let speed = 0.15;
      let liability = 0.30;
      let payment = 0.20;

      if (text.includes('speed') || text.includes('fast') || text.includes('timeline') || text.includes('quick')) {
        speed = 0.35;
        price = 0.25;
        payment = 0.10;
      } else if (text.includes('price') || text.includes('budget') || text.includes('cost') || text.includes('cheap')) {
        price = 0.45;
        speed = 0.10;
        payment = 0.15;
      } else if (text.includes('risk') || text.includes('liability') || text.includes('legal') || text.includes('indemnity')) {
        liability = 0.45;
        price = 0.25;
        speed = 0.10;
      }

      return {
        intentWeights: {
          price,
          speed,
          liability,
          payment,
          raw_intent: promptText,
        },
      };
    }),
}));

// Backwards compatibility alias
export const useSchemaStore = useDealRoomStore;
