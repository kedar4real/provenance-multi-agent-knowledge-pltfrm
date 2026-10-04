"""SEC EDGAR client: identifies itself, stays under SEC's rate limit, caches everything on disk."""

import asyncio
import json
import time
from collections.abc import Awaitable, Callable
from datetime import date
from pathlib import Path
from typing import Any

import httpx2
from pydantic import BaseModel

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
_SUBMISSIONS_PAGE_URL = "https://data.sec.gov/submissions/{name}"
_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
_ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_nodash}/{document}"


class FilingRef(BaseModel):
    cik: str
    accession: str
    filed: date
    report_date: date
    primary_document: str

    @property
    def url(self) -> str:
        return _ARCHIVE_URL.format(
            cik_int=int(self.cik),
            accession_nodash=self.accession.replace("-", ""),
            document=self.primary_document,
        )


class EdgarClient:
    """SEC asks for at most 10 requests/second and a User-Agent naming the requester."""

    def __init__(
        self,
        user_agent: str,
        cache_dir: Path,
        http: httpx2.AsyncClient | None = None,
        min_interval_s: float = 0.15,
        now: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        if not user_agent.strip():
            raise ValueError("SEC requires a User-Agent with a name and contact email")
        self._http = http or httpx2.AsyncClient(timeout=60)
        self._headers = {"User-Agent": user_agent}
        self._cache = cache_dir
        self._min_interval_s = min_interval_s
        self._now = now
        self._sleep = sleep
        self._last_request = -float("inf")
        self._lock = asyncio.Lock()

    async def ticker_map(self) -> dict[str, tuple[str, str]]:
        rows = json.loads(await self._get_cached(_TICKERS_URL, self._cache / "tickers.json"))
        return {r["ticker"]: (f"{r['cik_str']:010d}", r["title"]) for r in rows.values()}

    async def ten_k_filings(self, cik: str, limit: int) -> list[FilingRef]:
        """Most recent original 10-K filings (amendments excluded), newest first.

        `recent` holds at least a year of filings; heavy filers (big banks file tens of
        thousands of notes a year) push older 10-Ks into extra pages, read only if needed.
        """
        data = json.loads(await self._get(_SUBMISSIONS_URL.format(cik=cik)))
        refs = _ten_ks(cik, data["filings"]["recent"])
        for page in data["filings"].get("files", []):
            if len(refs) >= limit:
                break
            older = json.loads(await self._get(_SUBMISSIONS_PAGE_URL.format(name=page["name"])))
            refs += _ten_ks(cik, older)
        return refs[:limit]

    async def document_html(self, ref: FilingRef) -> str:
        path = self._cache / "filings" / ref.cik / ref.accession / ref.primary_document
        return await self._get_cached(ref.url, path)

    async def company_facts(self, cik: str) -> dict[str, Any]:
        path = self._cache / "companyfacts" / f"{cik}.json"
        facts: dict[str, Any] = json.loads(await self._get_cached(_FACTS_URL.format(cik=cik), path))
        return facts

    async def _get_cached(self, url: str, path: Path) -> str:
        cached = await asyncio.to_thread(_read_if_exists, path)
        if cached is not None:
            return cached
        body = await self._get(url)
        await asyncio.to_thread(_write_atomic, path, body)
        return body

    async def _get(self, url: str) -> str:
        async with self._lock:
            wait = self._last_request + self._min_interval_s - self._now()
            if wait > 0:
                await self._sleep(wait)
            self._last_request = self._now()
            response = await self._http.get(url, headers=self._headers)
        response.raise_for_status()
        return response.text


def _read_if_exists(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def _write_atomic(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(path)


def _ten_ks(cik: str, columns: dict[str, list[str]]) -> list[FilingRef]:
    rows = zip(
        columns["form"],
        columns["accessionNumber"],
        columns["filingDate"],
        columns["reportDate"],
        columns["primaryDocument"],
        strict=True,
    )
    return [
        FilingRef(
            cik=cik,
            accession=accession,
            filed=date.fromisoformat(filed),
            report_date=date.fromisoformat(report),
            primary_document=document,
        )
        for form, accession, filed, report, document in rows
        if form == "10-K"
    ]
