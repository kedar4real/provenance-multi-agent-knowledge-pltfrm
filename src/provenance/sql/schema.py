"""What the text-to-SQL model is told about the database. Only the two tables the read-only
SQL role can reach are described; the model never learns other tables exist."""

from provenance.ingest.corpus import COMMON_NAMES
from provenance.ingest.xbrl import METRICS


def schema_prompt() -> str:
    metrics = "\n".join(
        f"  - {m.metric} ({m.unit}{', balance at period end' if m.instant else ''})"
        for m in METRICS
    )
    companies = ", ".join(f"{t} = {n}" for t, n in sorted(COMMON_NAMES.items()))
    return f"""PostgreSQL tables:

companies(cik text primary key, ticker text, name text, sector text)

financial_facts(cik text references companies, metric text, value numeric, unit text,
                fiscal_year int, fiscal_period text, period_start date, period_end date)
  One row per company, metric and fiscal year (fiscal_period is always 'FY').
  value is in raw units: USD (not thousands or millions), or USD/shares for EPS.
  Fiscal years differ from calendar years for some companies (e.g. Nvidia, Walmart).
  metric is one of:
{metrics}

Join companies on cik and filter by companies.ticker. Tickers: {companies}"""
