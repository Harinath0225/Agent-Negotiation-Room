import { useEffect, useState, useCallback } from 'react';
import './App.css';
import {
  useDealRoomStore,
  UISchemaState,
  SimulationOutcome,
  Deal,
  DealAlternative,
} from './store';
import { SchemaRenderer, SchemaNode } from './renderer/SchemaRenderer';
import ContractSearchPage from './ContractSearchPage';
import AgentQAPage from './AgentQAPage';

interface ModelContextTool {
  name: string;
  title?: string;
  description: string;
  inputSchema: Record<string, unknown>;
  execute: (input: Record<string, unknown>) => Promise<unknown>;
}

interface ModelContextObject {
  tools: Record<string, ModelContextTool>;
  registerTool: (tool: ModelContextTool) => void;
  getTools: () => ModelContextTool[];
  executeTool: (name: string, input?: Record<string, unknown>) => Promise<unknown>;
}

declare global {
  interface Document {
    modelContext?: ModelContextObject;
  }
  interface Window {
    modelContext?: ModelContextObject;
    webmcp?: ModelContextObject;
  }
}

function App() {
  const {
    uiSchema,
    setUiSchema,
    setCurrentDeal,
    setAlternatives,
    approveProposal,
    rejectProposal,
    startSimulation,
    completeSimulation,
    failSimulation,
    addActivityEvent,
    setStageState,
    selectAlternative,
    setStagedMutation,
    selectDAGNode,
    updateDAGNodeStatus,
    compileIntentFromText,
  } = useDealRoomStore();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLiveConnected, setIsLiveConnected] = useState(false);

  // T015: Load schema and populate deal data from seed
  const fetchSchema = useCallback(async (isInitial = false) => {
    try {
      const response = await fetch('/api/ui-schema');
      if (!response.ok) {
        throw new Error(`Failed to fetch schema: ${response.statusText}`);
      }
      const data: UISchemaState & { data?: { deal?: Deal; alternatives?: DealAlternative[] } } = await response.json();
      setIsLiveConnected(true);
      setUiSchema(data);
      
      // Phase 3: Load deal and alternatives from schema data
      if (data.data?.deal) {
        setCurrentDeal(data.data.deal);
      }
      if (data.data?.alternatives) {
        setAlternatives(data.data.alternatives);
      }
      
      if (error) setError(null);
    } catch (err: unknown) {
      setIsLiveConnected(false);
      if (isInitial) {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg || 'Could not connect to backend.');
      }
    } finally {
      if (isInitial) setLoading(false);
    }
  }, [error, setUiSchema, setCurrentDeal, setAlternatives]);

  // T014: Explicit refresh method used only after UI-schema mutations
  const refreshSchema = useCallback(async () => {
    await fetchSchema(false);
  }, [fetchSchema]);

  // T014 & T015: Single initial fetch - continuous polling completely removed
  useEffect(() => {
    fetchSchema(true);
  }, [fetchSchema]);

  // T019 & T024: Simulation lifecycle methods calling FastAPI contract & recording activity events
  const applySimulationOutcome = useCallback(
    (outcome: SimulationOutcome) => {
      completeSimulation(outcome);

      // Stage 4: Decision Twin completed
      addActivityEvent({
        request_id: outcome.request_id,
        stage: 'decision_twin',
        status: 'completed',
        message: `Decision Twin computed risk delta (${outcome.risk_score_delta > 0 ? '+' : ''}${outcome.risk_score_delta}) and ${Math.round(outcome.acceptance_probability * 100)}% acceptance probability.`,
        source: 'decision_twin',
        tool_name: 'DecisionTwin.evaluate',
      });
      setStageState('decision_twin', 'completed');

      // Stage 5: Deal Room UI updated
      addActivityEvent({
        request_id: outcome.request_id,
        stage: 'deal_room',
        status: 'completed',
        message: `Deal Room rendered tradeoff outcome for contract ${outcome.contract_id}: Proposed $${outcome.proposed_price.toLocaleString()}.`,
        source: 'ui',
        tool_name: 'SchemaRenderer.render_result',
      });
      setStageState('deal_room', 'completed');
    },
    [completeSimulation, addActivityEvent, setStageState]
  );

  const applySimulationFailure = useCallback(
    (requestId: string, errMessage: string) => {
      failSimulation(errMessage);

      addActivityEvent({
        request_id: requestId,
        stage: 'decision_twin',
        status: 'failed',
        message: `Decision Twin evaluation failed: ${errMessage}`,
        source: 'decision_twin',
        tool_name: 'DecisionTwin.evaluate',
      });
      setStageState('decision_twin', 'failed');

      addActivityEvent({
        request_id: requestId,
        stage: 'deal_room',
        status: 'failed',
        message: 'Deal Room displayed simulation failure state with retry option.',
        source: 'ui',
        tool_name: 'SchemaRenderer.render_error',
      });
      setStageState('deal_room', 'failed');
    },
    [failSimulation, addActivityEvent, setStageState]
  );

  const invokeMCPTool = useCallback(
    async (toolName: string, toolArguments: Record<string, unknown>, requestId: string, stage: 'user_agent' | 'webmcp' | 'decision_twin' | 'deal_room') => {
      const payloadPreview = JSON.stringify(toolArguments);
      addActivityEvent({
        request_id: requestId,
        stage,
        status: 'started',
        message: `WebMCP calling ${toolName}.`,
        source: 'webmcp',
        tool_name: toolName,
        payload_preview: payloadPreview,
      });

      try {
        const rpcPayload = {
          jsonrpc: '2.0',
          method: 'tools/call',
          params: { name: toolName, arguments: toolArguments },
          id: requestId,
        };
        // Invoke FastMCP HTTP JSON-RPC proxy directly to avoid SSE session redirects & 400 Bad Request
        const response = await fetch('/api/mcp/tool-call', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(rpcPayload),
        });
        if (!response.ok) {
          throw new Error(`MCP ${toolName} failed with status ${response.status}`);
        }

        const rpcResult = await response.json();
        if (rpcResult.error) {
          throw new Error(rpcResult.error.message || `MCP ${toolName} returned an error`);
        }

        const content = rpcResult.result?.content;
        const result = Array.isArray(content) && typeof content[0]?.text === 'string'
          ? JSON.parse(content[0].text)
          : rpcResult.result ?? rpcResult;
        addActivityEvent({
          request_id: requestId,
          stage,
          status: 'completed',
          message: `WebMCP completed ${toolName} [HTTP 200 OK].`,
          source: 'webmcp',
          tool_name: toolName,
          payload_preview: JSON.stringify(result).slice(0, 300),
        });
        return result as Record<string, unknown>;
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        addActivityEvent({
          request_id: requestId,
          stage,
          status: 'failed',
          message: `WebMCP ${toolName} failed: ${message}`,
          source: 'webmcp',
          tool_name: toolName,
          payload_preview: payloadPreview,
        });
        throw error;
      }
    },
    [addActivityEvent]
  );

  const submitSimulation = useCallback(
    async (payload?: Record<string, unknown>) => {
      const requestId = `sim-${Date.now()}`;
      const contractId = (payload?.contract_id as string) || '1042-B';
      const currentPrice = typeof payload?.current_price === 'number' ? payload.current_price : 120000;
      const proposedPrice = typeof payload?.proposed_price === 'number' ? payload.proposed_price : 100000;
      const priceDelta = typeof payload?.price_delta === 'number' ? payload.price_delta : -20000;
      const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

      startSimulation(requestId, contractId);

      // Reset all DAG nodes to idle for fresh run
      updateDAGNodeStatus('node-discover', 'idle');
      updateDAGNodeStatus('node-read', 'idle');
      updateDAGNodeStatus('node-evaluate', 'idle');
      updateDAGNodeStatus('node-reason', 'idle');
      updateDAGNodeStatus('node-propose', 'idle');
      updateDAGNodeStatus('node-approve', 'idle');

      try {
        // Stage 1: Discover Tools
        updateDAGNodeStatus('node-discover', 'active');
        selectDAGNode('node-discover');
        setStageState('negotiator', 'active');
        await delay(350);
        await invokeMCPTool('inspect_ui_schema', {}, `${requestId}-discover`, 'user_agent');
        updateDAGNodeStatus('node-discover', 'completed');
        setStageState('negotiator', 'completed');

        // Stage 2: Read Deal State & Constraints
        updateDAGNodeStatus('node-read', 'active');
        selectDAGNode('node-read');
        setStageState('user_agent', 'active');
        await delay(350);
        await invokeMCPTool('get_current_deal', { contract_id: contractId }, `${requestId}-deal`, 'webmcp');
        await invokeMCPTool('get_constraints', { contract_id: contractId }, `${requestId}-constraints`, 'webmcp');
        updateDAGNodeStatus('node-read', 'completed');
        setStageState('user_agent', 'completed');

        // Stage 3: Evaluate Offer (Decision Twin)
        updateDAGNodeStatus('node-evaluate', 'active');
        selectDAGNode('node-evaluate');
        setStageState('webmcp', 'active');
        await delay(350);
        await invokeMCPTool(
          'evaluate_offer',
          {
            contract_id: contractId,
            offer_data: JSON.stringify({
              label: 'Agent Proposed Offer',
              price: proposedPrice,
              terms: {
                liability: payload?.liability ?? 1.5,
                payment_terms: payload?.payment_terms ?? 'Net 30',
                delivery_timeline: payload?.delivery_timeline ?? 90,
              },
              source: 'webmcp-agent',
            }),
          },
          `${requestId}-evaluate`,
          'decision_twin'
        );
        updateDAGNodeStatus('node-evaluate', 'completed');
        setStageState('webmcp', 'completed');

        // Stage 4: Agent Strategy (Simulation & Reasoning)
        updateDAGNodeStatus('node-reason', 'active');
        selectDAGNode('node-reason');
        setStageState('decision_twin', 'active');
        await delay(350);
        const data = (await invokeMCPTool(
          'simulate_tradeoff',
          {
            contract_id: contractId,
            proposed_change: JSON.stringify({
              current_price: currentPrice,
              price_delta: priceDelta,
              proposed_price: proposedPrice,
            }),
          },
          `${requestId}-simulate`,
          'decision_twin'
        )) as unknown as SimulationOutcome;
        applySimulationOutcome(data);
        updateDAGNodeStatus('node-reason', 'completed');
        setStageState('decision_twin', 'completed');

        // Stage 5: Propose Counteroffer
        updateDAGNodeStatus('node-propose', 'active');
        selectDAGNode('node-propose');
        setStageState('deal_room', 'active');
        await delay(350);
        await invokeMCPTool(
          'propose_counteroffer',
          {
            contract_id: contractId,
            proposal_data: JSON.stringify({
              proposed_price: proposedPrice,
              liability: payload?.liability ?? 1.5,
              payment_terms: payload?.payment_terms ?? 'Net 30',
              delivery_timeline: payload?.delivery_timeline ?? 90,
              counterparty: 'Apex Global Enterprise',
            }),
          },
          `${requestId}-propose`,
          'deal_room'
        );
        updateDAGNodeStatus('node-propose', 'completed');
        setStageState('deal_room', 'completed');

        // Stage 6: Human Approval Boundary
        updateDAGNodeStatus('node-approve', 'active');
        selectDAGNode('node-approve');
        addActivityEvent({
          request_id: `${requestId}-awaiting-approval`,
          stage: 'deal_room',
          status: 'started',
          message: `Counteroffer Proposal ($${proposedPrice.toLocaleString()}) submitted. Awaiting human approval sign-off.`,
          source: 'webmcp',
          tool_name: 'human_approval',
        });
      } catch (networkErr: unknown) {
        const netMsg = networkErr instanceof Error ? networkErr.message : 'Network connection failed.';
        applySimulationFailure(requestId, netMsg);
      }
    },
    [startSimulation, addActivityEvent, setStageState, invokeMCPTool, applySimulationOutcome, applySimulationFailure, updateDAGNodeStatus, selectDAGNode]
  );

  // Action Dispatcher for SchemaRenderer nodes
  const handleAction = useCallback(
    (actionName: string, payload?: Record<string, unknown>) => {
      if (actionName === 'simulateTradeoff' || actionName === 'retrySimulation') {
        submitSimulation(payload);
      } else if (actionName === 'refreshSchema') {
        refreshSchema();
      } else if (actionName === 'approveProposal') {
        const proposal_id = (payload?.proposal_id as string) || 'prop-mcp-1042';
        approveProposal(proposal_id);
        updateDAGNodeStatus('node-approve', 'completed');
        addActivityEvent({
          request_id: `manual-${Date.now()}`,
          stage: 'negotiator',
          status: 'completed',
          message: `User approved counteroffer proposal ${proposal_id} ($105,000). Deal progressing to closure.`,
          source: 'ui',
          tool_name: 'human_approval.approve',
        });
      } else if (actionName === 'rejectProposal') {
        const proposal_id = (payload?.proposal_id as string) || 'prop-mcp-1042';
        rejectProposal(proposal_id);
        updateDAGNodeStatus('node-approve', 'failed');
        addActivityEvent({
          request_id: `manual-${Date.now()}`,
          stage: 'negotiator',
          status: 'failed',
          message: `User rejected counteroffer proposal ${proposal_id}. New negotiations required.`,
          source: 'ui',
          tool_name: 'human_approval.reject',
        });
      } else if (actionName === 'selectAlternative') {
        const altId = payload?.alternative_id as string;
        if (altId) selectAlternative(altId);
      } else if (actionName === 'selectDAGNode') {
        const nodeId = payload?.node_id as string;
        if (nodeId) selectDAGNode(nodeId);
      } else if (actionName === 'previewWireAgentMutation') {
        const patch = {
          className: 'bg-slate-900 border-2 border-rose-500/90 shadow-2xl shadow-rose-950/80 ring-2 ring-rose-500/50',
          props: { title: '⚠️ CRITICAL: Hard Liability Limit Violated (< 1.5x) [Wire-Agent Active]' },
        };
        invokeMCPTool(
          'preview_ui_mutation',
          {
            base_version: 2,
            patch_data: JSON.stringify(patch),
            component_target: 'hard-constraint-result',
          },
          `wire-preview-${Date.now()}`,
          'webmcp'
        ).catch(() => {});
        setStagedMutation({
          mutation_id: 'mut-wire-01',
          base_version: 2,
          status: 'previewed',
          patch,
          last_guard_error: null,
        });
      } else if (actionName === 'publishWireAgentMutation') {
        invokeMCPTool(
          'publish_ui_mutation',
          { mutation_id: 'mut-wire-01' },
          `wire-publish-${Date.now()}`,
          'deal_room'
        ).catch(() => {});
        setStagedMutation({
          mutation_id: 'mut-wire-01',
          base_version: 2,
          status: 'published',
          last_guard_error: null,
        });
      } else if (actionName === 'testForbiddenMutation') {
        const forbiddenPatch = {
          price: 45000,
          path: '/deal/current_price',
          notes: 'Unauthorized financial override attempt',
        };
        invokeMCPTool(
          'preview_ui_mutation',
          {
            base_version: 2,
            patch_data: JSON.stringify(forbiddenPatch),
            component_target: 'deal',
          },
          `wire-guard-${Date.now()}`,
          'webmcp'
        ).catch((err) => {
          const errMsg = err instanceof Error ? err.message : String(err);
          setStagedMutation({
            ...useDealRoomStore.getState().stagedMutation,
            last_guard_error: errMsg,
          });
        });
      } else if (actionName === 'resetWireAgentMutation') {
        setStagedMutation({
          base_version: 2,
          status: 'none',
          last_guard_error: null,
        });
        addActivityEvent({
          request_id: `wire-reset-${Date.now()}`,
          stage: 'deal_room',
          status: 'completed',
          message: 'Reset Wire-Agent presentation mutations to default v2 layout.',
          source: 'webmcp',
        });
      } else if (actionName === 'simulateHostileProposal') {
        selectAlternative('alt_restrictive');
        addActivityEvent({
          request_id: `gov-block-${Date.now()}`,
          stage: 'decision_twin',
          status: 'failed',
          message: '🚨 GOVERNANCE BOUNDARY BLOCKED: Restrictive Seller Offer ($95,000, 0.8x liability) violates hard constraint #3. Agent execution halted.',
          source: 'decision_twin',
          tool_name: 'AgentGovernanceBoundary',
        });
      } else if (actionName === 'compileIntent') {
        const prompt = payload?.prompt as string;
        if (prompt) compileIntentFromText(prompt);
      } else {
        console.info(`[Action Dispatch] Unhandled action: ${actionName}`, payload);
      }
    },
    [
      submitSimulation,
      refreshSchema,
      approveProposal,
      rejectProposal,
      addActivityEvent,
      selectAlternative,
      selectDAGNode,
      setStagedMutation,
      compileIntentFromText,
      updateDAGNodeStatus,
      invokeMCPTool,
    ]
  );

  // In-Browser WebMCP Registration (for ChatGPT In-App Browser, Chrome DevTools & Autonomous Agents)
  useEffect(() => {
    const registerBrowserTools = () => {
      // Create unified ModelContext object adhering to WebMCP standard
      const existing = (document as unknown as { modelContext?: ModelContextObject }).modelContext;
      const modelContext: ModelContextObject = existing || {
        tools: {},
        registerTool(toolDef: ModelContextTool) {
          this.tools[toolDef.name] = toolDef;
        },
        getTools() {
          return Object.values(this.tools);
        },
        async executeTool(name: string, input: Record<string, unknown> = {}) {
          const tool = this.tools[name];
          if (!tool) {
            throw new Error(`WebMCP Tool "${name}" not found. Available tools: ${Object.keys(this.tools).join(', ')}`);
          }
          return await tool.execute(input);
        },
      };

      // Ensure helper methods exist if re-using existing object
      if (!modelContext.getTools) {
        modelContext.getTools = function () {
          return Object.values(this.tools);
        };
      }
      if (!modelContext.executeTool) {
        modelContext.executeTool = async function (name: string, input: Record<string, unknown> = {}) {
          const tool = this.tools[name];
          if (!tool) {
            throw new Error(`WebMCP Tool "${name}" not found. Available tools: ${Object.keys(this.tools).join(', ')}`);
          }
          return await tool.execute(input);
        };
      }

      // Expose globally on document, window, and window.webmcp
      document.modelContext = modelContext;
      window.modelContext = modelContext;
      (window as unknown as { webmcp: ModelContextObject }).webmcp = modelContext;

      const reg = modelContext.registerTool.bind(modelContext);

      try {
        // --- 1. Pipeline Lifecycle Tools (as requested by ChatGPT / Agent QA) ---
        reg({
          name: 'create_deal',
          title: 'Create Deal',
          description: 'Create a new enterprise deal in the Nexus Deal Room repository.',
          inputSchema: {
            type: 'object',
            properties: {
              company: { type: 'string', description: 'Counterparty company name (e.g. Acme Corp)' },
              value: { type: 'number', description: 'Annual contract value in USD (e.g. 2000000)' },
              stage: { type: 'string', description: 'Deal stage: Draft, Negotiation, Approved, Closed Won' },
            },
            required: ['company', 'value'],
            additionalProperties: false,
          },
          execute: async (input: Record<string, unknown>) => {
            const res = await fetch('/api/contracts', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(input),
            });
            const data = await res.json();
            addActivityEvent({
              request_id: `deal-create-${Date.now()}`,
              stage: 'deal_room',
              status: 'completed',
              message: `WebMCP created deal #${data?.deal?.contract_id || 'new'} for ${input.company} ($${Number(input.value).toLocaleString()}).`,
              source: 'webmcp',
              tool_name: 'create_deal',
            });
            return data;
          },
        });

        reg({
          name: 'get_deals',
          title: 'Get Deals',
          description: 'Retrieve and search deals across the entire pipeline repository.',
          inputSchema: {
            type: 'object',
            properties: {
              query: { type: 'string', description: 'Search term' },
              status: { type: 'string', description: 'Filter by stage' },
            },
          },
          execute: async (input: Record<string, unknown>) => {
            const params = new URLSearchParams();
            if (input?.query) params.set('query', String(input.query));
            if (input?.status) params.set('status', String(input.status));
            const res = await fetch(`/api/contracts?${params.toString()}`);
            return await res.json();
          },
        });

        reg({
          name: 'get_deal',
          title: 'Get Deal',
          description: 'Retrieve detailed record and notes for a specific contract ID.',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: { type: 'string', description: 'Contract ID (e.g. #1042-B)' },
            },
            required: ['contract_id'],
          },
          execute: async (input: Record<string, unknown>) => {
            const cid = encodeURIComponent(String(input.contract_id || '1042-B'));
            const res = await fetch(`/api/contracts/${cid}`);
            return await res.json();
          },
        });

        reg({
          name: 'move_deal_stage',
          title: 'Move Deal Stage',
          description: 'Transition a deal stage (e.g. Draft -> Negotiation -> Approved -> Closed Won).',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: { type: 'string', description: 'Contract ID' },
              stage: { type: 'string', description: 'Target stage' },
            },
            required: ['contract_id', 'stage'],
          },
          execute: async (input: Record<string, unknown>) => {
            const cid = encodeURIComponent(String(input.contract_id || '1042-B'));
            const res = await fetch(`/api/contracts/${cid}/stage`, {
              method: 'PATCH',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ stage: input.stage }),
            });
            return await res.json();
          },
        });

        reg({
          name: 'add_deal_note',
          title: 'Add Deal Note',
          description: 'Append an analytical or context note to a contract record.',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: { type: 'string', description: 'Contract ID' },
              note: { type: 'string', description: 'Note content' },
              author: { type: 'string', description: 'Author' },
            },
            required: ['contract_id', 'note'],
          },
          execute: async (input: Record<string, unknown>) => {
            const cid = encodeURIComponent(String(input.contract_id || '1042-B'));
            const res = await fetch(`/api/contracts/${cid}/notes`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ note: input.note, author: input.author || 'ChatGPT Agent' }),
            });
            return await res.json();
          },
        });

        // --- 2. Real-Time Deal Room & Decision Twin Tools ---
        reg({
          name: 'get_current_deal',
          title: 'Get Current Deal',
          description: 'Retrieve current negotiation state, baseline price, and counterparty terms.',
          inputSchema: {
            type: 'object',
            properties: { contract_id: { type: 'string', default: '1042-B' } },
          },
          execute: async (args: Record<string, unknown>) => {
            const cid = (args.contract_id as string) || '1042-B';
            return await invokeMCPTool('get_current_deal', { contract_id: cid }, `browser-${Date.now()}`, 'webmcp');
          },
        });

        reg({
          name: 'get_constraints',
          title: 'Get Constraints',
          description: 'Retrieve non-negotiable hard limits and advisory trade-off rules for contract.',
          inputSchema: {
            type: 'object',
            properties: { contract_id: { type: 'string', default: '1042-B' } },
          },
          execute: async (args: Record<string, unknown>) => {
            const cid = (args.contract_id as string) || '1042-B';
            return await invokeMCPTool('get_constraints', { contract_id: cid }, `browser-${Date.now()}`, 'webmcp');
          },
        });

        reg({
          name: 'evaluate_offer',
          title: 'Evaluate Offer',
          description: 'Runs deterministic Decision Twin evaluation on proposed terms. Returns score and hard constraint violations.',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: { type: 'string', default: '1042-B' },
              proposed_price: { type: 'number' },
              liability: { type: 'number' },
            },
            required: ['contract_id', 'proposed_price'],
          },
          execute: async (args: Record<string, unknown>) => {
            const cid = (args.contract_id as string) || '1042-B';
            return await invokeMCPTool('evaluate_offer', { contract_id: cid, offer_data: JSON.stringify(args) }, `browser-${Date.now()}`, 'decision_twin');
          },
        });

        reg({
          name: 'simulate_tradeoff',
          title: 'Simulate Tradeoff',
          description: 'Runs a tradeoff simulation against contract terms using the Decision Twin.',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: { type: 'string' },
              proposed_price: { type: 'number' },
              liability: { type: 'number' },
              payment_terms: { type: 'string' },
              delivery_timeline: { type: 'number' },
            },
            required: ['contract_id', 'proposed_price'],
          },
          execute: async (input: Record<string, unknown>) => {
            await submitSimulation(input);
            return { status: 'submitted', note: 'Decision Twin calculation completed' };
          },
        });

        reg({
          name: 'propose_counteroffer',
          title: 'Propose Counteroffer',
          description: 'Submits a formal counteroffer to the Human Approval Boundary.',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: { type: 'string', default: '1042-B' },
              proposed_price: { type: 'number' },
              liability: { type: 'number' },
            },
            required: ['contract_id', 'proposed_price'],
          },
          execute: async (args: Record<string, unknown>) => {
            const cid = (args.contract_id as string) || '1042-B';
            return await invokeMCPTool('propose_counteroffer', { contract_id: cid, proposal_data: JSON.stringify(args) }, `browser-${Date.now()}`, 'deal_room');
          },
        });

        reg({
          name: 'execute_contract',
          title: 'Execute Contract',
          description: 'Attempts autonomous binding execution of contract terms. Strictly guarded by human sign-off.',
          inputSchema: {
            type: 'object',
            properties: {
              contract_id: { type: 'string', default: '1042-B' },
              signature_token: { type: 'string' },
            },
            required: ['contract_id'],
          },
          execute: async (args: Record<string, unknown>) => {
            const cid = (args.contract_id as string) || '1042-B';
            return await invokeMCPTool('execute_contract', { contract_id: cid, signature_token: args.signature_token }, `browser-${Date.now()}`, 'deal_room');
          },
        });

        reg({
          name: 'compile_intent',
          title: 'Compile Intent',
          description: 'Translates natural language human intent into mathematical weights for Decision Twin.',
          inputSchema: {
            type: 'object',
            properties: { prompt: { type: 'string' } },
            required: ['prompt'],
          },
          execute: async (args: Record<string, unknown>) => {
            const prompt = (args.prompt as string) || '';
            compileIntentFromText(prompt);
            return { status: 'compiled', intent: prompt };
          },
        });

        reg({
          name: 'mutate_ui_schema',
          title: 'Mutate UI Schema',
          description: 'Mutate website layout and Tailwind CSS styling dynamically in real-time (presentation only).',
          inputSchema: {
            type: 'object',
            properties: {
              component_target: { type: 'string' },
              schema_patch: { type: 'string' },
            },
            required: ['component_target', 'schema_patch'],
          },
          execute: async (input: Record<string, unknown>) => {
            const result = await invokeMCPTool('mutate_ui_schema', input, `browser-${Date.now()}`, 'webmcp');
            await refreshSchema();
            return result;
          },
        });
      } catch (e) {
        console.warn('[WebMCP] In-browser registration note:', e);
      }
    };

    registerBrowserTools();
  }, [refreshSchema, submitSimulation, invokeMCPTool, compileIntentFromText, addActivityEvent]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white font-sans">
        <div className="text-center space-y-4">
          <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-base font-medium text-slate-300">Loading Nexus Deal Room...</p>
        </div>
      </div>
    );
  }

  if (error && !uiSchema) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-red-400 font-sans p-6">
        <div className="max-w-md bg-slate-900 border border-red-500/30 rounded-xl p-6 text-center shadow-2xl space-y-4">
          <div className="w-12 h-12 bg-red-500/10 rounded-full flex items-center justify-center mx-auto text-red-400 text-xl font-bold">
            !
          </div>
          <h2 className="text-xl font-bold text-white">Connection Error</h2>
          <p className="text-sm text-slate-300">{error}</p>
          <button
            onClick={() => fetchSchema(true)}
            className="w-full px-4 py-2.5 bg-red-600 hover:bg-red-500 text-white rounded-lg text-sm font-semibold transition shadow-lg"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  if (window.location.pathname === '/contracts') {
    return <ContractSearchPage />;
  }

  if (window.location.pathname === '/agent-qa') {
    return <AgentQAPage />;
  }

  if (!uiSchema || !uiSchema.layout) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-amber-400">
        <p className="text-xl">No valid UI schema returned from backend.</p>
      </div>
    );
  }

  return (
    <div className="app-root relative bg-slate-950 min-h-screen">
      {/* High-Signal System Status Badge */}
      <aside
        aria-label="System status"
        className="fixed bottom-4 right-4 z-50 flex items-center space-x-3 bg-slate-900/95 backdrop-blur-md border border-slate-800 text-xs px-4 py-2.5 rounded-full shadow-2xl"
      >
        <span className="flex h-2 w-2 relative">
          <span
            className={`animate-ping absolute inline-flex h-full w-full rounded-full ${
              isLiveConnected ? 'bg-emerald-400' : 'bg-rose-400'
            } opacity-75`}
          ></span>
          <span
            className={`relative inline-flex rounded-full h-2 w-2 ${
              isLiveConnected ? 'bg-emerald-500' : 'bg-rose-500'
            }`}
          ></span>
        </span>
        <span className="font-semibold text-slate-200">
          {isLiveConnected ? 'Decision Twin Active' : 'Reconnecting...'}
        </span>
        <span className="text-slate-600">|</span>
        <span className="text-sky-400 font-mono text-[11px]">document.modelContext Ready</span>
        <span className="text-slate-600">|</span>
        <span className="text-emerald-400 font-medium">Human Authority Enforced</span>
        <span className="text-slate-600">|</span>
        <a href="/contracts" className="font-medium text-slate-400 hover:text-white">Contracts</a>
        <span className="text-slate-600">|</span>
        <a href="/agent-qa" className="font-medium text-sky-400 hover:text-white flex items-center space-x-1">
          <span>🧪</span>
          <span>Agent QA</span>
        </a>
      </aside>

      {/* 100% Dynamic Schema-Driven Renderer */}
      <SchemaRenderer node={uiSchema.layout as SchemaNode} onAction={handleAction} />
    </div>
  );
}

export default App;
