-- Stores each section's redacted text so chunk offsets (char_start/char_end) resolve to a
-- real passage for citations, and adds a context header to chunks for embedding and BM25.

CREATE TABLE sections (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id    bigint NOT NULL REFERENCES documents ON DELETE CASCADE,
    item           text NOT NULL,
    title          text NOT NULL,
    text           text NOT NULL,
    pii_redactions int NOT NULL DEFAULT 0,
    acl_groups     text[] NOT NULL CHECK (cardinality(acl_groups) > 0),
    UNIQUE (document_id, item)
);

ALTER TABLE chunks ADD COLUMN section_id bigint NOT NULL REFERENCES sections ON DELETE CASCADE;
-- e.g. "Apple Inc. (AAPL) 10-K fiscal 2025, Item 1A Risk Factors". Chunks often say "the
-- Company" instead of the name, so without this a search for "Apple" would miss them.
ALTER TABLE chunks ADD COLUMN context text NOT NULL DEFAULT '';

DROP INDEX chunks_bm25;
CREATE INDEX chunks_bm25 ON chunks USING bm25 (id, text, context, section) WITH (key_field = 'id');

GRANT SELECT ON sections TO provenance_app;
ALTER TABLE sections ENABLE ROW LEVEL SECURITY;
CREATE POLICY sections_by_group ON sections FOR SELECT
    TO provenance_app USING (acl_groups && (SELECT app_groups()));
