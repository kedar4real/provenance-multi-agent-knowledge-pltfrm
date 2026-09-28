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
