// Typed client for the provenance API. Shapes mirror the Pydantic models in src/provenance.

export type Mode = "hybrid" | "dense" | "bm25";

export interface Me {
  name: string;
  display_name: string;
  groups: string[];
  visible: { documents: number; chunks: number; financial_facts: number; tickers: string[] };
}

export interface Hit {
  chunk_id: number;
  document_id: number;
  ticker: string;
  company: string;
  fiscal_year: number;
  item: string;
  section_title: string;
  text: string;
  context: string;
  char_start: number;
  char_end: number;
  url: string;
  dense_rank: number | null;
  bm25_rank: number | null;
  fused_score: number;
  rerank_score: number | null;
}

export interface SearchResult {
  query: string;
  search_query: string;
  filters: { tickers: string[]; fiscal_years: number[]; items: string[] };
  filters_relaxed: boolean;
  rewrite: "off" | "ok" | "failed";
  mode: Mode;
  reranked: boolean;
  hits: Hit[];
  timings_ms: Record<string, number>;
}

export interface Source {
  chunk_id: number;
  ticker: string;
  company: string;
  fiscal_year: number;
  item: string;
  section_title: string;
  document_title: string;
  url: string;
  accession: string;
  text: string;
  highlight_start: number;
  highlight_end: number;
  window_start: number;
  section_length: number;
}

export interface SearchParams {
  query: string;
  k: number;
  mode: Mode;
  rerank: boolean;
  rewrite: boolean;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly requestId: string | null,
  ) {
    super(message);
  }
}

async function request<T>(path: string, apiKey: string | null, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (apiKey) headers.set("X-API-Key", apiKey);
  if (init.body) headers.set("Content-Type", "application/json");
  let response: Response;
  try {
    response = await fetch(path, { ...init, headers });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ApiError(0, "network", "Can't reach the API. Is `python -m provenance.api` running?", null);
  }
  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const err = (body as { error?: { code?: string; message?: string; request_id?: string } } | null)?.error;
    throw new ApiError(
      response.status,
      err?.code ?? "http_error",
      err?.message ?? `Request failed (${response.status})`,
      err?.request_id ?? response.headers.get("X-Request-ID"),
    );
  }
  return body as T;
}

export const api = {
  me: (apiKey: string, signal?: AbortSignal) => request<Me>("/v1/me", apiKey, { signal }),
  search: (apiKey: string, params: SearchParams, signal?: AbortSignal) =>
    request<SearchResult>("/v1/search", apiKey, { method: "POST", body: JSON.stringify(params), signal }),
  source: (apiKey: string, chunkId: number, signal?: AbortSignal) =>
    request<Source>(`/v1/sources/${chunkId}?window=1500`, apiKey, { signal }),
  ready: (signal?: AbortSignal) =>
    request<{ status: string; checks: Record<string, string> }>("/health/ready", null, { signal }),
  stats: (apiKey: string, signal?: AbortSignal) => request<Stats>("/v1/stats", apiKey, { signal }),
  audit: (apiKey: string, signal?: AbortSignal) => request<AuditReport>("/v1/audit?limit=300", apiKey, { signal }),
};

// ---- Dashboard (/v1/stats) and audit (/v1/audit) ----------------------------------------

export interface MetricsSnapshot {
  started_at: number;
  queries: Record<string, Record<string, number>>;
  cache_lookups: Record<string, number>;
  escalations: Record<string, number>;
  tokens: Record<string, Record<string, number>>;
  cost_usd: Record<string, number>;
  /** [upper bound in seconds, cumulative count] */
  latency_buckets: [number, number][];
  latency_sum_s: number;
  shed: Record<string, number>;
  running: number;
  waiting: number;
}

export interface Stats {
  metrics: MetricsSnapshot | null;
  budget: { spent: number; limit: number } | null;
  breakers_open: string[];
}

export interface AuditEntry {
  at: string;
  request_id: string;
  principal: string;
  groups: string[];
  tool: string;
  input_preview: string;
  outcome: "ok" | "denied" | "error" | string;
  detail: Record<string, unknown>;
}

export interface AuditReport {
  entries: AuditEntry[];
  daily: { day: string; tool: string; outcome: string; calls: number }[];
  scanned: number;
  flagged: number;
  quarantined: {
    chunk_id: number;
    ticker: string;
    company: string;
    fiscal_year: number | null;
    item: string;
    reasons: string[];
    score: number | null;
    preview: string;
  }[];
}

export const ITEM_TITLES: Record<string, string> = {
  "1": "Business",
  "1A": "Risk Factors",
  "7": "MD&A",
};

// ---- Agent (/v1/query, Server-Sent Events) ---------------------------------------------

export interface TraceEvent {
  step:
    | "route" | "cache" | "plan" | "search" | "sql" | "write" | "revise" | "verify" | "score"
    | "escalate" | "abstain" | string;
  detail: Record<string, unknown>;
  ms: number;
}

/** One model call made while answering, attributed to the step that made it. */
export interface LLMCall {
  node: string;
  role: string;
  provider: string;
  model: string;
  input_tokens: number;
  cached_input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  cost_usd: number;
}

/** What the controller decided around the agent run, and what it cost (M8). */
export interface ControlReport {
  tier: "small" | "large";
  tier_reasons: string[];
  escalated: string | null;
  abstained: string | null;
  cache: { hit: boolean; kind: string; similarity: number | null; matched_question: string | null; ms: number } | null;
  usage: {
    input_tokens: number;
    output_tokens: number;
    cached_input_tokens: number;
    cost_usd: number;
    calls: LLMCall[];
  };
  budget_left: number | null;
}

export interface Evidence {
  id: string;
  kind: "passage" | "fact";
  label: string;
  text: string;
  chunk_id: number | null;
}

export interface Verification {
  ok: boolean;
  unknown_citations: string[];
  unsupported_numbers: string[];
  uncited: boolean;
}

export interface SqlResult {
  question: string;
  sql: string;
  columns: string[];
  rows: unknown[][];
  error: string | null;
  attempts: number;
}

export interface AgentResult {
  question: string;
  answer: string;
  declined: boolean;
  evidence: Evidence[];
  passages: Hit[];
  sql: SqlResult | null;
  plan: { needs_text: boolean; needs_numbers: boolean; sql_question: string };
  verification: Verification | null;
  revisions: number;
  steps: number;
  trace: TraceEvent[];
  /** Calibrated per-claim confidence; null until a calibrator has been fit. */
  claims: { text: string; cited: string[]; confidence: number | null }[];
  confidence: number | null;
  tier: "small" | "large";
  control: ControlReport | null;
}

/** A fragment of the answer as the model writes it; `reset` starts the text over. */
export interface AnswerDelta {
  step: "write" | "revise" | string;
  text: string;
  reset: boolean;
}

export type AgentEvent =
  | { kind: "step"; data: TraceEvent }
  | { kind: "delta"; data: AnswerDelta }
  | { kind: "result"; data: AgentResult }
  | { kind: "error"; data: { code: string; message: string } };

/** POSTs a question and calls `onEvent` for each SSE event as it arrives. EventSource only
 *  does GET, so the stream is read with fetch. */
export async function streamQuery(
  apiKey: string,
  question: string,
  onEvent: (event: AgentEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  let response: Response;
  try {
    response = await fetch("/v1/query", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
      body: JSON.stringify({ question }),
      signal,
    });
  } catch (e) {
    if (e instanceof DOMException && e.name === "AbortError") throw e;
    throw new ApiError(0, "network", "Can't reach the API. Is `python -m provenance.api` running?", null);
  }
  if (!response.ok || !response.body) {
    const body = (await response.json().catch(() => null)) as { error?: { code: string; message: string } } | null;
    throw new ApiError(
      response.status,
      body?.error?.code ?? "http_error",
      body?.error?.message ?? `Request failed (${response.status})`,
      response.headers.get("X-Request-ID"),
    );
  }
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const block = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const event = /^event: (.*)$/m.exec(block)?.[1];
      const data = /^data: (.*)$/m.exec(block)?.[1];
      if (event && data) onEvent({ kind: event, data: JSON.parse(data) } as AgentEvent);
    }
  }
}
