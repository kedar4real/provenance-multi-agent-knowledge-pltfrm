-- Reading the audit log from the app, for auditors only. The app role still cannot SELECT
-- audit_log (migration 0003); these functions run as the owner and refuse any caller whose
-- signed groups (app_groups(), HMAC-checked) don't include 'auditor'. A misled request
-- holding an ordinary principal therefore still can't read, or learn from, the log.

CREATE FUNCTION audit_recent(max_rows int DEFAULT 200)
RETURNS TABLE (
    at timestamptz, request_id text, principal text, groups text[], tool text,
    input_preview text, outcome text, detail jsonb
)
LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF NOT ('auditor' = ANY (app_groups())) THEN
        RAISE EXCEPTION 'reading the audit log requires the auditor group'
            USING ERRCODE = 'insufficient_privilege';
    END IF;
    RETURN QUERY
        SELECT a.at, a.request_id, a.principal, a.groups, a.tool, a.input_preview, a.outcome,
               a.detail
        FROM audit_log a
        ORDER BY a.at DESC
        LIMIT least(greatest(max_rows, 1), 1000);
END;
$$;

-- Tool calls per day, tool and outcome, for the activity chart.
CREATE FUNCTION audit_daily(days int DEFAULT 14)
RETURNS TABLE (day date, tool text, outcome text, calls bigint)
LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
BEGIN
    IF NOT ('auditor' = ANY (app_groups())) THEN
        RAISE EXCEPTION 'reading the audit log requires the auditor group'
            USING ERRCODE = 'insufficient_privilege';
    END IF;
    RETURN QUERY
        SELECT (a.at AT TIME ZONE 'UTC')::date, a.tool, a.outcome, count(*)
        FROM audit_log a
        WHERE a.at >= now() - make_interval(days => least(greatest(days, 1), 90))
        GROUP BY 1, 2, 3
        ORDER BY 1, 2, 3;
END;
$$;

REVOKE ALL ON FUNCTION audit_recent(int), audit_daily(int) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION audit_recent(int), audit_daily(int) TO provenance_app;
