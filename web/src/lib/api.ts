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
};

export const ITEM_TITLES: Record<string, string> = {
  "1": "Business",
  "1A": "Risk Factors",
  "7": "MD&A",
};

// ---- Agent (/v1/query, Server-Sent Events) ---------------------------------------------

export interface TraceEvent {
  step: "plan" | "search" | "sql" | "write" | "revise" | "verify" | string;
  detail: Record<string, unknown>;
  ms: number;
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
}

export type AgentEvent =
  | { kind: "step"; data: TraceEvent }
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
