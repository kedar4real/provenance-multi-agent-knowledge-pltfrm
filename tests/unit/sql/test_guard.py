import pytest

from provenance.sql.guard import MAX_ROWS, UnsafeSQL, guard

OK = (
    "SELECT c.ticker, f.fiscal_year, f.value FROM financial_facts f "
    "JOIN companies c ON c.cik = f.cik WHERE f.metric = 'revenue' AND c.ticker = 'AAPL'"
)


def test_a_plain_select_passes_and_gets_a_row_limit() -> None:
    sql = guard(OK)

    assert sql.startswith("SELECT")
    assert sql.endswith(f"LIMIT {MAX_ROWS}")


def test_a_small_limit_is_kept_and_a_large_one_capped() -> None:
    assert guard(OK + " LIMIT 5").endswith("LIMIT 5")
    assert guard(OK + " LIMIT 100000").endswith(f"LIMIT {MAX_ROWS}")


def test_aggregates_windows_and_ctes_are_allowed() -> None:
    sql = (
        "WITH r AS (SELECT fiscal_year, value, LAG(value) OVER (ORDER BY fiscal_year) AS prev "
        "FROM financial_facts WHERE metric = 'revenue') "
        "SELECT fiscal_year, ROUND((value - prev) / NULLIF(prev, 0) * 100, 1) FROM r"
    )

    assert guard(sql)


@pytest.mark.parametrize(
    ("sql", "reason"),
    [
        ("DELETE FROM financial_facts", "only SELECT"),
        ("UPDATE financial_facts SET value = 0", "only SELECT"),
        ("SELECT 1; DROP TABLE companies", "exactly one statement"),
        ("SELECT * FROM documents", "table 'documents'"),
        ("SELECT * FROM chunks", "table 'chunks'"),
        ("SELECT * FROM pg_catalog.pg_roles", "schema-qualified"),
        ("SELECT * FROM app_secrets", "table 'app_secrets'"),
        ("SELECT set_config('app.groups', 'research_all', true)", "set_config"),
        ("SELECT current_setting('app.groups_sig')", "current_setting"),
        ("SELECT pg_sleep(30)", "pg_sleep"),
        ("SELECT * INTO stolen FROM financial_facts", "INTO"),
        ("SELECT * FROM financial_facts WHERE cik IN (SELECT cik FROM documents)", "documents"),
        ("not sql at all (", "not valid SQL"),
    ],
)
def test_unsafe_sql_is_rejected_with_a_reason(sql: str, reason: str) -> None:
    with pytest.raises(UnsafeSQL, match=reason):
        guard(sql)


def test_comments_are_dropped_from_the_sql_that_runs() -> None:
    assert "DROP" not in guard("SELECT * FROM financial_facts /* ; DROP TABLE companies */")
