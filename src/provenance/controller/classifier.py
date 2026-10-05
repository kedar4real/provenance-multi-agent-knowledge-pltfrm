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
_FORM = re.compile(r"\b(?:10|8)-[KQ]\b", re.IGNORECASE)  # "10-K" names a filing, not a number
# Models write typographic hyphens, quotes and spaces (non-breaking hyphens in
# names, curly apostrophes); match them as their ASCII forms.
_TYPOGRAPHY = str.maketrans({
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u2018": "'", "\u2019": "'", "\u00a0": " ",
})  # fmt: skip

# Metric words -> one canonical name, so a rewording ("sales" for "revenue") keeps the same
# signature while a different metric ("net income" for "revenue") doesn't.
METRICS = {
    "revenue": "revenue", "sales": "revenue", "net sales": "revenue", "top line": "revenue",
    "net income": "net income", "profit": "net income", "net earnings": "net income",
    "earnings": "net income", "bottom line": "net income",
    # Not "per share": a dividend per share is a dividend, not EPS.
    "eps": "eps", "earnings per share": "eps",
    "operating income": "operating income", "operating profit": "operating income",
    "gross margin": "gross margin", "margin": "margin",
    "assets": "assets", "liabilities": "liabilities", "debt": "debt", "borrowings": "debt",
    "cash flow": "cash flow", "operating activities": "cash flow",
    "cash provided by": "cash flow", "cash from": "cash flow", "cash generated": "cash flow",
    "cash": "cash", "capex": "capex",
    "capital expenditure": "capex", "capital spending": "capex", "capital spend": "capex",
    "r&d": "r&d", "research and development": "r&d",
    "dividend": "dividend", "buyback": "buyback", "repurchase": "buyback",
    "repurchasing": "buyback", "repurchased": "buyback",
    "employees": "employees", "headcount": "employees", "workforce": "employees",
    "staff": "employees",
    "segment": "segment", "risk": "risk", "guidance": "guidance", "outlook": "guidance",
    "tax": "tax",
}  # fmt: skip
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
    question = question.translate(_TYPOGRAPHY)
    tickers = {_NAMES[m.lower()] for m in _NAME_RE.findall(question)}
    tickers |= set(_TICKER_RE.findall(question))
    years = {int(y) for y in _YEAR.findall(question)}
    without_years = _YEAR.sub(" ", _FORM.sub(" ", question))
    numbers = {n.replace(",", "") for n in _NUMBER.findall(without_years)}
    metrics = {METRICS[m.lower()] for m in _METRIC_RE.findall(question)}
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
