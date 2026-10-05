"""Deterministic question features: which tier to start on, and the entity signature the
answer cache checks.

Rules, not a model: the classifier runs on every request, so it costs microseconds and no
tokens, and its decisions are explainable. A wrong "simple" call is cheap to recover from,
because the controller escalates small-tier answers that fail verification or confidence.
"""

import re

from pydantic import BaseModel

from provenance.ingest.corpus import COMMON_NAMES

_ALIASES = {
    "google": "GOOGL", "exxon": "XOM", "jpmorgan": "JPM", "j&j": "JNJ", "lilly": "LLY",
    "general electric": "GE", "coke": "KO", "p&g": "PG", "conoco": "COP", "facebook": "META",
}  # fmt: skip
_NAMES = {name.lower(): t for t, name in COMMON_NAMES.items()} | _ALIASES
_NAME_RE = re.compile(
    r"(?<![\w&])(" + "|".join(re.escape(n) for n in sorted(_NAMES, key=len, reverse=True))
    + r")(?![\w&])",
    re.IGNORECASE,
)  # fmt: skip
# Tickers count only in capitals and with 2+ letters: "V" or "GE" in prose is too ambiguous.
_TICKER_RE = re.compile(r"\b(" + "|".join(t for t in COMMON_NAMES if len(t) >= 2) + r")\b")
_YEAR = re.compile(r"\b(?:FY\s?)?((?:19|20)\d{2})\b", re.IGNORECASE)
_NUMBER = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*%?")

METRICS = (
    "revenue", "sales", "net income", "earnings", "eps", "per share", "operating income",
    "gross margin", "margin", "assets", "liabilities", "debt", "cash flow", "cash", "capex",
    "capital expenditure", "r&d", "research and development", "dividend", "buyback",
    "repurchase", "employees", "headcount", "segment", "risk", "guidance", "tax",
)  # fmt: skip
# Plurals count as the same metric: "risks" and "risk factors" are both about risk.
_METRIC_RE = re.compile(
    r"\b(" + "|".join(re.escape(m) for m in sorted(METRICS, key=len, reverse=True))
    + r")(?:s|es)?\b",
    re.IGNORECASE,
)  # fmt: skip

_COMPARISON = re.compile(
    r"\b(compare|compared|comparison|versus|vs\.?|relative to|difference|differ|both|"
    r"each of|between|higher|lower|more than|less than|rank|which of)\b",
    re.IGNORECASE,
)
_CALCULATION = re.compile(
    r"\b(growth|grow|grows|grew|rise|rose|fall|fell|decline|declined|change|changed|"
    r"increase|decrease|ratio|percent|percentage|cagr|"
    r"per cent|calculate|total|combined|average|share of)\b",
    re.IGNORECASE,
)
_EXPLANATION = re.compile(
    r"\b(why|explain|how did|how does|what drove|drivers?|impact|implications?|strategy)\b",
    re.IGNORECASE,
)
LONG_QUESTION_WORDS = 30


class Entities(BaseModel):
    """What a question is about. Two questions with different entities never share an
    answer, however similar their wording."""

    tickers: list[str]
    years: list[int]
    numbers: list[str]
    metrics: list[str]


class Classification(BaseModel):
    complex: bool
    reasons: list[str]
    entities: Entities


def entities(question: str) -> Entities:
    tickers = {_NAMES[m.lower()] for m in _NAME_RE.findall(question)}
    tickers |= set(_TICKER_RE.findall(question))
    years = {int(y) for y in _YEAR.findall(question)}
    without_years = _YEAR.sub(" ", question)
    numbers = {n.replace(",", "") for n in _NUMBER.findall(without_years)}
    metrics = {m.lower() for m in _METRIC_RE.findall(question)}
    return Entities(
        tickers=sorted(tickers), years=sorted(years), numbers=sorted(numbers),
        metrics=sorted(metrics),
    )  # fmt: skip


def classify(question: str) -> Classification:
    found = entities(question)
    reasons = []
    if len(found.tickers) >= 2:
        reasons.append("multiple_companies")
    if len(found.years) >= 2:
        reasons.append("multiple_years")
    if _COMPARISON.search(question):
        reasons.append("comparison")
    if _CALCULATION.search(question) or "%" in question:
        reasons.append("calculation")
    if _EXPLANATION.search(question):
        reasons.append("explanation")
    if len(question.split()) > LONG_QUESTION_WORDS:
        reasons.append("long")
    return Classification(complex=bool(reasons), reasons=reasons, entities=found)
