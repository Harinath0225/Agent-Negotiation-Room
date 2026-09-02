import React from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MarkerType,
  type Node as FlowNode,
  type Edge as FlowEdge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  useDealRoomStore,
  WorkflowStageId,
  INITIAL_ALTERNATIVES,
} from '../store';

export interface SchemaNode {
  type: string;
  props?: Record<string, unknown>;
  className?: string;
  children?: SchemaNode[];
}

export interface SchemaRendererProps {
  node: SchemaNode;
  onAction?: (actionName: string, payload?: Record<string, unknown>) => void;
}

const ConstraintKitchenCard: React.FC<{
  title?: string;
  onAction?: (actionName: string, payload?: Record<string, unknown>) => void;
}> = ({ title, onAction }) => {
  const { intentWeights, compileIntentFromText, addActivityEvent } = useDealRoomStore();
  const [promptInput, setPromptInput] = React.useState('');

  const handleSubmitIntent = (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptInput.trim()) return;
    compileIntentFromText(promptInput);
    if (onAction) {
      onAction('compileIntent', { prompt: promptInput });
    }
    addActivityEvent({
      request_id: `intent-${Date.now()}`,
      stage: 'negotiator',
      status: 'completed',
      message: `Constraint Kitchen compiled natural language intent: "${promptInput}" into dynamic mathematical weights.`,
    });
    setPromptInput('');
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-semibold text-white">{title || 'Constraint Kitchen (Human Intent Compiler)'}</h2>
          <p className="text-xs text-slate-400">State strategic intent in plain language to compile mathematical weights</p>
        </div>
        <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-sky-500/10 text-sky-400 border border-sky-500/30">
          Node 1: Intent
        </span>
      </div>

      <form onSubmit={handleSubmitIntent} className="space-y-3">
        <div className="flex space-x-2">
          <input
            type="text"
            value={promptInput}
            onChange={(e) => setPromptInput(e.target.value)}
            placeholder="e.g. Speed is more important than budget right now..."
            className="flex-1 px-3.5 py-2.5 bg-slate-950/80 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition-colors"
          />
          <button
            type="submit"
            className="py-2.5 px-4 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs rounded-lg transition-colors shadow-md"
          >
            Compile Intent
          </button>
        </div>
      </form>

      <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-lg space-y-3 text-xs">
        <div className="flex items-center justify-between text-slate-300">
          <span className="font-semibold text-slate-200">Current Intent Weights:</span>
          <span className="font-mono text-[11px] text-slate-400 truncate max-w-xs">{intentWeights.raw_intent || 'Default distribution'}</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
          <div className="p-2 bg-slate-900 border border-slate-800 rounded text-center">
            <span className="text-slate-400 text-[10px] block uppercase">Price Weight</span>
            <span className="text-sky-400 font-bold text-sm">{Math.round(intentWeights.price * 100)}%</span>
          </div>
          <div className="p-2 bg-slate-900 border border-slate-800 rounded text-center">
            <span className="text-slate-400 text-[10px] block uppercase">Speed Weight</span>
            <span className="text-emerald-400 font-bold text-sm">{Math.round(intentWeights.speed * 100)}%</span>
          </div>
          <div className="p-2 bg-slate-900 border border-slate-800 rounded text-center">
            <span className="text-slate-400 text-[10px] block uppercase">Liability Weight</span>
            <span className="text-amber-400 font-bold text-sm">{Math.round(intentWeights.liability * 100)}%</span>
          </div>
          <div className="p-2 bg-slate-900 border border-slate-800 rounded text-center">
            <span className="text-slate-400 text-[10px] block uppercase">Payment Weight</span>
            <span className="text-purple-400 font-bold text-sm">{Math.round(intentWeights.payment * 100)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const SchemaRenderer: React.FC<SchemaRendererProps> = ({ node, onAction }) => {
  const {
    simulationStatus,
    lastOutcome,
    simulationError,
    workflowStages,
    selectedStageId,
    activityEvents,
    selectStage,
    alternatives,
    comparison,
    selectAlternative,
    dagNodes,
    dagEdges,
    selectedDAGNodeId,
    selectDAGNode,
    stagedMutation,
    setStagedMutation,
    addActivityEvent,
    approvalStatus,
  } = useDealRoomStore();

  const { type, props = {}, className = '', children = [] } = node;

  // Render children recursively
  const renderedChildren = children.map((child, index) => (
    <SchemaRenderer key={index} node={child} onAction={onAction} />
  ));

  // Dispatch click actions for action-bound buttons
  const handleButtonClick = (e: React.MouseEvent) => {
    if (typeof props.action === 'string' && onAction) {
      e.preventDefault();
      onAction(props.action, props);
    } else if (typeof props.onClick === 'function') {
      (props.onClick as (e: React.MouseEvent) => void)(e);
    }
  };

  // 1. Simulation Control Node
  if (type === 'simulation-control') {
    const isPending = simulationStatus === 'pending';
    const label = (props.label as string) || 'Simulate Tradeoff';
    const actionName = (props.action as string) || 'simulateTradeoff';

    return (
      <div className="space-y-3 pt-2">
        <button
          id="simulate-tradeoff-btn"
          disabled={isPending}
          onClick={() => onAction && onAction(actionName, props)}
          className={`w-full py-3.5 px-5 rounded-lg font-semibold text-sm flex items-center justify-center space-x-2 transition-all duration-200 shadow-lg ${
            isPending
              ? 'bg-slate-800 text-slate-400 cursor-not-allowed border border-slate-700'
              : 'bg-gradient-to-r from-sky-600 to-sky-500 hover:from-sky-500 hover:to-sky-400 text-white shadow-sky-900/30 hover:shadow-sky-800/50 hover:scale-[1.01] active:scale-[0.99] border border-sky-400/30'
          }`}
        >
          {isPending ? (
            <>
              <svg
                className="animate-spin -ml-1 mr-2 h-4 w-4 text-sky-400"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Simulating Tradeoff with Decision Twin...</span>
            </>
          ) : (
            <>
              <svg
                className="w-4 h-4 text-sky-200"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              <span>{label}</span>
            </>
          )}
        </button>
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span>Target Contract: #1042-B</span>
          <span>Delta: -$20,000 (-16.7%)</span>
        </div>
      </div>
    );
  }

  // 2. Simulation Result Node
  if (type === 'simulation-result') {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800/80 mb-4">
          <h2 className="text-lg font-semibold text-white flex items-center space-x-2">
            <span>{(props.title as string) || 'Simulation Outcome'}</span>
          </h2>
          <span
            className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
              simulationStatus === 'succeeded'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : simulationStatus === 'pending'
                ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                : simulationStatus === 'failed'
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                : 'bg-slate-800 text-slate-400'
            }`}
          >
            {simulationStatus === 'succeeded'
              ? 'Calculated'
              : simulationStatus === 'pending'
              ? 'Evaluating...'
              : simulationStatus === 'failed'
              ? 'Error'
              : 'Idle'}
          </span>
        </div>

        {/* State 1: Idle / Ready */}
        {simulationStatus === 'ready' && (
          <div className="py-8 text-center text-slate-400 space-y-2">
            <div className="w-10 h-10 mx-auto rounded-full bg-slate-800/60 flex items-center justify-center text-slate-500">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <p className="text-sm">Ready to evaluate negotiation scenarios.</p>
            <p className="text-xs text-slate-500">
              Trigger a tradeoff simulation above to view Decision Twin sensitivity.
            </p>
          </div>
        )}

        {/* State 2: Pending */}
        {simulationStatus === 'pending' && (
          <div className="py-8 text-center space-y-3">
            <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-sm font-medium text-slate-300">
              Decision Twin evaluating price tradeoff...
            </p>
            <p className="text-xs text-slate-500">
              Computing risk scores, acceptance probability, and elasticity.
            </p>
          </div>
        )}

        {/* State 3: Failure */}
        {simulationStatus === 'failed' && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-lg space-y-3">
            <div className="flex items-start space-x-3">
              <span className="text-rose-400 text-lg">⚠️</span>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-rose-300">Simulation Failed</p>
                <p className="text-xs text-rose-200/80">
                  {simulationError || 'The tradeoff simulation could not be completed.'}
                </p>
              </div>
            </div>
            <button
              id="retry-simulation-btn"
              onClick={() => onAction && onAction('simulateTradeoff', { retry: true })}
              className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-semibold transition shadow"
            >
              Retry Simulation
            </button>
          </div>
        )}

        {/* State 4: Succeeded */}
        {simulationStatus === 'succeeded' && lastOutcome && (
          <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
                <span className="text-xs text-slate-400 block mb-0.5">Proposed Price</span>
                <span className="text-xl font-bold font-mono text-emerald-400">
                  ${lastOutcome.proposed_price.toLocaleString()}
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">
                  Base: ${lastOutcome.current_price.toLocaleString()}
                </span>
              </div>

              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg">
                <span className="text-xs text-slate-400 block mb-0.5">Acceptance Prob.</span>
                <div className="flex items-baseline space-x-1">
                  <span className="text-xl font-bold font-mono text-sky-400">
                    {Math.round(lastOutcome.acceptance_probability * 100)}%
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                  <div
                    className="bg-sky-400 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.round(lastOutcome.acceptance_probability * 100)}%` }}
                  ></div>
                </div>
              </div>

              <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg col-span-2 sm:col-span-1">
                <span className="text-xs text-slate-400 block mb-0.5">Risk Score Delta</span>
                <span
                  className={`text-xl font-bold font-mono ${
                    lastOutcome.risk_score_delta > 0 ? 'text-amber-400' : 'text-emerald-400'
                  }`}
                >
                  {lastOutcome.risk_score_delta > 0 ? '+' : ''}
                  {lastOutcome.risk_score_delta.toFixed(2)}
                </span>
                <span className="text-[10px] text-slate-500 block mt-0.5">
                  {lastOutcome.risk_score_delta > 0 ? 'Higher exposure' : 'Lower exposure'}
                </span>
              </div>
            </div>

            {/* Recommendation Box */}
            <div className="p-4 bg-sky-950/30 border border-sky-800/40 rounded-lg space-y-1.5">
              <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider block">
                Decision Twin Strategic Guidance
              </span>
              <p className="text-sm text-slate-200 leading-relaxed">
                {lastOutcome.recommendation}
              </p>
            </div>

            {/* Terms and metadata */}
            <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/60 gap-2">
              <div className="flex items-center space-x-2">
                <span>Affected Terms:</span>
                {lastOutcome.affected_terms.map((term, i) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px]"
                  >
                    {term}
                  </span>
                ))}
              </div>
              <span className="text-[11px] font-mono text-slate-500">
                {new Date(lastOutcome.completed_at).toLocaleTimeString()}
              </span>
            </div>
          </div>
        )}
      </div>
    );
  }

  // 3. WebMCP Workflow Stages Node
  if (type === 'workflow-stages' || type === 'workflow-architecture') {
    const selectedStage = workflowStages.find((s) => s.id === selectedStageId);

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-white">
              {(props.title as string) || 'WebMCP Workflow Diagram'}
            </h2>
            <p className="text-xs text-slate-400">
              Interactive 5-stage architecture • Click a stage to inspect
            </p>
          </div>
          {selectedStageId && (
            <button
              onClick={() => selectStage(null)}
              className="text-xs text-slate-400 hover:text-slate-200 underline"
            >
              Clear selection
            </button>
          )}
        </div>

        {/* 5 Stages Flow */}
        <div className="space-y-3">
          {workflowStages.map((stage, idx) => {
            const isSelected = selectedStageId === stage.id;
            const isLast = idx === workflowStages.length - 1;

            return (
              <div key={stage.id} className="relative">
                <div
                  id={`workflow-stage-${stage.id}`}
                  role="button"
                  tabIndex={0}
                  aria-pressed={isSelected}
                  onClick={() => selectStage(isSelected ? null : stage.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      selectStage(isSelected ? null : stage.id);
                    }
                  }}
                  className={`p-3.5 rounded-lg border transition-all duration-150 cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? 'bg-sky-950/60 border-sky-400 shadow-lg shadow-sky-950/50 ring-1 ring-sky-400'
                      : stage.state === 'active'
                      ? 'bg-slate-800/90 border-sky-500/70 animate-pulse'
                      : stage.state === 'completed'
                      ? 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                      : stage.state === 'failed'
                      ? 'bg-rose-950/40 border-rose-500/60'
                      : 'bg-slate-950/50 border-slate-800/80 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                        isSelected
                          ? 'bg-sky-500 text-white'
                          : stage.state === 'completed'
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                          : stage.state === 'active'
                          ? 'bg-sky-500/20 text-sky-400 border border-sky-500/40'
                          : stage.state === 'failed'
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {idx + 1}
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-slate-200">{stage.label}</div>
                      <div className="text-xs text-slate-400">{stage.role}</div>
                    </div>
                  </div>

                  <span
                    className={`text-[11px] px-2 py-0.5 rounded font-mono uppercase tracking-wider ${
                      stage.state === 'active'
                        ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                        : stage.state === 'completed'
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : stage.state === 'failed'
                        ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        : 'bg-slate-800 text-slate-500'
                    }`}
                  >
                    {stage.state}
                  </span>
                </div>

                {!isLast && (
                  <div className="flex justify-center my-1 text-slate-600">
                    <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                      <path
                        fillRule="evenodd"
                        d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Selected Stage Detail Panel */}
        {selectedStage && (
          <div className="p-3.5 bg-slate-950 border border-sky-500/40 rounded-lg space-y-1.5 animate-fadeIn">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-sky-400">
                Stage {selectedStage.label}
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                Role: {selectedStage.role}
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {selectedStage.description}
            </p>
          </div>
        )}
      </div>
    );
  }

  // 4. Activity Timeline / Agent Activity Log Node (US2)
  if (type === 'activity-timeline' || type === 'agent-activity-log') {
    const getStageColor = (stage: WorkflowStageId) => {
      switch (stage) {
        case 'negotiator':
          return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
        case 'user_agent':
          return 'text-sky-400 bg-sky-500/10 border-sky-500/20';
        case 'webmcp':
          return 'text-purple-400 bg-purple-500/10 border-purple-500/20';
        case 'decision_twin':
          return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
        case 'deal_room':
          return 'text-teal-400 bg-teal-500/10 border-teal-500/20';
        default:
          return 'text-slate-400 bg-slate-800 border-slate-700';
      }
    };

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-semibold text-white">
              {(props.title as string) || 'Activity Timeline'}
            </h2>
            <span className="text-xs font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
              {activityEvents.length} events
            </span>
          </div>
          <span className="text-[11px] text-slate-500">Capped at 50 (newest first)</span>
        </div>

        <div className="max-h-80 overflow-y-auto space-y-2.5 pr-1 text-xs">
          {activityEvents.map((evt) => {
            const isStageSelected = selectedStageId === evt.stage;

            return (
              <div
                key={evt.id}
                role="button"
                tabIndex={0}
                onClick={() => selectStage(isStageSelected ? null : evt.stage)}
                className={`p-3 rounded-lg border transition-all cursor-pointer ${
                  isStageSelected
                    ? 'bg-sky-950/70 border-sky-400 shadow-sm'
                    : 'bg-slate-950/60 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider border ${getStageColor(
                      evt.stage
                    )}`}
                  >
                    {evt.stage.replace('_', ' ')}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        evt.status === 'completed'
                          ? 'bg-emerald-400'
                          : evt.status === 'started'
                          ? 'bg-sky-400 animate-ping'
                          : 'bg-rose-400'
                      }`}
                    ></span>
                    <span className="text-[10px] font-mono text-slate-500">
                      {new Date(evt.occurred_at).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                <p className="text-slate-300 leading-snug">{evt.message}</p>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // 5. Hard Constraint Result Node (Phase 3: US1)
  if (type === 'hard-constraint-result') {
    if (!lastOutcome || simulationStatus !== 'succeeded') {
      return (
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
          <div className="py-6 text-center text-slate-400">
            <p className="text-sm">Run a simulation to see constraint evaluation results.</p>
          </div>
        </div>
      );
    }

    // Mock: Extract hard failures from recommendation or create mock data
    const hasHardFailure = lastOutcome.proposed_price < 100000; // Restrictive offer logic
    const hardFailures = hasHardFailure
      ? ['Liability Coverage must be at least 1.5x annual contract value (current: 0.8x)']
      : [];

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-white">
            {(props.title as string) || 'Hard Constraint Evaluation'}
          </h2>
          <span
            className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${
              hasHardFailure
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
            }`}
          >
            {hasHardFailure ? 'HARD FAILURE' : 'PASSES'}
          </span>
        </div>

        {hasHardFailure ? (
          <div className="space-y-3">
            <div className="p-4 bg-rose-950/30 border border-rose-800/40 rounded-lg space-y-3">
              <div className="flex items-start space-x-3">
                <span className="text-rose-400 text-xl flex-shrink-0">✗</span>
                <div className="space-y-1 flex-1">
                  <p className="font-semibold text-rose-300">Offer violates hard constraint</p>
                  <p className="text-sm text-rose-200/80">
                    This offer cannot be approved without addressing the constraint violations below.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Constraint Violations
              </span>
              {hardFailures.map((failure, idx) => (
                <div key={idx} className="p-3 bg-slate-950/60 border border-slate-800 rounded space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-rose-400 text-sm">▸</span>
                    <span className="text-sm font-medium text-slate-200">{failure}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-3 bg-slate-950/40 border border-slate-800/60 rounded text-xs text-slate-400">
              <p>
                <strong>Approval Status:</strong>{' '}
                <span className="text-rose-400 font-semibold">BLOCKED</span>
              </p>
              <p className="mt-1">Hard constraints must be satisfied before approval is possible.</p>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-emerald-950/30 border border-emerald-800/40 rounded-lg flex items-start space-x-3">
            <span className="text-emerald-400 text-xl flex-shrink-0">✓</span>
            <div className="space-y-1">
              <p className="font-semibold text-emerald-300">All constraints satisfied</p>
              <p className="text-sm text-emerald-200/80">This offer meets all hard requirements.</p>
            </div>
          </div>
        )}
      </div>
    );
  }

  // 6. Next Best Move Node (Phase 3: US1)
  if (type === 'next-best-move') {
    if (!lastOutcome || simulationStatus !== 'succeeded') {
      return (
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm">
          <div className="py-6 text-center text-slate-400">
            <p className="text-sm">Run a simulation to see negotiation recommendations.</p>
          </div>
        </div>
      );
    }

    // Mock trade-off suggestions based on price
    const tradeMoves =
      lastOutcome.proposed_price < 100000
        ? [
            'Increase seller offer to $105,000 to reach liability constraint target',
            'Request seller to accept shared liability structure (co-insurance)',
            'Propose phased delivery with reduced liability exposure in Phase 1',
          ]
        : ['Current price is competitive. Consider accepting to close quickly.'];

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-white">
            {(props.title as string) || 'Next Best Negotiation Move'}
          </h2>
          <span className="text-xs text-slate-400">Strategic guidance</span>
        </div>

        <div className="space-y-3">
          {tradeMoves.map((move, idx) => (
            <div key={idx} className="p-3 bg-sky-950/20 border border-sky-800/30 rounded-lg space-y-1.5">
              <div className="flex items-start space-x-2.5">
                <span className="text-sky-400 font-bold text-sm">{idx + 1}.</span>
                <p className="text-sm text-slate-200 leading-relaxed">{move}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="p-3 bg-slate-950/40 border border-slate-800/60 rounded text-xs text-slate-400 space-y-1">
          <p>
            <strong>Score:</strong>{' '}
            <span className="font-mono font-semibold text-sky-400">
              {Math.round(lastOutcome.acceptance_probability * 100)}%
            </span>{' '}
            acceptance probability
          </p>
          <p>
            <strong>Rationale:</strong> {lastOutcome.recommendation}
          </p>
        </div>
      </div>
    );
  }

  // 7. Proposal Approval Node (Phase 4: US2)
  if (type === 'proposal-approval') {
    const proposalStatus = approvalStatus || (props.status as string) || 'pending';
    const proposedPrice = typeof props.proposed_price === 'number' ? props.proposed_price : 105000;
    const canApprove = proposalStatus === 'pending';

    const handleApprove = () => {
      if (onAction) {
        onAction('approveProposal', { proposal_id: props.proposal_id });
      }
    };

    const handleReject = () => {
      if (onAction) {
        onAction('rejectProposal', { proposal_id: props.proposal_id });
      }
    };

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-white">
            {(props.title as string) || 'Proposal Approval'}
          </h2>
          <span
            className={`text-xs px-2.5 py-0.5 rounded-full font-medium border ${
              proposalStatus === 'approved'
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : proposalStatus === 'rejected'
                ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                : 'bg-sky-500/10 text-sky-400 border-sky-500/20'
            }`}
          >
            {proposalStatus.toUpperCase()}
          </span>
        </div>

        <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-lg space-y-2">
          <p className="text-sm text-slate-400">
            <strong>Proposed Price:</strong>
          </p>
          <p className="text-2xl font-bold text-sky-400">
            ${proposedPrice.toLocaleString()}
          </p>
          <p className="text-xs text-slate-500">
            Counterparty: {(props.counterparty as string) || 'Apex Global Enterprise'}
          </p>
        </div>

        {canApprove && (
          <div className="flex space-x-3 pt-2">
            <button
              onClick={handleApprove}
              className="flex-1 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold text-sm transition-all"
            >
              ✓ Approve
            </button>
            <button
              onClick={handleReject}
              className="flex-1 py-2.5 px-4 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-semibold text-sm transition-all"
            >
              ✗ Reject
            </button>
          </div>
        )}

        {proposalStatus === 'approved' && (
          <div className="p-3 bg-emerald-950/30 border border-emerald-800/40 rounded-lg">
            <p className="text-sm text-emerald-300">✓ Proposal approved. Deal progressing to closure.</p>
          </div>
        )}

        {proposalStatus === 'rejected' && (
          <div className="p-3 bg-rose-950/30 border border-rose-800/40 rounded-lg">
            <p className="text-sm text-rose-300">✗ Proposal rejected. New negotiations required.</p>
          </div>
        )}
      </div>
    );
  }

  // 8. Term Table Node (Phase 5: US3, T026)
  if (type === 'term-table' || type === 'decision-term-table') {
    const isRestrictive =
      (lastOutcome && lastOutcome.proposed_price < 100000) ||
      comparison.selected_id === 'alt_restrictive';

    const termsData = [
      {
        term: 'Base Contract Price',
        current: isRestrictive ? '$95,000' : '$120,000',
        target: '$105,000',
        status: isRestrictive ? 'Below Target (-$10k)' : 'Under Negotiation',
        statusColor: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
      },
      {
        term: 'Liability Cap',
        current: isRestrictive ? '0.8x Value' : '2.0x Value',
        target: '1.5x Value (hard limit: 1.5x)',
        status: isRestrictive ? 'HARD FAILURE (< 1.5x)' : 'Compliant (>= 1.5x)',
        statusColor: isRestrictive
          ? 'text-rose-400 bg-rose-500/10 border-rose-500/30 font-bold'
          : 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      },
      {
        term: 'Payment Schedule',
        current: 'Net 30 Days',
        target: 'Net 30 Days',
        status: 'Match (Advisory Pass)',
        statusColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      },
      {
        term: 'Delivery Timeline',
        current: '90 Calendar Days',
        target: '90 Calendar Days',
        status: 'Match (Advisory Pass)',
        statusColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      },
    ];

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-white">{(props.title as string) || 'Contract Decision Terms Table'}</h2>
            <p className="text-xs text-slate-400">Material terms evaluated by Decision Twin</p>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
            Contract #1042-B
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Term</th>
                <th className="py-3 px-4">Current</th>
                <th className="py-3 px-4">Target</th>
                <th className="py-3 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {termsData.map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 font-semibold text-slate-200">{row.term}</td>
                  <td className="py-3 px-4 font-mono text-slate-300">{row.current}</td>
                  <td className="py-3 px-4 font-mono text-slate-400">{row.target}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2.5 py-1 rounded-full text-[11px] border ${row.statusColor}`}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  // 9. Deal Comparison Node (Phase 5: US3, T027)
  if (type === 'deal-comparison' || type === 'decision-comparison') {
    const alts = alternatives && alternatives.length > 0 ? alternatives : INITIAL_ALTERNATIVES;
    const selectedAltId = comparison.selected_id || 'alt_counter_a';

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-white">{(props.title as string) || 'Compare Decision Alternatives'}</h2>
            <p className="text-xs text-slate-400">Current Deal vs. Strategic Counteroffers</p>
          </div>
          <span className="text-xs text-sky-400 font-medium">3-Way Comparison Matrix</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {alts.map((alt) => {
            const isSelected = selectedAltId === alt.id;
            const evalResult = alt.evaluation;
            const isFeasible = evalResult?.is_feasible ?? true;
            const score = evalResult?.score ?? 50;

            return (
              <div
                key={alt.id}
                onClick={() => selectAlternative(alt.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer space-y-3 flex flex-col justify-between ${
                  isSelected
                    ? 'bg-sky-950/40 border-sky-400 ring-1 ring-sky-400/80 shadow-lg shadow-sky-950/50'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{alt.label}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        isFeasible
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                      }`}
                    >
                      {isFeasible ? 'FEASIBLE' : 'HARD FAILURE'}
                    </span>
                  </div>

                  <div className="flex items-baseline space-x-2">
                    <span className="text-2xl font-bold font-mono text-white">${alt.price.toLocaleString()}</span>
                    <span className="text-xs text-slate-400">price</span>
                  </div>

                  <div className="space-y-1 text-xs text-slate-300">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Acceptance Score:</span>
                      <span className="font-mono font-semibold text-sky-400">{score}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Liability Cap:</span>
                      <span className="font-mono">{alt.terms?.liability ? `${String(alt.terms.liability)}x` : 'N/A'}</span>
                    </div>
                  </div>

                  {evalResult?.hard_failures && evalResult.hard_failures.length > 0 && (
                    <div className="p-2.5 rounded bg-rose-950/50 border border-rose-800/40 text-[11px] text-rose-200">
                      <span className="font-semibold block mb-0.5">⚠️ Hard Constraint Violation:</span>
                      {evalResult.hard_failures[0]}
                    </div>
                  )}

                  {evalResult?.trade_offs && evalResult.trade_offs.length > 0 && isFeasible && (
                    <div className="p-2.5 rounded bg-sky-950/30 border border-sky-800/30 text-[11px] text-sky-200">
                      <span className="font-semibold block mb-0.5">💡 Trade-Off Move:</span>
                      {evalResult.trade_offs[0]}
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">Source: {alt.source}</span>
                  {alt.id === 'alt_counter_a' && (
                    <span className="text-sky-400 font-semibold">★ Next Best Move</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // 10. Wire-Agent Schema Mutation Panel (Phase 6: US4, T035)
  if (type === 'schema-mutation-panel') {
    const isPreviewed = stagedMutation.status === 'previewed';
    const isPublished = stagedMutation.status === 'published';
    const currentVersion = isPublished ? 3 : 2;

    const handlePreview = () => {
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
        request_id: 'wire-mut-preview',
        stage: 'webmcp',
        status: 'completed',
        message: 'Wire-Agent generated visual-only mutation preview (mut-wire-01). Invariance verified.',
      });
    };

    const handlePublish = () => {
      setStagedMutation({
        mutation_id: 'mut-wire-01',
        base_version: 2,
        status: 'published',
      });
      addActivityEvent({
        request_id: 'wire-mut-publish',
        stage: 'deal_room',
        status: 'completed',
        message: 'Published UI schema version 3. Decision Twin results 100% invariant.',
      });
    };

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-white">Wire-Agent UX Evolution & Safety Guard</h2>
            <p className="text-xs text-slate-400">Presentation-only schema mutation workflow</p>
          </div>
          <span className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-sky-500/10 text-sky-400 border border-sky-500/30">
            UI Schema v{currentVersion}
          </span>
        </div>

        <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-lg text-xs space-y-2">
          <div className="flex items-center space-x-2 text-emerald-400 font-semibold">
            <span>🛡️</span>
            <span>Safety Immutability Guard: Active</span>
          </div>
          <p className="text-slate-400 leading-relaxed">
            Wire-Agent can safely refine UI layout and Tailwind styling via WebMCP. All patches targeting business terms, constraints, or Decision Twin logic are blocked.
          </p>
        </div>

        {isPreviewed && (
          <div className="p-3.5 bg-amber-950/30 border border-amber-500/40 rounded-lg text-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-amber-300">Staged Preview: `mut-wire-01`</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">
                PREVIEWED
              </span>
            </div>
            <p className="text-slate-300">
              Presentation patch: Added high-contrast danger outline for hard liability failure banner.
            </p>
            <div className="text-[11px] text-slate-400">
              Base Version: <strong>2</strong> • Proposed Target: <strong>v3</strong> • Decision Invariance: <span className="text-emerald-400 font-semibold">VERIFIED</span>
            </div>
          </div>
        )}

        {isPublished && (
          <div className="p-3.5 bg-emerald-950/30 border border-emerald-500/40 rounded-lg text-xs space-y-1">
            <div className="flex items-center space-x-2 text-emerald-300 font-semibold">
              <span>✓</span>
              <span>Successfully Published Version 3!</span>
            </div>
            <p className="text-slate-300">
              New layout is active live. Decision Twin calculations for contract #1042-B remain 100% invariant.
            </p>
          </div>
        )}

        <div className="flex space-x-3 pt-2">
          {!isPreviewed && !isPublished && (
            <button
              id="wire-agent-preview-btn"
              onClick={handlePreview}
              className="flex-1 py-2.5 px-4 bg-sky-600 hover:bg-sky-500 text-white rounded-lg font-semibold text-xs transition-all shadow-md"
            >
              Preview Wire-Agent Mutation
            </button>
          )}

          {isPreviewed && (
            <button
              id="wire-agent-publish-btn"
              onClick={handlePublish}
              className="flex-1 py-2.5 px-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-semibold text-xs transition-all shadow-md"
            >
              Publish Mutation to v3
            </button>
          )}

          {(isPreviewed || isPublished) && (
            <button
              onClick={() => setStagedMutation({ base_version: 2, status: 'none' })}
              className="py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-semibold text-xs transition-all"
            >
              Reset Mutation
            </button>
          )}
        </div>
      </div>
    );
  }

  // 11. React Flow DAG Node (Phase 7: US7, T038, T039)
  if (type === 'agent-workflow-dag' || type === 'workflow-diagram') {
    const selectedNode = dagNodes.find((n) => n.id === selectedDAGNodeId) || dagNodes[0];

    const flowNodes: FlowNode[] = dagNodes.map((n, i) => {
      const isSelected = n.id === selectedDAGNodeId;
      const borderColor =
        n.status === 'completed'
          ? '#10b981'
          : n.status === 'active'
          ? '#38bdf8'
          : n.status === 'failed'
          ? '#f43f5e'
          : '#475569';

      return {
        id: n.id,
        position: { x: i * 165 + 15, y: 35 },
        data: { label: n.label },
        style: {
          background: isSelected ? '#0369a1' : '#0f172a',
          color: '#f8fafc',
          border: `2px solid ${borderColor}`,
          borderRadius: '8px',
          padding: '8px 10px',
          fontSize: '11px',
          fontWeight: '600',
          width: 140,
          textAlign: 'center',
          cursor: 'pointer',
          boxShadow: isSelected
            ? '0 0 15px rgba(56, 189, 248, 0.5)'
            : n.status === 'active'
            ? '0 0 12px rgba(56, 189, 248, 0.3)'
            : 'none',
        },
      };
    });

    const flowEdges: FlowEdge[] = dagEdges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      animated: true,
      markerEnd: { type: MarkerType.ArrowClosed, color: '#38bdf8' },
      style: { stroke: '#0284c7', strokeWidth: 2 },
    }));

    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-xl backdrop-blur-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold text-white">
              {(props.title as string) || 'WebMCP Agent Execution DAG'}
            </h2>
            <p className="text-xs text-slate-400">
              Interactive React Flow execution graph • Click a node to inspect payload
            </p>
          </div>
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
            @xyflow/react
          </span>
        </div>

        {/* Interactive React Flow Canvas */}
        <div className="h-40 w-full rounded-lg border border-slate-800 bg-slate-950 overflow-hidden relative">
          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            onNodeClick={(_: React.MouseEvent, n: FlowNode) => selectDAGNode(n.id)}
            fitView
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#1e293b" gap={16} />
            <Controls showInteractive={false} className="bg-slate-800 border-slate-700 text-white" />
          </ReactFlow>
        </div>

        {/* Selected Node Inspector Drawer */}
        {selectedNode && (
          <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-sm text-white">{selectedNode.label}</span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase font-bold border ${
                  selectedNode.status === 'completed'
                    ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                    : selectedNode.status === 'active'
                    ? 'bg-sky-500/20 text-sky-400 border-sky-500/40'
                    : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}
              >
                {selectedNode.status}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1">
              <div>
                <span className="text-slate-400">Tool / Channel:</span>{' '}
                <code className="text-sky-300 font-mono text-[11px]">
                  {String(selectedNode.details?.tool_name || 'N/A')}
                </code>
              </div>
              <div>
                <span className="text-slate-400">Request ID:</span>{' '}
                <code className="text-slate-300 font-mono text-[11px]">
                  {String(selectedNode.details?.request_id || 'N/A')}
                </code>
              </div>
            </div>

            <p className="text-xs text-slate-300 pt-1 border-t border-slate-800/80 leading-relaxed">
              {String(selectedNode.details?.summary || selectedNode.details?.description || 'Active WebMCP call')}
            </p>
          </div>
        )}
      </div>
    );
  }

  // 12. Constraint Kitchen Node (Phase 3: US1, T009)
  if (type === 'constraint-kitchen') {
    return <ConstraintKitchenCard title={props.title as string} onAction={onAction} />;
  }

  // 13. Standard HTML Elements
  switch (type) {
    case 'div':
    case 'header':
    case 'main':
    case 'footer':
    case 'section':
    case 'article':
    case 'nav':
    case 'h1':
    case 'h2':
    case 'h3':
    case 'h4':
    case 'p':
    case 'span':
    case 'ul':
    case 'ol':
    case 'li':
      return React.createElement(
        type,
        { className, ...props },
        (props.text as string) || renderedChildren
      );

    case 'button':
      return (
        <button className={className} onClick={handleButtonClick} {...props}>
          {(props.text as string) || renderedChildren}
        </button>
      );

    default:
      console.warn(`Unsupported schema type: ${type}`);
      return (
        <div className={`border border-amber-500/40 p-2 text-xs text-amber-300 ${className}`}>
          {type}
          {renderedChildren}
        </div>
      );
  }
};
