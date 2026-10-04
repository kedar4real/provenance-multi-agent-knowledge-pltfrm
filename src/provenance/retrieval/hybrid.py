"""The retrieval pipeline: rewrite -> dense + BM25 -> reciprocal rank fusion -> rerank.

Every query runs on the caller's connection, so row-level security applies to each stage.
"""

import asyncio
import time
from collections.abc import Callable
from typing import Protocol

import numpy as np
from psycopg import AsyncConnection

from provenance.retrieval.bm25 import bm25_search
from provenance.retrieval.dense import dense_search
from provenance.retrieval.fusion import reciprocal_rank_fusion
from provenance.retrieval.types import Hit, Mode, RewrittenQuery, SearchFilters, SearchResult
from provenance.security.pii import RedactedText, redact

CANDIDATES_PER_RETRIEVER = 50
# Measured: reranking 30 passages took 4.6s on 16 CPU threads, 20 took 3.6s, same top 5.
RERANK_POOL = 20

_HITS = """
SELECT c.id, c.document_id, co.ticker, co.name, d.fiscal_year, c.section, s.title, c.text,
       c.context, c.char_start, c.char_end, d.url
FROM chunks c
JOIN documents d ON d.id = c.document_id
JOIN sections s ON s.id = c.section_id
JOIN companies co ON co.cik = d.cik
WHERE c.id = ANY(%s)
"""

_FILTERED_DOCUMENTS = """
SELECT d.id FROM documents d JOIN companies co ON co.cik = d.cik
WHERE (%(tickers)s::text[] IS NULL OR co.ticker = ANY(%(tickers)s))
  AND (%(years)s::int[] IS NULL OR d.fiscal_year = ANY(%(years)s))
"""


class QueryEmbedder(Protocol):
    def embed_query(self, query: RedactedText) -> np.ndarray: ...


class PassageScorer(Protocol):
    def score(self, query: str, passages: list[str]) -> list[float]: ...


class Rewriter(Protocol):
    async def rewrite(self, question: RedactedText) -> RewrittenQuery | None: ...


class HybridRetriever:
    def __init__(
        self,
        embedder: QueryEmbedder,
        reranker: PassageScorer | None,
        rewriter: Rewriter | None,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._embedder = embedder
        self._reranker = reranker
        self._rewriter = rewriter
        self._clock = clock
        # The CPU models aren't made for concurrent calls; queue them instead of thrashing.
        self._model_lock = asyncio.Lock()

    @property
    def can_rerank(self) -> bool:
        return self._reranker is not None

    @property
    def can_rewrite(self) -> bool:
        return self._rewriter is not None

    async def search(
        self,
        conn: AsyncConnection,
        query: str,
        k: int = 8,
        mode: Mode = "hybrid",
        rerank: bool = True,
        rewrite: bool = True,
    ) -> SearchResult:
        timings: dict[str, float] = {}
        # Redact before the query goes anywhere: the LLM provider, the embedder, the logs.
        question = redact(query)

        search_query, filters, rewrite_status = question.text, SearchFilters(), "off"
        if rewrite and self._rewriter is not None:
            with self._timed(timings, "rewrite"):
                rewritten = await self._rewriter.rewrite(question)
            if rewritten is None:
                rewrite_status = "failed"
            else:
                rewrite_status = "ok"
                search_query, filters = redact(rewritten.query).text, rewritten.filters

        query_vector = None
        if mode != "bm25":
            with self._timed(timings, "embed"):
                async with self._model_lock:
                    query_vector = await asyncio.to_thread(
                        self._embedder.embed_query, redact(search_query)
                    )

        ranked = await self._retrieve(conn, mode, search_query, query_vector, filters, timings)
        relaxed = False
        if not ranked and not filters.is_empty:
            # Filters guessed by the rewriter can be wrong; better unfiltered than nothing.
            relaxed = True
            ranked = await self._retrieve(
                conn, mode, search_query, query_vector, SearchFilters(), timings
            )

        pool_size = RERANK_POOL if rerank and self._reranker is not None else k
        with self._timed(timings, "fetch"):
            hits = await _load_hits(conn, ranked[:pool_size])

        reranked = False
        if rerank and self._reranker is not None and hits:
            reranker = self._reranker
            with self._timed(timings, "rerank"):
                async with self._model_lock:
                    scores = await asyncio.to_thread(
                        reranker.score, search_query, [f"{h.context}\n{h.text}" for h in hits]
                    )
            for hit, score in zip(hits, scores, strict=True):
                hit.rerank_score = score
            hits.sort(key=lambda h: (-(h.rerank_score or 0.0), h.chunk_id))
            reranked = True

        return SearchResult(
            query=question.text,
            search_query=search_query,
            filters=filters,
            filters_relaxed=relaxed,
            rewrite=rewrite_status,
            mode=mode,
            reranked=reranked,
            hits=hits[:k],
            timings_ms=timings,
        )

    async def _retrieve(
        self,
        conn: AsyncConnection,
        mode: Mode,
        search_query: str,
        query_vector: np.ndarray | None,
        filters: SearchFilters,
        timings: dict[str, float],
    ) -> list[tuple[int, float, int | None, int | None]]:
        """(chunk_id, fused score, dense rank, bm25 rank), best first."""
        doc_ids = await _filtered_documents(conn, filters)
        items: list[str] = list(filters.items)
        dense: list[int] = []
        lexical: list[int] = []
        if query_vector is not None:
            with self._timed(timings, "dense"):
                dense = await dense_search(
                    conn, query_vector, CANDIDATES_PER_RETRIEVER, doc_ids, items
                )
        if mode != "dense":
            with self._timed(timings, "bm25"):
                lexical = await bm25_search(
                    conn, search_query, CANDIDATES_PER_RETRIEVER, doc_ids, items
                )
        dense_rank = {cid: r for r, cid in enumerate(dense, start=1)}
        bm25_rank = {cid: r for r, cid in enumerate(lexical, start=1)}
        fused = reciprocal_rank_fusion([r for r in (dense, lexical) if r])
        return [(cid, score, dense_rank.get(cid), bm25_rank.get(cid)) for cid, score in fused]

    def _timed(self, timings: dict[str, float], stage: str) -> "_Timer":
        return _Timer(timings, stage, self._clock)


class _Timer:
    def __init__(self, timings: dict[str, float], stage: str, clock: Callable[[], float]) -> None:
        self._timings, self._stage, self._clock = timings, stage, clock

    def __enter__(self) -> None:
        self._started = self._clock()

    def __exit__(self, *_: object) -> None:
        elapsed = (self._clock() - self._started) * 1000
        self._timings[self._stage] = round(self._timings.get(self._stage, 0.0) + elapsed, 1)


async def _filtered_documents(conn: AsyncConnection, filters: SearchFilters) -> list[int] | None:
    """Document IDs matching ticker/year filters; None means no document restriction."""
    if not (filters.tickers or filters.fiscal_years):
        return None
    cur = await conn.execute(
        _FILTERED_DOCUMENTS,
        {"tickers": filters.tickers or None, "years": filters.fiscal_years or None},
    )
    return [row[0] for row in await cur.fetchall()]


async def _load_hits(
    conn: AsyncConnection, ranked: list[tuple[int, float, int | None, int | None]]
) -> list[Hit]:
    if not ranked:
        return []
    cur = await conn.execute(_HITS, ([cid for cid, *_ in ranked],))
    rows = {row[0]: row for row in await cur.fetchall()}
    hits = []
    for cid, fused, dense_rank, bm25_rank in ranked:
        row = rows.get(cid)
        if row is None:
            continue
        hits.append(
            Hit(
                chunk_id=row[0],
                document_id=row[1],
                ticker=row[2],
                company=row[3],
                fiscal_year=row[4],
                item=row[5],
                section_title=row[6],
                text=row[7],
                context=row[8],
                char_start=row[9],
                char_end=row[10],
                url=row[11],
                dense_rank=dense_rank,
                bm25_rank=bm25_rank,
                fused_score=round(fused, 6),
            )
        )
    return hits
