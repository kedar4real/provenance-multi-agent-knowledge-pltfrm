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
