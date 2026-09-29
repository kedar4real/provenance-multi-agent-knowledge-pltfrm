-- Core schema: companies, documents, chunks (hybrid-search ready), financial facts,
-- and signed-principal row-level security. Runs as provenance_owner.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_search;

-- Secrets readable only by the owner. Holds the key that signs callers' access groups.
CREATE TABLE app_secrets (
    name  text PRIMARY KEY,
    value text NOT NULL
);
REVOKE ALL ON app_secrets FROM PUBLIC;

-- The caller's access groups, trusted only if their HMAC signature matches. Fails closed:
-- missing, empty or forged settings yield no groups, so RLS policies match no rows.
CREATE FUNCTION app_groups() RETURNS text[]
LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    groups    text := current_setting('app.groups', true);
    signature text := current_setting('app.groups_sig', true);
    key       text;
BEGIN
    IF groups IS NULL OR groups = '' OR signature IS NULL OR signature = '' THEN
        RETURN '{}';
    END IF;
    SELECT value INTO key FROM app_secrets WHERE name = 'rls_signing_key';
    IF key IS NULL OR encode(hmac(groups, key, 'sha256'), 'hex') <> signature THEN
        RETURN '{}';
    END IF;
    RETURN string_to_array(groups, ',');
END;
$$;
REVOKE ALL ON FUNCTION app_groups() FROM PUBLIC;

CREATE TABLE companies (
    cik      text PRIMARY KEY CHECK (cik ~ '^\d{10}$'),
    ticker   text NOT NULL UNIQUE,
    name     text NOT NULL,
    sector   text NOT NULL
);

CREATE TABLE documents (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source      text NOT NULL CHECK (source IN ('10-K', 'internal_note')),
    cik         text NOT NULL REFERENCES companies,
    accession   text UNIQUE,
    title       text NOT NULL,
    fiscal_year int,
    period_end  date,
    filed_date  date,
    url         text,
    acl_groups  text[] NOT NULL CHECK (cardinality(acl_groups) > 0),
    ingested_at timestamptz NOT NULL DEFAULT now()
);

-- acl_groups is copied from the parent document so search queries filter without a join.
CREATE TABLE chunks (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    document_id    bigint NOT NULL REFERENCES documents ON DELETE CASCADE,
    section        text NOT NULL,
    chunk_index    int NOT NULL,
    text           text NOT NULL,
    char_start     int NOT NULL,
    char_end       int NOT NULL CHECK (char_end > char_start),
    token_count    int NOT NULL,
    embedding      vector(384) NOT NULL,
    pii_redactions int NOT NULL DEFAULT 0,
    acl_groups     text[] NOT NULL CHECK (cardinality(acl_groups) > 0),
    UNIQUE (document_id, section, chunk_index)
);
CREATE INDEX chunks_embedding_hnsw ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX chunks_bm25 ON chunks USING bm25 (id, text, section) WITH (key_field = 'id');
CREATE INDEX chunks_acl ON chunks USING gin (acl_groups);

-- One row per company, metric and fiscal period. fiscal_year is the company's own label;
-- calendar_frame is SEC's calendar alignment (e.g. CY2024) and can differ from it.
CREATE TABLE financial_facts (
    id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cik            text NOT NULL REFERENCES companies,
    concept        text NOT NULL,
    metric         text NOT NULL,
    value          numeric NOT NULL,
    unit           text NOT NULL,
    fiscal_year    int NOT NULL,
    fiscal_period  text NOT NULL,
    period_start   date,
    period_end     date NOT NULL,
    calendar_frame text,
    form           text NOT NULL,
    accession      text NOT NULL,
    filed_date     date NOT NULL,
    acl_groups     text[] NOT NULL CHECK (cardinality(acl_groups) > 0),
    UNIQUE (cik, metric, fiscal_year, fiscal_period)
);
CREATE INDEX financial_facts_lookup ON financial_facts (cik, metric, fiscal_year);

-- Grants: the app reads everything through RLS; the SQL role sees only financial tables.
GRANT USAGE ON SCHEMA public TO provenance_app, provenance_sql_ro;
GRANT EXECUTE ON FUNCTION app_groups() TO provenance_app, provenance_sql_ro;
GRANT SELECT ON companies, documents, chunks, financial_facts TO provenance_app;
GRANT SELECT ON companies, financial_facts TO provenance_sql_ro;

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_facts ENABLE ROW LEVEL SECURITY;

-- (SELECT app_groups()) is evaluated once per query, not once per row.
CREATE POLICY documents_by_group ON documents FOR SELECT
    TO provenance_app USING (acl_groups && (SELECT app_groups()));
CREATE POLICY chunks_by_group ON chunks FOR SELECT
    TO provenance_app USING (acl_groups && (SELECT app_groups()));
CREATE POLICY financial_facts_by_group ON financial_facts FOR SELECT
    TO provenance_app, provenance_sql_ro USING (acl_groups && (SELECT app_groups()));
