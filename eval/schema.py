"""The golden-set format.

Passages are referenced by a stable key (filing accession, 10-K Item, character offset),
never by database ID: IDs change whenever a filing is re-ingested, keys don't.
"""

from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["text", "sql", "cross", "unanswerable", "adversarial"]

# Target mix from the spec (200 cases).
QUOTAS: dict[Category, int] = {
    "text": 90,
    "sql": 40,
    "cross": 40,
    "unanswerable": 20,
    "adversarial": 10,
}


def chunk_key(accession: str, item: str, char_start: int) -> str:
    return f"{accession}:{item}:{char_start}"


class GoldFact(BaseModel):
    ticker: str
    metric: str
    fiscal_year: int
    value: float
    unit: str


class GoldenCase(BaseModel):
    id: str
    category: Category
    question: str
    # Who asks. Most cases use full access; ACL cases use a narrower principal.
    groups: list[str] = Field(default_factory=lambda: ["research_all"])
    # Any of these passages fully supports the answer (the source plus near-duplicates,
    # e.g. the same risk factor repeated in the next year's 10-K).
    gold_chunks: list[str] = Field(default_factory=list)
    gold_facts: list[GoldFact] = Field(default_factory=list)
    reference_answer: str
    # unanswerable/adversarial: the system should decline or stay within the caller's access.
    expect_abstain: bool = False
    forbidden_tickers: list[str] = Field(default_factory=list)
    source: dict[str, str | int] = Field(default_factory=dict)
    generator_model: str = "template"
    filter_verdict: str = ""
    human_checked: bool = False
