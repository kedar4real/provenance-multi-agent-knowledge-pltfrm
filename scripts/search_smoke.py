"""Live retrieval check on the main database with the real models and LLM rewriter.

uv run python scripts/search_smoke.py

Runs a few questions as two principals and prints the top hits, the rewrite and the time
per stage. A smoke test, not an evaluation (that's eval/ in M4).
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pgvector.psycopg import register_vector_async
from psycopg import AsyncConnection

from provenance.config import Settings
from provenance.db.security import principal_sql
from provenance.llm.factory import build_router, load_config
from provenance.retrieval.embeddings import Embedder
from provenance.retrieval.hybrid import HybridRetriever
from provenance.retrieval.rerank import Reranker
from provenance.retrieval.rewrite import QueryRewriter

QUESTIONS = [
    "What supply chain risks from tariffs does Apple describe?",
    "How did JPMorgan's net interest income change in fiscal 2025?",
    "How sensitive are Exxon's earnings to oil and gas prices?",
    "What is driving data center demand at Nvidia?",
]
PRINCIPALS = {"research_all": ["research_all"], "tech analyst": ["analyst_tech"]}


async def main() -> None:
    load_dotenv()
    settings = Settings()
    key = settings.rls_signing_key.get_secret_value()
    print("loading models...", flush=True)
    embedder = await asyncio.to_thread(Embedder, threads=os.cpu_count() or 4)
    reranker = await asyncio.to_thread(Reranker)
    router = build_router(load_config(Path("config/llm.yaml")))

    async with await AsyncConnection.connect(settings.app_dsn) as conn:
        await register_vector_async(conn)
        cur = await conn.execute("SELECT ticker, name FROM companies")
        companies = {t: n for t, n in await cur.fetchall()}
        await conn.commit()
        retriever = HybridRetriever(embedder, reranker, QueryRewriter(router, companies))

        for who, groups in PRINCIPALS.items():
            for question in QUESTIONS:
                async with conn.transaction():
                    sql, params = principal_sql(groups, key)
                    await conn.execute(sql, params)
                    result = await retriever.search(conn, question, k=3)
                f = result.filters
                print(f"\n[{who}] {question}")
                print(
                    f"  rewrite={result.rewrite} query={result.search_query!r}"
                    f" filters=tickers{f.tickers} years{f.fiscal_years} items{f.items}"
                    f"{' (relaxed)' if result.filters_relaxed else ''}"
                )
                for h in result.hits:
                    snippet = " ".join(h.text.split())[:110]
                    print(
                        f"  {h.ticker:<5} FY{h.fiscal_year} Item {h.item:<2}"
                        f" rerank={h.rerank_score:6.2f} | {snippet}"
                    )
                if not result.hits:
                    print("  (no visible passages)")
                timings = " ".join(f"{k}={v:.0f}" for k, v in result.timings_ms.items())
                print(f"  ms: {timings}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
