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
  const [hasBrowserWebMCP, setHasBrowserWebMCP] = useState(false);

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
      });
      setStageState('decision_twin', 'completed');

      // Stage 5: Deal Room UI updated
      addActivityEvent({
        request_id: outcome.request_id,
        stage: 'deal_room',
        status: 'completed',
        message: `Deal Room rendered tradeoff outcome for contract ${outcome.contract_id}: Proposed $${outcome.proposed_price.toLocaleString()}.`,
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
      });
      setStageState('decision_twin', 'failed');

      addActivityEvent({
        request_id: requestId,
        stage: 'deal_room',
        status: 'failed',
        message: 'Deal Room displayed simulation failure state with retry option.',
      });
      setStageState('deal_room', 'failed');
    },
    [failSimulation, addActivityEvent, setStageState]
  );

  const submitSimulation = useCallback(
    async (payload?: Record<string, unknown>) => {
      const requestId = `sim-${Date.now()}`;
      const contractId = (payload?.contract_id as string) || '1042-B';
      const currentPrice = typeof payload?.current_price === 'number' ? payload.current_price : 120000;
      const proposedPrice = typeof payload?.proposed_price === 'number' ? payload.proposed_price : 100000;
      const priceDelta = typeof payload?.price_delta === 'number' ? payload.price_delta : -20000;

      startSimulation(requestId, contractId);

      // Stage 1: Negotiator
      addActivityEvent({
        request_id: requestId,
        stage: 'negotiator',
        status: 'started',
        message: `Negotiator proposed price concession from $${currentPrice.toLocaleString()} to $${proposedPrice.toLocaleString()} (${priceDelta < 0 ? '-' : '+'}$${Math.abs(priceDelta).toLocaleString()}).`,
      });
      setStageState('negotiator', 'completed');

      // Stage 2: User Agent
      addActivityEvent({
        request_id: requestId,
        stage: 'user_agent',
        status: 'started',
        message: 'User Agent (Microsoft Agentic AI) evaluating prompt and preparing simulate_tradeoff tool call.',
      });
      setStageState('user_agent', 'active');

      // Stage 3: WebMCP Gateway
      addActivityEvent({
        request_id: requestId,
        stage: 'webmcp',
        status: 'started',
        message: `WebMCP Gateway routing simulate_tradeoff request for contract #${contractId}.`,
      });
      setStageState('user_agent', 'completed');
      setStageState('webmcp', 'active');

      // Stage 4: Decision Twin
      setStageState('webmcp', 'completed');
      setStageState('decision_twin', 'active');

      try {
        const response = await fetch('/api/simulations/tradeoff', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request_id: requestId,
            contract_id: contractId,
            proposed_change: {
              current_price: currentPrice,
              price_delta: priceDelta,
              proposed_price: proposedPrice,
            },
          }),
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({ detail: response.statusText }));
          const message = errData.detail || `Request failed with status ${response.status}`;
          applySimulationFailure(requestId, message);
          return;
        }

        const data: SimulationOutcome = await response.json();
        applySimulationOutcome(data);
      } catch (networkErr: unknown) {
        const netMsg = networkErr instanceof Error ? networkErr.message : 'Network connection failed.';
        applySimulationFailure(requestId, netMsg);
      }
    },
    [startSimulation, addActivityEvent, setStageState, applySimulationOutcome, applySimulationFailure]
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
        });
      } else if (actionName === 'selectAlternative') {
        const altId = payload?.alternative_id as string;
        if (altId) selectAlternative(altId);
      } else if (actionName === 'selectDAGNode') {
        const nodeId = payload?.node_id as string;
        if (nodeId) selectDAGNode(nodeId);
      } else if (actionName === 'previewWireAgentMutation') {
        setStagedMutation({
          mutation_id: 'mut-wire-01',
          base_version: 2,
          status: 'previewed',
          patch: {
            className: 'bg-slate-900 border-2 border-rose-500/80 shadow-rose-900/20',
            props: { title: '⚠️ CRITICAL: Hard Liability Limit Violated (< 1.5x)' },
          },
        });
        addActivityEvent({
          request_id: 'wire-preview-action',
          stage: 'webmcp',
          status: 'completed',
          message: 'Wire-Agent previewed safety-focused mutation mut-wire-01.',
        });
      } else if (actionName === 'publishWireAgentMutation') {
        setStagedMutation({
          mutation_id: 'mut-wire-01',
          base_version: 2,
          status: 'published',
        });
        addActivityEvent({
          request_id: 'wire-publish-action',
          stage: 'deal_room',
          status: 'completed',
          message: 'Published UI schema version 3. Decision Twin results 100% invariant.',
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
    ]
  );

  // In-Browser WebMCP Registration (for ChatGPT In-App Browser & Chrome DevTools testing)
  useEffect(() => {
    const registerBrowserTools = () => {
      interface ModelContextTool {
        name: string;
        description: string;
        inputSchema: Record<string, unknown>;
        execute: (input: Record<string, unknown>) => Promise<unknown>;
      }
      interface ModelContextContainer {
        modelContext?: {
          registerTool: (tool: ModelContextTool) => void;
        };
      }

      const win = window as unknown as ModelContextContainer;
      const doc = document as unknown as ModelContextContainer;
      const nav = navigator as unknown as ModelContextContainer;
      const modelContext = doc.modelContext || win.modelContext || nav.modelContext;

      if (modelContext?.registerTool) {
        setHasBrowserWebMCP(true);
        try {
          modelContext.registerTool({
            name: 'mutate_ui_schema',
            description: 'Mutate website layout and Tailwind CSS styling dynamically in real-time.',
            inputSchema: {
              type: 'object',
              properties: {
                component_target: { type: 'string' },
                schema_patch: { type: 'string' },
              },
              required: ['component_target', 'schema_patch'],
            },
            execute: async (input: Record<string, unknown>) => {
              const res = await fetch('/api/mcp/messages', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  jsonrpc: '2.0',
                  method: 'tools/call',
                  params: { name: 'mutate_ui_schema', arguments: input },
                  id: 1,
                }),
              });
              await refreshSchema();
              return await res.json();
            },
          });

          modelContext.registerTool({
            name: 'simulate_tradeoff',
            description: 'Runs a tradeoff simulation against contract terms using the Decision Twin.',
            inputSchema: {
              type: 'object',
              properties: {
                contract_id: { type: 'string' },
                proposed_change: { type: 'string' },
              },
              required: ['contract_id', 'proposed_change'],
            },
            execute: async (input: Record<string, unknown>) => {
              await submitSimulation(input);
              return { status: 'submitted' };
            },
          });
        } catch (e) {
          console.warn('[WebMCP] In-browser registration note:', e);
        }
      }
    };

    registerBrowserTools();
  }, [refreshSchema, submitSimulation]);

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

  if (!uiSchema || !uiSchema.layout) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-amber-400">
        <p className="text-xl">No valid UI schema returned from backend.</p>
      </div>
    );
  }

  return (
    <div className="app-root relative bg-slate-950 min-h-screen">
      {/* Live WebMCP & Schema Version Badge */}
      <aside
        aria-label="System status"
        className="fixed bottom-4 right-4 z-50 flex items-center space-x-3 bg-slate-900/90 backdrop-blur-md border border-slate-800 text-xs px-3.5 py-2 rounded-full shadow-2xl"
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
          {isLiveConnected ? 'Nexus Connected' : 'Reconnecting...'}
        </span>
        {hasBrowserWebMCP && (
          <>
            <span className="text-slate-600">|</span>
            <span className="text-emerald-400 font-medium">ChatGPT In-App Ready</span>
          </>
        )}
        <span className="text-slate-600">|</span>
        <span className="text-sky-400 font-mono font-medium">Schema v{uiSchema.version}</span>
      </aside>

      {/* 100% Dynamic Schema-Driven Renderer */}
      <SchemaRenderer node={uiSchema.layout as SchemaNode} onAction={handleAction} />
    </div>
  );
}

export default App;
