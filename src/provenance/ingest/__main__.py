"""Ingest the demo corpus (or some tickers) from SEC EDGAR into Postgres.

uv run python -m provenance.ingest                  # all 30 companies, 2 filings each
uv run python -m provenance.ingest --tickers AAPL,JPM --filings 1
"""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

import psycopg

from provenance.config import Settings
from provenance.ingest.corpus import CORPUS, FILINGS_PER_COMPANY
from provenance.ingest.edgar import EdgarClient
from provenance.ingest.pipeline import ingest_company
from provenance.retrieval.embeddings import Embedder

CACHE_DIR = Path("data/raw/edgar")


async def main(tickers: list[str] | None, filings: int) -> int:
    settings = Settings()
    companies = [c for c in CORPUS if tickers is None or c.ticker in tickers]
    edgar = EdgarClient(settings.sec_user_agent, CACHE_DIR)
    embedder = Embedder()
    failures = 0
    started = time.perf_counter()
    with psycopg.connect(settings.owner_dsn) as conn:
        for n, company in enumerate(companies, 1):
            try:
                for r in await ingest_company(company, edgar, embedder, conn, filings):
                    print(
                        f"[{n}/{len(companies)}] {r.ticker:<5} FY{r.fiscal_year} {r.accession}"
                        f"  chunks {r.chunks_by_item}  pii {r.pii_redactions}  {r.seconds}s",
                        flush=True,
                    )
            except Exception as e:  # one bad filing must not stop the corpus run
                conn.rollback()
                failures += 1
                print(f"[{n}/{len(companies)}] {company.ticker:<5} FAILED: {e!r}", flush=True)
    print(f"done in {time.perf_counter() - started:.0f}s, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", help="comma-separated subset, default: whole corpus")
    parser.add_argument("--filings", type=int, default=FILINGS_PER_COMPANY)
    args = parser.parse_args()
    chosen = [t.strip().upper() for t in args.tickers.split(",")] if args.tickers else None
    sys.exit(asyncio.run(main(chosen, args.filings)))
