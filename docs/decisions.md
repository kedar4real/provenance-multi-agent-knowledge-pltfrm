# Decisions

Every non-obvious choice: what was picked, what was rejected, and why. Newest entries at the bottom of each section.

## Scope and corpus

### SEC 10-K filings as the demo corpus
- **Picked:** ~30 companies × 2 fiscal years of 10-K filings from EDGAR. Narrative sections (Item 1 Business, 1A Risk Factors, 7 MD&A) feed retrieval; XBRL financial facts (companyfacts API) feed Postgres tables for the SQL worker.
- **Rejected:** arXiv papers (the SQL side would be thin metadata), NTSB reports, open-source docs (the most common RAG demo).
- **Why:** the supervisor only has a real reason to decompose questions if the corpus has both prose and structured numbers about the *same* entities. "Which company grew revenue fastest, and what risks did it flag?" needs the SQL worker *and* the retrieval worker. Filings are also public and free, so the golden set and results can be published.

### Framed as an enterprise platform, demonstrated on public data
- **Why:** a real company's internal knowledge base can't be published or evaluated in the open. The pipeline itself doesn't care about the corpus: documents + structured tables + per-document access groups.

## Models and providers

### $0 budget: free cloud tiers, routed by role
- **Picked:** Gemini (AI Studio free tier) for live serving, with Flash-Lite as the small tier escalating to Flash; ~~Mistral free tier for bulk eval work~~ (removed, see below); fallback chain Gemini → Groq → OpenRouter `:free` → Ollama Cloud.
- **Rejected:** local inference on the laptop GPU (the owner wants the laptop's compute left free); paid Claude API (budget).
- **Why:** free tiers differ by an order of magnitude on the axis that matters for each job. Bulk eval needs ~10M+ tokens per full run, and only Mistral's free tier has that volume. Live serving needs quality and latency, which suits Gemini. Gemini's low requests-per-minute cap means the circuit-breaker fallback path gets exercised for real, not only in tests.
- **Consequence:** the spec's Haiku→Sonnet escalation becomes Flash-Lite→Flash escalation. The routing and calibration logic is identical; only model names change.

### One thin in-house `LLMProvider` instead of calling SDKs from each agent
- **Why:** every model call has to pass one choke point for token/cost accounting, retries, circuit breakers, per-provider concurrency caps, and record/replay for reproducibility. Scattering SDK calls across agents would scatter all of those too.
- **SDK:** the `openai` SDK pointed at each provider's OpenAI-compatible base URL (Gemini, Groq, OpenRouter, Ollama all expose one). No OpenAI account is involved.

### LangGraph over the OpenAI Agents SDK
- **Why:** LangGraph makes control flow explicit: nodes, edges, typed state, a hard termination condition, and checkpoints that make runs replayable. In handoff-style frameworks the model itself decides who runs next. A system that must be auditable, budget-capped and replayable needs control flow in code, not in model output.

### OmniRoute is not used for measured runs
- **Why:** it auto-switches the model behind a request and can compress prompts. Both invalidate the verifier's calibration (calibrated against specific models) and make the controller's audit trail untrue. It is supported only as an optional OpenAI-compatible config entry with auto-fallback and compression off.

## Departures from the original spec

1. **Logprob confidence signal.** Claude's API doesn't expose token logprobs. The signal comes from a provider that does (Gemini, checked in M2), falling back to a tiny local model, else dropped. An ablation reports what it contributes.
2. **Real BM25.** Postgres `tsvector`/`ts_rank` is not BM25 (no IDF saturation or length normalization in the BM25 sense). The ParadeDB image provides pg_search (true BM25) alongside pgvector.
3. **Calibration without leakage.** The calibrator is fit with 5-fold cross-validation and ECE is reported out-of-fold with a bootstrap confidence interval. Fitting and reporting on the same 200 cases would overstate calibration. Labels are per-claim (~800 points) rather than per-answer (200), giving a usable reliability diagram.
4. **LLM provider layer built early (M2).** Generating the golden set already needs an LLM.
5. **CI gate split.** Retrieval metrics (Recall@k, MRR, NDCG) are deterministic, need no LLM, and gate every PR on all 200 cases. Faithfulness needs an LLM judge, so it runs on a 25-case subset with a tolerance band for judge noise.
6. **Semantic cache is permission-scoped.** The cache key includes a hash of the caller's access groups. Otherwise a cached answer built from restricted documents would leak to a user who can't see them.
7. **Jev provider.** Its API couldn't be verified, so `JevProvider` implements the verifier interface and raises `ProviderNotConfigured` rather than containing guessed request code.

## Added beyond the spec
- **Abstention + risk-coverage curve.** Calibrated confidence lets the system decline instead of guessing. The risk-coverage curve (accuracy vs. fraction answered), with and without calibration, shows directly why calibration matters.
- **Permission-aware retrieval via Postgres row-level security.** Access filtering happens in the database, so no agent, prompt injection or code path can retrieve rows the caller can't see.
- **`mcpgate`.** A standalone MCP security proxy: per-caller tool policy, tool-poisoning scan of tool descriptions, rug-pull detection by pinning `tools/list` hashes, output injection scanning, and audit.
- **Web UI with a trace viewer**, because routing and confidence decisions are the interesting part and they're invisible in a plain API.

## Infrastructure

### Docker Compose for Postgres/Redis/Jaeger
- **Why:** pg_search ships Linux builds only and Redis has no official Windows build. Compose also gives anyone cloning the repo the same databases with one command.
- **Rejected:** free cloud databases (Neon/Supabase + Upstash). No true BM25 extension, and reviewers would need their own accounts.

### Secret hygiene
- `.gitignore` covering `.env` was the first file written, before any key existed on disk. gitleaks runs as a pre-commit hook and in CI.

## LLM provider layer (M2a)

### One adapter class for every provider, Claude included
- **Picked:** a single `OpenAICompatProvider`. Gemini, Groq, OpenRouter and Ollama Cloud all expose the OpenAI chat-completions API, and so does Anthropic (`https://api.anthropic.com/v1/`), so Claude is a config entry rather than a separate backend.
- **Why:** one error-mapping path to test. Vendor differences (Gemini wraps errors in a list; Groq signals rate limits with a `retry-after` header, Gemini with a `RetryInfo` body) are normalized into three exceptions: `RateLimited(retry_after_s)`, `ProviderUnavailable` (retryable) and `ProviderRejected(status)` (not retryable).

### SDK retries disabled
- The `openai` SDK retries 429s silently by default. That would hide rate limits from the router and spend free-tier quota twice. `max_retries=0`; the router owns every retry and failover decision.

### Circuit breakers per provider+model, auth per provider
- **Why:** free-tier quotas and overloads are per model (Gemini's 429 names the model; 3.5-flash returned 503 while 3.1-flash-lite was healthy). A per-provider breaker let one overloaded model block every model from that vendor. A 401/403 means the key itself is bad, so that blocks the whole provider for an hour.

### Rejections fall back instead of failing the request
- A 400 is often model-specific (e.g. "logprobs not supported with this model"), so the router moves to the next choice without retrying the same one.

### Record/replay response cache
- Responses are stored under a SHA-256 of (role, full request). `read_write` makes eval re-runs free; `replay` never calls a model and raises `CacheMiss`, which proves a run is fully reproducible.

### Model picks by measured latency, not by version number
- Measured on this free-tier key: `gemini-3.5-flash-lite` took 42-90s per request (thinking disabled made no difference), `gemini-3.5-flash` and `gemini-3-flash-preview` returned 503, the 2.5 models returned 404, and Pro returned 429 (no free quota). `gemini-3.1-flash-lite` answered in ~1.5s and `gemini-3.6-flash` in ~2s, so those are the small and large tiers. Gemini's timeout is 30s so a stalled request fails over instead of hanging.

### `httpx2`, not `httpx`
- `openai` v3 is built on `httpx2`, a separate package. Injected HTTP clients and test transports must come from `httpx2`; an `httpx` client only worked by duck typing, and `respx` (which patches `httpx`) never intercepted real calls.

### Mistral removed
- **Decision (owner):** drop Mistral entirely. Its free-tier key returned 429 on the first request, and activating the free plan needs extra account setup.
- **Consequence:** bulk eval work (golden-set generation, judging, self-consistency) runs on Groq, spread across `gpt-oss-20b`, `qwen3.8-27b` and then Gemini Flash-Lite. Groq's limits are per model (1,000 requests/day and 8,000 tokens/minute each), so three models give ~3,000 requests/day, plus Gemini's quota. A full eval run (~4,000 calls) fits in about a day. The eval runner must therefore be chunked and resumable, and wait for quota rather than fail; the record/replay cache means no call is repeated.
- **Tradeoff:** judge and generator now share model families with the system under test (Gemini), which risks self-preference bias in the judge. Mitigation: the judge chain leads with a different model than the answering tier where possible, and the human spot-check of the golden set is kept.

## Database and access control (M2b)

### Three database roles, least privilege
- `provenance_owner` owns tables and runs migrations. It is a superuser that bypasses RLS, so **no request path ever connects as it**.
- `provenance_app` serves API requests. It owns nothing, so row-level security always applies.
- `provenance_sql_ro` runs model-generated SQL: read-only by default (`default_transaction_read_only`), a 3-second `statement_timeout`, and `SELECT` on the financial tables only. It can't see document text at all.

### Row-level security with a signed principal
- **Problem:** RLS policies usually read the caller's groups from a session setting. The SQL worker runs SQL written by an LLM, and `SELECT set_config('app.groups', 'restricted', true)` is a valid `SELECT`, so a manipulated model could grant itself access.
- **Picked:** the app sets both the group list and an HMAC-SHA256 signature of it. `app_groups()` (a `SECURITY DEFINER` function) recomputes the HMAC with a key stored in `app_secrets`, which query roles can't read. A forged or modified list yields no groups, so policies match no rows (fails closed). Proven by an attack test, and by a mutation test showing the attack succeeds when the check is removed.
- **Rejected:** a database role per group (roles explode combinatorially with multi-group users); trusting a SQL-parsing guard alone (one bypass away from a leak; the guard stays as a second layer).
- Settings are transaction-scoped (`set_config(..., true)`), so a pooled connection can't carry one caller's groups into another's request.
- `(SELECT app_groups())` in the policy makes Postgres evaluate it once per query instead of once per row.

### Access groups copied onto chunks
- `chunks.acl_groups` duplicates the parent document's groups so vector and BM25 search filter without a join. Both search paths are tested to respect RLS.

### Plain SQL migrations with a 40-line runner
- **Rejected:** Alembic. Its value is autogenerating migrations from ORM models, and this project uses raw SQL (pgvector, pg_search, RLS policies are all hand-written DDL anyway).

### Local-only database passwords
- Compose ships dev-default passwords and binds every port to `127.0.0.1`, so nothing is reachable from the network. Real deployments override them from the environment.

## PII redaction (M2c)
- **Type-enforced ordering:** `RedactedText` can only be built by `redact()` (a private construction token), and the embedder and chunk store accept only `RedactedText`. Skipping redaction is a type error caught by mypy, not a code-review item.
- **Detected:** emails, phone numbers (US and international), SSNs (with invalid-range exclusions), card numbers (issuer prefix + Luhn).
- **Not redacted:** people's names, because executives' names in public filings are facts users ask about, and NER-based detection needs a large model (spaCy/Presidio) for little benefit on this corpus. Company EINs identify organizations, not people.
- **Rejected:** Presidio. Its value is NER-based entity types this corpus doesn't need; regex + validators are transparent and fast, and every rule is unit-tested including against false positives from real filings.

## Ingestion (M2c)

### Section-aware semantic chunking
- **Picked:** chunks never cross a 10-K Item boundary. Within a section, paragraphs are embedded and a new chunk starts where the topic shifts most (cosine distance between neighbouring paragraphs above the section's 90th percentile), bounded by 80-400 tokens of the embedding model's own tokenizer. Paragraphs over the limit split by sentence, then by word windows.
- **Rejected:** fixed-size character windows (cut mid-sentence and mix topics, which hurts both retrieval and citation quality).
- **Measured:** Apple Item 1A (68K chars) → 41 chunks, 82-396 tokens, median 320.

### Contextual chunk headers
- Each chunk stores a `context` like "Apple Inc. (AAPL) 10-K fiscal 2025, Item 1A Risk Factors". It is prepended when embedding and is part of the BM25 index. Chunk text usually says "the Company", so without it a query naming the company misses relevant chunks.

### Section text stored for citations
- `sections.text` holds the redacted section; chunk `char_start`/`char_end` index into it, so every citation resolves to an exact span. An integration test and a real-data check (0 of 490 chunks broken) verify it. Section rows carry the same RLS as chunks.

### XBRL fiscal-year attribution
- A 10-K reports prior years too, all tagged with the filing's `fy`. A value is attributed to fiscal year `fy` only when it is the current period of its own filing; later amendments win; calendar frames (`CY2024`) are borrowed from whichever copy SEC tagged. Both labels are stored because they differ for non-calendar fiscal years (NVIDIA fiscal 2024 = calendar 2023).

### Local embeddings: bge-small-en-v1.5
- 384 dimensions, CPU-only PyTorch build, 4 threads. Free, private (text never leaves the machine for embedding), and small enough to embed the corpus in ~35 minutes on a laptop CPU. Queries get the model's retrieval instruction prefix; passages don't.

## API skeleton (M2d)

### API keys map to principals; only hashes are stored
- `config/principals.yaml` (committed) lists demo principals and their access groups. `python -m provenance.api.keys issue <name>` prints a random 256-bit key once and saves only its SHA-256 to `config/api_keys.local.json` (gitignored). A leaked hash file can't be replayed. Keys have full entropy, so a plain hash is enough (no bcrypt, which exists for low-entropy passwords).
- **Rejected:** JWT/OAuth for now. There is no identity provider to issue tokens, and principals → groups is the part RLS needs. Swapping the authenticator later doesn't touch RLS.

### One transaction per request, carrying the signed principal
- The `get_db` dependency opens a pooled connection as the non-owner app role, starts a transaction and sets the HMAC-signed group list (`principal_sql`) before the route runs. Routes contain no group filters; RLS filters every query. The settings are transaction-local, so a pooled connection can't carry one caller's groups into the next request (tested by alternating callers).

### Raw ASGI middleware, not `BaseHTTPMiddleware`
- `BaseHTTPMiddleware` buffers streaming bodies and breaks SSE, which `/query` needs in M5.

### One error shape, no internals
- `{"error": {"code", "message", "request_id"}}` for every failure. Unhandled exceptions are logged and returned as a bare 500 (a test checks that a secret in the exception message doesn't reach the client).

### Selector event loop on Windows
- psycopg's async driver can't use the Proactor loop that Windows defaults to. The launcher passes `asyncio:SelectorEventLoop` to uvicorn on Windows only. In Docker (Linux), uvicorn's default applies.

## Retrieval (M3)

### Hybrid: dense + BM25, fused by rank
- Dense (bge-small, pgvector HNSW, cosine) catches paraphrases; BM25 (ParadeDB) catches exact terms, tickers and figures that embeddings blur. Each returns 50 candidates; **Reciprocal Rank Fusion** (k=60) merges them by position only, so the incomparable score scales (cosine distance vs BM25) never need calibrating.
- BM25 queries go through `paradedb.match`, which tokenizes input as plain text: user queries can't inject query syntax, and a stray `(` can't cause an error. Both `text` and the contextual header are searched.

### Iterative HNSW scans under row-level security
- RLS filters rows *after* the vector index returns them. With 1,000 hidden chunks nearer to the query than any visible one, a plain HNSW scan returned **0** results to a tech analyst (reproduced in a test); `hnsw.iterative_scan = relaxed_order` keeps scanning until enough visible rows are found and returns all 3. The test forces the HNSW plan and was verified to fail with the setting off.
- On today's corpus (9.3K chunks) the planner actually prefers fetching the caller's rows through the ACL index and sorting them exactly (60-150 ms, perfect recall). The iterative scan is the guard for when the corpus grows and the plan flips.

### Cross-encoder reranking, all cores, top 20
- `bge-reranker-base` rescoring the fused candidates. Measured on the laptop CPU: 30 passages on 4 threads 11-14 s; 16 threads 4.6 s; 20 passages 3.6 s with the same top 5. Serving uses all cores (torch's thread count is process-wide, so it's set once, by the embedder); ingestion keeps 4 threads so the laptop stays usable.
- **Rejected for now:** ONNX/int8 export (the optimum exporter failed on this model with current library versions) and torch dynamic quantization (deprecated, and it broke inference). Reranking is a per-request switch so M4 can measure whether it earns its latency.

### LLM query rewriting, with guards
- The small model rewrites the question into a keyword-rich query and proposes filters (tickers, fiscal years, 10-K Items). Every field is validated (known tickers only). Any failure falls back to the original query unfiltered, and filters that match nothing are relaxed.
- **Measured:** Gemini Flash-Lite added section filters the question never asked for ("data center demand at Nvidia" → MD&A only), which silently hides relevant passages. Section and year filters are now kept only when the question itself names the section or year; tickers stay with the model, since mapping "Apple" to AAPL is what it's good at.
- The query is PII-redacted before the rewrite call, embedding, search or logging.
