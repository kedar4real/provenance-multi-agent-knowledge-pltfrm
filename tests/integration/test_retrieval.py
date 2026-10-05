"""The retrieval pipeline against the real Postgres (pgvector + pg_search + RLS), with fake
models whose behaviour the tests control."""

import json
from collections.abc import AsyncIterator
from pathlib import Path

import numpy as np
import psycopg
import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from psycopg import AsyncConnection

from provenance.api.main import create_app
from provenance.api.principals import hash_key
from provenance.config import Settings
from provenance.db.security import principal_sql
from provenance.retrieval.hybrid import HybridRetriever
from provenance.retrieval.types import RewrittenQuery, SearchFilters
from provenance.security.pii import RedactedText

pytestmark = pytest.mark.integration

TOPICS = ["tariff", "interest", "cloud", "restricted"]


def topic_vector(topic: str) -> np.ndarray:
    v = np.zeros(384, dtype=np.float32)
    v[TOPICS.index(topic)] = 1.0
    return v


class FakeEmbedder:
    """Maps a query to the first topic word it contains."""

    def embed_query(self, query: RedactedText) -> np.ndarray:
        for topic in TOPICS:
            if topic in query.text.lower():
                return topic_vector(topic)
        return np.full(384, 1 / np.sqrt(384), dtype=np.float32)


class KeywordReranker:
    """Scores a passage by how often it contains the word 'decisive'."""

    def score(self, query: str, passages: list[str]) -> list[float]:
        return [float(p.count("decisive")) for p in passages]


class FixedRewriter:
    def __init__(self, result: RewrittenQuery | None) -> None:
        self.result = result

    async def rewrite(self, question: RedactedText) -> RewrittenQuery | None:
        return self.result


# (ticker, fiscal year, item, text, topic, acl)
CHUNKS = [
    ("AAPL", 2025, "1A", "Tariffs on imported components raise costs.", "tariff", "analyst_tech"),
    ("AAPL", 2024, "1A", "Tariff exposure in the supply chain grew.", "tariff", "analyst_tech"),
    ("AAPL", 2025, "7", "Cloud services revenue grew; decisive quarter.", "cloud", "analyst_tech"),
    ("JPM", 2025, "7", "Net interest income rose with rates; tariff talk.", "interest", "analyst_finance"),
]  # fmt: skip
COMPANIES = {"AAPL": ("0000320193", "Apple Inc."), "JPM": ("0000019617", "JPMorgan Chase & Co")}


@pytest.fixture
def corpus(owner: psycopg.Connection) -> None:
    owner.execute("TRUNCATE companies, documents, chunks, financial_facts RESTART IDENTITY CASCADE")
    for ticker, (cik, name) in COMPANIES.items():
        owner.execute(
            "INSERT INTO companies (cik, ticker, name, sector) VALUES (%s, %s, %s, 'x')",
            (cik, ticker, name),
        )
    documents: dict[tuple[str, int], tuple[int, int]] = {}
    for i, (ticker, year, item, text, topic, acl) in enumerate(CHUNKS):
        cik, name = COMPANIES[ticker]
        if (ticker, year) not in documents:
            doc_id = owner.execute(
                "INSERT INTO documents (source, cik, accession, title, fiscal_year, url,"
                " acl_groups) VALUES ('10-K', %s, %s, %s, %s, %s, %s) RETURNING id",
                (cik, f"{ticker}-{year}", f"{name} {year}", year, f"https://sec/{ticker}/{year}",
                 [acl]),
            ).fetchone()[0]  # type: ignore[index]  # fmt: skip
            documents[(ticker, year)] = (doc_id, 0)
        doc_id, _ = documents[(ticker, year)]
        section_id = owner.execute(
            "INSERT INTO sections (document_id, item, title, text, acl_groups)"
            " VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (doc_id, item, f"Item {item}", text, [acl]),
        ).fetchone()[0]  # type: ignore[index]
        owner.execute(
            "INSERT INTO chunks (document_id, section_id, section, chunk_index, text, char_start,"
            " char_end, token_count, embedding, context, acl_groups)"
            " VALUES (%s, %s, %s, %s, %s, 0, %s, 10, %s, %s, %s)",
            (doc_id, section_id, item, i, text, len(text), str(topic_vector(topic).tolist()),
             f"{name} ({ticker}) 10-K fiscal {year}, Item {item}", [acl]),
        )  # fmt: skip


async def connect_as(settings: Settings, groups: list[str]) -> AsyncConnection:
    from pgvector.psycopg import register_vector_async

    conn = await AsyncConnection.connect(settings.app_dsn)
    await register_vector_async(conn)
    sql, params = principal_sql(groups, settings.rls_signing_key.get_secret_value())
    await conn.execute(sql, params)
    return conn


@pytest.fixture
async def tech(migrated: Settings, corpus: None) -> AsyncIterator[AsyncConnection]:
    conn = await connect_as(migrated, ["analyst_tech"])
    yield conn
    await conn.close()


@pytest.fixture
async def everyone(migrated: Settings, corpus: None) -> AsyncIterator[AsyncConnection]:
    conn = await connect_as(migrated, ["analyst_tech", "analyst_finance"])
    yield conn
    await conn.close()


def retriever(rewrite: RewrittenQuery | None = None, rerank: bool = False) -> HybridRetriever:
    return HybridRetriever(
        FakeEmbedder(),
        KeywordReranker() if rerank else None,
        FixedRewriter(rewrite) if rewrite else None,
    )


async def test_hybrid_finds_the_topic_and_returns_citable_hits(tech: AsyncConnection) -> None:
    result = await retriever().search(tech, "tariff risk", k=5)

    first = result.hits[0]
    assert "ariff" in first.text
    assert (first.ticker, first.item) == ("AAPL", "1A")
    assert first.url.startswith("https://sec/AAPL/")
    assert first.char_end - first.char_start == len(first.text)
    assert first.dense_rank is not None and first.bm25_rank is not None


async def test_rows_outside_the_callers_groups_never_appear(tech: AsyncConnection) -> None:
    # The JPM chunk is the best match for "interest", but tech analysts can't see it.
    for mode in ("hybrid", "dense", "bm25"):
        result = await retriever().search(tech, "net interest income", k=10, mode=mode)
        assert all(h.ticker == "AAPL" for h in result.hits), mode


async def test_caller_with_both_groups_sees_both(everyone: AsyncConnection) -> None:
    result = await retriever().search(everyone, "net interest income", k=3)

    assert result.hits[0].ticker == "JPM"


async def test_dense_search_survives_many_invisible_nearer_rows(
    owner: psycopg.Connection, tech: AsyncConnection
) -> None:
    # 1,000 restricted chunks sit close to the query vector; the visible ones are further away.
    doc_id = owner.execute(
        "INSERT INTO documents (source, cik, title, acl_groups) VALUES"
        " ('10-K', '0000019617', 'Board memos', '{internal_restricted}') RETURNING id"
    ).fetchone()[0]  # type: ignore[index]
    section_id = owner.execute(
        "INSERT INTO sections (document_id, item, title, text, acl_groups)"
        " VALUES (%s, '7', 'x', 'x', '{internal_restricted}') RETURNING id",
        (doc_id,),
    ).fetchone()[0]  # type: ignore[index]
    rng = np.random.default_rng(0)
    near = topic_vector("restricted") + rng.normal(0, 0.05, (1000, 384)).astype(np.float32)
    with owner.cursor() as cur:
        cur.executemany(
            "INSERT INTO chunks (document_id, section_id, section, chunk_index, text, char_start,"
            " char_end, token_count, embedding, acl_groups)"
            " VALUES (%s, %s, '7', %s, 'memo', 0, 4, 1, %s, '{internal_restricted}')",
            [(doc_id, section_id, i, str(v.tolist())) for i, v in enumerate(near)],
        )
    # At this size Postgres would rather fetch the caller's rows by ACL and sort them exactly
    # (as it does on the real corpus today); force the HNSW path that larger corpora take.
    # (The ACL index only supports bitmap scans, so this leaves HNSW as the only plan.)
    for setting in ("enable_seqscan", "enable_bitmapscan"):
        await tech.execute("SELECT set_config(%s, 'off', false)", (setting,))

    result = await retriever().search(tech, "restricted", k=3, mode="dense")

    assert len(result.hits) == 3
    assert all(h.ticker == "AAPL" for h in result.hits)


async def test_rewriter_filters_narrow_by_company_year_and_item(everyone: AsyncConnection) -> None:
    rewrite = RewrittenQuery(
        query="tariff", filters=SearchFilters(tickers=["AAPL"], fiscal_years=[2024], items=["1A"])
    )

    result = await retriever(rewrite).search(everyone, "anything", k=5)

    assert result.rewrite == "ok"
    assert result.search_query == "tariff"
    assert [(h.ticker, h.fiscal_year, h.item) for h in result.hits] == [("AAPL", 2024, "1A")]


async def test_filters_that_match_nothing_are_relaxed(tech: AsyncConnection) -> None:
    rewrite = RewrittenQuery(query="tariff", filters=SearchFilters(tickers=["JPM"]))

    result = await retriever(rewrite).search(tech, "JPM tariffs", k=5)

    assert result.filters_relaxed
    assert result.hits and all(h.ticker == "AAPL" for h in result.hits)


async def test_failed_rewrite_falls_back_to_the_original_query(tech: AsyncConnection) -> None:
    r = HybridRetriever(FakeEmbedder(), None, FixedRewriter(None))

    result = await r.search(tech, "tariff risk", k=3)

    assert result.rewrite == "failed"
    assert result.search_query == "tariff risk"
    assert result.hits


async def test_reranker_reorders_the_fused_candidates(tech: AsyncConnection) -> None:
    plain = await retriever().search(tech, "tariff cloud", k=3)
    reranked = await retriever(rerank=True).search(tech, "tariff cloud", k=3)

    assert reranked.reranked and not plain.reranked
    assert "decisive" in reranked.hits[0].text
    assert reranked.hits[0].rerank_score == 1.0


async def test_query_syntax_characters_are_treated_as_text(tech: AsyncConnection) -> None:
    result = await retriever().search(tech, 'tariff (AND "OR: -cloud', k=3, mode="bm25")

    assert result.hits


async def test_pii_in_the_query_is_redacted_before_use(tech: AsyncConnection) -> None:
    result = await retriever().search(tech, "tariff risk, mail me at jo@example.com", k=1)

    assert "jo@example.com" not in result.query
    assert "jo@example.com" not in result.search_query


async def test_search_endpoint_applies_the_callers_permissions(
    migrated: Settings, corpus: None, tmp_path: Path
) -> None:
    principals = tmp_path / "principals.yaml"
    principals.write_text(
        "principals:\n  tech: {display_name: Tech, groups: [analyst_tech]}\n", encoding="utf-8"
    )
    api_keys = tmp_path / "keys.json"
    api_keys.write_text(json.dumps({hash_key("pk_tech"): "tech"}), encoding="utf-8")
    settings = migrated.model_copy(
        update={"principals_path": principals, "api_keys_path": api_keys, "load_models": False}
    )
    app = create_app(settings, retriever=retriever(rerank=True))

    async with (
        LifespanManager(app) as manager,
        AsyncClient(transport=ASGITransport(manager.app), base_url="http://test") as client,
    ):
        response = await client.post(
            "/v1/search",
            json={"query": "net interest income", "k": 5, "rewrite": False},
            headers={"X-API-Key": "pk_tech"},
        )
        unauthenticated = await client.post("/v1/search", json={"query": "x"})
        invalid = await client.post(
            "/v1/search", json={"query": "", "k": 99}, headers={"X-API-Key": "pk_tech"}
        )

    body = response.json()
    assert response.status_code == 200, response.text
    assert body["hits"] and {h["ticker"] for h in body["hits"]} == {"AAPL"}
    assert body["reranked"] is True
    assert set(body["timings_ms"]) >= {"embed", "dense", "bm25", "fetch", "rerank"}
    assert unauthenticated.status_code == 401
    assert invalid.status_code == 422


async def test_source_endpoint_highlights_the_span_and_hides_other_groups(
    migrated: Settings, corpus: None, owner: psycopg.Connection, tmp_path: Path
) -> None:
    ids: dict[str, int] = dict(
        owner.execute(
            "SELECT co.ticker, c.id FROM chunks c JOIN documents d ON d.id = c.document_id"
            " JOIN companies co ON co.cik = d.cik WHERE c.chunk_index IN (0, 3)"
        ).fetchall()
    )
    principals = tmp_path / "principals.yaml"
    principals.write_text(
        "principals:\n  tech: {display_name: Tech, groups: [analyst_tech]}\n", encoding="utf-8"
    )
    api_keys = tmp_path / "keys.json"
    api_keys.write_text(json.dumps({hash_key("pk_tech"): "tech"}), encoding="utf-8")
    settings = migrated.model_copy(
        update={"principals_path": principals, "api_keys_path": api_keys, "load_models": False}
    )
    headers = {"X-API-Key": "pk_tech"}
    async with (
        LifespanManager(create_app(settings)) as manager,
        AsyncClient(transport=ASGITransport(manager.app), base_url="http://test") as client,
    ):
        own = await client.get(f"/v1/sources/{ids['AAPL']}", headers=headers)
        hidden = await client.get(f"/v1/sources/{ids['JPM']}", headers=headers)
        missing = await client.get("/v1/sources/999999", headers=headers)

    body = own.json()
    assert own.status_code == 200
    assert body["company"] == "Apple"
    cited = body["text"][body["highlight_start"] : body["highlight_end"]]
    assert cited == "Tariffs on imported components raise costs."
    # A hidden source and a missing one are indistinguishable.
    assert hidden.status_code == missing.status_code == 404
    assert hidden.json()["error"]["code"] == missing.json()["error"]["code"] == "source_not_found"


class RecordingReranker:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def score(self, query: str, passages: list[str]) -> list[float]:
        self.queries.append(query)
        return [0.5] * len(passages)


async def test_rerank_judges_relevance_to_the_users_question_not_the_rewrite(
    tech: AsyncConnection,
) -> None:
    # The rewrite widens the candidate pool; relevance is still judged against what was
    # asked. Scoring against the rewrite made unanswerable questions look answerable.
    reranker = RecordingReranker()
    rewrite = RewrittenQuery(query="tariff exposure")
    retriever = HybridRetriever(FakeEmbedder(), reranker, FixedRewriter(rewrite))

    await retriever.search(tech, "What were Tesla's tariff costs?", k=3)

    assert reranker.queries == ["What were Tesla's tariff costs?"]
