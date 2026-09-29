import json
from datetime import date
from pathlib import Path
from typing import Any

import httpx2
import pytest

from provenance.ingest.edgar import EdgarClient, FilingRef

SUBMISSIONS = {
    "filings": {
        "recent": {
            "form": ["10-Q", "10-K", "8-K", "10-K/A", "10-K", "10-K"],
            "accessionNumber": [
                "q",
                "0000320193-25-000079",
                "e",
                "a",
                "0000320193-24-000123",
                "old",
            ],
            "filingDate": [
                "2026-01-30",
                "2025-10-31",
                "2025-10-30",
                "2025-01-01",
                "2024-11-01",
                "2023-11-03",
            ],
            "reportDate": [
                "2025-12-27",
                "2025-09-27",
                "",
                "2024-09-28",
                "2024-09-28",
                "2023-09-30",
            ],
            "primaryDocument": [
                "q.htm",
                "aapl-20250927.htm",
                "e.htm",
                "a.htm",
                "aapl-20240928.htm",
                "o.htm",
            ],
        }
    }
}


class FakeSec:
    def __init__(self) -> None:
        self.requests: list[httpx2.Request] = []

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        url = str(request.url)
        if url.endswith("/submissions/CIK0000320193.json"):
            return httpx2.Response(200, json=SUBMISSIONS)
        if url.endswith("company_tickers.json"):
            return httpx2.Response(
                200, json={"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}
            )
        if url.endswith("/companyfacts/CIK0000320193.json"):
            return httpx2.Response(200, json={"facts": {}})
        if url.endswith(".htm"):
            return httpx2.Response(200, text="<html>10-K</html>")
        return httpx2.Response(404)


@pytest.fixture
def sec() -> FakeSec:
    return FakeSec()


def client(sec: FakeSec, tmp_path: Path, **kw: Any) -> EdgarClient:
    http = httpx2.AsyncClient(transport=httpx2.MockTransport(sec.handle))
    return EdgarClient(
        user_agent="provenance test@example.com", cache_dir=tmp_path, http=http, **kw
    )


async def test_every_request_identifies_itself_to_the_sec(sec: FakeSec, tmp_path: Path) -> None:
    await client(sec, tmp_path).ticker_map()

    assert sec.requests[0].headers["user-agent"] == "provenance test@example.com"


async def test_resolves_tickers_to_zero_padded_ciks(sec: FakeSec, tmp_path: Path) -> None:
    tickers = await client(sec, tmp_path).ticker_map()

    assert tickers["AAPL"] == ("0000320193", "Apple Inc.")


async def test_lists_most_recent_original_10k_filings(sec: FakeSec, tmp_path: Path) -> None:
    refs = await client(sec, tmp_path).ten_k_filings("0000320193", limit=2)

    assert [r.accession for r in refs] == ["0000320193-25-000079", "0000320193-24-000123"]
    assert refs[0].report_date == date(2025, 9, 27)
    assert refs[0].url == (
        "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm"
    )


async def test_documents_are_cached_on_disk(sec: FakeSec, tmp_path: Path) -> None:
    ref = FilingRef(
        cik="0000320193",
        accession="0000320193-25-000079",
        filed=date(2025, 10, 31),
        report_date=date(2025, 9, 27),
        primary_document="aapl-20250927.htm",
    )

    first = await client(sec, tmp_path).document_html(ref)
    second = await client(sec, tmp_path).document_html(ref)

    assert first == second == "<html>10-K</html>"
    assert len(sec.requests) == 1


async def test_company_facts_are_cached_on_disk(sec: FakeSec, tmp_path: Path) -> None:
    await client(sec, tmp_path).company_facts("0000320193")
    facts = await client(sec, tmp_path).company_facts("0000320193")

    assert facts == {"facts": {}}
    assert len(sec.requests) == 1
    assert json.loads((tmp_path / "companyfacts" / "0000320193.json").read_text()) == facts


async def test_requests_are_spaced_to_respect_sec_rate_limit(sec: FakeSec, tmp_path: Path) -> None:
    clock = {"t": 0.0}
    waits: list[float] = []

    async def fake_sleep(s: float) -> None:
        waits.append(s)
        clock["t"] += s

    edgar = client(sec, tmp_path, min_interval_s=0.2, now=lambda: clock["t"], sleep=fake_sleep)

    await edgar.ticker_map()
    await edgar.company_facts("0000320193")

    assert waits == [pytest.approx(0.2)]
