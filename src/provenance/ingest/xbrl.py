"""Annual financial facts from SEC's XBRL companyfacts API, normalized to named metrics.

A 10-K reports prior years too, and every value in it carries the *filing's* `fy`. A value
is attributed to fiscal year `fy` only when it is the current period of its own filing (the
latest period end that filing reports for the concept); later amendments win.
"""

from datetime import date
from typing import Any

from pydantic import BaseModel


class MetricSpec(BaseModel):
    metric: str
    concepts: tuple[str, ...]
    unit: str = "USD"
    instant: bool = False


METRICS: tuple[MetricSpec, ...] = (
    MetricSpec(
        metric="revenue",
        concepts=(
            "Revenues",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "SalesRevenueNet",
            "RevenuesNetOfInterestExpense",
        ),
    ),
    MetricSpec(metric="gross_profit", concepts=("GrossProfit",)),
    MetricSpec(metric="operating_income", concepts=("OperatingIncomeLoss",)),
    MetricSpec(metric="net_income", concepts=("NetIncomeLoss",)),
    MetricSpec(metric="eps_diluted", concepts=("EarningsPerShareDiluted",), unit="USD/shares"),
    MetricSpec(metric="research_and_development", concepts=("ResearchAndDevelopmentExpense",)),
    MetricSpec(
        metric="operating_cash_flow", concepts=("NetCashProvidedByUsedInOperatingActivities",)
    ),
    MetricSpec(
        metric="capital_expenditures", concepts=("PaymentsToAcquirePropertyPlantAndEquipment",)
    ),
    MetricSpec(metric="total_assets", concepts=("Assets",), instant=True),
    MetricSpec(metric="total_liabilities", concepts=("Liabilities",), instant=True),
    MetricSpec(metric="stockholders_equity", concepts=("StockholdersEquity",), instant=True),
    MetricSpec(
        metric="cash_and_equivalents",
        concepts=("CashAndCashEquivalentsAtCarryingValue",),
        instant=True,
    ),
    MetricSpec(
        metric="long_term_debt", concepts=("LongTermDebtNoncurrent", "LongTermDebt"), instant=True
    ),
)

_ANNUAL_FORMS = {"10-K", "10-K/A"}
_FULL_YEAR_DAYS = range(350, 381)


class FinancialFact(BaseModel):
    cik: str
    concept: str
    metric: str
    value: float
    unit: str
    fiscal_year: int
    fiscal_period: str = "FY"
    period_start: date | None
    period_end: date
    calendar_frame: str | None
    form: str
    accession: str
    filed_date: date


def annual_facts(cik: str, company_facts: dict[str, Any]) -> list[FinancialFact]:
    gaap: dict[str, Any] = company_facts.get("facts", {}).get("us-gaap", {})
    out: list[FinancialFact] = []
    for spec in METRICS:
        by_year: dict[int, FinancialFact] = {}
        for concept in spec.concepts:
            raw = gaap.get(concept, {}).get("units", {}).get(spec.unit, [])
            # SEC tags the calendar frame on only one copy of each period's value.
            frames = {(f.get("start"), f["end"]): f["frame"] for f in raw if f.get("frame")}
            for fact in _current_annual(raw, spec.instant):
                year = int(fact["fy"])
                if year in by_year and by_year[year].concept != concept:
                    continue  # an earlier concept in the list already covers this year
                candidate = _to_fact(cik, concept, spec, fact)
                if candidate.calendar_frame is None:
                    frame = frames.get((fact.get("start"), fact["end"]))
                    candidate = candidate.model_copy(update={"calendar_frame": frame})
                if year not in by_year or candidate.filed_date > by_year[year].filed_date:
                    by_year[year] = candidate
        out.extend(by_year[y] for y in sorted(by_year))
    return out


def _current_annual(facts: list[dict[str, Any]], instant: bool) -> list[dict[str, Any]]:
    annual = [f for f in facts if _is_annual(f, instant)]
    latest_end: dict[str, str] = {}
    for f in annual:
        latest_end[f["accn"]] = max(latest_end.get(f["accn"], ""), f["end"])
    return [f for f in annual if f["end"] == latest_end[f["accn"]]]


def _is_annual(fact: dict[str, Any], instant: bool) -> bool:
    if fact.get("form") not in _ANNUAL_FORMS or fact.get("fp") != "FY" or "fy" not in fact:
        return False
    if instant:
        return "start" not in fact
    if "start" not in fact:
        return False
    days = (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days
    return days in _FULL_YEAR_DAYS


def _to_fact(cik: str, concept: str, spec: MetricSpec, fact: dict[str, Any]) -> FinancialFact:
    return FinancialFact(
        cik=cik,
        concept=concept,
        metric=spec.metric,
        value=float(fact["val"]),
        unit=spec.unit,
        fiscal_year=int(fact["fy"]),
        period_start=date.fromisoformat(fact["start"]) if "start" in fact else None,
        period_end=date.fromisoformat(fact["end"]),
        calendar_frame=fact.get("frame"),
        form=fact["form"],
        accession=fact["accn"],
        filed_date=date.fromisoformat(fact["filed"]),
    )
