"""Keyword search with real BM25 (ParadeDB pg_search) over chunk text and its context header."""

from psycopg import AsyncConnection

# paradedb.match tokenizes the input as plain text, so user queries can't inject query
# syntax (a stray "(" or "AND" would break, or change, a parsed query string).
_SEARCH = """
SELECT id, paradedb.score(id) AS score
FROM chunks
WHERE id @@@ paradedb.boolean(should => ARRAY[
        paradedb.match('text', %(q)s),
        paradedb.match('context', %(q)s)
      ])
  AND (%(doc_ids)s::bigint[] IS NULL OR document_id = ANY(%(doc_ids)s))
  AND (%(items)s::text[] IS NULL OR section = ANY(%(items)s))
ORDER BY score DESC, id
LIMIT %(limit)s
"""


async def bm25_search(
    conn: AsyncConnection,
    query: str,
    limit: int,
    document_ids: list[int] | None = None,
    items: list[str] | None = None,
) -> list[int]:
    """Chunk IDs by BM25 score, best first; only rows the caller may see."""
    if not query.strip():
        return []
    cur = await conn.execute(
        _SEARCH,
        {"q": query, "doc_ids": document_ids, "items": items or None, "limit": limit},
    )
    return [row[0] for row in await cur.fetchall()]
