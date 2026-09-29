from typing import Any

from provenance.ingest.xbrl import annual_facts


def fact(
    val: float,
    end: str,
    fy: int,
    accn: str,
    start: str | None = None,
    form: str = "10-K",
    fp: str = "FY",
    frame: str | None = None,
    filed: str = "2024-11-01",
) -> dict[str, Any]:
    f: dict[str, Any] = {
        "end": end,
        "val": val,
        "fy": fy,
        "fp": fp,
        "form": form,
        "accn": accn,
        "filed": filed,
    }
    if start:
        f["start"] = start
    if frame:
        f["frame"] = frame
    return f


def company_facts(concepts: dict[str, list[dict[str, Any]]], unit: str = "USD") -> dict[str, Any]:
    return {"facts": {"us-gaap": {c: {"units": {unit: fs}} for c, fs in concepts.items()}}}


FY24 = "0000320193-24-000123"
FY23 = "0000320193-23-000106"


def test_fiscal_year_comes_from_the_filing_where_the_period_is_current() -> None:
    data = company_facts(
        {
            "Revenues": [
                # The FY2024 10-K reports both years, both tagged fy=2024.
                fact(391_035e6, "2024-09-28", 2024, FY24, start="2023-10-01", frame="CY2024"),
                fact(383_285e6, "2023-09-30", 2024, FY24, start="2022-10-02"),
                # The FY2023 10-K, where 2023 was the current period.
                fact(383_285e6, "2023-09-30", 2023, FY23, start="2022-10-02", frame="CY2023"),
            ]
        }
    )

    facts = {(f.metric, f.fiscal_year): f for f in annual_facts("0000320193", data)}

    assert facts[("revenue", 2024)].value == 391_035e6
    assert facts[("revenue", 2024)].calendar_frame == "CY2024"
    assert facts[("revenue", 2023)].value == 383_285e6
    assert facts[("revenue", 2023)].accession == FY23


def test_calendar_frame_is_borrowed_from_another_copy_of_the_same_period() -> None:
    data = company_facts(
        {
            "Revenues": [
                # SEC puts the frame on only one copy: here, the one in the next year's filing.
                fact(383_285e6, "2023-09-30", 2023, FY23, start="2022-10-02"),
                fact(383_285e6, "2023-09-30", 2024, FY24, start="2022-10-02", frame="CY2023"),
                fact(391_035e6, "2024-09-28", 2024, FY24, start="2023-10-01"),
            ]
        }
    )

    facts = {f.fiscal_year: f for f in annual_facts("0000320193", data)}

    assert facts[2023].calendar_frame == "CY2023"
    assert facts[2023].accession == FY23


def test_quarterly_and_non_10k_facts_are_ignored() -> None:
    data = company_facts(
        {
            "Revenues": [
                fact(1.0, "2024-06-29", 2024, "q", start="2024-03-31", form="10-Q", fp="Q3"),
                fact(2.0, "2024-09-28", 2024, FY24, start="2024-06-30", fp="Q4"),
            ]
        }
    )

    assert annual_facts("0000320193", data) == []


def test_duration_metrics_need_a_full_year_period() -> None:
    data = company_facts({"Revenues": [fact(9.0, "2024-09-28", 2024, FY24, start="2024-06-30")]})

    assert annual_facts("0000320193", data) == []


def test_balance_sheet_metrics_use_instant_facts() -> None:
    data = company_facts({"Assets": [fact(364_980e6, "2024-09-28", 2024, FY24)]})

    [assets] = annual_facts("0000320193", data)

    assert (assets.metric, assets.value, assets.period_start) == ("total_assets", 364_980e6, None)


def test_first_matching_concept_wins_when_several_tag_the_same_metric() -> None:
    data = company_facts(
        {
            "Revenues": [fact(100.0, "2024-09-28", 2024, FY24, start="2023-10-01")],
            "RevenueFromContractWithCustomerExcludingAssessedTax": [
                fact(99.0, "2024-09-28", 2024, FY24, start="2023-10-01")
            ],
        }
    )

    [revenue] = annual_facts("0000320193", data)

    assert (revenue.value, revenue.concept) == (100.0, "Revenues")


def test_falls_back_to_the_next_concept_when_the_first_is_absent() -> None:
    data = company_facts(
        {
            "RevenueFromContractWithCustomerExcludingAssessedTax": [
                fact(99.0, "2024-09-28", 2024, FY24, start="2023-10-01")
            ]
        }
    )

    [revenue] = annual_facts("0000320193", data)

    assert revenue.value == 99.0


def test_per_share_metrics_use_the_per_share_unit() -> None:
    data = company_facts(
        {"EarningsPerShareDiluted": [fact(6.08, "2024-09-28", 2024, FY24, start="2023-10-01")]},
        unit="USD/shares",
    )

    [eps] = annual_facts("0000320193", data)

    assert (eps.metric, eps.unit, eps.value) == ("eps_diluted", "USD/shares", 6.08)


def test_later_amendment_of_the_same_filing_year_wins() -> None:
    data = company_facts(
        {
            "Revenues": [
                fact(100.0, "2024-09-28", 2024, FY24, start="2023-10-01", filed="2024-11-01"),
                fact(
                    101.0,
                    "2024-09-28",
                    2024,
                    "amend",
                    start="2023-10-01",
                    form="10-K/A",
                    filed="2025-02-01",
                ),
            ]
        }
    )

    [revenue] = annual_facts("0000320193", data)

    assert revenue.value == 101.0
