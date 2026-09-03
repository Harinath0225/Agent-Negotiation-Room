import { FormEvent, useCallback, useEffect, useState } from 'react';

interface SearchCriteria {
  query: string;
  status: string;
  min_value: string;
  max_value: string;
}

interface ContractRecord {
  id: string;
  contract_id: string;
  title: string;
  counterparty: string;
  status: string;
  annual_value: number;
  liability_cap: string;
  updated_at: string;
}

const initialCriteria: SearchCriteria = { query: '', status: '', min_value: '', max_value: '' };

export default function ContractSearchPage() {
  const [criteria, setCriteria] = useState<SearchCriteria>(initialCriteria);
  const [records, setRecords] = useState<ContractRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastAgentAction, setLastAgentAction] = useState<string | null>(null);

  const runSearch = useCallback(async (nextCriteria: SearchCriteria) => {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    Object.entries(nextCriteria).forEach(([key, value]) => {
      if (value.trim()) params.set(key, value.trim());
    });

    try {
      const response = await fetch(`/api/contracts?${params.toString()}`);
      if (!response.ok) throw new Error(`Search failed: ${response.statusText}`);
      const result: { records: ContractRecord[] } = await response.json();
      setRecords(result.records);
    } catch (searchError) {
      setError(searchError instanceof Error ? searchError.message : 'Search failed.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load: Fetch and display all contracts automatically
  useEffect(() => {
    runSearch(initialCriteria);
  }, [runSearch]);

  // Register in-browser WebMCP tool on document.modelContext
  useEffect(() => {
    const modelContext = (document as unknown as { modelContext?: Record<string, unknown> }).modelContext || {
      tools: {} as Record<string, unknown>,
      registerTool(toolDef: { name: string; description: string; inputSchema: unknown; execute: (args: Record<string, unknown>) => Promise<unknown> }) {
        (this.tools as Record<string, unknown>)[toolDef.name] = toolDef;
      },
    };
    (document as unknown as { modelContext: typeof modelContext }).modelContext = modelContext;

    const reg = modelContext.registerTool as (t: Record<string, unknown>) => void;

    reg.call(modelContext, {
      name: 'search_previous_deals',
      description: 'Search contract database using query, status, min_value, or max_value criteria.',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'Contract ID, title, or counterparty' },
          status: { type: 'string', enum: ['Under Negotiation', 'Approved', 'Closed', 'Rejected'] },
          min_value: { type: 'number', minimum: 0 },
          max_value: { type: 'number', minimum: 0 },
        },
      },
      execute: async (input: Record<string, unknown>) => {
        const nextCrit: SearchCriteria = {
          query: input.query !== undefined ? String(input.query) : '',
          status: input.status !== undefined ? String(input.status) : '',
          min_value: input.min_value !== undefined ? String(input.min_value) : '',
          max_value: input.max_value !== undefined ? String(input.max_value) : '',
        };
        setCriteria(nextCrit);
        setLastAgentAction(`search_previous_deals(${JSON.stringify(input)})`);
        await runSearch(nextCrit);
        return { status: 'success', criteria: nextCrit };
      },
    });

    const fillCriteria = (event: Event) => {
      const detail = (event as CustomEvent<Partial<SearchCriteria>>).detail;
      if (!detail) return;
      setCriteria((current) => ({ ...current, ...Object.fromEntries(Object.entries(detail).map(([key, value]) => [key, String(value)])) }));
    };
    const showResults = (event: Event) => {
      const detail = (event as CustomEvent<{ records?: ContractRecord[] }>).detail;
      if (detail?.records) setRecords(detail.records);
    };
    document.addEventListener('deal-room:search-criteria', fillCriteria);
    document.addEventListener('deal-room:search-results', showResults);
    return () => {
      document.removeEventListener('deal-room:search-criteria', fillCriteria);
      document.removeEventListener('deal-room:search-results', showResults);
    };
  }, [runSearch]);

  const updateCriteria = (field: keyof SearchCriteria, value: string) => setCriteria((current) => ({ ...current, [field]: value }));
  
  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    runSearch(criteria);
  };

  const triggerAgentSearch = async (agentInput: Record<string, unknown>) => {
    setLastAgentAction(`Agent executed: search_previous_deals(${JSON.stringify(agentInput)})`);
    const nextCrit: SearchCriteria = {
      query: agentInput.query !== undefined ? String(agentInput.query) : '',
      status: agentInput.status !== undefined ? String(agentInput.status) : '',
      min_value: agentInput.min_value !== undefined ? String(agentInput.min_value) : '',
      max_value: agentInput.max_value !== undefined ? String(agentInput.max_value) : '',
    };
    setCriteria(nextCrit);
    await runSearch(nextCrit);
  };

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-8 text-slate-100 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex items-start justify-between border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center space-x-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-sky-400">Nexus Deal Room</p>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                WebMCP In-Browser Enabled
              </span>
            </div>
            <h1 className="mt-1 text-2xl font-bold text-white">Previous Deals & Contracts System of Record</h1>
            <p className="text-xs text-slate-400 mt-1">Autonomous agents can search and inspect deal history via `document.modelContext`</p>
          </div>
          <div className="flex items-center space-x-2">
            <a href="/" className="rounded-lg border border-slate-700 px-3.5 py-2 text-sm font-medium text-slate-200 hover:border-sky-500 hover:text-white transition shadow-sm">
              ← Active Deal Room
            </a>
            <a href="/agent-qa" className="rounded-lg border border-slate-700 bg-slate-900 px-3.5 py-2 text-sm font-medium text-sky-400 hover:border-sky-500 hover:text-white transition shadow-sm flex items-center space-x-1.5">
              <span>🧪</span>
              <span>Agent QA</span>
            </a>
          </div>
        </header>

        {/* In-Browser WebMCP Demonstration Controller */}
        <section className="rounded-xl border border-slate-800 bg-slate-900/90 p-4 space-y-3 shadow-lg">
          <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs font-semibold text-white tracking-wide uppercase">
                WebMCP Agent In-Browser Demonstration
              </span>
              <code className="text-[11px] font-mono text-sky-400 bg-sky-950/60 px-2 py-0.5 rounded border border-sky-800/40">
                document.modelContext.tools.search_previous_deals
              </code>
            </div>
            <span className="text-[11px] text-slate-400">
              DevTools & Agent Execution Ready
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-slate-400 font-medium">Trigger Agent Searches:</span>
            <button
              type="button"
              onClick={() => triggerAgentSearch({ query: 'Apex' })}
              className="px-3 py-1.5 bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white rounded-lg border border-slate-700 transition flex items-center space-x-1.5"
            >
              <span>🤖</span>
              <span>Search "Apex"</span>
            </button>
            <button
              type="button"
              onClick={() => triggerAgentSearch({ status: 'Under Negotiation' })}
              className="px-3 py-1.5 bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white rounded-lg border border-slate-700 transition flex items-center space-x-1.5"
            >
              <span>🤖</span>
              <span>Filter "Under Negotiation"</span>
            </button>
            <button
              type="button"
              onClick={() => triggerAgentSearch({ status: 'Approved' })}
              className="px-3 py-1.5 bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white rounded-lg border border-slate-700 transition flex items-center space-x-1.5"
            >
              <span>🤖</span>
              <span>Filter "Approved"</span>
            </button>
            <button
              type="button"
              onClick={() => triggerAgentSearch({ min_value: 200000 })}
              className="px-3 py-1.5 bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white rounded-lg border border-slate-700 transition flex items-center space-x-1.5"
            >
              <span>🤖</span>
              <span>High Value (&gt; $200k)</span>
            </button>
            <button
              type="button"
              onClick={() => triggerAgentSearch({})}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
            >
              🔄 Reset / View All
            </button>
          </div>

          {lastAgentAction && (
            <div className="p-2 bg-slate-950 rounded border border-slate-800 flex items-center justify-between text-[11px] font-mono">
              <span className="text-emerald-400">⚡ {lastAgentAction}</span>
              <span className="text-slate-500">Updated via WebMCP Event</span>
            </div>
          )}
        </section>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 rounded-lg border border-slate-800 bg-slate-900 p-5 sm:grid-cols-2 lg:grid-cols-5">
          <label className="space-y-1.5 lg:col-span-2">
            <span className="text-xs font-medium text-slate-300">Contract, title, or counterparty</span>
            <input value={criteria.query} onChange={(event) => updateCriteria('query', event.target.value)} placeholder="e.g. Apex or 1042-B" className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-sky-500 focus:outline-none" />
          </label>
          <label className="space-y-1.5">
            <span className="text-xs font-medium text-slate-300">Status</span>
            <select value={criteria.status} onChange={(event) => updateCriteria('status', event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white focus:border-sky-500 focus:outline-none">
              <option value="">All statuses</option>
              <option>Under Negotiation</option>
              <option>Approved</option>
              <option>Closed</option>
              <option>Rejected</option>
            </select>
          </label>
          <label className="space-y-1.5">
            <span className="text-xs font-medium text-slate-300">Minimum value</span>
            <input type="number" min="0" value={criteria.min_value} onChange={(event) => updateCriteria('min_value', event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white focus:border-sky-500 focus:outline-none" />
          </label>
          <label className="space-y-1.5">
            <span className="text-xs font-medium text-slate-300">Maximum value</span>
            <input type="number" min="0" value={criteria.max_value} onChange={(event) => updateCriteria('max_value', event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white focus:border-sky-500 focus:outline-none" />
          </label>
          <button type="submit" className="rounded-lg bg-sky-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-sky-400 sm:col-span-2 lg:col-span-5">{loading ? 'Searching...' : 'Search contracts'}</button>
        </form>

        {error && <p className="rounded-lg border border-rose-900 bg-rose-950/30 p-3 text-sm text-rose-300">{error}</p>}
        <section className="overflow-hidden rounded-lg border border-slate-800 bg-slate-900">
          <div className="border-b border-slate-800 px-5 py-3 text-sm text-slate-400 flex items-center justify-between">
            <span>{records.length} matching contract{records.length === 1 ? '' : 's'}</span>
            <span className="text-xs font-mono text-slate-500">System of Record: SQLite DB</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950 text-xs uppercase tracking-wider text-slate-400"><tr><th className="px-5 py-3">Contract</th><th className="px-5 py-3">Counterparty</th><th className="px-5 py-3">Status</th><th className="px-5 py-3">Annual value</th><th className="px-5 py-3">Liability</th></tr></thead>
              <tbody>{records.map((record) => <tr key={record.id} className="border-t border-slate-800"><td className="px-5 py-4"><p className="font-medium text-white">{record.title}</p><p className="mt-1 font-mono text-xs text-sky-400">#{record.contract_id}</p></td><td className="px-5 py-4 text-slate-300">{record.counterparty}</td><td className="px-5 py-4 text-slate-300"><span className={`px-2 py-0.5 rounded text-xs font-medium border ${record.status === 'Approved' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : record.status === 'Under Negotiation' ? 'bg-sky-500/10 text-sky-400 border-sky-500/30' : record.status === 'Rejected' ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' : 'bg-slate-800 text-slate-400 border-slate-700'}`}>{record.status}</span></td><td className="px-5 py-4 font-mono text-emerald-400">${record.annual_value.toLocaleString()}</td><td className="px-5 py-4 text-slate-300">{record.liability_cap}</td></tr>)}</tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}