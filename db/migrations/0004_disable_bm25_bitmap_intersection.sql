-- pg_search can intersect the BM25 index with a btree index (here, document_id) inside a
-- parallel scan. After the first full injection scan rewrote every chunk, filtered BM25
-- queries failed with "bitmap intersection stream ... claimed twice" and the answer evals
-- crashed. It could not be reproduced on demand afterwards, so this removes the code path the
-- error names: on all 200 golden questions the results are identical with it off, at the same
-- speed. The filter is then applied as a recheck on the BM25 matches instead.
DO $$
BEGIN
    EXECUTE format(
        'ALTER DATABASE %I SET paradedb.enable_bitmap_intersection = off', current_database()
    );
END
$$;
