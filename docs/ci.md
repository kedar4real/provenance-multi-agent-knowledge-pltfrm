# CI and the retrieval gate

Two workflows in `.github/workflows/`:

| workflow | runs on | what it checks |
|---|---|---|
| `ci.yml` | every push to main and every PR | gitleaks over the full history; ruff, ruff format, mypy; unit tests (including mcpgate against its malicious fixture server); integration tests on real ParadeDB and Redis from `docker-compose.yml`; the web build; that `mcpgate` installs and runs on its own |
| `eval-gate.yml` | PRs touching retrieval, ingestion, security, the database, or `eval/` | the retrieval regression gate below |

Both are free: GitHub Actions on a private repo includes 2,000 minutes a month. The gate
needs no API keys and makes no model calls.

## What the gate checks

`eval/gate.py` restores the search index, runs hybrid search plus the cross-encoder reranker
(config `c` of the retrieval eval) over every golden question, as each question's own
principal and through row-level security, and fails the PR if:

- any of Recall@1, @5, @10, MRR@10 or nDCG@10 falls below its **floor** in `eval/thresholds.yaml`;
- any principal sees a company outside their sectors (floor: zero leaks);
- fewer golden cases have gold passages than when the baseline was recorded (a smaller set
  can flatter every metric).

A floor is the recorded measurement minus 0.03 (about four questions' worth of Recall@1),
which absorbs small numerical differences between machines. Floors are never moved to make
a change pass. When the golden set or the pipeline legitimately changes, re-record in its own
commit so the reviewer sees the baseline move:

```powershell
uv run python -m eval.gate --record
```

## One-time setup (owner)

1. **Push the repo** (it's private): `git push -u origin main`.
2. **Upload the search index.** CI can't re-ingest from EDGAR, so it restores a dump of the
   documents, chunks, embeddings and financial facts (about 26 MB; SEC filings plus the demo's
   synthetic internal notes; no secrets):
   ```powershell
   docker compose up -d
   uv run python scripts/index_dump.py export data/index.dump
   gh release create eval-index-v1 data/index.dump --title "Eval index v1" --notes "Search index for the retrieval gate (scripts/index_dump.py)."
   ```
   Re-export and publish a new release (`eval-index-v2`, and change `INDEX_RELEASE` in the
   workflow) whenever ingestion, chunking or the embedding model changes. If the repo is made
   public, the release is public too; its contents are SEC filings and synthetic notes.
3. **Require the checks.** In the repo's Settings, Branches, add a rule for `main` that
   requires the `ci` jobs and `retrieval gate` before merging.
4. **See it fail.** Open a throwaway PR that weakens retrieval (for example, shrink
   `RERANK_POOL` in `src/provenance/retrieval/hybrid.py` to 3). `retrieval gate` should go
   red with a table naming the metrics that dropped. Close it without merging.

## Reproduce a failure locally

```powershell
docker compose up -d
uv run python -m eval.gate
```

The gate prints the same table the job summary shows. It uses whatever database your `.env`
points at (your full ingest), so numbers can differ slightly from CI's restored index.

## Not in the gate (yet)

An answer-quality (faithfulness) gate over a 25-question subset needs a Groq key as a
repository secret and a baseline measured from the agent eval; it will be added once that
eval has run. Until then answer quality is measured, not gated.

## Verified locally

Against an index restored from `scripts/index_dump.py` into a fresh, migrated database (the
path CI takes):

- On `main`: the gate passes and reproduces the recorded baseline exactly (Recall@1 0.792,
  Recall@10 0.946, MRR 0.853, 0 leaks), in 883 s on a laptop CPU shared with other jobs.
- On the local branch `proof/gate-regression` (reranker pool 20 to 3): it fails all five
  quality metrics (Recall@1 0.731 vs floor 0.762, Recall@10 0.800 vs 0.916) and exits 1.
