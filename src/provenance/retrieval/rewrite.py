"""LLM query rewriting: a keyword-rich search query plus filters (company, year, 10-K Item).

The rewrite is advisory. Output is validated against what exists (known tickers, real
years, the three Items); anything invalid is dropped, and any failure falls back to the
original query with no filters, so a flaky free-tier model can't break search.
"""

import json
import re
from typing import Protocol

from pydantic import ValidationError

from provenance.llm.types import ChatRequest, ChatResponse, Message
from provenance.retrieval.types import RewrittenQuery, SearchFilters
from provenance.security.pii import RedactedText

REWRITE_ROLE = "serve_small"
# The model over-applies section and year filters (measured: it restricted "What is
# driving data center demand at Nvidia?" to MD&A). A wrong filter silently hides the right
# passages, so these are kept only when the question itself names the section or year.
_SECTION_MENTIONS: dict[str, re.Pattern[str]] = {
    "1": re.compile(r"\bitem\s*1\b(?!\s*a)|\bbusiness (section|overview|description)\b", re.I),
    "1A": re.compile(r"\brisk factors?\b|\bitem\s*1\s*a\b", re.I),
    "7": re.compile(r"\bmd&a|\bmanagement.s discussion\b|\bitem\s*7\b(?!\s*a)", re.I),
}
_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")

_SYSTEM = """You turn a question about SEC 10-K filings into a search request.
Return only JSON: {"query": str, "tickers": [str], "fiscal_years": [int], "items": [str]}.
- query: a standalone keyword-rich search query. Keep company names and specific terms;
  drop filler words; expand abbreviations (e.g. "R&D" -> "research and development").
- tickers: only companies the question names, mapped with the list below. Empty if none.
- fiscal_years: only years the question states explicitly. Never guess. Empty if none.
- items: only if the question asks for a specific section: "1" Business, "1A" Risk Factors,
  "7" Management's Discussion and Analysis (results, outlook, liquidity). Else empty.
Companies:
{companies}"""


class Completer(Protocol):
    async def complete(self, role: str, request: ChatRequest) -> ChatResponse: ...


class QueryRewriter:
    def __init__(self, llm: Completer, companies: dict[str, str]) -> None:
        """`companies` maps ticker -> company name (public data from the companies table)."""
        self._llm = llm
        self._companies = companies
        listing = "\n".join(f"{t}: {n}" for t, n in sorted(companies.items()))
        self._system = _SYSTEM.replace("{companies}", listing)

    async def rewrite(self, question: RedactedText) -> RewrittenQuery | None:
        """None when the model fails or returns something unusable."""
        request = ChatRequest(
            messages=[
                Message(role="system", content=self._system),
                Message(role="user", content=question.text),
            ],
            json_mode=True,
            max_tokens=200,
        )
        try:
            response = await self._llm.complete(REWRITE_ROLE, request)
            return self._parse(response.content, question.text)
        except Exception:
            return None

    def _parse(self, content: str, question: str) -> RewrittenQuery | None:
        named_items = {i for i, pattern in _SECTION_MENTIONS.items() if pattern.search(question)}
        named_years = {int(y) for y in _YEAR.findall(question)}
        try:
            raw = json.loads(content)
            query = str(raw["query"]).strip()
            tickers = [str(t).upper() for t in raw.get("tickers") or []]
            years = [int(y) for y in raw.get("fiscal_years") or []]
            items = [str(i).upper() for i in raw.get("items") or []]
            filters = SearchFilters(
                tickers=sorted({t for t in tickers if t in self._companies}),
                fiscal_years=sorted({y for y in years if y in named_years}),
                items=sorted({i for i in items if i in named_items}),
            )
        except (ValueError, KeyError, TypeError, AttributeError, ValidationError):
            return None
        return RewrittenQuery(query=query, filters=filters) if query else None
