"""Exhaustive access-control check: no principal ever sees another sector's data.

uv run python -m eval.acl_eval

For every sector analyst (and a principal holding only an internal group), search for every
one of the 30 companies by name, through the real retrieval path and row-level security,
and run an unrestricted SQL query as the read-only SQL role. Any passage or financial row
from a company outside the principal's groups is a leak. Deterministic: no LLM involved.
"""

import asyncio
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from pgvector.psycopg import register_vector_async
from psycopg import AsyncConnection

from provenance.config import Settings
from provenance.db.security import principal_sql
from provenance.ingest.corpus import ALL_RESEARCH_GROUP, COMMON_NAMES, CORPUS
from provenance.retrieval.embeddings import Embedder
from provenance.retrieval.hybrid import HybridRetriever

REPORTS = Path("eval/reports")
QUESTIONS = ["{name} risk factors", "{name} revenue growth and outlook", "{name} business segments"]
ALL_FACTS_SQL = (
    "SELECT c.ticker FROM financial_facts f JOIN companies c ON c.cik = f.cik GROUP BY c.ticker"
)


def principals() -> dict[str, list[str]]:
    sectors = sorted({c.sector for c in CORPUS})
    out = {f"analyst_{s}": [f"analyst_{s}"] for s in sectors}
    out["internal_only"] = ["internal_restricted"]
    out["research_all"] = [ALL_RESEARCH_GROUP]
    return out


def visible_tickers(groups: list[str]) -> set[str]:
    return {c.ticker for c in CORPUS if set(c.acl_groups) & set(groups)}


async def run() -> dict[str, object]:
    settings = Settings()
    key = settings.rls_signing_key.get_secret_value()
    retriever = HybridRetriever(Embedder(threads=os.cpu_count() or 4), None, None)
    leaks: list[dict[str, object]] = []
    checks = 0
    async with (
        await AsyncConnection.connect(settings.app_dsn) as app,
        await AsyncConnection.connect(settings.sql_ro_dsn) as sql_ro,
    ):
        await register_vector_async(app)
        await app.commit()
        for name, groups in principals().items():
            allowed = visible_tickers(groups)
            sql, params = principal_sql(groups, key)
            for company in CORPUS:
                for template in QUESTIONS:
                    question = template.format(name=COMMON_NAMES[company.ticker])
                    async with app.transaction():
                        await app.execute(sql, params)
                        result = await retriever.search(
                            app, question, k=10, rewrite=False, rerank=False
                        )
                    seen = {h.ticker for h in result.hits}
                    checks += 1
                    if seen - allowed:
                        leaks.append({"principal": name, "via": "search", "question": question,
                                      "leaked": sorted(seen - allowed)})  # fmt: skip
            async with sql_ro.transaction():
                await sql_ro.execute(sql, params)
                cur = await sql_ro.execute(ALL_FACTS_SQL)
                seen = {row[0] for row in await cur.fetchall()}
            checks += 1
            if seen - allowed:
                leaks.append({"principal": name, "via": "sql", "leaked": sorted(seen - allowed)})
            print(
                f"{name:22} allowed {len(allowed):2} companies; leaks so far {len(leaks)}",
                flush=True,
            )
    return {"checks": checks, "leaks": leaks, "principals": len(principals())}


def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(run())
    REPORTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M")
    (REPORTS / f"acl-{stamp}.json").write_text(json.dumps(result, indent=2), "utf-8")
    summary = (
        f"ACL eval: {len(result['leaks'])} leaks in {result['checks']} checks "  # type: ignore[arg-type]
        f"across {result['principals']} principals (search over all 30 companies x "
        f"{len(QUESTIONS)} questions, plus unrestricted SQL)."
    )
    (REPORTS / f"acl-{stamp}.md").write_text(f"# Access control\n\n{summary}\n", "utf-8")
    print(summary)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    main()
