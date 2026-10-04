"""Vector search over chunk embeddings (pgvector HNSW, cosine distance)."""

import numpy as np
from psycopg import AsyncConnection

# Row-level security (and filters) remove rows *after* the index scan. Without iterative
# scans, a sector analyst who can see 1/7 of the chunks would get ~1/7 of the requested
# results. relaxed_order keeps scanning until enough visible rows are found; the outer
# ORDER BY restores exact order.
_SCAN_SETTINGS = (
    "SELECT set_config('hnsw.iterative_scan', 'relaxed_order', true),"
    " set_config('hnsw.ef_search', '100', true)"
)

_SEARCH = """
WITH nearest AS MATERIALIZED (
    SELECT id, embedding <=> %(vec)s AS distance
    FROM chunks
    WHERE (%(doc_ids)s::bigint[] IS NULL OR document_id = ANY(%(doc_ids)s))
      AND (%(items)s::text[] IS NULL OR section = ANY(%(items)s))
    ORDER BY distance
    LIMIT %(limit)s
)
SELECT id FROM nearest ORDER BY distance, id
"""


async def dense_search(
    conn: AsyncConnection,
    query_vector: np.ndarray,
    limit: int,
    document_ids: list[int] | None = None,
    items: list[str] | None = None,
) -> list[int]:
    """Chunk IDs nearest to the query, best first; only rows the caller may see."""
    await conn.execute(_SCAN_SETTINGS)
    cur = await conn.execute(
        _SEARCH,
        {
            "vec": query_vector.astype(np.float32),
            "doc_ids": document_ids,
            "items": items or None,
            "limit": limit,
        },
    )
    return [row[0] for row in await cur.fetchall()]
