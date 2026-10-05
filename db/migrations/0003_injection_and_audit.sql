-- Prompt-injection verdicts stored per chunk (classified once at ingest, not per question),
-- and an append-only audit log of every tool call the agent makes.

-- NULL = not scanned yet; the agent treats unscanned chunks with runtime heuristics only.
ALTER TABLE chunks ADD COLUMN injection_flagged boolean;
ALTER TABLE chunks ADD COLUMN injection_reasons text[] NOT NULL DEFAULT '{}';
ALTER TABLE chunks ADD COLUMN injection_score real;

CREATE TABLE audit_log (
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    at            timestamptz NOT NULL DEFAULT now(),
    request_id    text NOT NULL,
    principal     text NOT NULL,
    groups        text[] NOT NULL,
    tool          text NOT NULL,
    -- What the tool was asked, redacted and truncated; never the raw prompt or results.
    input_preview text NOT NULL,
    outcome       text NOT NULL CHECK (outcome IN ('ok', 'denied', 'error')),
    detail        jsonb NOT NULL DEFAULT '{}'
);
CREATE INDEX audit_log_at ON audit_log (at);
CREATE INDEX audit_log_principal ON audit_log (principal, at);

-- The app may append audit rows but never read, change or delete them: a compromised or
-- misled request can't cover its tracks. Reading the log is an owner (operator) task.
GRANT INSERT ON audit_log TO provenance_app;
